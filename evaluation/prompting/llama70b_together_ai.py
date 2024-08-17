import os
import time
from propreitary_inference import *

from tqdm import tqdm
import json
from pathlib import Path

import os
from together import Together

import sys
sys.path.insert(0, '../../')
from common import *

with open("together3.key", "r") as f:
  os.environ["TOGETHER_API_KEY"] = f.read().strip()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

def get_output(prompt, model="meta-llama/Llama-3-70b-chat-hf"):
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature = 0,
        max_tokens = OUTPUT_TOKEN_LIMIT
    )

    model_output = ''
    for chunk in stream:
        model_output += chunk.choices[0].delta.content or ""
    return model_output

# Define the variables
model = 'llama70b'
PROMPTS = ['few_shot_1'] #'few_shot_5',

# DOMAINS = ['blocksworld']# , 'depots', 'driverlog', 'goldminer', 'grippers', 'logistics','miconic', 'mystery', 'npuzzle',
# 'satellite', 'spanner', 'visitall', 'zenotravel']
INSTANCES = [f'Instance_{i}' for i in range(1, 11)]

SUBS = 'without_random_sub'
RAMS = 'without_ramifications'
INPUT_DIR = f'{PROJECT_PATH}/data/prompts_for_test.pruned'
OUTPUT_DIR = f'{PROJECT_PATH}/results'
# INPUT_DIR = f'../../../data/composite_questions_for_test'
# OUTPUT_DIR = '../../../results_composite'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    args = parser.parse_args()

    domain = args.domain
    for instance in INSTANCES:
        for prompt in PROMPTS:
            try:
                print(f'\n\n\n Running {SUBS} {RAMS} {domain} {instance} {prompt} \n\n\n')

                output_dir = f'{OUTPUT_DIR}/{model}/{SUBS}/{RAMS}/{prompt}/{domain}/{instance}.jsonl'
                input_dir = f'{INPUT_DIR}/{SUBS}/{RAMS}/{prompt}/{domain}/{instance}.jsonl'
                if os.path.exists(output_dir):
                    continue
                # Reading the instance
                with open(input_dir, 'r') as f:
                    data = [json.loads(jline) for jline in f.readlines()]

                # Creating the directory where the files will be saved
                dir_path = '/'.join(output_dir.split('/')[:-1])
                Path(dir_path).mkdir(parents=True, exist_ok=True)

                # Prompting the model
                with tqdm(total=len(data)) as pbar:
                    for idx, ele in enumerate(data):
                        num_tries = 10
                        while num_tries > 0:
                            try:
                                response = get_output(ele['prompt'])
                                num_tries = 0
                            except Exception as e:
                                print(e)
                                backoff_time = get_backoff_time(str(e))
                                print(f"Backing off for {backoff_time} seconds. Number of tries left: {num_tries}")
                                time.sleep(backoff_time)
                                num_tries -= 1
                        ele['response'] = response
                        print(response)
                        write_response(ele, output_dir)
                        pbar.update(1)
            except Exception as e:
                print(e)

