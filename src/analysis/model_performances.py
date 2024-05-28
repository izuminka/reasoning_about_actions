import json
from sklearn.metrics import f1_score, accuracy_score
from rouge_score import rouge_scorer
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from collections import defaultdict

import sys

sys.path.insert(0, '../../')
from src.questions_construction.main import PLAN_LENGTHS, QUESTION_CATEGORIES
from src.questions_construction.domains import DOMAIN_NAMES
from src.common import *

# STATS dict keys
SK_RAMIFICATION = 'ramification_type'
SK_SUBSTITUTION = 'substitution_type'
SK_MODEL = 'model'
SK_PROMPT_TYPE = 'prompt_type'
SK_RESULT = 'result'
SK_RESULT_OTHER = 'result_other'
SK_STATS = 'stats'
SK_UNIQUE_ID = 'unique_id'
SK_ERROR_MESSAGE = 'error_message'

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

ALL_LENGTHS_KEY = 'ALL_LENGTHS'
ALL_QUESTION_CATEGORIES_KEY = 'ALL_CATEGORIES'

ALL_DOMAINS_KEY = 'ALL_DOMAINS'
TRANSPORTATION_DOMAIN_KEY = 'TRANSPORTATION'
TRANSPORTATION_DOMAINS = ['logistics', 'depots', 'driverlog', 'grippers', 'miconic', 'mystery', 'zenotravel']
NON_TRANSPORTATION_DOMAIN_KEY = 'NON_TRANSPORTATION'
NON_TRANSPORTATION_DOMAINS = ['blocksworld', 'goldminer', 'npuzzle', 'satellite', 'spanner', 'visitall']
BY_DOMAIN_KEY = {TRANSPORTATION_DOMAIN_KEY: TRANSPORTATION_DOMAINS,
                 NON_TRANSPORTATION_DOMAIN_KEY: NON_TRANSPORTATION_DOMAINS,
                 ALL_DOMAINS_KEY: DOMAIN_NAMES}
RESULTS_FILE_NAME = 'results.json'
IS_POS_FLUENT_TYPES = [True, False, None]

PLAN_LENGTHS = [1, 10, 19]
SMALL_MODELS = ['gemma-2b', 'gemma-7b', 'llama2-7b-chat', 'llama2-13b-chat']
BIG_MODELS = ['gemini'] #, 'GPT-4'
PROMPT_MODEL_NAMES = SMALL_MODELS + BIG_MODELS
PROMPT_TYPES = ['few_shot_1', 'few_shot_5'] #, 'few_shot_3'
SUBSTITUTION_TYPES = [WITH_RANDOM_SUB, WITHOUT_RANDOM_SUB]
RAMIFICATION_TYPES = [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]


def gather_data_iterator():
    for substitutions in SUBSTITUTION_TYPES:
        for ramifications in RAMIFICATION_TYPES:
            for model_name in PROMPT_MODEL_NAMES:
                for prompt_type in PROMPT_TYPES:
                    yield substitutions, ramifications, model_name, prompt_type
def for_loop_all_iterator():
    domains = DOMAIN_NAMES + [ALL_DOMAINS_KEY, TRANSPORTATION_DOMAIN_KEY, NON_TRANSPORTATION_DOMAIN_KEY]
    question_categories = QUESTION_CATEGORIES + [ALL_QUESTION_CATEGORIES_KEY]

    total_len = len(list(gather_data_iterator()))*len(PLAN_LENGTHS)*len(domains)*len(question_categories)
    with tqdm(total=total_len) as pbar:
        for substitutions, ramifications, model_name, prompt_type in gather_data_iterator():
            for domain in domains:
                for plan_length in PLAN_LENGTHS:
                    for question_category in QUESTION_CATEGORIES + [ALL_QUESTION_CATEGORIES_KEY]:
                        pbar.update(1)
                        yield domain, plan_length, question_category, ramifications, substitutions, model_name, prompt_type

