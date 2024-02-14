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



root_directory = '/data_4/data/shri/reasoning_about_actions/data/questions/'
domain_class = Visitall()
domain_name = 'visitall'
instance_id = 1
with open(f'/data_4/data/shri/reasoning_about_actions/data/questions/visitall/Instance_1.jsonl', 'r') as f:
    data = f.readlines()
unique_instance_dict = [json.loads(x) for x in data]

def zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict):
    set_of_unique_instances = set()
    data = []
    for i in range(len(unique_instance_dict)):
        if (unique_instance_dict[i]['plan_length'],unique_instance_dict[i]['question_name'],unique_instance_dict[i]['question_category'],unique_instance_dict[i]['answer_type']) not in set_of_unique_instances:
            set_of_unique_instances.add((unique_instance_dict[i]['plan_length'], unique_instance_dict[i]['question_name'], unique_instance_dict[i]['question_category'], unique_instance_dict[i]['answer_type']))
            zero_shot_prompt = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[i]).zero_shot_prompt()
            unique_instance_dict[i]['prompt'] = zero_shot_prompt[0]['zero_shot_model_input']
            data.append(unique_instance_dict[i])
        else:
            continue    
        
    #save data to jsonl
    with open(f'/data_4/data/shri/reasoning_about_actions/data/data_files/zero_shot_data/{domain_name}.jsonl', 'w') as f:
        for item in data:
            f.write(json.dumps(item))
            f.write('\n')
    
    
    


zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name,unique_instance_dict)
# with open('/data_4/data/shri/reasoning_about_actions/data/final_data/zero_shot_data/blocksworld.jsonl', 'r') as f:
#     data = f.readlines()
# unique_instance_dict = [json.loads(x) for x in data]
# results = defaultdict(int)
# for item in unique_instance_dict:
#     if item['plan_length'] == 1:
#         results[(item['question_category'],item['question_name'],item['answer'].split(' ')[0])] += 1
# for k,v in results.items():
#     print(k,v)