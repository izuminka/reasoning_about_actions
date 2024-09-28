import random
import concurrent.futures  # for multithreading
import multiprocessing  # for multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from together_ai_common import *

DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo" #"meta-llama/Llama-3-70b-chat-hf"
OUTPUT_TOKEN_LIMIT = 5000

def paraphrase_prompt(text_for_paraphrasing):
    return f'''Your task is to paraphrase the following text while keeping the original meaning intact and the structure same.

Text: {text_for_paraphrasing}

Provide the paraphrased text below:
'''

def process_data(data_d, paraphrased_ids, massive_dump_dir):
    if data_d[OUT_OBJ_ID] in paraphrased_ids:
        return False

    for k_input, k_output in [[OUT_OBJ_QUESTION, OUT_OBJ_QUESTION_PARAPHRASED], [OUT_OBJ_INITIAL_STATE_NL, OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED]]:
        prompt = paraphrase_prompt(data_d[k_input])
        response = api_call(prompt, DEFAULT_MODEL, OUTPUT_TOKEN_LIMIT)
        if not response:
            return False
        data_d[k_output] = response.strip()

    with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
        json.dump(data_d, f)

    return True


def check_lengths():
    data_by_id = {}
    massive_dump_dir = f'{PROJECT_PATH}/data/paraphrased'
    for f in os.listdir(massive_dump_dir):
        if not f.endswith('.json'):
            continue
        with open(f'{massive_dump_dir}/{f}', 'r') as f:
            data_d = json.load(f)
            data_by_id[data_d[OUT_OBJ_ID]] = data_d

    lens_question = {}
    lens_init = {}
    for q_id, d in data_by_id.items():
        lens_question[q_id] = np.abs(len(d[OUT_OBJ_QUESTION]) - len(d[OUT_OBJ_QUESTION_PARAPHRASED]))
        lens_init[q_id] = np.abs(len(d[OUT_OBJ_INITIAL_STATE_NL]) - len(d[OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED]))

    plt.hist(list(lens_question.values()), bins=100)
    plt.show()
    plt.hist(list(lens_init.values()), bins=100)
    plt.show()

    cutoff_question = np.mean(list(lens_question.values())) + 2*np.std(list(lens_question.values()))
    cutoff_init = np.mean(list(lens_init.values())) + 2*np.std(list(lens_init.values()))
    count = 0
    for q_id, d in data_by_id.items():
        if lens_question[q_id] > cutoff_question or lens_init[q_id] > cutoff_init:
            count+=1
            # os.remove(f'{massive_dump_dir}/{q_id}.json')
            # print(q_id, lens_question[q_id], lens_init[q_id])
    lens_question_sorted = sorted(lens_question.items(), key=lambda x: x[1], reverse=True)


if __name__ == '__main__':
    massive_dump_dir = f'{PROJECT_PATH}/data/paraphrased'
    os.makedirs(massive_dump_dir, exist_ok=True)

    paraphrased_ids = set([f.strip('.json') for f in os.listdir(massive_dump_dir) if f.endswith('.json')])
    print(len(paraphrased_ids))
    print('gathered ids')

    test_data = open_jsonl(f'{PROJECT_PATH}/data/test_dataset.jsonl')
    random.shuffle(test_data)

    chosen_data = [d for d in test_data if d[OUT_OBJ_ID] not in paraphrased_ids]
    # for data_d in tqdm(chosen_data):
    #     process_data(data_d, paraphrased_ids, massive_dump_dir)

    # Multithreading: Using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=90) as executor:
        futures = []
        for data_d in chosen_data:
            if data_d[OUT_OBJ_ID] not in paraphrased_ids:
                futures.append(executor.submit(process_data, data_d, paraphrased_ids, massive_dump_dir))

        # Iterate over the results to ensure all tasks complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                future.result()  # Get the result (or raise exceptions if any occurred)
            except Exception as e:
                print(f"Exception occurred: {e}")