def gather_questions(questions_dir, selected_ids=None, delete_other_keys=True):
    all_data = defaultdict(dict)
    for substitutions in SUBSTITUTION_TYPES:
        for domain in DOMAIN_NAMES:
            for instance in [f'Instance_{i}' for i in range(1, 11)]:
                results_domain_path = f'{questions_dir}/{substitutions}/{domain}/{instance}.jsonl'
                if not os.path.exists(results_domain_path):
                    print("missing", results_domain_path)
                else:
                    qa_objects = open_jsonl(results_domain_path)
                    for d in qa_objects:
                        if selected_ids and d[OUT_OBJ_ID] not in selected_ids:
                            continue
                        if d[OUT_OBJ_ID] in all_data and substitutions in all_data[d[OUT_OBJ_ID]]:
                            raise ValueError(f"Duplicate question {d[OUT_OBJ_ID]}, {substitutions}")
                        if delete_other_keys:
                            del d[OUT_OBJ_INITIAL_STATE_ASP]
                            del d[OUT_OBJ_INITIAL_STATE_NL]
                            del d[OUT_OBJ_ACTION_SEQUENCE]
                        all_data[d[OUT_OBJ_ID]][substitutions] = d
    print('questions gathered')
    return all_data


def sanity_checks(questions_by_id, data_all):
    results_ids = set([d[OUT_OBJ_ID] for d in data_all])
    questions_ids = set(questions_by_id.keys())
    assert results_ids <= questions_ids
    print('checks passed')
    return True


def gather_data(questions_by_id, selected_ids=None, iterator=gather_data_iterator, results_dir=RESULTS_PATH):
    if selected_ids and set(selected_ids).intersection(set(questions_by_id.keys())) != set(selected_ids):
        raise ValueError(f"Missing questions set(selected_ids).intersection(set(questions_by_id.keys())) != set(selected_ids)")

    all_data = []
    missing_data = []
    unique_ids = set()
    total_len = len(list(iterator()))
    with tqdm(total=total_len*len(DOMAIN_NAMES)*10) as pbar:
        for substitutions, ramifications, model_name, prompt_type in iterator():
            for domain in DOMAIN_NAMES:
                for instance in [f'Instance_{i}' for i in range(1, 11)]:
                    pbar.update(1)
                    results_domain_path = f'{results_dir}/{model_name}/{substitutions}/{ramifications}/{prompt_type}/{domain}/{instance}.jsonl'
                    if not os.path.exists(results_domain_path):
                        missing_data.append({SK_MODEL: model_name,
                                             SK_PROMPT_TYPE: prompt_type,
                                             SK_RAMIFICATION: ramifications,
                                             SK_SUBSTITUTION: substitutions,
                                             OUT_OBJ_DOMAIN_NAME: domain,
                                             OUT_OBJ_INSTANCE_ID: instance})
                        continue
                    extra_kv = {SK_MODEL: model_name,
                                SK_PROMPT_TYPE: prompt_type,
                                SK_RAMIFICATION: ramifications,
                                SK_SUBSTITUTION: substitutions}
                    qa_objects = open_jsonl(results_domain_path)
                    if selected_ids:
                        qa_objects = [d for d in qa_objects if d[OUT_OBJ_ID] in selected_ids]
                        if not qa_objects:
                            print(f"Selected IDs are missing for: {model_name}, {substitutions}, {ramifications}, {prompt_type}, {domain}, {instance}")
                    for d in qa_objects:
                        if d[OUT_OBJ_ID] not in questions_by_id:
                            raise ValueError(f"Missing question {d[OUT_OBJ_ID]}")
                        d.update(questions_by_id[d[OUT_OBJ_ID]][substitutions])
                        d.update(deepcopy(extra_kv))
                        d[SK_UNIQUE_ID] = f"{d[OUT_OBJ_ID]}::{model_name}::{prompt_type}::{ramifications}::{substitutions}"
                        if d[SK_UNIQUE_ID] not in unique_ids:
                            unique_ids.add(d[SK_UNIQUE_ID])
                            all_data.append(d)
    print('data is gathered')
    return all_data, missing_data


