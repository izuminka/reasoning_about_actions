import json
import os
from pathlib import Path
from tqdm import tqdm
import random

DATA_PATH = '../../../data/data_for_evaluation'
SAVE_PATH = '../../../data/data_for_tuning'
RANDOM_SEED = 21

TRAINING_DOMAINS = [
    'blocksworld',
    'depots',
    'goldminer',
    'miconic',
    'npuzzle',
    'visitall',
]
VALIDATION_DOMAINS = [
    'driverlog',
    'gripper',
]
TEST_DOMAINS = [
    'logistics',
    'mystery',
    'satellite',
    'spanner',
    'zenotravel',
]

if __name__ == '__main__':
    total_domains = len(TRAINING_DOMAINS) + len(VALIDATION_DOMAINS) + len(TEST_DOMAINS)
    print(f'Out of {total_domains} domains :- \
          \nTraining Domains   - {len(TRAINING_DOMAINS)} - {len(TRAINING_DOMAINS)*100/total_domains:.2f}%,\
          \nValidation Domains - {len(VALIDATION_DOMAINS)} - {len(VALIDATION_DOMAINS)*100/total_domains:.2f}%,\
          \nTest Domains       - {len(TEST_DOMAINS)} - {len(TEST_DOMAINS)*100/total_domains:.2f}%\n')
    
    # Reading training data
    print('Creating Training Data...')
    training_data = []
    with tqdm(total=len(TRAINING_DOMAINS)*20) as pbar:
        for domain in TRAINING_DOMAINS:
            for ramification in ['with_ramifications', 'without_ramifications']:
                for instance in range(1, 11):
                    with open(os.path.join(DATA_PATH, 'without_random_sub', ramification, 'zero_shot', domain, f'Instance_{instance}.jsonl'), 'r') as f:
                        training_data += [json.loads(jline) for jline in f.readlines()]
                    pbar.update(1)
    print(f'Training Data Length: {len(training_data)}')
    # Saving training data
    Path(os.path.join(SAVE_PATH, 'train.jsonl')).mkdir(parents=True, exist_ok=True)
    random.Random(RANDOM_SEED).shuffle(training_data)    # Shuffling the data
    with open(os.path.join(SAVE_PATH, f'train.jsonl'), 'w') as f:
        for instance in training_data:
            f.write(json.dumps(instance)+'\n')
    