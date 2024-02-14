from tqdm import tqdm
import os
from helper import *
import argparse

# START_IDX = 1    # Index from where to start getting the response (1-index)
# PROMPT_TECHNIQUE = 'zero_shot'    # cot, few_shot, self_consistency, zero_shot, few_shot_cot

DATA_FILE_PATH = '../../../data/questions'
OUTPUT_DIR = '../../../results/gemini/'
FEW_SHOT_EXAMPLES = 9

if __name__ == '__main__':
    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name')
    parser.add_argument('-p', '--prompt', type=str, required=True, help='Prompting technique')
    args = parser.parse_args()
    OUTPUT_DIR = os.path.join(OUTPUT_DIR, args.prompt)
    domain_path = os.path.join(DATA_FILE_PATH, args.domain)
    
    # Iterating over all instances
    for instance_name in os.listdir(domain_path):
        instance_path = os.path.join(domain_path, instance_name)
        print(f'Starting {args.domain}/{instance_name} with {args.prompt}')

        # Reading the instance
        with open(instance_path, 'r') as f:
            data = [json.loads(jline) for jline in f.readlines()]
        with tqdm(total=len(data)) as pbar:
            for idx, ele in enumerate(data):
                # Getting the prompt
                if args.prompt == 'zero_shot':
                    prompt = get_prompt(args.domain, instance_name, ele, args.prompt)[0]['zero_shot_model_input']
                elif args.prompt == 'few_shot':
                    prompt = get_prompt(args.domain, instance_name, ele, args.prompt, FEW_SHOT_EXAMPLES)[0]
                elif args.prompt == 'few_shot_cot':
                    prompt = get_prompt(args.domain, instance_name, ele, args.prompt, FEW_SHOT_EXAMPLES)[0]

                response = get_response('gemini-pro', prompt)
                # Getting the response
                ele['prompt'] = prompt
                ele['response'] = response
                # Writing the data
                write_data(ele, OUTPUT_DIR + f'/{args.domain}/{instance_name}')
                pbar.update(1)