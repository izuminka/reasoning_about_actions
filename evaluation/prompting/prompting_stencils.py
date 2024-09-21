import json
import os
from tqdm import tqdm
import argparse
import sys
sys.path.insert(0, '../../../')
from questions_construction.domains import *

ROOT_DIRECTORY = "../../../data/"
ALL_DOMAIN_CLASSES = [
    Blocksworld,
    Depots,
    Driverlog,
    Goldminer,
    Grippers,
    Logistics,
    Miconic,
    Mystery,
    Npuzzle,
    Satellite,
    Spanner,
    Visitall,
    Zenotravel
]

class Generate_prompting_template:
    def __init__(self, root_directory, domain_class, selected_file, domain_folder_name):
        self.root_directory = root_directory
        self.domain_class = domain_class
        self.domain_folder_name = domain_folder_name
        # self.instance_id = instance_id
        self.selected_file = selected_file
    
    def zero_shot_prompt(self, jsonl_instance):
        results = []
        with open(jsonl_instance, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for dictionary_item in question_jsonl:
            dictionary_item['prompt'] = f'''[DOMAIN DESCRIPTION]
{self.domain_class.domain_description}

[INITIAL CONDITIONS]
Initially, {dictionary_item["initial_state_nl"]}

[QUESTION]
{dictionary_item["question"]}.

Answer the above question in the following format:

[REASON]
<Write your reasoning here>

[ANSWER]
<Write the final answer here>
'''
            dictionary_item['label'] = {dictionary_item['answer']}
            results.append(dictionary_item)
        return results
    
    def few_shot_prompt(self, n_shot):
        jsonl_instance_list = [os.path.join(self.root_directory, file) for file in os.listdir(self.root_directory) if file.endswith('.jsonl')]
        selected_jsonl = jsonl_instance_list.pop(jsonl_instance_list.index(self.selected_file))
        results = []
        
        with open(selected_jsonl, 'r') as f:
            data = f.readlines()
            question_jsonl = [json.loads(x) for x in data]
        
        for i in range(len(question_jsonl)):
            result_sublist = []
            for j in range(len(jsonl_instance_list)):
                if len(result_sublist) == n_shot:
                    results.append(result_sublist)
                    break
                else:
                    with open(jsonl_instance_list[j], 'r') as f:
                        random_selected_jsonl = f.readlines()
                    random_selected_jsonl = [json.loads(x) for x in random_selected_jsonl]
                    random.shuffle(random_selected_jsonl)
                    for k in range(len(random_selected_jsonl)):
                        if (
                            question_jsonl[i]['question_category'] == random_selected_jsonl[k]['question_category']
                            and question_jsonl[i]['fluent_type'] == random_selected_jsonl[k]['fluent_type']
                            and question_jsonl[i]['plan_length'] == random_selected_jsonl[k]['plan_length']
                            and question_jsonl[i]['answer_type'] == random_selected_jsonl[k]['answer_type']
                        ):
                            result_sublist.append({
                                'initial_state_nl' : random_selected_jsonl[k]['initial_state_nl'],
                                'question' : random_selected_jsonl[k]['question'],
                                'answer' : random_selected_jsonl[k]['answer']
                            })
                            break
        
        final_prompts = []
        labels = []
        id = []
        for i in range(len(question_jsonl)):
            final_prompt_sublist = []
            final_prompt_sublist.append(f'[DOMAIN DESCRIPTION]\n\n{self.domain_class.domain_description}\n\n')
            for k in range(len(results[i])):
                # Contruct a prompt template with k examples from the random selected jsonl
                if question_jsonl[i]['answer_type'] == 'free_answer':
                    final_prompt_sublist.append(f'''[EXAMPLE {k+1}]

[INITIAL CONDITIONS]
Initially, {results[i][k]["initial_state_nl"]}

[QUESTION]
{results[i][k]["question"]}.
Provide your final answer in between [[ and ]].

[ANSWER]: [[{results[i][k]["answer"]}]]

''')
                else:
                    final_prompt_sublist.append(f'''[EXAMPLE {k+1}]

[INITIAL CONDITIONS]
Initially, {results[i][k]["initial_state_nl"]}

[QUESTION]
{results[i][k]["question"]}
Just provide your answer as TRUE/FALSE.

[ANSWER]: {results[i][k]["answer"]}

''')
            if question_jsonl[i]['answer_type']=='free_answer':
                final_prompt_sublist.append(f'''
Based on the above examples, answer the below question:

[INITIAL CONDITIONS]
Initially, {question_jsonl[i]['initial_state_nl']}

[QUESTION]
{question_jsonl[i]['question']}.
Provide your final answer in between [[ and ]].

[ANSWER]:''')
                labels.append(f"[[{question_jsonl[i]['answer']}]]")
                id.append(question_jsonl[i]['id'])
            else:
                final_prompt_sublist.append(f'''
Based on the above examples, answer the below question:

[INITIAL CONDITIONS]
Initially, {question_jsonl[i]['initial_state_nl']}

[QUESTION]
{question_jsonl[i]['question']}.
Just provide your answer as TRUE/FALSE.

[ANSWER]:''')
                labels.append(question_jsonl[i]['answer'])
                id.append(question_jsonl[i]['id'])
            final_prompts.append(''.join(final_prompt_sublist))

        return final_prompts, labels, id

def get_folder_name(domain_instance):
    """Generate a valid folder name from a domain instance."""
    return type(domain_instance).__name__.lower() + '/'

def save_few_shot_prompts(domain_class, is_random_sub, is_ramifications, root_directory, n_shot):
    """Unified function to save few-shot prompts with simplified path handling."""
    domain_instance = domain_class(is_random_sub=is_random_sub, is_ramifications=is_ramifications)
    domain_folder_name = get_folder_name(domain_instance)
    
    sub_dir = 'with_random_sub' if is_random_sub else 'without_random_sub'
    ram_dir = 'with_ramifications' if is_ramifications else 'without_ramifications'
    domain_path = os.path.join(root_directory, "questions_m1", sub_dir, domain_folder_name)
    output_directory = os.path.join(root_directory, "data_for_evaluation", sub_dir, ram_dir, f'few_shot_{n_shot}', domain_folder_name)
    print(f'Creating output directory: {output_directory}')
    os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

    # Ensure the domain directory is correctly formatted and exists
    if not os.path.exists(domain_path):
        raise FileNotFoundError(f"Directory not found: {domain_path}")

    # Collect all .jsonl files in the domain directory
    selected_files = [os.path.join(domain_path, file) for file in os.listdir(domain_path) if file.endswith('.jsonl')]
    
    with tqdm(total=len(selected_files)) as pbar:
        for i, selected_file in enumerate(selected_files):
            few_shot = Generate_prompting_template(domain_path, domain_instance, selected_file, domain_folder_name)
            final_prompts, labels,id = few_shot.few_shot_prompt(n_shot)
            with open(os.path.join(output_directory, f'Instance_{i+1}.jsonl'), 'w') as f:
                for prompt, label,x in zip(final_prompts, labels,id):
                    f.write(json.dumps({'prompt': prompt, 'label': label,'id':x}) + '\n')
            pbar.update(1)

def parse_args():
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate few-shot prompting templates for all domains.")
    parser.add_argument('--domain', type=str, required=True, help="Name of the domain")
    parser.add_argument('--random', type=str2bool, required=True, help="Boolean flag for random substitutions")
    parser.add_argument('--ramification', type=str2bool, required=True, help="Boolean flag for ramification questions")
    parser.add_argument('--n_shot', type=int, required=True, help="Number of examples for n-shot")
    return parser.parse_args()

def get_domain_class(domain_name):
    for domain_class in ALL_DOMAIN_CLASSES:
        if domain_class.__name__.lower() == domain_name:
            return domain_class

if __name__ == '__main__':
    args = parse_args()
    print(args.ramification, type(args.ramification))

    save_few_shot_prompts(
        get_domain_class(args.domain),
        is_random_sub = args.random,
        is_ramifications = args.ramification,
        root_directory = ROOT_DIRECTORY,
        n_shot = args.n_shot
    )
