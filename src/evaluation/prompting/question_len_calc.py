import json
import jsonlines 
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict
from promping_stencils import Generate_prompting_template
from src.questions_construction.domains import *
root_directory = '/data_4/data/shri/reasoning_about_actions/data/questions/'
domain_class = Zenotravel()
domain_name = 'zenotravel'
instance_id = 1
with open(f'/data_4/data/shri/reasoning_about_actions/data/questions/zenotravel/Instance_1.jsonl', 'r') as f:
    data = f.readlines()
unique_instance_dict = [json.loads(x) for x in data]
zero_shot = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[0]).zero_shot_prompt()
# print(len(zero_shot))
def get_question_lengths(zero_shot,domain_name):
    zero_shot_question_lengths = defaultdict(dict)
    for item in zero_shot: 
        if zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]:
            zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]['question_len'].append(len(item['zero_shot_model_input']))
            zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]['answer_len'].append(len(item['answer']))
        else:
            zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"] = {'question_len':[len(item['zero_shot_model_input'])], 'answer_len':[len(item['answer'])]}
    lengths = 0
    for item in zero_shot_question_lengths:
        lengths += len(zero_shot_question_lengths[item]['question_len'])
    for item in zero_shot_question_lengths:
        zero_shot_question_lengths[item]['question_len'] = max(zero_shot_question_lengths[item]['question_len'])
        zero_shot_question_lengths[item]['answer_len'] = max(zero_shot_question_lengths[item]['answer_len'])
    df = pd.DataFrame(zero_shot_question_lengths).T
    print(lengths)
    return df.to_csv(domain_name+'_zero_shot_question_lengths.csv')

get_question_lengths(zero_shot,domain_name)    
# print(zero_shot_question_lengths)        
# print(len(zero_shot_question_lengths))
# print('==================================================================================================================')
# lengths = 0
# for item in zero_shot_question_lengths:
#     lengths += len(zero_shot_question_lengths[item]['question_len'])
# print(lengths)
# print('==================================================================================================================')
# print(zero_shot_question_lengths)

# df = pd.DataFrame(zero_shot_question_lengths).T
# df.to_csv('blocksworld_zero_shot_question_lengths.csv')
