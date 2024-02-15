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
from collections import defaultdict
from promping_stencils import Generate_prompting_template
from src.questions_construction.domains import *
from src.questions_construction.domains import *

# root_directory = '/data_4/data/shri/reasoning_about_actions/data/questions/'
# # root_directory = '/data_4/data/shri/reasoning_about_actions/'
# domain_class = Visitall()
# domain_name = 'visitall'
# instance_id = 1
# with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files/zero_shot_data/visitall.jsonl', 'r') as f:
#     data = f.readlines()
# unique_instance_dict = [json.loads(x) for x in data]

# def zero_shot_prompt(unique_instance_dict):
#     results = []
#     # with open(self.jsonl_instance_path, 'r') as f:
#     #     data = f.readlines()
#     # question_jsonl = [json.loads(x) for x in data]
#     for dictionary_item in unique_instance_dict:
#         # if dictionary_item['id'] == self.unique_instance_dict['id']:
#         if dictionary_item['id']:
#             initial_state_nl = asp_to_nl(dictionary_item['initial_state']['fluents'], domain_class.fluent_to_natural_language,None)
#             if len(dictionary_item.keys()) == 0:
#                 continue
#             dictionary_item['prompt'] = f'{domain_class.domain_description_ram}\n\n[INITIAL CONDITIONS]\nInitially, {initial_state_nl}\n\n[QUESTION]\n{dictionary_item["question"]}\n\n[ANSWER]:\n'
#             results.append(dictionary_item)
#     return results

# result = zero_shot_prompt(unique_instance_dict)
# with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files_ramifications/zero_shot_data/{domain_name}.jsonl', 'w') as f:
#     for item in result:
#         f.write(json.dumps(item))
#         f.write('\n')
    

# def zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict):
#     set_of_unique_instances = set()
#     data = []
#     for i in range(len(unique_instance_dict)):
#         if (unique_instance_dict[i]['plan_length'],unique_instance_dict[i]['question_name'],unique_instance_dict[i]['question_category'],unique_instance_dict[i]['answer_type']) not in set_of_unique_instances:
#             set_of_unique_instances.add((unique_instance_dict[i]['plan_length'], unique_instance_dict[i]['question_name'], unique_instance_dict[i]['question_category'], unique_instance_dict[i]['answer_type']))
#             zero_shot_prompt = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[i]).zero_shot_prompt()
#             unique_instance_dict[i]['prompt'] = zero_shot_prompt[0]['zero_shot_model_input']
#             data.append(unique_instance_dict[i])
#         else:
#             continue    
        
#     #save data to jsonl
#     with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files/zero_shot_data/{domain_name}.jsonl', 'w') as f:
#         for item in data:
#             f.write(json.dumps(item))
#             f.write('\n')

# def few_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict):
#     data = []
#     for i in range(len(unique_instance_dict)):
#             zero_shot_prompt,l = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[i],is_ramifications=False).few_shot_prompt(4,False)
#             unique_instance_dict[i]['prompt'] = zero_shot_prompt
#             data.append(unique_instance_dict[i])
#     with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files/few_shot_4/{domain_name}.jsonl', 'w') as f:
#         for item in data:
#             f.write(json.dumps(item))
#             f.write('\n')        

# def few_shot_cot_data_gen(few_shot_file):
#     with open(few_shot_file, 'r') as f:
#         data = f.readlines()
#     unique_instance_dict = [json.loads(x) for x in data]
#     data = []
#     for item in unique_instance_dict:
#         item['prompt'] = item['prompt'].rstrip()+" let's think step by step."
#         data.append(item)
        
#     #save data to jsonl
#     with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files/few_shot_4_cot/{domain_name}.jsonl', 'w') as f:
#         for item in data:
#             f.write(json.dumps(item))
#             f.write('\n')

# domain_name = 'visitall'            
# few_shot_cot_data_gen('/data_4/data/shri/reasoning_about_actions/data/data_files/few_shot_4/visitall.jsonl')            
    
