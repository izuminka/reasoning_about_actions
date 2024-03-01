from transformers import pipeline
from tqdm import tqdm
import os
from helper import *
import argparse

# START_IDX = 1    # Index from where to start getting the response (1-index)
# PROMPT_TECHNIQUE = 'zero_shot'    # cot, few_shot, self_consistency, zero_shot, few_shot_cot
MODEL_SIZE = '7B'
MODEL_NAME = f'mistralai/Mistral-{MODEL_SIZE}-Instruct-v0.2'
DATA_FILE_PATH = '../../../data/data_files'
OUTPUT_DIR = f'../../../results/mistral_{MODEL_SIZE}_instruct/'
# FEW_SHOT_EXAMPLES = 9

if __name__ == '__main__':
    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    parser.add_argument('-p', '--prompt', type=str, required=True, help='Prompting technique')
    args = parser.parse_args()

    OUTPUT_DIR = os.path.join(OUTPUT_DIR, args.prompt)
    file_path = os.path.join(DATA_FILE_PATH, args.prompt, args.domain+'.jsonl')
    generate_text = pipeline('text-generation', model=MODEL_NAME, device_map='auto', max_length=4096, truncation=True, padding =True)

    # Reading the instance
    with open(file_path, 'r') as f:
        data = [json.loads(jline) for jline in f.readlines()]
    with tqdm(total=len(data)) as pbar:
        for idx, ele in enumerate(data):
            response = get_response('mistral', ele['prompt'], generate_text)
            # Getting the response
            ele['response'] = response
            # Writing the data
            write_data(ele, OUTPUT_DIR + f'/{args.domain}.jsonl')
            pbar.update(1)