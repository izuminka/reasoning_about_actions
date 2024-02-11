from tqdm import tqdm
from helper import *

START_IDX = 30    # Index from where to start getting the response (1-index)
DATA_FILE_PATH = 'model_input.jsonl'
OUTPUT_DIR = '../../../results/gemini/zero_shot'

if __name__ == '__main__':
    data = read_data(DATA_FILE_PATH)[START_IDX-1:]
    try:
        with tqdm(total=len(data)) as pbar:
            for idx, ele in enumerate(data):
                response = get_response('gemini-pro', ele['zero_shot_model_input'])
                write_data(response, idx, OUTPUT_DIR+f'/{ele["domain_name"]}/{ele["instance_id"]}.jsonl')
                pbar.update(1)
    except Exception as e:
        print(e)
        print('Stopped at index', idx+1)