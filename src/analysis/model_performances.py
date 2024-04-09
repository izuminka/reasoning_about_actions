import os.path
import sys
import json

sys.path.append('..')
sys.path.append('../questions_construction')
sys.path.append('../../')

from sklearn.metrics import f1_score, accuracy_score
from rouge_score import rouge_scorer
import numpy as np

from src.questions_construction.main import *
from src.common import *

# STATS dict keys
SK_PLAN_LENGTH = OUT_OBJ_PLAN_LENGTH
SK_CATEGORY = OUT_OBJ_QUESTION_CATEGORY
SK_RAMIFICATION = 'ramification_type'
SK_ANSWER_TYPE = OUT_OBJ_ANSWER_TYPE
SK_MODEL = 'model'
SK_PROMPT_TYPE = 'prompt_type'
SK_RESULT = 'result'
SK_DOMAIN = 'domain'

# Metrics & Metrics Related
F1_SCORE_KEY = 'f1'
F1_SCORE_TYPE = 'micro'
ACCURACY_SCORE_KEY = 'accuracy'
SCORE_KEYS = [F1_SCORE_KEY, ACCURACY_SCORE_KEY]

ROUGE_SCORE_TYPE = 'rougeL'
ROUGE_SCORER = rouge_scorer.RougeScorer([ROUGE_SCORE_TYPE], use_stemmer=True)

TRUE_ANSWER = 'True'
FALSE_ANSWER = 'False'
ANSWER_RESPONSES = [TRUE_FALSE_ANSWER_TYPE, FREE_ANSWER_TYPE]


ALL_LENGTHS_KEY = 'all_lengths'
ALL_DOMAINS_KEY = 'all_domains'
ALL_CATEGORIES_KEY = 'all_categories'

DOMAIN_NAMES = ['blocksworld', 'depots', 'driverlog', 'goldminer', 'grippers', 'logistics', 'miconic', 'mystery',
                'npuzzle', 'satellite', 'spanner', 'visitall', 'zenotravel']

PROMPT_MODEL_NAMES = ['gemini', 'llama-2-7b', 'mistral_7b_instruct']  # TODO add , 'gpt4'
PROMPT_TYPES = ['zero_shot_data', 'few_shot_4', 'few_shot_4_cot']  # TODO clean up dirs

def gather_data():
    all_data = []
    for ramifications in RAMIFICATION_TYPES:
        if ramifications == WITH_RAMIFICATIONS:
            results_dir = f'{PROJECT_PATH}/results_ramifications'  # todo rn to results dir
        elif ramifications == WITHOUT_RAMIFICATIONS:
            results_dir = RESULTS_PATH
        else:
            raise f"{ramifications} is not defined"
        for model_name in PROMPT_MODEL_NAMES:
            for prompt_type in PROMPT_TYPES:
                for domain in DOMAIN_NAMES:
                    results_domain_path = f'{results_dir}/{model_name}/{prompt_type}/{domain}.jsonl'
                    if not os.path.exists(results_domain_path):
                        print("missing", results_domain_path)
                    else:
                        extra_kv = {SK_PROMPT_TYPE: prompt_type, SK_MODEL: model_name, SK_RAMIFICATION: ramifications,
                                    SK_DOMAIN: domain}
                        qa_objects = open_jsonl(results_domain_path)
                        all_data.extend([d | deepcopy(extra_kv) for d in qa_objects])
    return all_data


def filter_helper(data_ls, filter_by):
    results = []
    for d in data_ls:
        if all(d[k] == v for k, v in filter_by):
            results.append(d)
    return results


def filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                          answer_type):
    """ if ALL_DOMAINS_KEY or ALL_CATEGORIES_KEY or ALL_LENGTHS_KEY selects multiple values from data_all"""
    filter_by = [(SK_RAMIFICATION, ramifications),
                 (SK_MODEL, model_name),
                 (SK_PROMPT_TYPE, prompt_type),
                 (OUT_OBJ_ANSWER_TYPE, answer_type)]
    if domain != ALL_DOMAINS_KEY:
        filter_by.append((SK_DOMAIN, domain))
    if question_category != ALL_CATEGORIES_KEY:
        filter_by.append((OUT_OBJ_QUESTION_CATEGORY, question_category))
    if plan_length != ALL_LENGTHS_KEY:
        filter_by.append((OUT_OBJ_PLAN_LENGTH, plan_length))
    return filter_helper(data_all, filter_by)


def filter_single_selector(results_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                           answer_type):
    filter_by = [(SK_RAMIFICATION, ramifications),
                 (SK_MODEL, model_name),
                 (SK_PROMPT_TYPE, prompt_type),
                 (OUT_OBJ_ANSWER_TYPE, answer_type),
                 (SK_DOMAIN, domain),
                 (OUT_OBJ_QUESTION_CATEGORY, question_category),
                 (OUT_OBJ_PLAN_LENGTH, plan_length)]
    return filter_helper(results_all, filter_by)


