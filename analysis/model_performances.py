import json
from sklearn.metrics import f1_score, accuracy_score
from rouge_score import rouge_scorer
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from collections import defaultdict
import sys

# import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from torch.utils.data import DataLoader
# from datasets import Dataset

sys.path.insert(0, '../../')
from questions_construction.main import QUESTION_CATEGORIES
from questions_construction.domains import DOMAIN_NAMES
from common import *
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

NO_RESPONSE_MESSAGE = 'NO RESPONSE'

EVALUATED_FREE_ANSWER_RESPONSE_KEY = 'evaluated_free_answer_response'

PLAN_LENGTHS = [1, 10, 19]
SMALL_MODELS = ['llama_8b', 'llama_70b']#['llama2-13b-chat', 'llama-3-8b-instruct', 'llama2-7b-chat', 'gemma-7b', 'gemma-2b']
BIG_MODELS = ['gemini', 'gpt-4o']
TUNED_MODELS = ['llama_8b.finetuned_tf', 'llama_8b.finetuned_free'] #['llama-3-8b-instruct-finetuned', 'gemma-7b-finetuned']
PROMPT_MODEL_NAMES = BIG_MODELS + SMALL_MODELS + TUNED_MODELS
PROMPT_TYPES = ['zero_shot','few_shot_0', 'few_shot_1', 'few_shot_3', 'few_shot_5']
SUBSTITUTION_TYPES = [WITHOUT_RANDOM_SUB, WITH_RANDOM_SUB]
RAMIFICATION_TYPES = [WITHOUT_RAMIFICATIONS, WITH_RAMIFICATIONS]



def gather_data_iterator():
    for substitutions in SUBSTITUTION_TYPES:
        for ramifications in RAMIFICATION_TYPES:
            for model_name in PROMPT_MODEL_NAMES:
                for prompt_type in PROMPT_TYPES:
                    yield substitutions, ramifications, model_name, prompt_type

def gather_data_iterator_new():
    for ramifications in RAMIFICATION_TYPES:
        for model_name in PROMPT_MODEL_NAMES:
            for prompt_type in PROMPT_TYPES:
                yield ramifications, model_name, prompt_type
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
        qa_objects = open_jsonl(f'{questions_dir}/questions.{substitutions}.jsonl')
        for d in qa_objects:
            if selected_ids and d[OUT_OBJ_ID] not in selected_ids:
                continue
            if delete_other_keys:
                pass
                # del d[OUT_OBJ_INITIAL_STATE_ASP]
                # del d[OUT_OBJ_ACTION_SEQUENCE]
            all_data[d[OUT_OBJ_ID]][substitutions] = d
    print('questions gathered')
    return all_data

def gather_questions_old_format(questions_dir, selected_ids=None, delete_other_keys=True):
    """old format"""
    all_data = defaultdict(dict)
    for substitutions in SUBSTITUTION_TYPES:
        for domain in DOMAIN_NAMES:
            for instance in [f'Instance_{i}' for i in range(1, 11)]:
                for ext in ['', '_composite']:
                    results_domain_path = f'{questions_dir}{ext}/{substitutions}/{domain}/{instance}.jsonl'
                    if not os.path.exists(results_domain_path):
                        pass
                        # print("missing", results_domain_path)
                    else:
                        qa_objects = open_jsonl(results_domain_path)
                        for d in qa_objects:
                            if selected_ids and d[OUT_OBJ_ID] not in selected_ids:
                                continue
                            if d[OUT_OBJ_ID] in all_data and substitutions in all_data[d[OUT_OBJ_ID]]:
                                raise ValueError(f"Duplicate question {d[OUT_OBJ_ID]}, {substitutions}")
                            if delete_other_keys:
                                pass
                                # del d[OUT_OBJ_INITIAL_STATE_ASP]
                                # del d[OUT_OBJ_ACTION_SEQUENCE]
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
                    for ext in ['', '_composite']:
                        pbar.update(1)
                        results_domain_path = f'{results_dir}{ext}/{model_name}/{substitutions}/{ramifications}/{prompt_type}/{domain}/{instance}.jsonl'
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
                          answer_type, substitutions, fluent_sign_question=None):
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

    if fluent_sign_question is not None:
        filter_by.append((OUT_OBJ_FLUENT_SIGN_QUESTION, {fluent_sign_question}))

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


