import json
import os
import glob
import sys
sys.path.insert(0,'../../../')
from src.questions_construction.domains import *




class Generate_prompting_template:
    def __init__(self, root_directory,domain_class,instance_id,selected_file,domain_folder_name):
        self.root_directory = root_directory
        self.domain_class = domain_class
        self.domain_folder_name = domain_folder_name
        self.instance_id = instance_id
        self.selected_file = selected_file
    
    def zero_shot_prompt(self,jsonl_instance):
        results = []
        with open(jsonl_instance, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for dictionary_item in question_jsonl:
            if dictionary_item['answer_type']=='free_answer':
                dictionary_item['prompt'] = f'[DOMAIN DESCRIPTION]\n\n{self.domain_class.domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {dictionary_item["initial_state_nl"]}\n\n[QUESTION]\n{dictionary_item["question"]}.\nProvide your final answer in between [[ and ]]'
                dictionary_item['label'] = [dictionary_item['answer']]
            else:
                dictionary_item['prompt'] = f'[DOMAIN DESCRIPTION]\n\n{self.domain_class.domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {dictionary_item["initial_state_nl"]}\n\n[QUESTION]\n{dictionary_item["question"]}.\nJust provide your answer as TRUE/FALSE.'
                dictionary_item['label'] = dictionary_item['answer']
            results.append(dictionary_item)
        return results
                
        
    
    def few_shot_prompt(self,n_shot,cot_key):
        jsonl_instance_list = [os.path.join(self.root_directory, self.domain_folder_name, file) for file in os.listdir(os.path.join(self.root_directory, self.domain_folder_name)) if file.endswith('.jsonl')]
        selected_jsonl = jsonl_instance_list.pop(jsonl_instance_list.index(self.selected_file))
        with open(selected_jsonl, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        n_shot_selected_jsonl = random.sample(jsonl_instance_list,n_shot)
        results = []
        with open(selected_jsonl, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for n in range(len(n_shot_selected_jsonl)):
            with open(n_shot_selected_jsonl[n], 'r') as f:
                random_selected_jsonl = f.readlines()
            random_selected_jsonl = [json.loads(x) for x in random_selected_jsonl]
            for i in range(len(question_jsonl)):
                result_sublist = []
                for j in range(len(random_selected_jsonl)):
                    if question_jsonl[i]['question_category'] == random_selected_jsonl[j]['question_category'] and question_jsonl[i]['question_name'] == random_selected_jsonl[j]['question_name'] and question_jsonl[i]['fluent_type'] == random_selected_jsonl[j]['fluent_type'] and question_jsonl[i]['plan_length'] == random_selected_jsonl[j]['plan_length'] and question_jsonl[i]['answer_type'] == random_selected_jsonl[j]['answer_type']:
                        result_sublist.append({'plan_length':random_selected_jsonl[j]['plan_length'],'question_name':random_selected_jsonl[j]['question_name'],'question_category':random_selected_jsonl[j]['question_category'],'initial_state_nl':random_selected_jsonl[j]['initial_state_nl'],'question':random_selected_jsonl[j]['question'],'answer':random_selected_jsonl[j]['answer']})
                        results.append(result_sublist)
                        break
        print(results[0:5])
        print(len(results))
        print(n_shot_selected_jsonl)

                
if __name__ == '__main__':
    root_directory = "../../../data/questions_m1/with_random_sub/"
    selected_file = "../../../data/questions_m1/with_random_sub/blocksworld/Instance_2.jsonl"
    domain_class = Zenotravel(is_random_sub=True,is_ramifications=False)
    instance_id = 1 
    domain_folder_name = 'zenotravel/'
    # few_shot = Generate_prompting_template(root_directory,domain_class,instance_id,selected_file,'blocksworld/')
    # few_shot.few_shot_prompt(3,False)
    zero_shot = Generate_prompting_template(root_directory,domain_class,instance_id,selected_file,domain_folder_name)
    jsonl_instance_list = [os.path.join(root_directory, domain_folder_name, file) for file in os.listdir(os.path.join(root_directory, domain_folder_name)) if file.endswith('.jsonl')]
    output_dir = f'../../../data/data_for_evaluation/with_random_sub/without_ramifications/zero_shot/{domain_folder_name}'
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
    count = 1
    for jsonl_instance in jsonl_instance_list:
        results = zero_shot.zero_shot_prompt(jsonl_instance)
        with open(os.path.join(output_dir, f'Instance_{count}.jsonl'), 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        count += 1


            
            
            
            
            
        
    
        

     






