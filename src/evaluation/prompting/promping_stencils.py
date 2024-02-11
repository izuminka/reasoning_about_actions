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

def zero_shot_prompt(domain_class, jsonl_instance):
    # return f'{domain_description}\n[INITIAL CONDITIONS]\n{initial_state_nl}\n[QUESTION] What is the next action?\n[ANSWER]:'
    results = []
    for i in range(len(jsonl_instance)):
        with open(jsonl_instance[i], 'r') as f:
            data = f.readlines()
        question_jsonl = [json.loads(x) for x in data]
        for dictionary_item in question_jsonl:
            initial_state_nl = asp_to_nl(dictionary_item['initial_state']['fluents'], domain_class.fluent_to_natural_language,None)
            domain_description = domain_class.domain_description_without_ram
            if len(dictionary_item.keys()) == 0:
                continue
            if dictionary_item['answer_type'] == 'true_false_answer':
                dictionary_item['zero_shot_model_input'] = f'{domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]} Answer either True or False.\n\n[ANSWER]:\n'
                results.append(dictionary_item)
            else:
                dictionary_item['zero_shot_model_input'] = f'{domain_description}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]}\n\n[ANSWER]:\n'
                results.append(dictionary_item)    
    return results

import os

directory = '/data_5/data/shri/reasoning_about_actions/data/questions/blocksworld/'

data_instances = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.jsonl')]
data_instances
# print(data_instances)
model_input = zero_shot_prompt(Blocksworld(), data_instances)
# print(len(model_input))
# import json

# # Assuming model_input is the output of zero_shot_prompt function
# for item in model_input:
#     print(item['zero_shot_model_input'])

#write the model_input to a file
with open('model_input.jsonl', 'w') as f:
    for item in model_input:
        f.write(json.dumps(item))
        f.write('\n')




# with open('/data_5/data/shri/reasoning_about_actions/data/questions/blocksworld/Instance_1.jsonl', 'r') as f:
#     data = f.readlines()
# question_jsonl = [json.loads(x) for x in data]
# print(zero_shot_prompt(Blocksworld(), jsonl_instance, 1,question_jsonl))
# print(question_jsonl[0].keys())