def find_text_within_brackets(text):
    i_start = text.find('[[')
    i_end = text.find(']]')
    if i_start == -1 or i_end == -1:
        return text.strip(' ')
    return text[i_start+2:i_end].strip(' ')

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
                 substitutions, score_type):
        super().__init__(plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions)
        self.answer_type = TRUE_FALSE_ANSWER_TYPE
        self.score_type = score_type
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name,
                                          prompt_type, domain, self.answer_type, substitutions)


    @staticmethod
    def prediction_selection_criteria(d, model_response_key=MODEL_RESPONSE_KEY):
        model_response = clean_response(d[model_response_key])
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

    def true_pred(self, not_corrupted_data):
        true = []
        pred = []
        both_present = 0
        both_absent = 0
        #TODO tune this
        for d in not_corrupted_data:
            prediction = self.prediction_selection_criteria(d)
            # if the model response is unknown, set the response to the opposite of the ground truth
            response_to_unknown = str(not eval(d[OUT_OBJ_ANSWER]))
            if prediction == self.BOTH_ARE_PRESENT_KEY:
                both_present += 1
                # pred.append(response_to_unknown)
            elif prediction == self.BOTH_ARE_ABSENT_KEY:
                both_absent += 1
                # pred.append(response_to_unknown)
            else:
                pred.append(prediction)
                true.append(d[OUT_OBJ_ANSWER])

        stats = {self.BOTH_ARE_PRESENT_KEY: both_present,
                  self.BOTH_ARE_ABSENT_KEY: both_absent,
                  self.BOTH_ARE_PRESENT_KEY + '_%': both_present / len(not_corrupted_data),
                  self.BOTH_ARE_ABSENT_KEY + '_%': both_absent / len(not_corrupted_data)}

        return true, pred, stats

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
        true, pred, stats2 = self.true_pred(not_corrupted_data)
        stats |= stats2

        result_other = None
        if self.score_type == F1_SCORE_KEY:
            self.result = f1_score(true, pred, average=F1_SCORE_TYPE)
        elif self.score_type == ACCURACY_SCORE_KEY:
            self.result = accuracy_score(true, pred)
            std = np.std([1 if t == p else 0 for t, p in zip(true, pred)])
            result_other = {'sem_95': self.confidence_interval(self.result, len(true)),
                            'std': std,
                            'sem': self.confidence_interval(self.result, len(true), z=1),
                            'sem_old': std / np.sqrt(len(true))}
        else:
            raise f"Unknown score_type {self.score_type}"
        return self.out_object(self.result, result_other, stats)

class FreeAnswerStats(TrueFalseStats):
    def __init__(self, data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions, score_type):
        super().__init__(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain, substitutions, score_type)
        self.answer_type = FREE_ANSWER_TYPE
        self.score_type = score_type
        self.data = filter_multi_selector(data_all, plan_length, question_category, ramifications, model_name, prompt_type, domain, self.answer_type, substitutions)

    @staticmethod
    def prediction_selection_criteria(d, model_response_key=EVALUATED_FREE_ANSWER_RESPONSE_KEY):
        return TrueFalseStats.prediction_selection_criteria(d, model_response_key)

    def true_pred(self, not_corrupted_data):
        true = []
        pred = []
        both_present = 0
        both_absent = 0
        for d in not_corrupted_data:
            prediction = self.prediction_selection_criteria(d)
            if prediction == self.BOTH_ARE_PRESENT_KEY:
                both_present += 1
            elif prediction == self.BOTH_ARE_ABSENT_KEY:
                both_absent += 1
            else:
                pred.append(prediction)
                true.append(TRUE_ANSWER)

        stats = {self.BOTH_ARE_PRESENT_KEY: both_present,
                  self.BOTH_ARE_ABSENT_KEY: both_absent,
                  self.BOTH_ARE_PRESENT_KEY + '_%': both_present / len(not_corrupted_data),
                  self.BOTH_ARE_ABSENT_KEY + '_%': both_absent / len(not_corrupted_data)}

        return true, pred, stats

class FreeAnswerStatsOld(BaseStats):

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

    def compute(self, best_threshold=95, model_response_key=MODEL_RESPONSE_CLEAN_KEY):
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
        pred_free_answer = [find_text_within_brackets(d[model_response_key]) for d in not_corrupted_data]
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
            result_other = {'sem_95': self.confidence_interval(accuracy, len(probabilities)),
                            'std': std,
                            'sem':  self.confidence_interval(accuracy, len(probabilities), z=1),
                            'sem_old': std / np.sqrt(len(probabilities))}
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

    answer_response_type, tf_score_key = answer_response_type.split('.')
    if answer_response_type == FREE_ANSWER_TYPE:
        stats = FreeAnswerStats(data_all, plan_length, question_category, ramifications,
                               model_name, prompt_type, domain, random_sub, tf_score_key)
    elif answer_response_type == TRUE_FALSE_ANSWER_TYPE:
        stats = TrueFalseStats(data_all, plan_length, question_category, ramifications,
                               model_name, prompt_type, domain, random_sub, tf_score_key)
    else:
        raise ValueError(f"Unknown answer_response_type {answer_response_type}")

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


def clean_response(response):
    keyword = '[ANSWER]'.lower()
    ind = response.lower().find(keyword)
    if ind == -1:
        return response
    return response[ind+len(keyword):].strip()


