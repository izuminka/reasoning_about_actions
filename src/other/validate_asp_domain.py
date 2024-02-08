
import os
import jsonlines
from clyngor.inline import ASP_one_model
from src.common import *

ASP_EXECUTION_TIME_LIMIT = 10

def assemble_asp_code(paths, additional_asp_code='', separator='\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n'):
    asp_code = []
    if type(paths) is str:
        paths = [paths]
    for path in paths:
        with open(path, 'r') as f:
            asp_code.append(f.read())
    asp_code = separator.join(asp_code)
    if additional_asp_code:
        asp_code += f"{separator}{additional_asp_code}"
    return asp_code


def open_jsonl(path):
    with jsonlines.open(path, 'r') as r:
        data = [obj for obj in r]
    return data

########################## TODO from common import * # COMMON DOESNT WORK


CODE_PATH = '/Users/paveldolin/dev/research/current/reasoning_about_actions/pipeline/src'
DATA_PATH ='/Users/paveldolin/dev/research/current/reasoning_about_actions/pipeline/data'
ASP_CODE_PATH = CODE_PATH+ '/ASP'


# def check_validity(domain_name, instance_name):
#     paths = [ASP_CODE_PATH + '/check_sequence.lp',
#              f'{DATA_PATH}/initial/asp/{domain_name}/domain.lp',
#              f'{DATA_PATH}/initial/asp/{domain_name}/instances/{instance_name}/init.lp',
#              f'{DATA_PATH}/initial/asp/{domain_name}/instances/{instance_name}/objects.lp',
#              f'{DATA_PATH}/initial/asp/{domain_name}/instances/{instance_name}/plan.lp']
#     asp_code = assemble_asp_code(paths)
#     asp_model = execute_asp_code(asp_code)
#
#     for prefix, contents in asp_model:
#         if prefix == 'not_exec':
#             print(prefix, contents)
#             raise('Bad ASP code')