def base_filter(ramifications, model_name, prompt_type, answer_type, substitutions):
    """ if ALL_DOMAINS_KEY or ALL_CATEGORIES_KEY or ALL_LENGTHS_KEY selects multiple values from data_all"""
    return [(SK_RAMIFICATION, {ramifications}),
            (SK_MODEL, {model_name}),
            (SK_PROMPT_TYPE, {prompt_type}),
            (SK_SUBSTITUTION, {substitutions}),
            (OUT_OBJ_ANSWER_TYPE, {answer_type})]


def filter_gather(data_all, filter_by):
    results = []
    for d in data_all:
        if all(d[k] in v for k, v in filter_by):
            results.append(d)
    return results


def filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                          answer_type, substitutions):
    """ if ALL_DOMAINS_KEY or ALL_CATEGORIES_KEY or ALL_LENGTHS_KEY selects multiple values from data_all"""
    filter_by = base_filter(ramifications, model_name, prompt_type, answer_type, substitutions)
    if domain == TRANSPORTATION_DOMAIN_KEY:
        filter_by.append((OUT_OBJ_DOMAIN_NAME, set(TRANSPORTATION_DOMAINS)))
    elif domain == NON_TRANSPORTATION_DOMAIN_KEY:
        filter_by.append((OUT_OBJ_DOMAIN_NAME, set(NON_TRANSPORTATION_DOMAINS)))
    elif domain != ALL_DOMAINS_KEY:
        filter_by.append((OUT_OBJ_DOMAIN_NAME, {domain}))

    if question_category != ALL_QUESTION_CATEGORIES_KEY:
        filter_by.append((OUT_OBJ_QUESTION_CATEGORY, {question_category}))
    if plan_length != ALL_LENGTHS_KEY:
        filter_by.append((OUT_OBJ_PLAN_LENGTH, {plan_length}))

    return filter_gather(data_all, filter_by)


def filter_single_selector(stats_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                           answer_type, substitutions):
    filter_by = base_filter(ramifications, model_name, prompt_type, answer_type, substitutions)
    filter_by.extend([(OUT_OBJ_QUESTION_CATEGORY, {question_category}),
                      (OUT_OBJ_DOMAIN_NAME, {domain}),
                      (OUT_OBJ_PLAN_LENGTH, {plan_length})
                      ])

    results = filter_gather(stats_all, filter_by)
    if len(results) == 0:
        return None
    elif not len(results) == 1:
        raise ValueError(f'len(instance) == {len(results)}')
    else:
        return results[0]  # [SK_RESULT]


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

    def out_object(self, result, stats=None, result_other=None, error_message=None):
        '''returns a dictionary with the stats of the object,
        result is a float'''
        return {SK_RESULT: result,
                SK_STATS: stats,
                SK_RESULT_OTHER: result_other,

                SK_MODEL: self.model_name,
                SK_PROMPT_TYPE: self.prompt_type,
                SK_RAMIFICATION: self.ramifications,
                SK_SUBSTITUTION: self.substitutions,

                OUT_OBJ_DOMAIN_NAME: self.domain,
                OUT_OBJ_PLAN_LENGTH: self.plan_length,
                OUT_OBJ_QUESTION_CATEGORY: self.question_category,
                OUT_OBJ_ANSWER_TYPE: self.answer_type,

                SK_ERROR_MESSAGE: error_message}

    def remove_corrupted(self, message='NO RESPONSE'):
        not_corrupted = []
        for d in self.data:
            if d[MODEL_RESPONSE_KEY] != message:
                not_corrupted.append(d)
        return not_corrupted


