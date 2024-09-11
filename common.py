import os
import jsonlines

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
OUT_OBJ_ID = 'id' # question id, has multiplicity of 2 (due to random vs non-random)
OUT_OBJ_DOMAIN_NAME = 'domain_name'
OUT_OBJ_INSTANCE_ID = 'instance_id'
OUT_OBJ_INITIAL_STATE_ASP = 'initial_state_asp'
OUT_OBJ_INITIAL_STATE_NL = 'initial_state_nl'
OUT_OBJ_ACTION_SEQUENCE = 'action_sequence'
OUT_OBJ_PLAN_LENGTH = 'plan_length'
OUT_OBJ_QUESTION_CATEGORY = 'question_category'
OUT_OBJ_QUESTION_NAME = 'question_name'
OUT_OBJ_QUESTION = 'question'
OUT_OBJ_ANSWER_TYPE = 'answer_type'
OUT_OBJ_ANSWER = 'answer' # ground truth answer #TODO rename
OUT_OBJ_FLUENT_TYPE = 'fluent_type'  # base, derived or persistent
OUT_OBJ_IS_POS_FLUENT_QUESTION = 'is_pos_fluent_question'
OUT_OBJ_TEST_KEY = 'for_testing'

# OUTPUT ANSWER TYPES
FREE_ANSWER_TYPE = 'free_answer'
TRUE_FALSE_ANSWER_TYPE = 'true_false_answer'

# ramifications
WITH_RAMIFICATIONS = 'with_ramifications'
WITHOUT_RAMIFICATIONS = 'without_ramifications'
RAMIFICATION_TYPES = [WITHOUT_RAMIFICATIONS, WITH_RAMIFICATIONS]

# random sub
WITH_RANDOM_SUB = 'with_random_sub'
WITHOUT_RANDOM_SUB = 'without_random_sub'


# model and prompts
MODEL_RESPONSE_KEY = 'response'  # TODO add to all scripts

BASE_FLUENTS = 'base_fluents'
DERIVED_FLUENTS = 'derived_fluents'
PERSISTENT_FLUENTS = 'persistent_fluents'
STATIC_FLUENTS = 'static_fluents'
FLUENT_TYPES_ALL = None
FLUENT_TYPES_LIST = (BASE_FLUENTS, DERIVED_FLUENTS, PERSISTENT_FLUENTS, STATIC_FLUENTS)

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
FLUENTS_NL_BY_KEY = {BASE_FLUENTS: BASE_FLUENTS_NL,
                     DERIVED_FLUENTS: DERIVED_FLUENTS_NL,
                     PERSISTENT_FLUENTS: PERSISTENT_FLUENTS_NL,
                     STATIC_FLUENTS: STATIC_FLUENTS_NL,
                     FLUENT_TYPES_ALL: FLUENTS_NL}

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


def open_jsonl(path):
    with jsonlines.open(path, 'r') as r:
        data = [obj for obj in r]
    return data


def save_jsonl(data, save_path, mode='w'):
    with jsonlines.open(save_path, 'w') as w:
        w.write_all(data)

def ramifications_keyword(is_ramifications):
    if is_ramifications:
        return WITH_RAMIFICATIONS
    else:
        return WITHOUT_RAMIFICATIONS


def capitalize_first_letter(string):
    return string[0].upper() + string[1:]
