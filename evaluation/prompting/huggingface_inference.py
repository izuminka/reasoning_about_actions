from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import json
from pathlib import Path
import argparse


def get_response(text, tokenizer, context_length, model):
    '''
    Generate a response given an input text using a tokenizer and a model.
    The response is generated by the model if the input text is smaller than the context length.

    Parameters:
        text (str): The input text.
        tokenizer (Tokenizer): The tokenizer used to tokenize the input text.
        context_length (int): The maximum length of the context.
        model (Model): The model used for generating the response.

    Returns:
        str: The generated response or 'NO RESPONSE' if the input text is bigger than the context length.
    '''
    input_ids = tokenizer(text, return_tensors='pt', return_token_type_ids=False)
    if input_ids['attention_mask'].shape[1] > context_length:
        return 'NO RESPONSE'
    
    return tokenizer.decode(
        model.generate(**input_ids.to('cuda'), max_new_tokens=200)[0],
        skip_special_tokens=True
    )[len(text):]

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
    parser.add_argument('-c', '--context', type=int, required=True, help='Context length')
    parser.add_argument('-d', '--huggingface_cache_dir', type=str, required=False, help='Huggingface cache directory')
    parser.add_argument('-t', '--huggingface_token', type=str, required=True, help='Huggingface token')
    parser.add_argument('-i', '--index', type=int, required=False, help='Starting zero-index for evaluation')
    return parser.parse_args()

if __name__ == '__main__':
    # Getting arguments
    args = parse_args()

    # Loading the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        cache_dir = args.huggingface_cache_dir,
        token = args.huggingface_token,
        trust_remote_code = True
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map = 'auto',
        cache_dir = args.huggingface_cache_dir,
        token = args.huggingface_token,
        trust_remote_code = True
    )

    # Reading the instance
    with open(args.file, 'r') as f:
        if args.index:
            data = [json.loads(jline) for jline in f.readlines()][args.index:]
        else:
            data = [json.loads(jline) for jline in f.readlines()]
    
    # Creating the directory where the files will be saved
    dir_path = '/'.join(args.output.split('/')[:-1])
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    with tqdm(total=len(data)) as pbar:
        for idx, ele in enumerate(data):
            response = get_response(ele['prompt'], tokenizer, args.context, model)
            ele['response'] = response
            write_response(ele, args.output)
            pbar.update(1)