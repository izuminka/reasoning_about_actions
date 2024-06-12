import time

from tqdm import tqdm
import json
from pathlib import Path
import argparse
import google.generativeai as genai    # pip install -q -U google-generativeai
import openai           # pip install openai

GEMINI_MODEL_NAME = 'gemini-pro'
GPT_MODEL_NAME = 'gpt-4o' #'gpt-4-0125-preview'
# CLAUDE_MODEL_NAME = 'claude-opus'


# model = genai.get_model(f'models/{GEMINI_MODEL_NAME}') # get model info
INPUT_TOKEN_LIMIT = 30720
OUTPUT_TOKEN_LIMIT = 2048

REGEX_TIME = r"try again in (\d+\.\d+)s"
import re

def get_backoff_time(text, default=15, backoff_factor=1.1):
    match = re.search(REGEX_TIME, text)
    if match:
        return int(float(match.group(1))*backoff_factor)
    else:
        return default


def get_response(text, model_name, model=None, temp=0.0):
    '''
    Generates a response based on the given text using the specified model.

    Args:
        text (str): The input text for generating the response.
        model_name (str): The name of the model to use for generating the response.
        model (object, optional): The model object to use for generating the response. Defaults to None.
        temp (float, optional): The temperature value for controlling the randomness of the response. Defaults to 0.0.

    Returns:
        str: The generated response. "NO RESPONSE" is returned if the model refuses to generate a response due to Recitation.

    Raises:
        Exception: If an invalid model name is provided.
    '''
    if model_name == GEMINI_MODEL_NAME:
        response = model.generate_content(
            text,
            generation_config = genai.types.GenerationConfig(
                candidate_count = 1,
                temperature = temp,
                max_output_tokens = OUTPUT_TOKEN_LIMIT
            )
        )
        try:
            return response.text
        except:
            return "NO RESPONSE"
    elif model_name == GPT_MODEL_NAME:
        response = openai.ChatCompletion.create(
            model = GPT_MODEL_NAME,
            messages = [
                {"role": "user", "content": text}
            ],
            temperature = temp,
            max_tokens = OUTPUT_TOKEN_LIMIT
        )
        return response.choices[0].message.content
    else:
        raise Exception(f'{model_name} is an invalid model')

def write_response(json_ele, file_path):
    '''
    Write the JSON element to a file.

    Args:
        json_ele (dict): The JSON element to write.
        file_path (str): The path to the file.

    Returns:
        None
    '''
    with open(file_path, 'a+') as f:
        f.write(json.dumps(json_ele)+'\n')

def parse_args():
    '''
    Parse the arguments for the script
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, required=True, help='Model name')
    parser.add_argument('-f', '--file', type=str, required=True, help='Input file path')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file path')
    # parser.add_argument('-k', '--model_api_key', type=str, required=True, help='API key')
    parser.add_argument('-i', '--index', type=int, required=False, help='Starting zero-index for evaluation')
    parser.add_argument('-t', '--temperature', type=float, required=False, default=0.0, help='Temperature for generation')
    return parser.parse_args()


if __name__ == '__main__':
    # Getting arguments
    args = parse_args()

    # Loading the Gemini-Pro and OpenAI API instances
    if args.model.lower()=='gemini-pro' or args.model.lower()=='gemini':
        genai.configure(api_key=args.model_api_key)
        model_name = GEMINI_MODEL_NAME
        model = genai.GenerativeModel(model_name)
    elif args.model.lower()=='gpt4' or args.model.lower()=='gpt' or args.model.lower()=='gpt-4' or args.model.lower()=='gpt-4o':
        with open('openai.api.key') as f:
            openai.api_key = f.read()
        model_name = GPT_MODEL_NAME
    else:
        raise Exception(f'{args.model} is an invalid model')

    # Reading the instance
    with open(args.file, 'r') as f:
        if args.index:
            data = [json.loads(jline) for jline in f.readlines()][args.index:]
        else:
            data = [json.loads(jline) for jline in f.readlines()]
    
    # Creating the directory where the files will be saved
    dir_path = '/'.join(args.output.split('/')[:-1])
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Prompting the model
    with tqdm(total=len(data)) as pbar:
        for idx, ele in enumerate(data):
            num_tries = 10
            while num_tries > 0:
                try:
                    if model_name == GEMINI_MODEL_NAME:
                        response = get_response(
                            text = ele['prompt'],
                            model_name = model_name,
                            model = model,
                            temp = args.temperature
                        )
                    elif model_name == GPT_MODEL_NAME:
                        response = get_response(
                            text = ele['prompt'],
                            model_name = model_name,
                            temp = args.temperature
                        )
                    num_tries = 0
                except openai.error.RateLimitError as e:
                    print(e)
                    backoff_time = get_backoff_time(str(e))
                    print(f"Backing off for {backoff_time} seconds. Number of tries left: {num_tries}")
                    time.sleep(backoff_time)
                    num_tries -= 1
            ele['response'] = response
            print(response)
            write_response(ele, args.output)
            pbar.update(1)