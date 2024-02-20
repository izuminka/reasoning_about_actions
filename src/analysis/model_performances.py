import os.path
import sys
import json

sys.path.append('..')
sys.path.append('../questions_construction')
sys.path.append('../../')

from sklearn.metrics import f1_score
from rouge_score import rouge_scorer
import numpy as np

from src.questions_construction.main import *
from src.common import *

ALL_LENGTHS_KEY = 'all_lengths'
ALL_DOMAINS_KEY = 'all_domains'
ALL_CATEGORIES_KEY = 'all_categories'

F1_SCORE_TYPE = 'micro'
ROUGE_SCORE_TYPE = 'rougeL'
ROUGE_SCORER = rouge_scorer.RougeScorer([ROUGE_SCORE_TYPE], use_stemmer=True)


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


def filter(data_all, filter_by):
    results = []
    for d in data_all:
        if all(d[k] == v for k, v in filter_by):
            results.append(d)
    return results


def filter_data(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain, answer_type):
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

    return filter(data_all, filter_by)


def filter_results(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                   answer_type):
    filter_by = [(SK_RAMIFICATION, ramifications),
                 (SK_MODEL, model_name),
                 (SK_PROMPT_TYPE, prompt_type),
                 (OUT_OBJ_ANSWER_TYPE, answer_type),
                 (SK_DOMAIN, domain),
                 (OUT_OBJ_QUESTION_CATEGORY, question_category),
                 (OUT_OBJ_PLAN_LENGTH, plan_length)]
    return filter(data_all, filter_by)


class BaseStats:
    def __init__(self, plan_length, question_category, ramifications, model_name, prompt_type, domain):
        self.plan_length = plan_length
        self.question_category = question_category
        self.ramifications = ramifications
        self.model_name = model_name
        self.prompt_type = prompt_type
        self.domain = domain
        self.result = None

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
    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain)
        self.answer_type = TRUE_FALSE_ANSWER
        self.data = filter_data(data_all, plan_length, question_category, ramifications, model_name,
                                prompt_type, domain, self.answer_type)

    def f1_score_in_response(self, score_type=F1_SCORE_TYPE):
        if not self.data:
            return None

        true = []
        pred = []
        UNKNOWN = 'unknown'
        for d in self.data:
            true.append(d[OUT_OBJ_ANSWER])
            # pred.append(d[MODEL_RESPONSE_KEY])
            if d[OUT_OBJ_ANSWER] in d[MODEL_RESPONSE_KEY]:
                pred.append(d[OUT_OBJ_ANSWER])
            else:
                pred.append(UNKNOWN)
        return f1_score(true, pred, average=score_type)

    def compute(self):
        self.result = self.f1_score_in_response()
        return self.out_object(self.result)


class FreeAnswerStats(BaseStats):

    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain)
        self.answer_type = FREE_ANSWER
        self.data = filter_data(data_all, plan_length, question_category, ramifications, model_name,
                                prompt_type, domain, self.answer_type)

    def get_rouge_score(self):
        stats = []
        for d in self.data:
            scores = ROUGE_SCORER.score(d[OUT_OBJ_ANSWER], d[MODEL_RESPONSE_KEY])
            stats.append(scores[ROUGE_SCORE_TYPE].fmeasure)
        return np.mean(stats)

    def compute(self):
        self.result = self.get_rouge_score()
        return self.out_object(self.result)


def big_for_loop(answer_response):
    results = []
    for domain in DOMAIN_NAMES + [ALL_DOMAINS_KEY]:
        for plan_length in PLAN_LENGTHS + [ALL_LENGTHS_KEY]:
            for question_category in QUESTION_CATEGORIES + [ALL_CATEGORIES_KEY]:
                for ramifications in RAMIFICATION_TYPES:
                    for model_name in PROMPT_MODEL_NAMES:
                        for prompt_type in PROMPT_TYPES:
                            if answer_response == TRUE_FALSE_ANSWER:
                                stats = TrueFalseStats(data_all, plan_length, question_category, ramifications,
                                                       model_name,
                                                       prompt_type, domain)
                            else:
                                stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                                                        model_name,
                                                        prompt_type, domain)
                            results.append(stats.compute())
    return results


if __name__ == '__main__':
    data_all = gather_data()

    for answer_response in [TRUE_FALSE_ANSWER, FREE_ANSWER]:
        results = big_for_loop(answer_response)
        if not os.path.exists(STATISTICS_PATH):
            os.makedirs(STATISTICS_PATH)
        save_jsonl(results, os.path.join(STATISTICS_PATH, f'{answer_response}.jsonl'))
        print('saved', answer_response)
