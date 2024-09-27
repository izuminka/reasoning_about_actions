import os
import jsonlines

CODE_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CODE_PATH)
DATA_PATH = f'{PROJECT_PATH}/data'
QUESTIONS_PATH = f'{DATA_PATH}/questions'
STATES_ACTIONS_PATH = f'{DATA_PATH}/states_actions'
STATISTICS_PATH = f'{PROJECT_PATH}/stats'
RESULTS_PATH = f'{PROJECT_PATH}/results'

# JSONL KEYS for states_actions_generation
INIT_ACTION_KEY = 'action_init'
PART_OF_PLAN_KEY = "part_of_plan?"
FLUENTS_KEY = "fluents"
NEG_FLUENTS_KEY = "neg_fluents"
EXECUTABLE_ACTION_BOOL_KEY = 'executable?'
OBJECTS_KEY = 'objects'

# QUESTION GENERATION OUTPUT OBJECT KEYS
OUT_OBJ_ID = 'question_id' # question id, has multiplicity of 2 (due to random vs non-random)
OUT_OBJ_ID_LEGACY_KEY = 'id'
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
OUT_OBJ_FLUENT_SIGN_QUESTION = 'fluent_sign_question'
OUT_OBJ_IS_POS_FLUENT_QUESTION = 'is_pos_fluent_question' # Legacy key
OUT_OBJ_TEST_KEY = 'for_testing'
OUT_OBJ_QUESTION_SUBCATEGORIES = 'question_subcategories'

OUT_OBJ_QUESTION_PARAPHRASED = 'question_paraphrased'
OUT_OBJ_INITIAL_STATE_NL_PARAPHRASED = 'initial_state_nl_paraphrased'


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

# question involving pos or neg fluents
NEG_FLUENTS_QUESTION = 'neg'
POS_FLUENTS_QUESTION = 'pos'
POS_PLUS_NEG_FLUENTS_QUESTION = 'pos_neg'
POS_NEG_FLUENTS_KEY_LIST = [POS_FLUENTS_QUESTION, NEG_FLUENTS_QUESTION, POS_PLUS_NEG_FLUENTS_QUESTION]

# model and prompts
MODEL_RESPONSE_KEY = 'response'  # TODO add to all scripts

BASE_FLUENTS = 'base_fluents'
DERIVED_FLUENTS = 'derived_fluents'
PERSISTENT_FLUENTS = 'persistent_fluents'
STATIC_FLUENTS = 'static_fluents'
FLUENT_TYPES_ALL = 'all_fluents'
FLUENT_TYPES_ALL_LEGACY_KEY = None # old key comp. with old data
FLUENT_TYPES_LIST = (BASE_FLUENTS, DERIVED_FLUENTS, PERSISTENT_FLUENTS, STATIC_FLUENTS)

# fluent names for QA and domains
POS_AND_NEG_FLUENTS_NL = 'valid properties of the state (both with and without negations)'
POSITIVE_FLUENTS_NL = 'valid properties of the state that do not involve negations'
NEGATIVE_FLUENTS_NL = 'valid properties of the state that involve negations'

BASE_FLUENTS_NL = 'base ' + POS_AND_NEG_FLUENTS_NL
DERIVED_FLUENTS_NL = 'derived ' + POS_AND_NEG_FLUENTS_NL
PERSISTENT_FLUENTS_NL = 'self constraint ' + POS_AND_NEG_FLUENTS_NL
STATIC_FLUENTS_NL = 'static ' + POS_AND_NEG_FLUENTS_NL
FLUENTS_NL_BY_KEY = {BASE_FLUENTS: BASE_FLUENTS_NL,
                     DERIVED_FLUENTS: DERIVED_FLUENTS_NL,
                     PERSISTENT_FLUENTS: PERSISTENT_FLUENTS_NL,
                     STATIC_FLUENTS: STATIC_FLUENTS_NL,
                     FLUENT_TYPES_ALL: POS_AND_NEG_FLUENTS_NL}

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
