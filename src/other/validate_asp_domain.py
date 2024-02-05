
import os
import jsonlines
from clyngor.inline import ASP_one_model

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


def execute_asp_code(asp_code):
    return ASP_one_model(asp_code)


def open_jsonl(path):
    with jsonlines.open(path, 'r') as r:
        data = [obj for obj in r]
    return data

########################## TODO from common import * # COMMON DOESNT WORK


CODE_PATH = '/Users/paveldolin/dev/research/current/reasoning_about_actions/pipeline/src'
DATA_PATH ='/Users/paveldolin/dev/research/current/reasoning_about_actions/pipeline/data'
ASP_CODE_PATH = CODE_PATH+ '/ASP'

def domain_instance_exec_asp_code(domain_name, instance):
    paths = [ASP_CODE_PATH + '/check_sequence.lp',
             f'{DATA_PATH}/initial/asp/{domain_name}/domain.lp']
    instance_init_path = f'{DATA_PATH}/initial/asp/{domain_name}/instances/{instance}'
    for fname in os.listdir(instance_init_path):
        paths.append(instance_init_path + '/' + fname)
    return assemble_asp_code(paths)


if __name__ == '__main__':
    domain_name = 'blocksworld'
    instance = 'Instance_1'
    asp_code = domain_instance_exec_asp_code(domain_name, instance)
    asp_model = execute_asp_code(asp_code)

    for prefix, contents in asp_model:
        if prefix == 'not_exec':
            print(prefix, contents)
            raise('Bad ASP code')
