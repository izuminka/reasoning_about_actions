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
import random


DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo" #"meta-llama/Llama-3-70b-chat-hf"
OUTPUT_TOKEN_LIMIT = 5000

with open("together5.key", "r") as f:
  os.environ["TOGETHER_API_KEY"] = f.read().strip()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

def get_output_stream(prompt, model=DEFAULT_MODEL):
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature = 0,
        max_tokens = OUTPUT_TOKEN_LIMIT
    )

    model_output = ''
    for chunk in stream:
        try:
            model_output += chunk.choices[0].message.content or ""
        except Exception as e:
            return None
    return model_output

def get_output(prompt, model=DEFAULT_MODEL):
    output = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        temperature = 0,
        max_tokens = OUTPUT_TOKEN_LIMIT
    )

    try:
        if output.choices:
            return output.choices[0].message.content
    except Exception as e:
        print(e)
        return None
    return None


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
    parser.add_argument('-i', '--instance', type=str, required=True, help='Domain name')
    args = parser.parse_args()

    paraphrased_ids = set([f.strip('.json') for f in os.listdir(massive_dump_dir) if f.endswith('.json')])
    print(len(paraphrased_ids))
    print('gathered ids')


    test_data = open_jsonl(f'{PROJECT_PATH}/data/test_dataset.jsonl')
    random.shuffle(test_data) # TODO rm
    last_ind = 0

    try:
        for data_d in tqdm(test_data):
            if data_d[OUT_OBJ_ID] in paraphrased_ids or (data_d[OUT_OBJ_DOMAIN_NAME] != args.domain and data_d[OUT_OBJ_INSTANCE_ID  ] != args.instance):
                continue

            for k_input, k_output in [[OUT_OBJ_QUESTION, OUT_OBJ_QUESTION_PARAPHRASED],
                                      [OUT_OBJ_INITIAL_STATE_NL, OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED]]:
                prompt = paraphrase_prompt(data_d[k_input])
                response = api_call(prompt)
                if not response:
                    break
                data_d[k_output] = response.strip()
            if not response:
                with open(f'{PROJECT_PATH}/data/failed_ids', 'a') as f:
                    f.write(f'{data_d[OUT_OBJ_ID]}\n')
            else:
                with open(f'{massive_dump_dir}/{data_d[OUT_OBJ_ID]}.json', 'w') as f:
                    json.dump(data_d, f)
    except Exception as e:
        print(e)


#TODO make sure paraphrased are within acceptable char len from the original


