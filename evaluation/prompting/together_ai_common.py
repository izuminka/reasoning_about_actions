import os
import time

import numpy as np

from propreitary_inference import *

from tqdm import tqdm
import json
from pathlib import Path

import os
from together import Together

import sys
sys.path.insert(0, '../../')
from common import *




with open("together5.key", "r") as f:
  os.environ["TOGETHER_API_KEY"] = f.read().strip()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))


def get_output_stream(prompt, model, max_tokens):
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature = 0,
        max_tokens = max_tokens,
    )

    model_output = ''
    for chunk in stream:
        try:
            model_output += chunk.choices[0].message.content or ""
        except Exception as e:
            return None
    return model_output

def get_output(prompt, model, max_tokens):
    output = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        temperature = 0,
        max_tokens = max_tokens
    )

    try:
        if output.choices:
            return output.choices[0].message.content
    except Exception as e:
        print(e)
        return None
    return None


def api_call(prompt, model, max_tokens, num_tries = 10):
    response = None
    while num_tries > 0:
        try:
            response = get_output(prompt, model, max_tokens)
            num_tries = 0
        except Exception as e:
            print(e)
            backoff_time = get_backoff_time(str(e))
            print(f"Backing off for {backoff_time} seconds. Number of tries left: {num_tries}")
            time.sleep(backoff_time)
            num_tries -= 1
    return response

