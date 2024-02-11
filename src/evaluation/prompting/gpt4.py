from tqdm import tqdm
from helper import *

START_IDX = 1    # Index from where to start getting the response (1-index)

if __name__ == '__main__':
    data = read_data()[START_IDX-1:]
    try:
        for idx, ele in tqdm(enumerate(data)):
            response = get_response('gpt4', ele)
            write_data(response, idx, '')
    except Exception as e:
        print(e)
        print('Stopped at index', idx+1)