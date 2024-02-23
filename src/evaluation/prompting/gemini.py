from tqdm import tqdm
import os
from helper import *
import argparse

DATA_FILE_PATH = '../../../data/data_files_ramifications'
OUTPUT_DIR = '../../../results_ramifications/gemini/'

if __name__ == '__main__':
    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    parser.add_argument('-p', '--prompt', type=str, required=True, help='Prompting technique')
    parser.add_argument('-i', '--index', type=str, required=False, help='Starting 0-index for evaluation')
    args = parser.parse_args()

    OUTPUT_DIR = os.path.join(OUTPUT_DIR, args.prompt)
    file_path = os.path.join(DATA_FILE_PATH, args.prompt, args.domain+'.jsonl')

    # Reading the instance
    with open(file_path, 'r') as f:
        data = [json.loads(jline) for jline in f.readlines()][args.index:]
    with tqdm(total=len(data)) as pbar:
        for idx, ele in enumerate(data):
            # Getting the response
            response = get_response('gemini-pro', ele['prompt'])
            ele['response'] = response
            # Writing the data
            write_data(ele, OUTPUT_DIR + f'/{args.domain}.jsonl')
            pbar.update(1)