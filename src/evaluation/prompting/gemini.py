from tqdm import tqdm
import os
from helper import *

# START_IDX = 1    # Index from where to start getting the response (1-index)
DATA_FILE_PATH = '../../../data/questions'
OUTPUT_DIR = '../../../results/gemini/zero_shot'
PROMPT_TECHNIQUE = 'zero_shot'    # cot, few_shot, self_consistency, zero_shot

if __name__ == '__main__':
    # Iterating over all domains
    for domain_name in os.listdir(DATA_FILE_PATH):
        domain_path = os.path.join(DATA_FILE_PATH, domain_name)

        # Iterating over all instances
        for instance_name in os.listdir(domain_path):
            instance_path = os.path.join(domain_path, instance_name)

            # Reading all the instances
            print(f'Starting {domain_name}/{instance_name}')
            with open(instance_path, 'r') as f:
                data = [json.loads(jline) for jline in f.readlines()]
            with tqdm(total=len(data)) as pbar:
                for idx, ele in enumerate(data):
                    print(instance_name)
                    prompt = get_prompt(domain_name, instance_name, {}, PROMPT_TECHNIQUE)
                    
                pbar.update(1)
            exit()
    exit()
    data = read_data(DATA_FILE_PATH)[START_IDX-1:]
    try:
        with tqdm(total=len(data)) as pbar:
            for idx, ele in enumerate(data):
                response = get_response('gemini-pro', ele['zero_shot_model_input'])
                write_data(response, idx, OUTPUT_DIR+f'/{ele["domain_name"]}/{ele["instance_id"]}.jsonl')
                pbar.update(1)
        with tqdm(total=len(data)) as pbar:
            for idx, ele in enumerate(data):
                response = get_response('gemini-pro', ele['zero_shot_model_input'])
                write_data(response, idx, OUTPUT_DIR+f'/{ele["domain_name"]}/{ele["instance_id"]}.jsonl')
                pbar.update(1)
    except Exception as e:
        print(e)
        print('Stopped at index', idx+1)