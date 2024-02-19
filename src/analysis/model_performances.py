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
ALL_CATEGORIES = 'all_categories'
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


def split_by_category(results):
    by_category = defaultdict(list)
    for d in results:
        by_category[d[OUT_OBJ_QUESTION_CATEGORY]].append(d)
    return by_category


def split_by_category_by_answer_type(results):
    tf_by_category = defaultdict(list)
    fa_by_category = defaultdict(list)

    for d in results:
        if d[OUT_OBJ_ANSWER_TYPE] == TRUE_FALSE_ANSWER:
            tf_by_category[d[OUT_OBJ_QUESTION_CATEGORY]].append(d)
        else:
            fa_by_category[d[OUT_OBJ_QUESTION_CATEGORY]].append(d)
    return tf_by_category, fa_by_category


def is_desired_length(qa_object, lenth):
    return lenth == ALL_LENGTHS_KEY or qa_object[OUT_OBJ_PLAN_LENGTH] == lenth


# def stats_qa_objects_ls(results):
#     tf_results, fa_results = split_by_answer_type(results)
#     tf_by_length = f1_score_by_length(tf_results, score_type=F1_SCORE_TYPE)
#     tf_in_response_by_length = f1_score_in_response_by_length(tf_results, score_type=F1_SCORE_TYPE)
#     fa_by_length = f1_rouge_by_length(fa_results, score_type=ROUGE_SCORE_TYPE)
#     return {TRUE_FALSE_ANSWER: tf_by_length, f'{TRUE_FALSE_ANSWER}_in_response': tf_in_response_by_length,
#             FREE_ANSWER: fa_by_length}

def across_domains(ramifications, stats_type, model_name, eval_type):
    if ramifications == WITH_RAMIFICATIONS:
        results_dir = f'{PROJECT_PATH}/results_ramifications'  # todo rn to results dir
    elif ramifications == WITHOUT_RAMIFICATIONS:
        results_dir = RESULTS_PATH
    else:
        raise f"{ramifications} is not defined"

    all_stats = []
    all_domains_qa_objects = []
    meta_info = {MODEL_NAME_KEY: model_name, EVAL_TYPE_KEY: eval_type}
    for domain in DOMAIN_NAMES:
        meta_info[DOMAIN_KEY] = domain
        try:
            results_domain_path = f'{results_dir}/{model_name}/{eval_type}/{domain}.jsonl'
            qa_objects = open_jsonl(results_domain_path)
            all_domains_qa_objects.extend(qa_objects)
            if stats_type == TRUE_FALSE_ANSWER:
                all_stats.append(TrueFalseStats.stats_qa_objects_ls(qa_objects) | deepcopy(meta_info))
            elif stats_type == FREE_ANSWER:
                all_stats.append(FreeAnswerStats.stats_qa_objects_ls(qa_objects) | deepcopy(meta_info))
            else:
                raise f"{stats_type} is not defined"
        except Exception as e:
            print(domain, '---------------------------')
            print(e)
            all_stats.append({TRUE_FALSE_ANSWER: {}, FREE_ANSWER: {}} | deepcopy(meta_info))  # TODO fix
    meta_info[DOMAIN_KEY] = ALL_DOMAINS_KEY
    if stats_type == TRUE_FALSE_ANSWER:
        all_stats.append(TrueFalseStats.stats_qa_objects_ls(all_domains_qa_objects) | deepcopy(meta_info))
    elif stats_type == FREE_ANSWER:
        all_stats.append(FreeAnswerStats.stats_qa_objects_ls(all_domains_qa_objects) | deepcopy(meta_info))
    return all_stats


def compute_stats(ramifications, stats_type):
    save_dir = os.path.join(STATISTICS_PATH, ramifications)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    all_stats = []
    for model_name in PROMPT_MODEL_NAMES:
        for eval_type in PROMPT_TYPES:
            try:
                cross_domains_stats = across_domains(ramifications, stats_type, model_name, eval_type)
                all_stats.extend(cross_domains_stats)

                save_dir_model_eval_type = f'{save_dir}/{model_name}/{eval_type}'  # f1_rouge_everything.json'
                if not os.path.exists(save_dir_model_eval_type):
                    os.makedirs(save_dir_model_eval_type)
                with open(f'{save_dir_model_eval_type}/{stats_type}.json', 'w') as f:
                    json.dump(cross_domains_stats, f)
            except Exception as e:
                print(model_name, eval_type, '---------------------------')
                print(e)

    # save_path = f'{save_dir}/{stats_type}.{EVERYTHING_POSTFIX}.json' #f1_rouge_everything.json'
    # with open(save_path, 'w') as f:
    #     json.dump(all_stats, f)
    return all_stats


