import json
import jsonlines 
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict
from promping_stencils import Generate_prompting_template
from src.questions_construction.domains import *
root_directory = '/data_4/data/shri/reasoning_about_actions/data/questions/'
domain_class = Miconic()
domain_name = 'miconic'
instance_id = 1
with open(f'/data_4/data/shri/reasoning_about_actions/data/questions/miconic/Instance_1.jsonl', 'r') as f:
    data = f.readlines()
unique_instance_dict = [json.loads(x) for x in data]
# zero_shot = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[0]).zero_shot_prompt()
# print(len(zero_shot))
# def get_question_lengths(zero_shot,domain_name):
#     zero_shot_question_lengths = defaultdict(dict)
#     for item in zero_shot: 
#         if zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]:
#             zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]['question_len'].append(len(item['zero_shot_model_input']))
#             zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"]['answer_len'].append(len(item['answer']))
#         else:
#             zero_shot_question_lengths[f"{item['question_category']}_{str(item['plan_length'])}_{item['answer_type']}_{item['question_name']}"] = {'question_len':[len(item['zero_shot_model_input'])], 'answer_len':[len(item['answer'])]}
#     lengths = 0
#     for item in zero_shot_question_lengths:
#         lengths += len(zero_shot_question_lengths[item]['question_len'])
#     for item in zero_shot_question_lengths:
#         zero_shot_question_lengths[item]['question_len'] = max(zero_shot_question_lengths[item]['question_len'])
#         zero_shot_question_lengths[item]['answer_len'] = max(zero_shot_question_lengths[item]['answer_len'])
#     df = pd.DataFrame(zero_shot_question_lengths).T
#     print(lengths)
#     return df.to_csv(domain_name+'_zero_shot_question_lengths.csv')

# get_question_lengths(zero_shot,domain_name)    

def few_shot_prompt_len_calc(root_directory, domain_class, instance_id, domain_name, unique_instance_dict):
    few_shot_length = defaultdict(dict)
    for i in range(len(unique_instance_dict)):
        few_shot_prompt, included_instances_list = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[i]).few_shot_prompt(9,True)
        if few_shot_length[f"{unique_instance_dict[i]['question_category']}_{str(unique_instance_dict[i]['plan_length'])}_{unique_instance_dict[i]['answer_type']}_{unique_instance_dict[i]['question_name']}"]:
            few_shot_length[f"{unique_instance_dict[i]['question_category']}_{str(unique_instance_dict[i]['plan_length'])}_{unique_instance_dict[i]['answer_type']}_{unique_instance_dict[i]['question_name']}"]['question_len'].append(len(few_shot_prompt))
        else:
            few_shot_length[f"{unique_instance_dict[i]['question_category']}_{str(unique_instance_dict[i]['plan_length'])}_{unique_instance_dict[i]['answer_type']}_{unique_instance_dict[i]['question_name']}"] = {'question_len':[len(few_shot_prompt)]}    
    for item in few_shot_length:
        few_shot_length[item]['question_len'] = max(few_shot_length[item]['question_len'])
    df = pd.DataFrame(few_shot_length).T    
    total_question_len = df['question_len'].sum()
    sum_df = pd.DataFrame({'total_question_len': total_question_len}, index=['total'])
    df = pd.concat([df, sum_df], axis=1)
    print(len(df))
    return df.to_csv('/data_4/data/shri/reasoning_about_actions/src/evaluation/csv_file_for_calculation_gpt_4/'+domain_name+'_few_shot_question_lengths.csv')

few_shot_prompt_len_calc(root_directory, domain_class, instance_id, domain_name, unique_instance_dict)
    

