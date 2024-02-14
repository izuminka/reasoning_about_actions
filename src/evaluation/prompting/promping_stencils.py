import json
import os
import random
import re
import numpy as np
import pandas as pd
import sys
import sys
sys.path.append('/data_4/data/shri/reasoning_about_actions/')
from src.common import *
from src.questions_construction.domains import *
from src.questions_construction.questions import *



class Generate_prompting_template:
    def __init__(self,root_directory,domain_class,instance_id,domain_folder_name,unique_instance_dict):
        self.root_directory = root_directory
        self.domain_class = domain_class
        self.domain_folder_name = domain_folder_name
        self.instance_id = instance_id
        self.jsonl_instance_path = self.root_directory + self.domain_folder_name + 'Instance_' + str(self.instance_id) + '.jsonl'
        self.domain_description = self.domain_class.domain_description_without_ram
        self.unique_instance_dict = unique_instance_dict

    def zero_shot_prompt(self):
        results = []
        with open(self.jsonl_instance_path, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for dictionary_item in question_jsonl:
            initial_state_nl = asp_to_nl(dictionary_item['initial_state']['fluents'], self.domain_class.fluent_to_natural_language,None)
            if len(dictionary_item.keys()) == 0:
                continue
            if dictionary_item['answer_type'] == 'true_false_answer':
                dictionary_item['zero_shot_model_input'] = f'{self.domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]}\n\n[ANSWER]:\n'
                results.append(dictionary_item)
            else:
                dictionary_item['zero_shot_model_input'] = f'{self.domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]}\n\n[ANSWER]:\n'
                results.append(dictionary_item)             
        return results
    
    def few_shot_prompt(self,n_shot,cot_key):
        jsonl_instance_list = [os.path.join(self.root_directory, self.domain_folder_name, file) for file in os.listdir(os.path.join(self.root_directory, self.domain_folder_name)) if file.endswith('.jsonl')]
        jsonl_instance_list.pop(jsonl_instance_list.index(self.jsonl_instance_path))
        results = []
        # print(results)
        # print(self.unique_instance_dict)
        # exit()
        for i in range(len(jsonl_instance_list)):
            with open(jsonl_instance_list[i], 'r') as f:
                data = f.readlines()
            question_jsonl = [json.loads(x) for x in data]
            for dictionary_item in question_jsonl:
                if dictionary_item['plan_length'] == self.unique_instance_dict['plan_length'] and dictionary_item['question_name'] == self.unique_instance_dict['question_name'] and dictionary_item['question_category'] == self.unique_instance_dict['question_category']:
                    if len(dictionary_item.keys()) == 0:
                        continue
                    else:
                        results.append(dictionary_item)
                        break
                else:
                    continue            
        examples_list = results
        prompts = []
        if examples_list:
            for i in range(n_shot):
                if i==0:
                    initial_state_nl = asp_to_nl(examples_list[i]['initial_state']['fluents'], self.domain_class.fluent_to_natural_language,None)
                    prompt = f'{self.domain_description}\n\n[EXAMPLE_{i+1}]:\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{examples_list[i]["question"]}\n\n[ANSWER]:{examples_list[i]["answer"]}'
                    prompts.append(prompt)
                else:
                    initial_state_nl = asp_to_nl(examples_list[i]['initial_state']['fluents'], self.domain_class.fluent_to_natural_language,None)
                    prompt = f'\n\n[EXAMPLE_{i+1}]:\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{examples_list[i]["question"]}\n\n[ANSWER]:{examples_list[i]["answer"]}'
                    prompts.append(prompt)
            initial_state_nl_actual_question = asp_to_nl(self.unique_instance_dict['initial_state']['fluents'], self.domain_class.fluent_to_natural_language,None)     
            if cot_key==True:   
                prompts.append(f'\n\nBased on the above examples, answer the below question:\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl_actual_question}\n\n[QUESTION]\n{self.unique_instance_dict["question"]}\n\n[ANSWER]: let\'s think step by step. \n')
            else:
                prompts.append(f'\n\nBased on the above examples, answer the below question:\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl_actual_question}\n\n[QUESTION]\n{self.unique_instance_dict["question"]}\n\n[ANSWER]:\n')
        else:
            print('No examples found for the given instance')    
        return ''.join(prompts),jsonl_instance_list
    
        
                
                
# if __name__ == '__main__':
#     root_directory = '/data_5/data/shri/reasoning_about_actions/data/questions/'
#     domain_class = Blocksworld()
#     instance_id = 2
#     with open('/data_5/data/shri/reasoning_about_actions/data/questions/blocksworld/Instance_1.jsonl', 'r') as f:
#         data = f.readlines()
#     unique_instance_dict = [json.loads(x) for x in data][0] 
#     prompting_instance = generate_prompting_template(root_directory,domain_class,instance_id,'blocksworld/',unique_instance_dict)   
#     result = prompting_instance.few_shot_prompt(1)
#     zero_shot = prompting_instance.zero_shot_prompt()
#     # print(unique_instance_dict)
#     print('==================================================================================================================')
#     print(result)
#     print('==================================================================================================================')
#     print(zero_shot[0]['zero_shot_model_input'])     
                            
                        


            
            
            
            
            
        
    
        
# #instantiate class
# root_directory = '/data_4/data/shri/reasoning_about_actions/data/questions/'
# domain_class = Blocksworld()
# domain_name = 'blocksworld'
# instance_id = 1
# with open(f'/data_4/data/shri/reasoning_about_actions/data/questions/blocksworld/Instance_1.jsonl', 'r') as f:
    # data = f.readlines()
# unique_instance_dict = [json.loads(x) for x in data][488]
# for item in unique_instance_dict:
#     # question_category - object_tracking, fluent_tracking, state_tracking, action_executability, effects, numerical_reasoning
#     if item['plan_length'] == 1 and item['question_category'] == 'effects':
#         print('==================================================================================================================')
#         print(asp_to_nl(item['initial_state']['fluents'], domain_class.fluent_to_natural_language,None))
#         print('\n\n')
#         print(item['question'])
#         print('==================================================================================================================')
#         print(item['answer'])
# s = set()
# q_length = 0
# a_length = 0
# prompt_instance = Generate_prompting_template(root_directory, domain_class, 1, domain_name+'/',unique_instance_dict)
# print(prompt_instance.few_shot_prompt(2))
# exit()
# for item in unique_instance_dict:
#     if (item['plan_length'], item['question_category'], item['answer_type']) not in s:
#         q_length += len(item['question'])
#         a_length += len(item['answer'])
#         s.add((item['plan_length'], item['question_category'], item['answer_type']))
# print(len(s), q_length/3.5, a_length/3.5)

# # print(len(unique_instance_dict))
# # print(unique_instance_dict[0])
# prompting_instance = Generate_prompting_template(root_directory,domain_class,instance_id,'blocksworld/',unique_instance_dict)   
# result,json_list = prompting_instance.few_shot_prompt(5,cot_key=True)
# zero_shot = prompting_instance.zero_shot_prompt()
# # print(unique_instance_dict)
# print('==================================================================================================================')
# print(result)
# for item in zero_shot:
    # print(item['zero_shot_model_input'])
# print('==================================================================================================================')
# # print(json_list)
# # print(zero_shot[0]['zero_shot_model_input'])

     






