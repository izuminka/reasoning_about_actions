import os
import jsonlines
from clyngor import ASP

CODE_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CODE_PATH)
DATA_PATH = f'{PROJECT_PATH}/data'
QUESTIONS_PATH = f'{DATA_PATH}/questions'
STATES_ACTIONS_PATH = f'{DATA_PATH}/states_actions'
STATISTICS_PATH = f'{PROJECT_PATH}/stats'
RESULTS_PATH = f'{PROJECT_PATH}/results'  # todo rn to results dir

# JSONL KEYS for states_actions_generation
INIT_ACTION_KEY = 'action_init'
PART_OF_PLAN_KEY = "part_of_plan?"
FLUENTS_KEY = "fluents"
NEG_FLUENTS_KEY = "neg_fluents"
EXECUTABLE_ACTION_BOOL_KEY = 'executable?'
OBJECTS_KEY = 'objects'

# QUESTION GENERATION OUTPUT OBJECT KEYS
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
OUT_OBJ_ANSWER = 'answer' # ground truth answer #TODO rename
OUT_OBJ_FLUENT_TYPE = 'fluent_type'  # base, derived or persistent

# OUTPUT ANSWER TYPES
FREE_ANSWER = 'free_answer'
TRUE_FALSE_ANSWER = 'true_false_answer'

# ramifications
WITH_RAMIFICATIONS = 'with_ramifications'
WITHOUT_RAMIFICATIONS = 'without_ramifications'
RAMIFICATION_TYPES = [WITH_RAMIFICATIONS, WITHOUT_RAMIFICATIONS]

# random sub
WITH_RANDOM_SUB = 'with_random_sub'
WITHOUT_RANDOM_SUB= 'without_random_sub'


# model and prompts
MODEL_RESPONSE_KEY = 'response'  # TODO add to all scripts

# fluent names for QA and domains
FLUENTS_NL = 'properties of the state'
POSITIVE_FLUENT_NL = 'valid property of the state'
NEGATIVE_FLUENT_NL = 'valid property of the state that involves a negation'
POSITIVE_FLUENTS_NL = 'valid properties of the state'
NEGATIVE_FLUENTS_NL = 'valid properties of the state that involve negations'

BASE_FLUENTS_NL = 'base ' + FLUENTS_NL
DERIVED_FLUENTS_NL = 'derived ' + FLUENTS_NL
PERSISTENT_FLUENTS_NL = 'self constraint ' + FLUENTS_NL
STATIC_FLUENTS_NL = 'static ' + FLUENTS_NL

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

def ramifications_keyword(is_ramifications):
    if is_ramifications:
        return WITH_RAMIFICATIONS
    else:
        return WITHOUT_RAMIFICATIONS