class BaseStats:
    def __init__(self, plan_length, question_category, ramifications, model_name, prompt_type, domain):
        self.plan_length = plan_length
        self.question_category = question_category
        self.ramifications = ramifications
        self.model_name = model_name
        self.prompt_type = prompt_type
        self.domain = domain
        self.result = None
        self.answer_type = None

    def out_object(self, result):
        return {SK_PLAN_LENGTH: self.plan_length,
                SK_CATEGORY: self.question_category,
                SK_RAMIFICATION: self.ramifications,
                SK_MODEL: self.model_name,
                SK_PROMPT_TYPE: self.prompt_type,
                SK_DOMAIN: self.domain,
                SK_ANSWER_TYPE: self.answer_type,
                SK_RESULT: result}


class TrueFalseStats(BaseStats):
    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                 score_type=F1_SCORE_KEY):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain)
        self.answer_type = TRUE_FALSE_ANSWER_TYPE
        self.score_type = score_type
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type)

    @staticmethod
    def prediction_selection_criteria(d):
        model_response = d[MODEL_RESPONSE_KEY]
        # if the model response is unknown, set the response to the opposite of the ground truth
        response_to_unknown = str(not eval(d[OUT_OBJ_ANSWER]))

        if TRUE_ANSWER in model_response and FALSE_ANSWER in model_response:  # both T and F are present
            return response_to_unknown
        elif TRUE_ANSWER not in model_response and FALSE_ANSWER not in model_response:  # neither T or F are present
            return response_to_unknown
        elif TRUE_ANSWER in model_response:
            return TRUE_ANSWER
        elif FALSE_ANSWER in model_response:
            return FALSE_ANSWER
        else:
            raise f"Unknown model response {model_response}"

    def compute(self):
        if not self.data:
            return self.out_object(None)

        true = [d[OUT_OBJ_ANSWER] for d in self.data]
        pred = [self.prediction_selection_criteria(d) for d in self.data]

        if self.score_type == F1_SCORE_KEY:
            self.result = f1_score(true, pred, average=F1_SCORE_TYPE)
        elif self.score_type == ACCURACY_SCORE_KEY:
            self.result = accuracy_score(true, pred)
        else:
            raise f"Unknown score_type {self.score_type}"
        return self.out_object(self.result)


class FreeAnswerStats(BaseStats):

    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain)
        self.answer_type = FREE_ANSWER_TYPE
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type)

    def get_rouge_score(self):
        stats = []
        for d in self.data:
            # TODO, hande a case when model gives "OUTPUT is TOO LONG"
            scores = ROUGE_SCORER.score(d[OUT_OBJ_ANSWER], d[MODEL_RESPONSE_KEY])
            stats.append(scores[ROUGE_SCORE_TYPE].fmeasure)
        return np.mean(stats)

    def compute(self):
        self.result = self.get_rouge_score()
        return self.out_object(self.result)


def big_for_loop(data_all, answer_response, tf_score_key=F1_SCORE_KEY):
    results = []
    for domain in DOMAIN_NAMES + [ALL_DOMAINS_KEY]:
        for plan_length in PLAN_LENGTHS + [ALL_LENGTHS_KEY]:
            for question_category in QUESTION_CATEGORIES + [ALL_CATEGORIES_KEY]:
                for ramifications in RAMIFICATION_TYPES:
                    for model_name in PROMPT_MODEL_NAMES:
                        for prompt_type in PROMPT_TYPES:
                            if answer_response == TRUE_FALSE_ANSWER_TYPE:
                                stats = TrueFalseStats(data_all, plan_length, question_category, ramifications,
                                                       model_name,
                                                       prompt_type, domain, tf_score_key)
                            else:
                                stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                                                        model_name,
                                                        prompt_type, domain)
                            results.append(stats.compute())
    return results


def save_stats_file(answer_response, score_key):
    return f'{answer_response}.{score_key}.jsonl'


if __name__ == '__main__':
    if not os.path.exists(STATISTICS_PATH):
        os.makedirs(STATISTICS_PATH)
    data_all = gather_data()
    print('data is gathered')

    answer_response = TRUE_FALSE_ANSWER_TYPE
    for score_key in SCORE_KEYS:
        results = big_for_loop(data_all, answer_response, score_key)
        save_jsonl(results, os.path.join(STATISTICS_PATH, save_stats_file(answer_response, score_key)))
        print('saved', answer_response, score_key)

    # answer_response = FREE_ANSWER
    # results = big_for_loop(answer_response)
    # save_jsonl(results, os.path.join(STATISTICS_PATH, f'{answer_response}.jsonl'))
    # print('saved', answer_response)
