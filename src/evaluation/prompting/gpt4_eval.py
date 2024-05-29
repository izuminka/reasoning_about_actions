import os

# Define the variables
model = 'gpt-4o'
DOMAINS = [
    'blocksworld', 'depots', 'driverlog', 'goldminer', 'grippers', 'logistics',
    'miconic', 'mystery', 'npuzzle', 'satellite', 'spanner', 'visitall', 'zenotravel'
]
PROMPTS = ['few_shot_1'] #'few_shot_5',
INSTANCES = [f'Instance_{i}' for i in range(1, 11)]


SUBS = 'with_random_sub'
# SUBS_RAMS_EXT = 'without_random_sub/without_ramifications'
INPUT_DIR = f'../../../data/data_for_test.pruned'
OUTPUT_DIR = '../../../results'

if __name__ == '__main__':
    # Iterate over all combinations of models, domains, instances, and prompts
    for subs in ['with_random_sub', 'without_random_sub']:
        for rams in ['without_ramifications', 'with_ramifications']:
            for instance in INSTANCES:
                for domain in DOMAINS:
                    for prompt in PROMPTS:
                        try:
                            print(f'\n\n\n Running {SUBS} {rams} {domain} {instance} {prompt} \n\n\n')

                            output_dir = f'{OUTPUT_DIR}/{model}/{SUBS}/{rams}/{prompt}/{domain}/{instance}.jsonl'
                            input_dir = f'{INPUT_DIR}/{SUBS}/{rams}/{prompt}/{domain}/{instance}.jsonl'
                            if os.path.exists(output_dir):
                                continue
                            command = (
                                f"python propreitary_inference.py "
                                f"-m {model} "
                                f"-f {input_dir} "
                                f"-o {output_dir}"
                            )
                            os.system(command)
                        except Exception as e:
                            print(e)

