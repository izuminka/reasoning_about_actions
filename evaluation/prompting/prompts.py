from tqdm import tqdm
from common import *
from questions_construction.domains import DOMAIN_NAMES

ZERO_SHOT_PROMPT_KEY = 'zero_shot'
PROMPT_KEY = 'prompt'
LABEL_KEY = 'lebel'
ID_KEY = OUT_OBJ_ID


def zero_shot_prompt(domain_description, initial_state_nl, question):
    return f'''[DOMAIN DESCRIPTION]
{domain_description}

[INITIAL CONDITIONS]
Initially, {initial_state_nl}

[QUESTION]
{question}

Answer the above question in the following format:

[REASON]
<Write your reasoning here>

[ANSWER]
<Write the final answer here>
'''


def create_prompts_dataset(questions, domain_descr_by_name, prompt_type):
    prompts = []
    for question_d in tqdm(questions, total=len(questions)):
        prompt_d = {ID_KEY: question_d[OUT_OBJ_ID], LABEL_KEY: question_d[OUT_OBJ_ANSWER]}
        domain_name = question_d[OUT_OBJ_DOMAIN_NAME]
        domain_description = domain_descr_by_name[domain_name]
        if prompt_type == ZERO_SHOT_PROMPT_KEY:
            prompt_d[PROMPT_KEY] = zero_shot_prompt(domain_description,
                                                    question_d[OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED],
                                                    question_d[OUT_OBJ_QUESTION_PARAPHRASED])
        else:
            raise ValueError(f'Unknown prompt type: {prompt_type}')
        prompts.append(prompt_d)
    return prompts


def get_domain_descriptions(data_path):
    domain_descr_by_name = {}
    for domain_name in DOMAIN_NAMES:
        with open(f'{data_path}/domain_descriptions/without_ramifications/{domain_name}.txt', 'r') as f:
            domain_descr_by_name[domain_name] = f.read().strip()
    return domain_descr_by_name


if __name__ == '__main__':
    questions = open_jsonl(f'{PROJECT_PATH}/data/test_data.paraphrased.cleaned.jsonl')
    domain_descr_by_name = get_domain_descriptions(f'{PROJECT_PATH}/data')

    save_dir = f'{PROJECT_PATH}/data/prompts'
    os.makedirs(save_dir, exist_ok=True)
    prompt_type = ZERO_SHOT_PROMPT_KEY
    if prompt_type == ZERO_SHOT_PROMPT_KEY:
        prompts = create_prompts_dataset(questions, domain_descr_by_name, ZERO_SHOT_PROMPT_KEY)
        save_jsonl(prompts, f'{save_dir}/{prompt_type}.jsonl')
    else:
        raise ValueError(f'Unknown prompt type: {prompt_type}')
