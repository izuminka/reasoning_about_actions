import json
from sklearn.metrics import f1_score, accuracy_score
from rouge_score import rouge_scorer
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from collections import defaultdict
import sys

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from datasets import Dataset

sys.path.insert(0, '../../')
from src.questions_construction.main import PLAN_LENGTHS, QUESTION_CATEGORIES
from src.questions_construction.domains import DOMAIN_NAMES
from src.common import *
import random


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
BIG_MODELS = ['gemini', 'gpt-4o']
PROMPT_MODEL_NAMES = SMALL_MODELS + BIG_MODELS
PROMPT_TYPES = ['few_shot_1', 'few_shot_3', 'few_shot_5']
SUBSTITUTION_TYPES = [WITH_RANDOM_SUB, WITHOUT_RANDOM_SUB]
RAMIFICATION_TYPES = [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]

NO_RESPONSE_MESSAGE = 'NO RESPONSE'

def gather_data_iterator():
    for substitutions in SUBSTITUTION_TYPES:
        for ramifications in RAMIFICATION_TYPES:
            for model_name in PROMPT_MODEL_NAMES:
                for prompt_type in PROMPT_TYPES:
                    yield substitutions, ramifications, model_name, prompt_type
def for_loop_all_iterator():
    domains = DOMAIN_NAMES + [ALL_DOMAINS_KEY, TRANSPORTATION_DOMAIN_KEY, NON_TRANSPORTATION_DOMAIN_KEY]
    question_categories = [ALL_QUESTION_CATEGORIES_KEY] + QUESTION_CATEGORIES

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
                            print(f"{d[OUT_OBJ_ID]} not in questions_by_id")
                            continue
                            # raise ValueError(f"Missing question {d[OUT_OBJ_ID]}")
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

    def out_object(self, result, result_other=None, stats=None, error_message=None):
        '''returns a dictionary with the stats of the object,
        result is a float'''
        return {SK_RESULT: result,
                SK_RESULT_OTHER: result_other,
                SK_STATS: stats,

                SK_MODEL: self.model_name,
                SK_PROMPT_TYPE: self.prompt_type,
                SK_RAMIFICATION: self.ramifications,
                SK_SUBSTITUTION: self.substitutions,

                OUT_OBJ_DOMAIN_NAME: self.domain,
                OUT_OBJ_PLAN_LENGTH: self.plan_length,
                OUT_OBJ_QUESTION_CATEGORY: self.question_category,
                OUT_OBJ_ANSWER_TYPE: self.answer_type,

                SK_ERROR_MESSAGE: error_message}

    def remove_corrupted(self, message=NO_RESPONSE_MESSAGE):
        not_corrupted = []
        for d in self.data:
            if d[MODEL_RESPONSE_KEY] != message:
                not_corrupted.append(d)
        return not_corrupted

    def confidence_interval(self, accuracy, n, z = 1.96): # 1.96 is 95% confidence interval
        return z * np.sqrt((accuracy * (1 - accuracy)) / n)

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
            res = self.out_object(None, stats=None, error_message='self.data is empty')
            # print(f"No data for {res}")
            return res

        not_corrupted_data = self.remove_corrupted()
        if not not_corrupted_data:
            res = self.out_object(None, stats=None, error_message='All corrupted')
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
            wilson = self.confidence_interval(self.result, len(true))
            std = np.std([1 if t == p else 0 for t, p in zip(true, pred)])
            result_other = {'wilson': wilson, 'std': std, 'sem': std / np.sqrt(len(true))}
        else:
            raise f"Unknown score_type {self.score_type}"
        return self.out_object(self.result, result_other, stats)


