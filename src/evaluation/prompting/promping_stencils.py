import json
import os
import random
import re
import numpy as np
import pandas as pd
import sys
import sys
sys.path.append('/data_5/data/shri/reasoning_about_actions')
from src.common import *
from src.questions_construction.domains import *
from src.questions_construction.questions import *
# jsonl_instance = '/data_5/data/shri/reasoning_about_actions/src/tests/data20.jsonl'
# with open(jsonl_instance, 'r') as f:
#     data = f.readlines()
# jsonl_instance = [json.loads(x) for x in data]
# domain_class = Blocksworld()
# qh = QuestionGenerationHelpers(jsonl_instance, domain_class,1)
# initial_states = QuestionGenerator(jsonl_instance,domain_class,1).init_state
# # initial_state_nl = ', '.join(['Initially'] + [QuestionGenerationHelpers.nl_fluents(fluent) for fluent in initial_states['fluents'][:-1]] + ['and', domain_class.fluent_to_natural_language(initial_states['fluents'][-1])]+['.'])
# initial_state_nl = qh.nl_fluents(initial_states['fluents'])
# domain_description = domain_class.domain_description_without_ram
# print('=========================================================================================================================')
# print(domain_description)
# print('=========================================================================================================================')
# print(initial_state_nl)

class generate_prompting_template:
    def __init__(self,root_directory,domain_class,instance_id,domain_folder_name):
        self.root_directory = root_directory
        self.domain_class = domain_class
        self.domain_folder_name = domain_folder_name
        # self.jsonl_instance_list = [os.path.join(self.root_directory, self.domain_folder_name, file) for file in os.listdir(os.path.join(self.root_directory, self.domain_folder_name)) if file.endswith('.jsonl')]
        self.instance_id = instance_id
        self.jsonl_instance_path = self.root_directory + self.domain_folder_name + 'Instance_' + str(self.instance_id) + '.jsonl'

    def zero_shot_prompt(self):
        results = []
        with open(self.jsonl_instance_path, 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for dictionary_item in question_jsonl:
            initial_state_nl = asp_to_nl(dictionary_item['initial_state']['fluents'], self.domain_class.fluent_to_natural_language,None)
            domain_description = self.domain_class.domain_description_without_ram
            if len(dictionary_item.keys()) == 0:
                continue
            if dictionary_item['answer_type'] == 'true_false_answer':
                dictionary_item['zero_shot_model_input'] = f'{domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]} Answer either True or False.\n\n[ANSWER]:\n'
                results.append(dictionary_item)
            else:
                dictionary_item['zero_shot_model_input'] = f'{domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]}\n\n[ANSWER]:\n'
                results.append(dictionary_item)             
        return results
    
        
if __name__ == '__main__':
    #instantiate class
    root_directory = '/data_5/data/shri/reasoning_about_actions/data/questions/'
    domain_class = Blocksworld()
    instance_id = 1
    prompting_instance = generate_prompting_template(root_directory,domain_class,instance_id,'blocksworld/')
    result = prompting_instance.zero_shot_prompt()
    print(result[0].keys())
    print(len(result))

# directory = '/data_5/data/shri/reasoning_about_actions/data/questions/blocksworld/'

# data_instances = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.jsonl')]
# data_instances
# # print(data_instances)
# model_input = zero_shot_prompt(Blocksworld(), data_instances)
# # print(len(model_input))

# def write_json(data, filename):
#     with open(filename, 'w') as f:
#         for item in data:
#             f.write(json.dumps(item))
#             f.write('\n')        







