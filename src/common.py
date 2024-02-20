import os
import jsonlines
from clyngor import ASP

CODE_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CODE_PATH)
DATA_PATH = f'{PROJECT_PATH}/data'
QUESTIONS_PATH = f'{DATA_PATH}/questions'
STATES_ACTIONS_PATH = f'{DATA_PATH}/states_actions'
STATISTICS_PATH = f'{PROJECT_PATH}/stats'

RESULTS_PATH = f'{PROJECT_PATH}/results' # todo rn to results dir

ASP_EXECUTION_TIME_LIMIT = 10
ASP_CODE_PATH = f'{CODE_PATH}/ASP'
TMP_ASP_EXEC_PATH = f'{ASP_CODE_PATH}/tmp'

# JSONL KEYS
INIT_ACTION_KEY = 'action_init'
PART_OF_PLAN_KEY = "part_of_plan?"
FLUENTS_KEY = "fluents"
NEG_FLUENTS_KEY = "neg_fluents"
EXECUTABLE_ACTION_BOOL_KEY = 'executable?'
OBJECTS_KEY = 'objects'

# QUESION GENERATION OUTPUT OBJECT KEYS
OUT_OBJ_ID = 'id'
OUT_OBJ_DOMAIN_NAME = 'domain_name'
OUT_OBJ_INSTANCE_ID = 'instance_id'
OUT_OBJ_INITIAL_STATE = 'initial_state'
OUT_OBJ_ACTION_SEQUENCE = 'action_sequence'
OUT_OBJ_PLAN_LENGTH = 'plan_length'
OUT_OBJ_QUESTION_CATEGORY = 'question_category'
OUT_OBJ_QUESTION_NAME = 'question_name'
OUT_OBJ_QUESTION = 'question'
OUT_OBJ_ANSWER_TYPE = 'answer_type'
OUT_OBJ_ANSWER = 'answer'

# OUTPUT ANSWER TYPES
FREE_ANSWER = 'free_answer'
TRUE_FALSE_ANSWER = 'true_false_answer'

# ramifications
WITH_RAMIFICATIONS = 'with_ramifications'
WITHOUT_RAMIFICATIONS = 'without_ramifications'

DOMAIN_NAMES = ['blocksworld','depots','driverlog','goldminer','grippers','logistics','miconic','mystery','npuzzle', 'satellite', 'spanner','visitall','zenotravel']
ANSWER_RESPONSES = [FREE_ANSWER, TRUE_FALSE_ANSWER]
RAMIFICATION_TYPES = [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]
PROMPT_MODEL_NAMES = ['gemini', 'llama-2-7b', 'mistral_7b_instruct'] # TODO add , 'gpt4'
PROMPT_TYPES = ['zero_shot_data', 'few_shot_4', 'few_shot_4_cot'] #TODO clean up dirs

MODEL_RESPONSE_KEY = 'response'


# STATS dict keys
SK_PLAN_LENGTH = OUT_OBJ_PLAN_LENGTH
SK_CATEGORY = OUT_OBJ_QUESTION_CATEGORY
SK_RAMIFICATION = 'ramification_type'
SK_ANSWER_TYPE = OUT_OBJ_ANSWER_TYPE
SK_MODEL = 'model'
SK_PROMPT_TYPE = 'prompt_type'
SK_RESULT = 'result'
SK_DOMAIN = 'domain'



def assemble_asp_code(paths, additional_asp_code='', separator='\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n'):
    asp_code = []
    # if type(paths) is str:
    #     paths = [paths]
    for path in paths:
        with open(path, 'r') as f:
            asp_code.append(f.read())
    asp_code = separator.join(asp_code)
    if additional_asp_code:
        asp_code += f"{separator}{additional_asp_code}"
    return asp_code


def execute_asp_code(asp_code, time_limit=0):
    answers = list(ASP(asp_code, time_limit=time_limit))
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