class FreeAnswerStats(BaseStats):

    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain,
                 substitutions, model, tokenizer, device):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions)
        self.answer_type = FREE_ANSWER_TYPE
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type, substitutions)
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def model_compute_similarity(self, dataloader):
        # get the predictions and probabilities
        # predictions = []
        probabilities = []
        self.model.eval()
        for batch in dataloader:
            with torch.no_grad():
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                # predictions.extend(torch.argmax(probs, dim=-1).cpu().numpy())
                probabilities.extend(probs.cpu().numpy())
        return probabilities

    def model_preprocess_function(self, batch, max_length=512):
        responses = [str(response) if response else "" for response in batch["s1"]]
        labels = [str(label) if label else "" for label in batch["s2"]]
        # return self.tokenizer(responses, labels, padding="max_length", max_length=512, truncation=False)
        tokenized_output = self.tokenizer(responses, labels, padding="max_length", max_length=max_length, truncation=False)
        return tokenized_output

    def prepare_data(self, true, pred, batch_size=128):
        data = [{'s1':t, 's2':p} for t,p in zip(true, pred)]
        test_data = Dataset.from_list(data)
        test_data = test_data.map(self.model_preprocess_function, batched=True)#, remove_columns=["s1", "s2"])

        # Filter out sequences with input_ids length less than 512
        # Filter out sequences with input_ids length not equal to 512
        def filter_valid_length(batch):
            valid_indices = [i for i, input_ids in enumerate(batch['input_ids']) if len(input_ids) <= 512]
            filtered_batch = {key: [batch[key][i] for i in valid_indices] for key in batch.keys()}
            return filtered_batch

        test_data = test_data.map(filter_valid_length, batched=True)

        # Ensure the dataset is not empty
        if not len(test_data) or 'input_ids' not in test_data.column_names or len(test_data['input_ids']) == 0:
            return None

        test_data.set_format(type='torch')#, columns=['input_ids', 'attention_mask'])
        return DataLoader(test_data, batch_size=batch_size)

    def compute(self, best_threshold=95):
        def find_text(text):
            i_start = text.find('[[')
            i_end = text.find(']]')
            if i_start == -1 or i_end == -1:
                return text.strip(' ')
            return text[i_start+2:i_end].strip(' ')

        if not self.data:
            res = self.out_object(None, stats=None, error_message='self.data is empty')
            return res

        not_corrupted_data = self.remove_corrupted()
        if not not_corrupted_data:
            res = self.out_object(None, stats=None, error_message='All corrupted')
            return res

        stats = {'num_original': len(self.data),
                 'num_corrupted': len(self.data) - len(not_corrupted_data),
                 'num_not_corrupted': len(not_corrupted_data)}

        true_free_answer = [d[OUT_OBJ_ANSWER] for d in not_corrupted_data]
        pred_free_answer = [find_text(d[MODEL_RESPONSE_KEY]) for d in not_corrupted_data]
        data_loader = self.prepare_data(true_free_answer, pred_free_answer)
        if not data_loader:
            res = self.out_object(None, stats=None, error_message='>512 length')
            return res
        probabilities = self.model_compute_similarity(data_loader)
        stats['fa_num_above_model_context'] = len(probabilities)

        # we want to compare true_free_answer, pred_free_answer
        # the ideal case is that they are the same, that is the label is "1"
        by_probability_threshold = {}
        for percent_threshfold in range(90,100,1):
            true = [1]*len(probabilities)
            pred = []
            for (d, s1, s2) in zip(probabilities, data_loader.dataset['s1'], data_loader.dataset['s2']):
                _p_label_0, p_label_1 = list(d)
                if p_label_1 > percent_threshfold/100 or s1.lower() == s2.lower():
                    pred.append(1)
                else:
                    pred.append(0)
            accuracy = accuracy_score(true, pred)
            std = np.std([1 if t == p else 0 for t, p in zip(true, pred)])
            wilson = self.confidence_interval(accuracy, len(probabilities))
            result_other = {'wilson': wilson, 'std': std, 'sem': std / np.sqrt(len(probabilities))}
            by_probability_threshold[percent_threshfold] = [accuracy, result_other]
        self.result, result_other = by_probability_threshold[best_threshold]
        stats |= by_probability_threshold
        rand_ids = random.sample(range(len(probabilities)), min(len(probabilities), 50))
        stats['examples'] = [{'true': v1, 'pred':v2, 'prob_same': float(v3[1])} for i, (v1,v2,v3) in enumerate(zip(data_loader.dataset['s1'], data_loader.dataset['s2'], probabilities)) if i in rand_ids]
        stats['best_threshold'] = best_threshold
        return self.out_object(self.result, result_other, stats)


def stats_data_path(answer_response_type, domain, plan_length, question_category, ramifications, random_sub, model_name,
                    prompt_type, save_main_dir=STATISTICS_PATH):
    return os.path.join(save_main_dir, answer_response_type, domain, str(plan_length), question_category,
                        ramifications, random_sub, model_name, prompt_type)


def calculate_stats(data_all, answer_response_type, domain, plan_length, question_category, ramifications, random_sub,
                    model_name, prompt_type, save_main_dir=STATISTICS_PATH, override=False,
                    model=None, tokenizer=None, device=None):
    save_dir = stats_data_path(answer_response_type, domain, plan_length, question_category, ramifications,
                               random_sub, model_name, prompt_type, save_main_dir=save_main_dir)
    file_path = os.path.join(save_dir, RESULTS_FILE_NAME)
    os.makedirs(save_dir, exist_ok=True)

    if os.path.exists(file_path) and not override:
        return False

    if answer_response_type == FREE_ANSWER_TYPE:
        assert model and tokenizer and device
        stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                                model_name, prompt_type, domain, random_sub, model, tokenizer, device)
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
                        override=False, model=None, tokenizer=None, device=None):
    for domain, plan_length, question_category, ramifications, random_sub, model_name, prompt_type in for_loop_all_iterator():
        if domain in DOMAIN_NAMES: # don't copute for individual domains
            continue
        calculate_stats(data_all, answer_response_type, domain, plan_length, question_category, ramifications,
                        random_sub, model_name, prompt_type, save_main_dir=save_main_dir, override=override,
                        model=model,tokenizer=tokenizer, device=device)


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
    ids_file_name = 'dataset_ids.test.pruned'
    if ids_file_name:
        selected_ids = open_jsonl(f'{DATA_PATH}/{ids_file_name}.jsonl')
        questions_by_id = gather_questions(questions_dir, selected_ids)
        data_all, missing_data = gather_data(questions_by_id, selected_ids=selected_ids)
        save_main_dir = f'{STATISTICS_PATH}.{ids_file_name}'
    else:
        questions_by_id = gather_questions(questions_dir)
        data_all, missing_data = gather_data(questions_by_id)
        save_main_dir = STATISTICS_PATH
    sanity_checks(questions_by_id, data_all)

    answer_response = f'{TRUE_FALSE_ANSWER_TYPE}.{ACCURACY_SCORE_KEY}'

    model, tokenizer, device = None, None, None
    if answer_response == FREE_ANSWER_TYPE:
        device = torch.device("cpu")  # "cuda:0" if torch.cuda.is_available() else
        model_name = 'roberta-base'
        path_to_fine_tuned_model = f'{CODE_PATH}/analysis/roberta_finetuned_models/checkpoint-2500_roberta'
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(path_to_fine_tuned_model)
        model.to(device)

    calculate_stats_all(data_all, answer_response,
                        save_main_dir=save_main_dir,
                        override=True,
                        tokenizer=tokenizer, model=model, device=device)
    print('saved', answer_response)