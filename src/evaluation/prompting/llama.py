from transformers import pipeline
from tqdm import tqdm
import os
from helper import *
import argparse
from src.common import open_jsonl

# START_IDX = 1    # Index from where to start getting the response (1-index)
# PROMPT_TECHNIQUE = 'zero_shot'    # cot, few_shot, self_consistency, zero_shot, few_shot_cot
MODEL_SIZE = '7b'
MODEL_NAME = f'meta-llama/Llama-2-{MODEL_SIZE}-chat-hf'
DATA_FILE_PATH = '../../../data/data_files_ramifications'
OUTPUT_DIR = f'../../../results_ramifications/llama-2-{MODEL_SIZE}/'
# FEW_SHOT_EXAMPLES = 9

def evaluate(file_path, pipeline_obj, save_path):
    data = open_jsonl(file_path)
    with tqdm(total=len(data)) as pbar:
        for idx, ele in enumerate(data):
            response = get_response('llama', ele['prompt'], pipeline_obj)
            # Getting the response
            ele['response'] = response
            # Writing the data
            write_data(ele,save_path)
            pbar.update(1)


if __name__ == '__main__':
    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    parser.add_argument('-p', '--prompt', type=str, required=True, help='Prompting technique')
    args = parser.parse_args()

    OUTPUT_DIR = os.path.join(OUTPUT_DIR, args.prompt)
    file_path = os.path.join(DATA_FILE_PATH, args.prompt, args.domain+'.jsonl')
    generate_text = pipeline('text-generation', model=MODEL_NAME, device_map='auto', max_length=4096, truncation=True)
    save_path =  OUTPUT_DIR + f'/{args.domain}.jsonl'
    evaluate(file_path, generate_text, save_path)