from sklearn.metrics import f1_score
from rouge_score import rouge_scorer
import numpy as np

from src.questions_construction.main import *
from src.common import *


ALL_LENGTHS_KEY = 'all'
ALL_DOMAINS_KEY = 'all'
MODEL_NAME_KEY = 'model_name'
EVAL_TYPE_KEY = 'eval_type'
DOMAIN_KEY = 'domain'

F1_SCORE_TYPE = 'micro'
ROUGE_SCORE_TYPE = 'rougeL'
ROUGE_SCORER = rouge_scorer.RougeScorer([ROUGE_SCORE_TYPE], use_stemmer=True)


def data_path(model_name, eval_type, domain):
    return f'{RESULTS_PATH}/{model_name}/{eval_type}/{domain}.jsonl'


def load_data(eval_type, model_name):
    if model_name:
        results = []
        for domain in DOMAIN_NAMES:
            results_path = data_path(model_name, eval_type, domain)
            results.extend(open_jsonl(results_path))
        return results
    else:
        by_domain = {}
        for domain in DOMAIN_NAMES:
            results_path = f'{RESULTS_PATH}/{model_name}/{eval_type}/{domain}.jsonl'
            by_domain[domain] = open_jsonl(results_path)
        return by_domain


def split_by_answer_type(results):
    tf_answer = []
    free_answer = []
    for d in results:
        if d[OUT_OBJ_ANSWER_TYPE] == TRUE_FALSE_ANSWER:
            tf_answer.append(d)
        else:
            free_answer.append(d)
    return tf_answer, free_answer


def is_desired_length(qa_object, lenth):
    return lenth == ALL_LENGTHS_KEY or qa_object[OUT_OBJ_PLAN_LENGTH] == lenth


def get_f1_score_tf(results, lenth=ALL_LENGTHS_KEY, score_type=F1_SCORE_TYPE):
    true = []
    pred = []
    for d in results:
        if is_desired_length(d, lenth):
            true.append(d[OUT_OBJ_ANSWER])
            pred.append(d[MODEL_RESPONSE_KEY])
    return f1_score(true, pred, average=score_type)


def get_f1_score_tf_in_response(results, lenth=ALL_LENGTHS_KEY, score_type=F1_SCORE_TYPE):
    true = []
    pred = []
    for d in results:
        if is_desired_length(d, lenth):
            true.append(d[OUT_OBJ_ANSWER])
            if d[OUT_OBJ_ANSWER] in d[MODEL_RESPONSE_KEY]:
                pred.append(d[OUT_OBJ_ANSWER])
            else:
                pred.append(d[MODEL_RESPONSE_KEY])
    return f1_score(true, pred, average=score_type)


def f1_score_by_length(tf_results, score_type=F1_SCORE_TYPE):
    return {l: get_f1_score_tf(tf_results, l, score_type) for l in PLAN_LENGTHS + [ALL_LENGTHS_KEY]}


def f1_score_in_response_by_length(tf_results, score_type=F1_SCORE_TYPE):
    return {l: get_f1_score_tf_in_response(tf_results, l, score_type) for l in PLAN_LENGTHS + [ALL_LENGTHS_KEY]}


def get_rouge_score(results, length=ALL_LENGTHS_KEY):
    stats = []
    for d in results:
        if is_desired_length(d, length):
            scores = ROUGE_SCORER.score(d[OUT_OBJ_ANSWER], d[MODEL_RESPONSE_KEY])
            stats.append(scores[ROUGE_SCORE_TYPE].fmeasure)
    return np.mean(stats)


def f1_rouge_by_length(fa_results, score_type=ROUGE_SCORE_TYPE):
    return {l: get_rouge_score(fa_results, l) for l in PLAN_LENGTHS + [ALL_LENGTHS_KEY]}


def stats_qa_objects_ls(results):
    tf_results, fa_results = split_by_answer_type(results)
    tf_by_length = f1_score_by_length(tf_results, score_type=F1_SCORE_TYPE)
    tf_in_response_by_length = f1_score_in_response_by_length(tf_results, score_type=F1_SCORE_TYPE)
    fa_by_length = f1_rouge_by_length(fa_results, score_type=ROUGE_SCORE_TYPE)
    return {TRUE_FALSE_ANSWER: tf_by_length, f'{TRUE_FALSE_ANSWER}_in_response': tf_in_response_by_length,
            FREE_ANSWER: fa_by_length}