def data_all_single_run(questions_by_id, model_results, substitution, ramification, model_name, prompt_type):
    data_all = []
    extra_kv = {SK_MODEL: model_name,
                  SK_PROMPT_TYPE: prompt_type,
                  SK_RAMIFICATION: ramification,
                  SK_SUBSTITUTION: substitution}
    for result_d in model_results:
        result_d.update(deepcopy(extra_kv))
        result_d.update(questions_by_id[result_d[OUT_OBJ_ID]])
        result_d[SK_UNIQUE_ID] = f"{result_d[OUT_OBJ_ID]}::{model_name}::{prompt_type}::{ramification}::{substitution}"
        data_all.append(result_d)
    return data_all

def calculate_stats_single_run(data_all, answer_response_type, ramification, substitution, model_name, prompt_type, save_main_dir, override=False):
    for plan_length in PLAN_LENGTHS:
        for question_category in [ALL_QUESTION_CATEGORIES_KEY] + QUESTION_CATEGORIES:
            for domain in [ALL_DOMAINS_KEY, TRANSPORTATION_DOMAIN_KEY, NON_TRANSPORTATION_DOMAIN_KEY]:
                calculate_stats(data_all, answer_response_type, domain, plan_length, question_category,
                                ramification, substitution, model_name, prompt_type, save_main_dir=save_main_dir,
                                override=override)


if __name__ == '__main__':
    questions_by_id = {d[OUT_OBJ_ID]: d for d in open_jsonl(f'{DATA_PATH}/test_data.paraphrased.cleaned.jsonl')}
    override = True
    answer_response_type = f'{FREE_ANSWER_TYPE}.{ACCURACY_SCORE_KEY}' #f'{TRUE_FALSE_ANSWER_TYPE}.{ACCURACY_SCORE_KEY}' #
    stats_save_dir = f'{STATISTICS_PATH}.trial_run.ED'

    model_name = 'llama_8b' #'gpt-4o' #'llama_8b.finetuned_free' #'llama_8b.finetuned_tf' #'llama_8b.finetuned_free' #'llama_70b'#

    substitution = WITHOUT_RANDOM_SUB
    ramification = WITHOUT_RAMIFICATIONS
    prompt_type = FEW_SHOT_3_PROMPT_KEY #ZERO_SHOT_PROMPT_KEY

    if answer_response_type.split('.')[0] == TRUE_FALSE_ANSWER_TYPE:
        model_results_dir = f'{PROJECT_PATH}/data/prompting_results/{ramification}/{prompt_type}/{model_name}.jsonl'
        model_results = open_jsonl(model_results_dir)
        data_all = data_all_single_run(questions_by_id, model_results, substitution, ramification, model_name,prompt_type)
    elif answer_response_type.split('.')[0] == FREE_ANSWER_TYPE:
        save_dir = f'{PROJECT_PATH}/data/free_answers/{ramification}/{prompt_type}'
        model_results = open_jsonl(os.path.join(save_dir, f'{model_name}.jsonl'))
        data_all = data_all_single_run(questions_by_id, model_results, substitution, ramification, model_name,
                                       prompt_type)
    else:
        raise ValueError(f"Unknown answer_response_type {answer_response_type}")

    calculate_stats_single_run(data_all, answer_response_type, ramification, substitution, model_name, prompt_type, stats_save_dir, override)

    # questions_dir = f'{DATA_PATH}/questions'
    # ids_file_name = 'dataset_ids.test.pruned'
    # if ids_file_name:
    #     selected_ids = open_jsonl(f'{DATA_PATH}/{ids_file_name}.jsonl') + open_jsonl(f'{DATA_PATH}/questions.composite.test_ids.jsonl')
    #     questions_by_id = gather_questions(questions_dir, selected_ids=selected_ids)
    #     data_all, missing_data = gather_data(questions_by_id, selected_ids=selected_ids)
    #     save_main_dir = f'{STATISTICS_PATH}.{ids_file_name}'
    # else:
    #     questions_by_id = gather_questions(questions_dir)
    #     data_all, missing_data = gather_data(questions_by_id)
    #     save_main_dir = STATISTICS_PATH
    # sanity_checks(questions_by_id, data_all)
    #
    # answer_response = f'{TRUE_FALSE_ANSWER_TYPE}.{ACCURACY_SCORE_KEY}'
    # #
    # model, tokenizer, device = None, None, None
    # # if answer_response == FREE_ANSWER_TYPE:
    # #     device = torch.device("cpu")  # "cuda:0" if torch.cuda.is_available() else
    # #     model_name = 'roberta-base'
    # #     path_to_fine_tuned_model = f'{CODE_PATH}/analysis/roberta_finetuned_models/checkpoint-2500_roberta'
    # #     tokenizer = AutoTokenizer.from_pretrained(model_name)
    # #     model = AutoModelForSequenceClassification.from_pretrained(path_to_fine_tuned_model)
    # #     model.to(device)
    # #
    # calculate_stats_all(data_all, answer_response,
    #                     save_main_dir=save_main_dir,
    #                     override=True,
    #                     tokenizer=tokenizer, model=model, device=device)
    # # print('saved', answer_response)