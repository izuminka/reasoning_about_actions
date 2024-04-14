import json
from sklearn.metrics import f1_score, accuracy_score
from rouge_score import rouge_scorer
import numpy as np
from copy import deepcopy

import sys

sys.path.insert(0, '../../')
from src.questions_construction.main import PLAN_LENGTHS, QUESTION_CATEGORIES
from src.common import *

# STATS dict keys
SK_RAMIFICATION = 'ramification_type'
SK_SUBSTITUTION = 'substitution_type'
SK_MODEL = 'model'
SK_PROMPT_TYPE = 'prompt_type'
SK_DOMAIN = 'domain'
SK_INSTANCE = 'instance'
SK_RESULT = 'result'

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

PROMPT_MODEL_NAMES = ['Mistral-7B-Instruct-v0.2', 'gemini', 'Llama-2-7b-chat-hf']  # TODO add , 'gpt4'
PROMPT_TYPES = ['few_shot_1', 'few_shot_3', 'few_shot_5']  # TODO clean up dirs, few_shot_5_cot
SUBSTITUTION_TYPES = [WITH_RANDOM_SUB, WITHOUT_RANDOM_SUB]

RAMIFICATION_TYPES = [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]
FLUENT_TYPES = [POSITIVE_FLUENT_NL, NEGATIVE_FLUENT_NL, POSITIVE_FLUENTS_NL, NEGATIVE_FLUENTS_NL, None]
IS_POS_FLUENT_TYPES = [True, False, None]


def gather_questions(questions_dir):
    all_data = {}
    for substitutions in SUBSTITUTION_TYPES:
        for domain in DOMAIN_NAMES:
            for instance in [f'Instance_{i}' for i in range(1, 11)]:
                results_domain_path = f'{questions_dir}/{substitutions}/{domain}/{instance}.jsonl'
                if not os.path.exists(results_domain_path):
                    print("missing", results_domain_path)
                else:
                    qa_objects = open_jsonl(results_domain_path)
                    for d in qa_objects:
                        if d[OUT_OBJ_ID] in all_data:
                            raise ValueError(f"Duplicate ID {d[OUT_OBJ_ID]}")
                        del d[OUT_OBJ_INITIAL_STATE_ASP]
                        del d[OUT_OBJ_INITIAL_STATE_NL]
                        del d[OUT_OBJ_ACTION_SEQUENCE]
                        all_data[d[OUT_OBJ_ID]] = d
    return all_data

def sanity_checks():
    def get_questions_ids(questions_dir):
        questions_ids = set()
        for substitutions in SUBSTITUTION_TYPES:
            for domain in DOMAIN_NAMES:
                for instance in [f'Instance_{i}' for i in range(1, 11)]:
                    try:
                        for d in open_jsonl(f'{questions_dir}/{substitutions}/{domain}/{instance}.jsonl'):
                            questions_ids.add(d[OUT_OBJ_ID])
                    except:
                        pass

        return questions_ids

    def get_results_ids(results_dir):
        results_ids = set()
        for substitutions in SUBSTITUTION_TYPES:
            for domain in DOMAIN_NAMES:
                for instance in [f'Instance_{i}' for i in range(1, 11)]:
                    for ramifications in RAMIFICATION_TYPES:
                        for prompt_type in PROMPT_TYPES:
                            for model in PROMPT_MODEL_NAMES:
                                try:
                                    for d in open_jsonl(f'{results_dir}/{model}/{substitutions}/{ramifications}/{prompt_type}/{domain}/{instance}.jsonl'):
                                        results_ids.add(d[OUT_OBJ_ID])
                                except:
                                    pass
        return results_ids

    # def get_data_for_evaluation_ids(data_for_evaluation_dir):
    #     data_for_evaluation_ids = set()
    #     for substitutions in SUBSTITUTION_TYPES:
    #         for domain in DOMAIN_NAMES:
    #             for instance in [f'Instance_{i}' for i in range(1, 11)]:
    #                 for ramifications in RAMIFICATION_TYPES:
    #                     for prompt_type in PROMPT_TYPES:
    #                         try:
    #                             for d in open_jsonl(f'{data_for_evaluation_dir}/{substitutions}/{ramifications}/{prompt_type}/{domain}/{instance}.jsonl'):
    #                                 data_for_evaluation_ids.add(d[OUT_OBJ_ID])
    #                         except:
    #                             pass
    #     return data_for_evaluation_ids


    # data_for_evaluation_dir = f'{DATA_PATH}/data_for_evaluation'

    results_ids = get_results_ids(RESULTS_PATH)
    questions_ids = get_questions_ids( f'{DATA_PATH}/questions_m1')
    # print(len(data_for_eval_ids), len(questions_ids), len(results_ids))
    # print(len(results_ids), len(questions_ids), len(results_ids - questions_ids), len(questions_ids - results_ids))
    assert results_ids <= questions_ids

    return True



