import sys
sys.path.insert(0,'../../')
from src.common import *
from src.questions_construction.domains import *
from tqdm import tqdm
from time import time

def fix_dict(result, domain):
    if domain.is_random_sub:
        if '[[' and ']]' in result["label"]:
            repl = result["label"].replace('[[', ' [[ ').replace(']]', ' ]] ')
            repl = domain.to_random_substring(repl)
            repl = repl.replace(' [[ ', '[[').replace(' ]] ', ']]')
            result["label"] = repl

        repl = result["prompt"].replace('[[', ' [[ ').replace(']]', ' ]] ')
        repl = domain.to_random_substring(repl)
        repl = repl.replace(' [[ ', '[[').replace(' ]] ', ']]')
        result["prompt"] = repl
    return result

if __name__ == '__main__':
    data_for_eval_path = os.path.join(DATA_PATH, 'data_for_test')

    ramifications = WITHOUT_RAMIFICATIONS
    corrupted_data = []
    with tqdm(total=2*3*13*10) as pbar:
        for ramifications in [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]:
            for prompt_type in ['few_shot_1', 'few_shot_3', 'few_shot_5']:
                for domain_class in ALL_DOMAIN_CLASSES:
                    domain_name = domain_class.DOMAIN_NAME
                    domain = domain_class(True, ramifications == WITH_RAMIFICATIONS)
                    for instance in [f'Instance_{i}' for i in range(1, 11)]:
                        pbar.update(1)
                        try:
                            data_path = os.path.join(data_for_eval_path, WITH_RANDOM_SUB, ramifications, prompt_type, domain_name,
                                                    instance + '.jsonl')
                            if not os.path.exists(data_path):
                                print('Missing', data_path)
                                continue
                            data = open_jsonl(data_path)
                            for i in range(len(data)):
                                data[i] = fix_dict(data[i], domain)
                            save_jsonl(data, data_path)
                        except:
                            print(data_path)
                            corrupted_data.append(data_path)
    # save_jsonl(corrupted_data, f'corrupted_data.{ramifications}.{int(time())}.jsonl')

