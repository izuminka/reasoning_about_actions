from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import json
from pathlib import Path
import argparse

HUGGINGFACE_CACHE_DIR = '/scratch/dhanda/huggingface_cache'
HUGGINGFACE_TOKEN = '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'

def get_response(text, tokenizer, context_length, model):
    input_ids = tokenizer(text, return_tensors='pt')
    if input_ids['attention_mask'].shape[1] > context_length:
        return 'INPUT BIGGER THAN CONTEXT LENGTH'
    return tokenizer.decode(model.generate(**input_ids.to('cuda'))[0], skip_special_tokens=True)[len(text):]

def write_response(json_ele, file_path):
    with open(file_path, 'a+') as f:
        f.write(json.dumps(json_ele)+'\n')

if __name__ == '__main__':
    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, required=True, help='Model name')
    parser.add_argument('-f', '--file', type=str, required=True, help='Input file path')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file path')
    parser.add_argument('-c', '--context', type=int, required=True, help='Context length')
    parser.add_argument('-i', '--index', type=int, required=False, help='Starting zero-index for evaluation')
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model, cache_dir=HUGGINGFACE_CACHE_DIR,
                                              token=HUGGINGFACE_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(args.model, device_map='auto', 
                                                 cache_dir=HUGGINGFACE_CACHE_DIR,
                                                 token=HUGGINGFACE_TOKEN)

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
            print(response)
            exit()
            write_response(ele, args.output)
            pbar.update(1)