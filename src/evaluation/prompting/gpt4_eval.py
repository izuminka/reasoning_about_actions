import os

# Define the variables
MODELS = ['gpt-4o']
DOMAINS = [
    'blocksworld', 'depots', 'driverlog', 'goldminer', 'grippers', 'logistics',
    'miconic', 'mystery', 'npuzzle', 'satellite', 'spanner', 'visitall', 'zenotravel'
]
PROMPTS = ['few_shot_1'] #'few_shot_5',
INSTANCES = [f'Instance_{i}' for i in range(1, 11)]


SUBS_RAMS_EXT = 'without_random_sub/without_ramifications'
INPUT_DIR = f'../../../data/data_for_test'
OUTPUT_DIR = '../../../results'

if __name__ == '__main__':
    # Iterate over all combinations of models, domains, instances, and prompts
    for model in MODELS:
        for domain in DOMAINS:
            for instance in INSTANCES:
                for prompt in PROMPTS:
                    print(f'Running {domain} {instance} {prompt}')

                    output_dir = f'{OUTPUT_DIR}/{model}/{SUBS_RAMS_EXT}/{prompt}/{domain}/{instance}.jsonl'
                    input_dir = f'{INPUT_DIR}/{SUBS_RAMS_EXT}/{prompt}/{domain}/{instance}.jsonl'
                    if os.path.exists(output_dir):
                        continue
                    command = (
                        f"python propreitary_inference.py "
                        f"-m {model} "
                        f"-f {input_dir} "
                        f"-o {output_dir}"
                    )
                    os.system(command)