class FreeAnswerStats:

    @staticmethod
    def get_rouge_score(results, length=ALL_LENGTHS_KEY):
        stats = []
        for d in results:
            if is_desired_length(d, length):
                scores = ROUGE_SCORER.score(d[OUT_OBJ_ANSWER], d[MODEL_RESPONSE_KEY])
                stats.append(scores[ROUGE_SCORE_TYPE].fmeasure)
        return np.mean(stats)

    @staticmethod
    def f1_rouge_by_length(fa_results, score_type=ROUGE_SCORE_TYPE):
        return {l: FreeAnswerStats.get_rouge_score(fa_results, l) for l in PLAN_LENGTHS + [ALL_LENGTHS_KEY]}

    @staticmethod
    def stats_qa_objects_ls(results):
        tf_results, fa_results = split_by_answer_type(results)
        fa_by_length = FreeAnswerStats.f1_rouge_by_length(fa_results, score_type=ROUGE_SCORE_TYPE)
        return {FREE_ANSWER: fa_by_length}


class TrueFalseStats:

    @staticmethod
    def f1_score_by_length(tf_results, score_type=F1_SCORE_TYPE):
        return {l: TrueFalseStats.get_f1_score(tf_results, l, score_type) for l in PLAN_LENGTHS + [ALL_LENGTHS_KEY]}

    @staticmethod
    def f1_score_in_response_by_length(tf_results, score_type=F1_SCORE_TYPE):
        return {l: TrueFalseStats.get_f1_score_in_response(tf_results, l, score_type) for l in
                PLAN_LENGTHS + [ALL_LENGTHS_KEY]}

    @staticmethod
    def get_f1_score(results, lenth=ALL_LENGTHS_KEY, score_type=F1_SCORE_TYPE):
        true = []
        pred = []
        for d in results:
            if is_desired_length(d, lenth):
                true.append(d[OUT_OBJ_ANSWER])
                pred.append(d[MODEL_RESPONSE_KEY])
        return f1_score(true, pred, average=score_type)

    @staticmethod
    def get_f1_score_in_response(results, lenth=ALL_LENGTHS_KEY, score_type=F1_SCORE_TYPE):
        true = []
        pred = []
        UNKNOWN = 'unknown'
        for d in results:
            if is_desired_length(d, lenth):
                true.append(d[OUT_OBJ_ANSWER])
                if d[OUT_OBJ_ANSWER] in d[MODEL_RESPONSE_KEY]:
                    pred.append(d[OUT_OBJ_ANSWER])
                else:
                    pred.append(UNKNOWN)
        return f1_score(true, pred, average=score_type)

    @staticmethod
    def stats_qa_objects_ls(results, meta_dict):
        tf_by_category, _fa_by_category = split_by_category_by_answer_type(results)
        by_category = {}
        in_response_by_category = {}
        for category, results in tf_by_category.items():
            by_category[category] = TrueFalseStats.f1_score_by_length(results)
            in_response_by_category[category] = TrueFalseStats.f1_score_in_response_by_length(results)

        tf_results, _fa_results = split_by_answer_type(results)
        by_category[ALL_CATEGORIES] = TrueFalseStats.f1_score_by_length(tf_results)
        in_response_by_category[ALL_CATEGORIES] = TrueFalseStats.f1_score_in_response_by_length(tf_results)

        return {f'{TRUE_FALSE_ANSWER}_by_category': by_category,
                f'{TRUE_FALSE_ANSWER}_in_response_by_category': in_response_by_category}


if __name__ == '__main__':
    tf_wor_stats = compute_stats(WITHOUT_RAMIFICATIONS, TRUE_FALSE_ANSWER)
    tf_wr_stats = compute_stats(WITH_RAMIFICATIONS, TRUE_FALSE_ANSWER)

    fa_wor_stats = compute_stats(WITHOUT_RAMIFICATIONS, FREE_ANSWER)
    fa_wr_stats = compute_stats(WITH_RAMIFICATIONS, FREE_ANSWER)
