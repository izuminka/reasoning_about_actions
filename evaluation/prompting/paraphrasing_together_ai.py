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


DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo" #"meta-llama/Llama-3-70b-chat-hf"
OUTPUT_TOKEN_LIMIT = 4000

with open("together4.key", "r") as f:
  os.environ["TOGETHER_API_KEY"] = f.read().strip()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

def get_output(prompt, model=DEFAULT_MODEL):
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


def api_call(prompt, num_tries = 10):
    response = None
    while num_tries > 0:
        try:
            response = get_output(prompt)
            num_tries = 0
        except Exception as e:
            print(e)
            backoff_time = get_backoff_time(str(e))
            print(f"Backing off for {backoff_time} seconds. Number of tries left: {num_tries}")
            time.sleep(backoff_time)
            num_tries -= 1
    return response


def paraphrase_prompt(text_for_paraphrasing):
    return f'''Your task is to paraphrase the following text while keeping the original meaning intact and the structure same.

Text: {text_for_paraphrasing}

Provide the paraphrased text below:
'''

massive_dump_dir = f'{PROJECT_PATH}/data/paraphrased'
os.makedirs(massive_dump_dir, exist_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    args = parser.parse_args()

    paraphrased_ids = set([int(f.split('.')[0]) for f in os.listdir(massive_dump_dir)])
    test_data = open_jsonl(f'{PROJECT_PATH}/data/test_dataset.jsonl')
    last_ind = 0
    try:
        for i, data_d in tqdm(enumerate(test_data)):
            last_ind = i
            if data_d[OUT_OBJ_DOMAIN_NAME] != args.domain or data_d[OUT_OBJ_ID] in paraphrased_ids:
                continue

            for k_input, k_output in [[OUT_OBJ_QUESTION, OUT_OBJ_QUESTION_PARAPHRASED],
                                      [OUT_OBJ_INITIAL_STATE_NL, OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED]]:
                prompt = paraphrase_prompt(data_d[k_input])
                response = api_call(prompt)
                data_d[k_output] = response.strip()
            with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
                json.dump(data_d, f)
    except Exception as e:
        print(e)