def gather_data(questions_by_id):
    results_dir = RESULTS_PATH
    all_data = []
    for substitutions in SUBSTITUTION_TYPES:
        for ramifications in RAMIFICATION_TYPES:
            for model_name in PROMPT_MODEL_NAMES:
                for prompt_type in PROMPT_TYPES:
                    for domain in DOMAIN_NAMES:
                        for instance in [f'Instance_{i}' for i in range(1, 11)]:
                            results_domain_path = f'{results_dir}/{model_name}/{substitutions}/{ramifications}/{prompt_type}/{domain}/{instance}.jsonl'
                            if not os.path.exists(results_domain_path):
                                print("missing", results_domain_path)
                            else:
                                extra_kv = {SK_PROMPT_TYPE: prompt_type,
                                            SK_MODEL: model_name,
                                            SK_RAMIFICATION: ramifications,
                                            SK_SUBSTITUTION: substitutions,
                                            SK_DOMAIN: domain,
                                            SK_INSTANCE: instance}
                                qa_objects = open_jsonl(results_domain_path)
                                for d in qa_objects:
                                    if d[OUT_OBJ_ID] not in questions_by_id:
                                        raise ValueError(f"Missing question {d[OUT_OBJ_ID]}")
                                    d.update(questions_by_id[d[OUT_OBJ_ID]])
                                    d.update(deepcopy(extra_kv))
                                all_data.extend(qa_objects)
    return all_data



def filter_helper(data_ls, filter_by):
    results = {}
    for d in data_ls:
        if all(d[k] == v for k, v in filter_by):
            if d[OUT_OBJ_ID] in results:
                raise ValueError(f"Duplicate ID {d[OUT_OBJ_ID]}")  # TODO rm after testing
            results[d[OUT_OBJ_ID]] = d
    return results


def filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                          answer_type, substitutions):
    """ if ALL_DOMAINS_KEY or ALL_CATEGORIES_KEY or ALL_LENGTHS_KEY selects multiple values from data_all"""
    filter_by = [(SK_RAMIFICATION, ramifications),
                 (SK_MODEL, model_name),
                 (SK_PROMPT_TYPE, prompt_type),
                 (SK_SUBSTITUTION, substitutions),
                 (OUT_OBJ_ANSWER_TYPE, answer_type)]
    if domain != ALL_DOMAINS_KEY:
        filter_by.append((SK_DOMAIN, domain))
    if question_category != ALL_CATEGORIES_KEY:
        filter_by.append((OUT_OBJ_QUESTION_CATEGORY, question_category))
    if plan_length != ALL_LENGTHS_KEY:
        filter_by.append((OUT_OBJ_PLAN_LENGTH, plan_length))
    return filter_helper(data_all, filter_by)


# def filter_single_selector(results_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
#                            answer_type):
#     filter_by = [(SK_RAMIFICATION, ramifications),
#                  (SK_MODEL, model_name),
#                  (SK_PROMPT_TYPE, prompt_type),
#                  (OUT_OBJ_ANSWER_TYPE, answer_type),
#                  (SK_DOMAIN, domain),
#                  (OUT_OBJ_QUESTION_CATEGORY, question_category),
#                  (OUT_OBJ_PLAN_LENGTH, plan_length)]
#     return filter_helper(results_all, filter_by)


class BaseStats:
    def __init__(self, plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions):
        self.plan_length = plan_length
        self.question_category = question_category
        self.ramifications = ramifications
        self.model_name = model_name
        self.prompt_type = prompt_type
        self.domain = domain
        self.substitutions = substitutions

        self.answer_type = None
        self.result = None

    def out_object(self, result):
        '''returns a dictionary with the stats of the object,
        result is a float'''
        return {SK_RESULT: result,

                SK_MODEL: self.model_name,
                SK_PROMPT_TYPE: self.prompt_type,
                SK_RAMIFICATION: self.ramifications,
                SK_SUBSTITUTION: self.substitutions,
                SK_DOMAIN: self.domain,

                OUT_OBJ_PLAN_LENGTH: self.plan_length,
                OUT_OBJ_ANSWER_TYPE: self.answer_type,
                OUT_OBJ_QUESTION_CATEGORY: self.question_category}


class TrueFalseStats(BaseStats):
    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                 substitutions,
                 score_type=F1_SCORE_KEY):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions)
        self.answer_type = TRUE_FALSE_ANSWER_TYPE
        self.score_type = score_type
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type, substitutions)

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

    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                 substitutions):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions)
        self.answer_type = FREE_ANSWER_TYPE
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type, substitutions)

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
                    for random_sub in SUBSTITUTION_TYPES:
                        for model_name in PROMPT_MODEL_NAMES:
                            for prompt_type in PROMPT_TYPES:
                                if answer_response == TRUE_FALSE_ANSWER_TYPE:
                                    stats = TrueFalseStats(data_all, plan_length, question_category, ramifications,
                                                           model_name,
                                                           prompt_type, domain, random_sub, tf_score_key)
                                else:
                                    stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                                                            model_name,
                                                            prompt_type, domain, random_sub)
                                stats_compute = stats.compute()
                                if stats_compute[SK_RESULT]:
                                    save_dir = os.path.join(STATISTICS_PATH, answer_response)
                                    os.makedirs(save_dir, exist_ok=True)
                                    file_name = f'{domain}.{prompt_type}.{question_category}.{ramifications}.{random_sub}.{model_name}.{answer_response}.{tf_score_key}.json'
                                    with open(os.path.join(save_dir, file_name), 'w') as f:
                                        json.dump(stats_compute, f)
                                results.append(stats.compute())
    return results


def save_stats_file(answer_response, score_key):
    return f'{answer_response}.{score_key}.jsonl'


if __name__ == '__main__':
    sanity_checks()


    if not os.path.exists(STATISTICS_PATH):
        os.makedirs(STATISTICS_PATH)

    questions_dir = f'{DATA_PATH}/questions_m1'
    questions_by_id = gather_questions(questions_dir)

    data_all = gather_data(questions_by_id)
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
