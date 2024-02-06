import os
import jsonlines
from clyngor.inline import *
from clyngor import solve

CODE_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CODE_PATH)
DATA_PATH = f'{PROJECT_PATH}/data'

ASP_EXECUTION_TIME_LIMIT = 10
ASP_CODE_PATH = f'{CODE_PATH}/ASP'
TMP_ASP_EXEC_PATH = f'{ASP_CODE_PATH}/tmp'

INIT_ACTION_KEY = 'action_init'
PART_OF_PLAN_KEY = "part_of_plan?"
FLUENTS_KEY = "fluents"
NEG_FLUENTS_KEY = "neg_fluents"
EXECUTABLE_ACTION_BOOL_KEY = 'executable?'  # TODO rename


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
    # answers = list(solve(inline=asp_code, stats=True, nb_model=None, options='--opt-mode=OptN', time_limit=10))
    answers = list(ASP(asp_code, time_limit=10))
    first = answers[0]
    for a in answers:
        if a != first:
            raise 'Returned ASP sets are not the same!'
    return first


def open_jsonl(path):
    with jsonlines.open(path, 'r') as r:
        data = [obj for obj in r]
    return data


def save_jsonl(data, save_path):
    with jsonlines.open(save_path, 'w') as w:
        w.write_all(data)