class TrueFalseStats(BaseStats):
    BOTH_ARE_PRESENT_KEY = 'both_present'
    BOTH_ARE_ABSENT_KEY = 'both_absent'

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
        tokens_to_consider = model_response.split()
        # tokens_to_consider = tokens_to_consider[:10]+tokens_to_consider[-10:]
        tokens = set([token.strip(',."\':;?!\n ').lower() for token in tokens_to_consider])

        if 'true' in tokens and 'false' in tokens:
            return TrueFalseStats.BOTH_ARE_PRESENT_KEY
        elif 'true' not in tokens and 'false' not in tokens:
            return TrueFalseStats.BOTH_ARE_ABSENT_KEY
        elif 'true' in tokens:
            return TRUE_ANSWER
        elif 'false' in tokens:
            return FALSE_ANSWER
        else:
            return ValueError(f"Unknown prediction {model_response}")

    def compute(self):
        if not self.data:
            res = self.out_object(None, None, error_message='self.data is empty')
            # print(f"No data for {res}")
            return res

        not_corrupted_data = self.remove_corrupted()
        if not not_corrupted_data:
            res = self.out_object(None, None, error_message='All corrupted')
            # print(f"All corrupted {res}")
            return res
        stats = {'num_original': len(self.data),
                 'num_corrupted': len(self.data) - len(not_corrupted_data),
                 'num_not_corrupted': len(not_corrupted_data)}

        true = []
        pred = []
        both_present = 0
        both_absent = 0
        for d in not_corrupted_data:
            true.append(d[OUT_OBJ_ANSWER])
            prediction = self.prediction_selection_criteria(d)
            # if the model response is unknown, set the response to the opposite of the ground truth
            response_to_unknown = str(not eval(d[OUT_OBJ_ANSWER]))
            if prediction == self.BOTH_ARE_PRESENT_KEY:
                both_present += 1
                pred.append(response_to_unknown)
            elif prediction == self.BOTH_ARE_ABSENT_KEY:
                both_absent += 1
                pred.append(response_to_unknown)
            else:
                pred.append(prediction)
        stats |= {self.BOTH_ARE_PRESENT_KEY: both_present,
                  self.BOTH_ARE_ABSENT_KEY: both_absent,
                  self.BOTH_ARE_PRESENT_KEY + '_%': both_present / len(not_corrupted_data),
                  self.BOTH_ARE_ABSENT_KEY + '_%': both_absent / len(not_corrupted_data)}

        result_other = None
        if self.score_type == F1_SCORE_KEY:
            self.result = f1_score(true, pred, average=F1_SCORE_TYPE)
        elif self.score_type == ACCURACY_SCORE_KEY:
            self.result = accuracy_score(true, pred)
            std = np.std([1 if t == p else 0 for t, p in zip(true, pred)])
            result_other = {'std': std, 'sem': std / np.sqrt(len(true))}
        else:
            raise f"Unknown score_type {self.score_type}"
        return self.out_object(self.result, stats, result_other)


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


def stats_data_path(answer_response_type, domain, plan_length, question_category, ramifications, random_sub, model_name,
                    prompt_type, save_main_dir=STATISTICS_PATH):
    return os.path.join(save_main_dir, answer_response_type, domain, str(plan_length), question_category,
                        ramifications, random_sub, model_name, prompt_type)


def calculate_stats(data_all, answer_response_type, domain, plan_length, question_category, ramifications, random_sub,
                    model_name, prompt_type, save_main_dir=STATISTICS_PATH, override=False):
    os.makedirs(save_main_dir, exist_ok=True)
    save_dir = stats_data_path(answer_response_type, domain, plan_length, question_category, ramifications,
                               random_sub, model_name, prompt_type, save_main_dir=save_main_dir)
    file_path = os.path.join(save_dir, RESULTS_FILE_NAME)
    if os.path.exists(file_path) and not override:
        return False

    if answer_response_type == FREE_ANSWER_TYPE:
        stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                                model_name, prompt_type, domain, random_sub)
    else:
        tf_score_key = answer_response_type.split('.')[1]
        stats = TrueFalseStats(data_all, plan_length, question_category, ramifications,
                               model_name, prompt_type, domain, random_sub, tf_score_key)

    try:
        stats_compute = stats.compute()
        if stats_compute[SK_RESULT] is None:
            file_path = file_path + '.error'
        with open(file_path, 'w') as f:
            json.dump(stats_compute, f)
    except Exception as e:
        try:
            file_path = file_path + '.exception'
            with open(file_path, 'w') as f:
                json.dump(str(e), f)
        except:
            print(file_path)
    return True


