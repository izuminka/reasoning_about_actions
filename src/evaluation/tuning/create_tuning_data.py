import json
import os
from pathlib import Path
from tqdm import tqdm
import random

DATA_PATH = '../../../data/data_for_evaluation'
SAVE_PATH = '../../../data/data_for_tuning'
TRAIN_SPLIT_IID = 0.8    # % of data to be used for training
NO_INSTANCES_PER_DOMAIN = 10
RANDOM_SEED = 21

TRAINING_DOMAINS = [
    'grippers',
    'blocksworld',
    'zenotravel',
    'logistics',
    'mystery',
    'npuzzle',
]
VALIDATION_DOMAINS = [
    'satellite',
    'miconic',
]
TEST_DOMAINS = [
    'depots',
    'spanner',
    'driverlog',
    'goldminer',
    'visitall',
]

def process_data():
    training_data = []
    validation_data = []
    ood_testing_data = []
    iid_testing_data = []

    DOMAINS = TRAINING_DOMAINS + VALIDATION_DOMAINS + TEST_DOMAINS

    for random_sub in [True, False]:
        if random_sub:
            data_path = os.path.join(DATA_PATH, 'with_random_sub')
            print('Reading files with random substitutions...')
        else:
            data_path = os.path.join(DATA_PATH, 'without_random_sub')
            print('Reading files without random substitutions...')

        with tqdm(total=2*len(DOMAINS)*NO_INSTANCES_PER_DOMAIN) as pbar:
            for ramification in ['with_ramifications', 'without_ramifications']:
                for domain in DOMAINS:
                    for instance in range(1, NO_INSTANCES_PER_DOMAIN+1):
                        with open(os.path.join(data_path, ramification, 'zero_shot', domain, f'Instance_{instance}.jsonl'), 'r') as f:
                            data = [json.loads(jline) for jline in f.readlines()]
                        
                        # If random_sub is True, then we are creating data for OOD testing
                        if random_sub:
                            ood_testing_data += data
                        # If domain is in TRAINING_DOMAINS, then we are splitting training data and for IID testing
                        elif domain in TRAINING_DOMAINS:
                            random.Random(RANDOM_SEED).shuffle(data)
                            training_data += data[:int(TRAIN_SPLIT_IID*len(data))]
                            iid_testing_data += data[int(TRAIN_SPLIT_IID*len(data)):]
                        # If domain is in VALIDATION_DOMAINS, then we are creating validation data
                        elif domain in VALIDATION_DOMAINS:
                            validation_data += data
                        # If domain is in TEST_DOMAINS, then we are creating OOD testing data
                        elif domain in TEST_DOMAINS:
                            ood_testing_data += data
                        else:
                            raise ValueError(f'Unknown domain: {domain}')
                        pbar.update(1)
    
    return training_data, validation_data, ood_testing_data, iid_testing_data

if __name__ == '__main__':
    total_domains = len(TRAINING_DOMAINS) + len(VALIDATION_DOMAINS) + len(TEST_DOMAINS)
    print(f'Out of {total_domains} domains :- \
          \nTraining Domains   - {len(TRAINING_DOMAINS)} - {len(TRAINING_DOMAINS)*100/total_domains:.2f}%,\
          \nValidation Domains - {len(VALIDATION_DOMAINS)} - {len(VALIDATION_DOMAINS)*100/total_domains:.2f}%,\
          \nTest Domains       - {len(TEST_DOMAINS)} - {len(TEST_DOMAINS)*100/total_domains:.2f}%\n')
    
    training_data, validation_data, ood_testing_data, iid_testing_data = process_data()
    print(f'\nTraining Data Size    : {len(training_data)}')
    print(f'Validation Data Size  : {len(validation_data)}')
    print(f'OOD Testing Data Size : {len(ood_testing_data)}')
    print(f'IID Testing Data Size : {len(iid_testing_data)}')
    
    Path(SAVE_PATH).mkdir(parents=True, exist_ok=True)
    
    with open(os.path.join(SAVE_PATH, 'training_data.jsonl'), 'w') as f:
        for data in training_data:
            f.write(json.dumps(data) + '\n')
    with open(os.path.join(SAVE_PATH, 'validation_data.jsonl'), 'w') as f:
        for data in validation_data:
            f.write(json.dumps(data) + '\n')
    with open(os.path.join(SAVE_PATH, 'ood_testing_data.jsonl'), 'w') as f:
        for data in ood_testing_data:
            f.write(json.dumps(data) + '\n')
    with open(os.path.join(SAVE_PATH, 'iid_testing_data.jsonl'), 'w') as f:
        for data in iid_testing_data:
            f.write(json.dumps(data) + '\n')
    