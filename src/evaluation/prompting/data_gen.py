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
domain_class = Blocksworld()
domain_name = 'blocksworld'
instance_id = 1
with open(f'/data_4/data/shri/reasoning_about_actions/data/questions/blocksworld/Instance_1.jsonl', 'r') as f:
    data = f.readlines()
unique_instance_dict = [json.loads(x) for x in data]

def zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name, unique_instance_dict):
    for i in range(len(unique_instance_dict)):
        prompt = Generate_prompting_template(root_directory, domain_class, instance_id, domain_name+'/',unique_instance_dict[i]).zero_shot_prompt()
        unique_instance_dict[i]['prompt']= prompt[0]['zero_shot_model_input']
    df = pd.DataFrame(unique_instance_dict).T
    return df.to_csv('/data_4/data/shri/reasoning_about_actions/data/data_files/'+domain_name+'_zero_shot_prompt.csv')


zero_shot_data_gen(root_directory, domain_class, instance_id, domain_name, unique_instance_dict)