# prompt ="Picking up a block is only possible if that block is clear, on the table, and the hand is empty. By picking up that block, it makes that block not present on the table and not clear. It also leads to the block being held and makes the hand not empty. Putting down the block can only be executed if the block is being held. Putting down the block causes that block to be clear and on the table. It also causes the hand to be not holding the block and makes the hand empty. A block can be stacked on the second block if it is being held and the second block is clear. By stacking the first block on the second, it causes the first block to clear and on top of the second block. Meanwhile, the second block is not clear, and the hand becomes empty as it is not holding the block. The block can also be unstacked from the top of the second block only if the hand is empty and the first block is clear and on top of the second block. Unstacking the first block from the second causes the second block to be clear. The first block is now being held, not clear, and not on top of the second block. Furthermore, the hand is not empty.\n\n[EXAMPLE_1]:\n\n[INITIAL CONDITIONS]\nInitially, block b7 is on the table, block b5 is on the table, block b2 is clear, block b3 is on block b4, block b1 is on block b7, hand is empty, block b9 is clear, block b4 is on the table, block b6 is on block b3, block b5 is clear, block b8 is on block b1, block b9 is on block b8 and block b2 is on block b6\n\n[QUESTION]\nGiven the initial condition, the following actions are performed: block b9 is unstacked from block b8, block b9 is put down, block b2 is unstacked from block b6, block b2 is stacked on top block b5 and block b6 is unstacked from block b3 to reach the current state. In this state, list all objects associated with type block. Write None if there are none.\n\n[ANSWER]:b1, b2, b3, b4, b5, b6, b7, b8 and b9\n\n[EXAMPLE_2]:\n\n[INITIAL CONDITIONS]\nInitially, block b9 is on block b2, block b9 is clear, block b1 is on the table, block b8 is on block b5, block b6 is on block b4, block b5 is on block b6, block b4 is on the table, block b3 is on the table, block b1 is clear, block b2 is on block b8, block b7 is on block b3, hand is empty and block b7 is clear\n\n[QUESTION]\nGiven the initial condition, the following actions are performed: block b9 is unstacked from block b2, block b9 is put down, block b2 is unstacked from block b8, block b2 is stacked on top block b9 and block b7 is unstacked from block b3 to reach the current state. In this state, list all objects associated with type block. Write None if there are none.\n\n[ANSWER]:b1, b2, b3, b4, b5, b6, b7, b8 and b9\n\n[EXAMPLE_3]:\n\n[INITIAL CONDITIONS]\nInitially, block b7 is on block b1, block b6 is on the table, block b5 is on block b7, hand is empty, block b4 is on the table, block b3 is on block b5, block b2 is on block b6, block b2 is clear, block b1 is on block b4 and block b3 is clear\n\n[QUESTION]\nGiven the initial condition, the following actions are performed: block b3 is unstacked from block b5, block b3 is put down, block b2 is unstacked from block b6, block b2 is put down and block b6 is picked up to reach the current state. In this state, list all objects associated with type block. Write None if there are none.\n\n[ANSWER]:b1, b2, b3, b4, b5, b6 and b7\n\n[EXAMPLE_4]:\n\n[INITIAL CONDITIONS]\nInitially, block b5 is on block b9, block b6 is on the table, block b7 is on block b4, block b1 is clear, block b1 is on the table, block b7 is clear, block b4 is on block b2, hand is empty, block b9 is on block b6, block b8 is on the table, block b8 is clear, block b3 is on block b5 and block b2 is on block b3\n\n[QUESTION]\nGiven the initial condition, the following actions are performed: block b7 is unstacked from block b4, block b7 is put down, block b4 is unstacked from block b2, block b4 is stacked on top block b7 and block b2 is unstacked from block b3 to reach the current state. In this state, list all objects associated with type block. Write None if there are none.\n\n[ANSWER]:b1, b2, b3, b4, b5, b6, b7, b8 and b9\n\nBased on the above examples, answer the below question:\n\n[INITIAL CONDITIONS]\nInitially, block b7 is on block b6, block b3 is clear, hand is empty, block b2 is clear, block b1 is on the table, block b6 is on the table, block b5 is clear, block b5 is on block b4, block b2 is on the table, block b4 is on block b1 and block b3 is on block b7\n\n[QUESTION]\nGiven the initial condition, the following actions are performed: block b3 is unstacked from block b7, block b3 is put down, block b5 is unstacked from block b4, block b5 is stacked on top block b2 and block b4 is unstacked from block b1 to reach the current state. In this state, list all objects associated with type block. Write None if there are none.\n\n[ANSWER]: let's think step by step."
# print(prompt)
    

# few_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict)
# zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict)
# with open('/data_4/data/shri/reasoning_about_actions/data/final_data/zero_shot_data/blocksworld.jsonl', 'r') as f:
#     data = f.readlines()
# unique_instance_dict = [json.loads(x) for x in data]
# results = defaultdict(int)
# for item in unique_instance_dict:
#     if item['plan_length'] == 1:
#         results[(item['question_category'],item['question_name'],item['answer'].split(' ')[0])] += 1
# for k,v in results.items():
#     print(k,v)


jsonl_instance_path = '/data_4/data/shri/reasoning_about_actions/data/data_files_ramifications/few_shot_4_cot/mystery.jsonl'
domian_name = 'mystery'
domain_class = Mystery()
#get full path
with open(jsonl_instance_path, 'r') as f:
    data = f.readlines()
question_jsonl = [json.loads(x) for x in data]
data = []
for dictionary_item in question_jsonl:
    dictionary_item['prompt'] = domain_class.domain_description_ram+'\n\n'+dictionary_item['prompt'][dictionary_item['prompt'].index('[EXAMPLE_1]:'):]
    # dictionary_item['prompt'] = domain_class.domain_description_ram+dictionary_item['prompt'][dictionary_item['prompt'].index('\n\n[INITIAL CONDITIONS]'):]    
    data.append(dictionary_item)
with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files_ramifications/few_shot_4_cot/{domian_name}.jsonl', 'w') as f:
    for item in data:
        f.write(json.dumps(item))
        f.write('\n')
    
