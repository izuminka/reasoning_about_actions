import random
import concurrent.futures  # for multithreading
import multiprocessing  # for multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from together_ai_common import *

from prompts import *

DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
OUTPUT_TOKEN_LIMIT = 5000

def process_data(data_d, paraphrased_ids, massive_dump_dir, model):
    if model == 'llama_70b':
        model_precise = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"

    if data_d[OUT_OBJ_ID] in paraphrased_ids:
        return False

    response = api_call(data_d[PROMPT_KEY], model_precise, OUTPUT_TOKEN_LIMIT)
    if not response:
        return False

    data_d[MODEL_RESPONSE_KEY] = response
    with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
        json.dump(data_d, f)
    return True

if __name__ == '__main__':
    model = 'llama_70b'

    prompt_type = FEW_SHOT_3_PROMPT_KEY
    ramification = WITHOUT_RAMIFICATIONS
    save_dir = f'{PROJECT_PATH}/data/prompting_results/{ramification}/{prompt_type}'
    massive_dump_dir = f'{save_dir}/{model}'
    os.makedirs(massive_dump_dir, exist_ok=True)

    computed_ids = set([f.strip('.json') for f in os.listdir(massive_dump_dir) if f.endswith('.json')])
    print(len(computed_ids))
    print('gathered ids')

    prompt_data = open_jsonl(f'{PROJECT_PATH}/data/prompts/{prompt_type}.jsonl')
    random.shuffle(prompt_data)

    chosen_data = [d for d in prompt_data if d[OUT_OBJ_ID] not in computed_ids]
    # Multithreading: Using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for data_d in chosen_data:
            if data_d[OUT_OBJ_ID] not in computed_ids:
                futures.append(executor.submit(process_data, data_d, computed_ids, massive_dump_dir, model))

        # Iterate over the results to ensure all tasks complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                future.result()  # Get the result (or raise exceptions if any occurred)
            except Exception as e:
                print(f"Exception occurred: {e}")

    collected_data = [open_json(f'{massive_dump_dir}/{f}') for f in os.listdir(massive_dump_dir) if f.endswith('.json')]
    save_jsonl(collected_data, f'{save_dir}/{model}.jsonl')