def calculate_stats_all(data_all, answer_response_type, save_main_dir=STATISTICS_PATH,
                        override=False):
    for domain, plan_length, question_category, ramifications, random_sub, model_name, prompt_type in for_loop_all_iterator():
        calculate_stats(data_all, answer_response_type, domain, plan_length, question_category, ramifications,
                        random_sub, model_name, prompt_type, save_main_dir=save_main_dir, override=override)


def save_stats_file(answer_response, score_key):
    return f'{answer_response}.{score_key}.jsonl'


def tf_answer_type(score_key=F1_SCORE_KEY):
    return f'{TRUE_FALSE_ANSWER_TYPE}.{score_key}'


def collect_stats_all(answer_response_type, save_main_dir=STATISTICS_PATH):
    stats_all = []
    for domain, plan_length, question_category, ramifications, random_sub, model_name, prompt_type in for_loop_all_iterator():
        dir = stats_data_path(answer_response_type, domain, plan_length, question_category, ramifications, random_sub,
                              model_name, prompt_type, save_main_dir=save_main_dir)
        path = os.path.join(dir, RESULTS_FILE_NAME)
        if os.path.exists(path):
            with open(path) as f:
                stats_all.append(json.load(f))
    return stats_all


###### Custom class for fluents ######
class TrueFalseStatsCustom(TrueFalseStats):
    def __init__(self, filtered_data, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                 substitutions, score_type=F1_SCORE_KEY):
        super().__init__(filtered_data, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                         substitutions, score_type=F1_SCORE_KEY)
        self.answer_type = TRUE_FALSE_ANSWER_TYPE
        self.score_type = score_type
        self.data = filtered_data


def filter_multi_selector_modified(data_all, ramifications, model_name, prompt_type, answer_type, substitutions,
                                   plan_length, other_keys_ls):
    """ if ALL_DOMAINS_KEY or ALL_CATEGORIES_KEY or ALL_LENGTHS_KEY selects multiple values from data_all"""
    filter_by = base_filter(ramifications, model_name, prompt_type, answer_type, substitutions)
    filter_by.append((OUT_OBJ_PLAN_LENGTH, {plan_length}))
    if other_keys_ls:
        filter_by.extend(other_keys_ls)

    results = []
    for d in data_all:
        if all(d[k] in v for k, v in filter_by):
            results.append(d)
    return results


if __name__ == '__main__':
    questions_dir = f'{DATA_PATH}/questions_m1'
    questions_by_id = gather_questions(questions_dir)

    ids_file_name = 'dataset_ids.test'
    if ids_file_name:
        selected_ids = open_jsonl(f'{DATA_PATH}/{ids_file_name}.jsonl')
        data_all, missing_data = gather_data(questions_by_id, selected_ids=selected_ids)
        save_main_dir = f'{STATISTICS_PATH}.{ids_file_name}'
    else:
        data_all, missing_data = gather_data(questions_by_id)
        save_main_dir = STATISTICS_PATH

    sanity_checks(questions_by_id, data_all)

    answer_response = f'{TRUE_FALSE_ANSWER_TYPE}.{ACCURACY_SCORE_KEY}'
    calculate_stats_all(data_all, answer_response,
                        save_main_dir=save_main_dir,
                        override=True)
    print('saved', answer_response)