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
from src.questions_construction.main import *
jsonl_instance = '/data_5/data/shri/reasoning_about_actions/src/tests/data20.jsonl'
with open(jsonl_instance, 'r') as f:
    data = f.readlines()
jsonl_instance = [json.loads(x) for x in data]
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

def zero_shot_prompt(domain_class, jsonl_instance, instance_number):
    qh = QuestionGenerationHelpers(jsonl_instance, domain_class, instance_number)
    initial_states = QuestionGenerator(jsonl_instance, domain_class, instance_number).init_state
    initial_state_nl = qh.nl_fluents(initial_states['fluents'])
    domain_description = domain_class.domain_description_without_ram
    return f'{domain_description}\n[INITIAL CONDITIONS]\n{initial_state_nl}\n[QUESTION] What is the next action?\n[ANSWER]:'

print(zero_shot_prompt(Blocksworld(), jsonl_instance, 1))





