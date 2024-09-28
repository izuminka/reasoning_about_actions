import copy
import sys
import uuid
from functools import partial
from itertools import chain

import numpy as np

sys.path.insert(0, '../../')
from questions_construction.domains import *
from common import *

INITIAL_CONDITION_PREFIX = 'Given the initial condition'
ACTIONS_ARE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are performed:'
ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are planned to be performed:'
TRUE_OR_FALSE = 'True or False'
NONE_STATEMENT = 'Write None if there are none'
NONE_ANSWER = 'None'

PART_OF_THE_STATE = 'part of the state'
PART_OF_THE_DOMAIN = 'part of the domain'
MAX_TIMEOUT = 50

OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
SUBSTRING_WITHIN_PARENTHESIS_REGEX = r'\([^)]*{}\w*[^)]*\)'

PLAN_LENGTHS = list(range(1, 20))  # [1, 5, 10, 15, 19]
FRACTION_TO_CORRUPT = 0.5

QUESTION_MULTIPLICITY = 1
CONTROLLED_REJECTED_QUESTION_FOR_BALANCE = 'sdfnksdbvsdbvjdsbvjh'


def unique_id(data):
    # TODO add, if QUESTION_MULTIPLICITY > 1
    import base64
    import hashlib
    hasher = hashlib.sha1(str(data).encode('ascii'))
    return base64.urlsafe_b64encode(hasher.digest())


def add_commas_and(nl_obj_ls):
    and_str = ' and '
    comma_str = ', '
    return comma_str.join(nl_obj_ls[:-1]) + and_str + nl_obj_ls[-1]


def asp_to_nl(obj_ls, converter, fluent_subs=None, is_sorted=True, is_list=False):
    if not obj_ls:
        raise 'Empty list'
    if len(obj_ls) == 1:
        nl_obj = converter(obj_ls[0])
        if fluent_subs:
            nl_obj = nl_obj.replace(fluent_subs[0], fluent_subs[1])
        if is_list:
            return [nl_obj]
        return nl_obj
    nl_obj_ls = [converter(f) for f in obj_ls]
    if fluent_subs:
        nl_obj_ls = [f.replace(fluent_subs[0], fluent_subs[1]) for f in nl_obj_ls]
    if is_sorted:
        nl_obj_ls = sorted(nl_obj_ls)
    if is_list:
        return nl_obj_ls
    return add_commas_and(nl_obj_ls)


def question_name(q_id, prefix=None):
    if prefix:
        return f'{prefix}_question_{q_id}'
    return f'question_{q_id}'


def fluents_negation_to_nl(fluent_sign_question):
    if fluent_sign_question == POS_FLUENTS_QUESTION:
        return POSITIVE_FLUENTS_NL
    elif fluent_sign_question == NEG_FLUENTS_QUESTION:
        return NEGATIVE_FLUENTS_NL
    elif fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION:
        return POS_AND_NEG_FLUENTS_NL
    else:
        raise ValueError(f'Undefined value {fluent_sign_question}')


class QuestionGenerationHelpers:
    """ Generates QAs * multiplicity for a given domain, init cond + plan sequence"""
    ACTION_JOIN_STR = ', '

    def __init__(self, states_actions_all, domain_class, instance_id):
        self.states_actions_all = states_actions_all
        # self.states_actions_all[i] defines all action->states at time i, i==0 is NULL->initial state
        self.init_state = self.states_actions_all[0][INIT_ACTION_KEY]  # initial state
        self.objects_by_type = self.init_state[OBJECTS_KEY]
        self.object_type_by_object_name = self.object_type_by_object_name()
        self.all_objects = [v for ls in self.objects_by_type.values() for v in ls]
        self.all_objects_set = set(self.all_objects)
        self.domain_class = domain_class
        self.states_actions = self.states_actions_all[1:]
        self.instance_id = instance_id
        self.given_plan_sequence = self.extract_given_plan_sequence()
        self.pos_fluents_given_plan = self.extract_fluents_for_given_plan()
        self.neg_fluents_given_plan = self.extract_fluents_for_given_plan(NEG_FLUENTS_KEY)
        self.plan_length_max = len(self.given_plan_sequence)
        self.executable_actions = self.extract_executable_actions()
        self.inexecutable_actions = self.extract_inexecutable_actions()
        self.init_state_nl = capitalize_first_letter(
            asp_to_nl(self.init_state[FLUENTS_KEY], self.domain_class.fluent_to_natural_language)) + '.'
        self.base_pos_fluents = self.extract_fluents_types_for_state(self.pos_fluents_given_plan,
                                                                     self.domain_class.BASE_POS_FLUENTS)
        self.base_neg_fluents = self.extract_fluents_types_for_state(self.neg_fluents_given_plan,
                                                                     self.domain_class.BASE_NEG_FLUENTS)
        self.derived_pos_fluents = self.extract_fluents_types_for_state(self.pos_fluents_given_plan,
                                                                        self.domain_class.DERIVED_POS_FLUENTS)
        self.derived_neg_fluents = self.extract_fluents_types_for_state(self.neg_fluents_given_plan,
                                                                        self.domain_class.DERIVED_NEG_FLUENTS)
        self.persistent_pos_fluents = self.extract_fluents_types_for_state(self.pos_fluents_given_plan,
                                                                           self.domain_class.PERSISTENT_POS_FLUENTS)
        self.persistent_neg_fluents = self.extract_fluents_types_for_state(self.neg_fluents_given_plan,
                                                                           self.domain_class.PERSISTENT_NEG_FLUENTS)
        self.static_pos_fluents = self.extract_fluents_types_for_state(self.pos_fluents_given_plan,
                                                                       self.domain_class.STATIC_POS_FLUENTS)
        self.static_neg_fluents = self.extract_fluents_types_for_state(self.neg_fluents_given_plan,
                                                                       self.domain_class.STATIC_NEG_FLUENTS)
    def extract_given_plan_sequence(self):
        given_plan_sequence = []
        for timestep in self.states_actions:
            for action, value in timestep.items():
                if value[PART_OF_PLAN_KEY]:
                    given_plan_sequence.append(action)
        return given_plan_sequence

    @staticmethod
    def is_action_executable(state_info):
        return state_info[EXECUTABLE_ACTION_BOOL_KEY] and len(state_info[FLUENTS_KEY]) > 0

    def extract_actions(self, is_executable):
        """extracts the executable actions for each time step"""
        actions_for_timestep = []
        for action_state_info in self.states_actions:  # timestep is a dictionary with action as key and value as another dictionary
            actions = []
            for action, value in action_state_info.items():
                if self.is_action_executable(value) == is_executable:
                    actions.append(action)
            actions_for_timestep.append(actions)
        return actions_for_timestep

    def extract_fluents_for_given_plan(self, fluent_type=FLUENTS_KEY):
        """extracts the executable actions for each time step"""
        states = [self.init_state[fluent_type]]
        # timestep is a dictionary with action as key and value as another dictionary
        for action_state_info, optimal_action in zip(self.states_actions, self.given_plan_sequence):
            states.append(action_state_info[optimal_action][fluent_type])
        return states

    def extract_executable_actions(self):
        """extracts the executable actions for each time step"""
        return self.extract_actions(is_executable=True)

    def extract_inexecutable_actions(self):
        """extracts the inexecutable actions for each time step"""
        return self.extract_actions(is_executable=False)

    @staticmethod
    def extract_fluents_based_on_prefix(fluent_list_for_state, fluents_prefixes):
        fluents = []
        for item in fluent_list_for_state:
            for prefix in fluents_prefixes:
                if item.startswith(prefix):
                    fluents.append(item)
        return fluents

    def extract_fluents_types_for_state(self, fluents_given_plan, fluents_prefixes):
        "Extracts the base fluents for each time step"
        return [self.extract_fluents_based_on_prefix(fluents_timestep, fluents_prefixes) for fluents_timestep in
                fluents_given_plan]

    def fluents_for_fluent_type(self, plan_length, fluent_type):
        if fluent_type == BASE_FLUENTS:
            pos_fluents = self.base_pos_fluents[plan_length]
            neg_fluents = self.base_neg_fluents[plan_length]
        elif fluent_type == DERIVED_FLUENTS:
            pos_fluents = self.derived_pos_fluents[plan_length]
            neg_fluents = self.derived_neg_fluents[plan_length]
        elif fluent_type == PERSISTENT_FLUENTS:
            pos_fluents = self.persistent_pos_fluents[plan_length]
            neg_fluents = self.persistent_neg_fluents[plan_length]
        elif fluent_type == STATIC_FLUENTS:
            pos_fluents = self.static_pos_fluents[plan_length]
            neg_fluents = self.static_neg_fluents[plan_length]
        elif fluent_type == FLUENT_TYPES_ALL:
            pos_fluents = self.pos_fluents_given_plan[plan_length]
            neg_fluents = self.neg_fluents_given_plan[plan_length]
        else:
            raise ValueError(f'Undefined fluent type {fluent_type}')
        return pos_fluents, neg_fluents

    def get_random_inexecutable_sequence(self, plan_length):
        # TODO rm
        # Checking whether any inexecutable actions are present till the sequence length
        all_empty = True
        for i in range(plan_length):
            if self.inexecutable_actions[i + 1]:
                all_empty = False
                break
        if all_empty:
            return None

        optimal_sequence = self.given_plan_sequence[:plan_length]
        index = random.randint(0, plan_length - 1)  # This contains index of the inexecutable action
        while not self.inexecutable_actions[index]:  # If no inexecutable action exists for that location
            index = random.randint(0, plan_length - 1)
        inexecutable_action = random.choice(self.inexecutable_actions[index])
        sequence = optimal_sequence[:index] + [inexecutable_action]
        # fill the rest with garbage
        while len(sequence) < plan_length:
            # Adding sequence from randomly generated optimal plan
            sequence += [random.choice(self.given_plan_sequence)]
        return sequence, index

    @staticmethod
    def is_substring_within_parentheses(input_string, substring):
        pattern = re.compile(SUBSTRING_WITHIN_PARENTHESIS_REGEX.format(re.escape(substring)))
        return bool(pattern.search(input_string))

    def fluents_for_obj(self, obj, plan_length, is_true_fluents=True, fluent_type=BASE_FLUENTS):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents = pos_fluents if is_true_fluents else neg_fluents
        fluents_for_object = []
        for fluent in fluents:
            if self.is_substring_within_parentheses(fluent, obj):
                fluents_for_object.append(fluent)
        return fluents_for_object

    def object_type_by_object_name(self):
        by_object_name = {}
        for obj_type, objects in self.objects_by_type.items():
            for obj in objects:
                by_object_name[obj] = obj_type
        return by_object_name

    def nl_objects(self, objects, is_sorted=True):
        return asp_to_nl(objects, lambda x: x, is_sorted=is_sorted)

    def nl_fluents(self, fluents, fluent_subs=None, is_sorted=True, is_capitalized=False):
        nl = asp_to_nl(fluents, self.domain_class.fluent_to_natural_language, fluent_subs=fluent_subs,
                       is_sorted=is_sorted)
        if is_capitalized:
            return capitalize_first_letter(nl)
        return nl

    def nl_actions(self, actions, fluent_subs=None, is_sorted=False):
        actions = [a[len('action_'):] for a in actions]
        return asp_to_nl(actions, self.domain_class.action_to_natural_language, fluent_subs=fluent_subs,
                         is_sorted=is_sorted)

    def nl_question_prefix(self, plan_length, is_planned=False):
        if is_planned:
            prefix = ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX
        else:
            prefix = ACTIONS_ARE_PERFORMED_PREFIX
        return f"{prefix} {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def nl_actions_up_to(self, plan_length):
        return self.nl_actions(self.given_plan_sequence[:plan_length])

    @staticmethod
    def corrupt_fluents(fluents, fraction_to_corrupt=FRACTION_TO_CORRUPT):
        def corrupt_fluent(fluent):
            return f"{fluent[1:]}" if fluent[0] == '-' else f"-{fluent}"

        if not fluents:
            raise ValueError('Empty list')
        elif len(fluents) == 1:
            return [corrupt_fluent(fluents[0])]
        else:
            corrupted_fluents = copy.deepcopy(fluents)
            num_samples_to_corrupt = int(fraction_to_corrupt * len(fluents)) or 1
            samples_to_corrupt_inds = random.sample(range(0, len(fluents)), num_samples_to_corrupt)
            for i in samples_to_corrupt_inds:
                corrupted_fluents[i] = corrupt_fluent(fluents[i])
            return corrupted_fluents

    def corrupt_action_sequence(self, plan_length):
        corrupted_actions = deepcopy(self.given_plan_sequence[:plan_length])
        random_corrupt_action_i = random.randint(0, plan_length - 1)
        random_corrupt_action = random.choice(self.inexecutable_actions[random_corrupt_action_i])
        corrupted_actions[random_corrupt_action_i] = random_corrupt_action
        return corrupted_actions, random_corrupt_action_i

    def sequence_of_actions(self, plan_length, is_correct_sequence):
        if not is_correct_sequence:
            sequence_of_actions, random_corrupt_action_i = self.corrupt_action_sequence(plan_length)
        else:
            sequence_of_actions = self.given_plan_sequence[:plan_length]
            random_corrupt_action_i = random.randint(0, plan_length - 1)
        return sequence_of_actions, random_corrupt_action_i

    def fluents_for_object_tracking(self, obj, plan_length, fluent_type):
        if fluent_type == BASE_FLUENTS:
            pos_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=True, fluent_type=BASE_FLUENTS)
            neg_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=False, fluent_type=BASE_FLUENTS)
        elif fluent_type == DERIVED_FLUENTS:
            pos_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=True, fluent_type=DERIVED_FLUENTS)
            neg_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=False, fluent_type=DERIVED_FLUENTS)
        elif fluent_type == PERSISTENT_FLUENTS:
            pos_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=True, fluent_type=PERSISTENT_FLUENTS)
            neg_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=False, fluent_type=PERSISTENT_FLUENTS)
        elif fluent_type == STATIC_FLUENTS:
            pos_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=True, fluent_type=STATIC_FLUENTS)
            neg_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=False, fluent_type=STATIC_FLUENTS)
        elif fluent_type == FLUENT_TYPES_ALL:
            pos_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=True, fluent_type=FLUENT_TYPES_ALL)
            neg_fluents = self.fluents_for_obj(obj, plan_length, is_true_fluents=False, fluent_type=FLUENT_TYPES_ALL)
        else:
            raise ValueError(f'Undefined fluent type {fluent_type}')
        return pos_fluents, neg_fluents

    def fluents_for_random_obj(self, plan_length, fluent_type, min_chosen_fluents=1, timeout=MAX_TIMEOUT):
        pos_fluents, neg_fluents = [], []
        while (len(pos_fluents) + len(neg_fluents)) < min_chosen_fluents and timeout > 0:
            obj = random.choice(self.all_objects)
            pos_fluents, neg_fluents = self.fluents_for_object_tracking(obj, plan_length, fluent_type)
            if len(pos_fluents) or len(neg_fluents):
                return pos_fluents, neg_fluents, obj
            timeout -= 1
        return None, None, None

    def sample_fluents(self, fluents):
        if len(fluents) == 0:
            raise ValueError('Empty list')
        elif len(fluents) == 1:
            num_samples = 1
        else:
            num_samples = random.randint(2, len(fluents) - 1)
        fluents = random.sample(fluents, num_samples)
        return self.corrupt_fluents(fluents)

    def fluent_helper(self, pos_fluents, neg_fluents, is_answer_true,
                      fluent_sign_question=POS_PLUS_NEG_FLUENTS_QUESTION):
        if not pos_fluents and not neg_fluents:
            return None

        if is_answer_true:
            if fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION:
                if not pos_fluents or not neg_fluents:
                    return None
                return pos_fluents + neg_fluents
            if fluent_sign_question == POS_FLUENTS_QUESTION:
                return pos_fluents
            elif fluent_sign_question == NEG_FLUENTS_QUESTION:
                return neg_fluents
            else:
                raise ValueError('Undefined fluent_sign_question')
        else:
            if fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION:
                return self.corrupt_fluents(pos_fluents + neg_fluents)
            else:
                if not pos_fluents or not neg_fluents:
                    return None
                fluents = self.corrupt_fluents(pos_fluents) + self.corrupt_fluents(neg_fluents)
                if fluent_sign_question == POS_FLUENTS_QUESTION:
                    return [f if f[0] != '-' else f[1:] for f in fluents]
                else:
                    return [f if f[0] == '-' else '-' + f for f in fluents]

    def pos_neg_fluent_question_helper(self, fluent_sign_question, pos_fluents=[], neg_fluents=[]):
        if fluent_sign_question == POS_FLUENTS_QUESTION and pos_fluents:
            return self.nl_fluents(pos_fluents)
        elif fluent_sign_question == NEG_FLUENTS_QUESTION and neg_fluents:
            return self.nl_fluents(neg_fluents)
        elif fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION and pos_fluents and neg_fluents:
            return self.nl_fluents(pos_fluents + neg_fluents)
        return None


class QuestionGenerator(QuestionGenerationHelpers):
    digit_regex = '\d+'
    word_regex = '[a-zA-Z]+'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def qa_data_object(self, question, answer, answer_type, question_name, plan_length, fluent_type,
                       fluent_sign_question, subcategories=None):
        if subcategories is None:
            subcategories = []
        result = {OUT_OBJ_ID: str(uuid.uuid4()),
                  OUT_OBJ_DOMAIN_NAME: self.domain_class.DOMAIN_NAME,
                  OUT_OBJ_INSTANCE_ID: self.instance_id,
                  OUT_OBJ_QUESTION_CATEGORY: self.QUESTION_CATEGORY,
                  OUT_OBJ_QUESTION_NAME: question_name,
                  OUT_OBJ_FLUENT_TYPE: fluent_type,
                  OUT_OBJ_ANSWER_TYPE: answer_type,
                  OUT_OBJ_QUESTION: question,
                  OUT_OBJ_ANSWER: str(answer),
                  OUT_OBJ_PLAN_LENGTH: plan_length,
                  OUT_OBJ_INITIAL_STATE_NL: self.init_state_nl,
                  OUT_OBJ_FLUENT_SIGN_QUESTION: fluent_sign_question,
                  OUT_OBJ_QUESTION_SUBCATEGORIES: subcategories,
                  # OUT_OBJ_ACTION_SEQUENCE: self.given_plan_sequence,
                  # OUT_OBJ_INITIAL_STATE_ASP: self.init_state,
                  }
        if self.domain_class.is_random_sub:
            result[OUT_OBJ_QUESTION] = self.domain_class.to_random_substring(result[OUT_OBJ_QUESTION])
            if answer_type == FREE_ANSWER_TYPE:
                result[OUT_OBJ_ANSWER] = self.domain_class.to_random_substring(result[OUT_OBJ_ANSWER])
        return result

    @staticmethod
    def question_category():
        raise 'Implement it in the child class'

    @staticmethod
    def unique_questions(question_constructor, plan_length, multiplicity, timeout_outer=1, timeout_inner=10):
        # Note: if is using multiplicty >1 increase the timeout_outer
        results = {}
        while (len(results) < multiplicity) and timeout_outer > 0:
            qa_object = question_constructor(plan_length)
            if qa_object == CONTROLLED_REJECTED_QUESTION_FOR_BALANCE:
                return []
            while timeout_inner > 0 and (qa_object is None):
                qa_object = question_constructor(plan_length)
                timeout_inner -= 1
            if not qa_object:
                return []
            qa_id = (qa_object['question'], qa_object['answer'])
            results[qa_id] = qa_object
            timeout_outer -= 1
        return list(results.values())

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY, plan_lengths=PLAN_LENGTHS):
        results = []
        for plan_length in plan_lengths:
            for question_constructor in self.question_iterators():
                results += self.unique_questions(question_constructor, plan_length, multiplicity)
        return results

    def question_iterators(self):
        raise ValueError('Implement it in the child class')


class ObjectTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'object_tracking'
#
#     def __init__(self, states_actions_all, domain_class, instance_id):
#         super().__init__(states_actions_all, domain_class, instance_id)
#
#     def questions_iter_1_helper(self, plan_length, fluent_type, fluent_sign_question, is_answer_true, question_name):
#         pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type)
#         fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true, fluent_sign_question)
#         if not fluents:
#             return None
#         nl_fluents = self.nl_fluents(fluents)
#         question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that the following {FLUENTS_NL} are correct for {obj}: {nl_fluents}?"
#         return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
#                                    fluent_type, fluent_sign_question)
#
#     def questions_iter_1(self):
#         counter = 0
#         for fluent_type in FLUENT_TYPES_LIST:
#             for fluent_sign_question in [True, False, None]:
#                 for is_answer_true in [True, False]:
#                     counter += 1
#                     yield partial(self.questions_iter_1_helper,
#                                   fluent_type=fluent_type,
#                                   fluent_sign_question=fluent_sign_question,
#                                   is_answer_true=is_answer_true,
#                                   question_name=question_name(counter, 'iter_1'))
#
#     ########## Free Answer questions ##########
#
#     def question_1(self, plan_length):
#         random_object_type = random.choice(list(self.objects_by_type.keys()))
#         question = f"{self.nl_question_prefix(plan_length)} list all objects associated with type {random_object_type}. {NONE_STATEMENT}."
#         answer = self.objects_by_type[random_object_type]
#         nl_answer = asp_to_nl(sorted(answer), lambda x: x)
#         return self.qa_data_object(question, nl_answer, FREE_ANSWER_TYPE, self.question_1.__name__, plan_length, None)
#
#     def question_2(self, plan_length):
#         random_object_type = random.choice(list(self.objects_by_type.keys()))
#         random_objects = random.sample(self.objects_by_type[random_object_type],
#                                        random.randint(1, len(self.objects_by_type[random_object_type])))
#         nl_random_objects = asp_to_nl(random_objects, lambda x: x)
#         question = f"{self.nl_question_prefix(plan_length)} what is the object type for {nl_random_objects}. {NONE_STATEMENT}."
#         return self.qa_data_object(question, random_object_type, FREE_ANSWER_TYPE, self.question_2.__name__,
#                                    plan_length, None)
#
#     def question_iterators(self):
#         return chain(self.questions_iter_1(),
#                      [self.question_1, self.question_2])


class FluentTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'fluent_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, fluent_type, fluent_sign_question, is_answer_true, question_name):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        if is_answer_true and fluent_sign_question == POS_FLUENTS_QUESTION and pos_fluents:
            fluent = random.choice(pos_fluents)
        elif is_answer_true and fluent_sign_question == NEG_FLUENTS_QUESTION and neg_fluents:
            fluent = random.choice(neg_fluents)

        elif not is_answer_true and fluent_sign_question == NEG_FLUENTS_QUESTION and pos_fluents:
            fluent = '-' + random.choice(pos_fluents)
        elif not is_answer_true and fluent_sign_question == POS_FLUENTS_QUESTION and neg_fluents:
            fluent = random.choice(neg_fluents)[1:]
        else:
            return None
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {self.domain_class.fluent_to_natural_language(fluent)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   fluent_type, fluent_sign_question)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST[:-1]:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_1_helper,
                                  fluent_type=fluent_type,
                                  fluent_sign_question=fluent_sign_question,
                                  is_answer_true=is_answer_true,
                                  question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, fluent_type, fluent_sign_question, is_answer_true, question_name):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true, fluent_sign_question)
        if not fluents:
            return None
        fluent_negation_nl = fluents_negation_to_nl(fluent_sign_question)
        question = f"{self.nl_question_prefix(plan_length)} are all of the following {fluent_negation_nl} {TRUE_OR_FALSE}: {self.nl_fluents(fluents)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   fluent_type, fluent_sign_question)

    def questions_iter_2(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_2_helper,
                                  fluent_type=fluent_type,
                                  fluent_sign_question=fluent_sign_question,
                                  is_answer_true=is_answer_true,
                                  question_name=question_name(counter, 'iter_2'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_3_helper(self, plan_length, fluent_sign_question, obj, question_name):
        fluent_type = FLUENT_TYPES_ALL
        fluent_type_negation_nl = fluents_negation_to_nl(fluent_sign_question)
        pos_fluents, neg_fluents = self.fluents_for_object_tracking(obj, plan_length, fluent_type)
        if fluent_sign_question == POS_FLUENTS_QUESTION and not pos_fluents:
            return None
        elif fluent_sign_question == NEG_FLUENTS_QUESTION and not neg_fluents:
            return None
        elif not pos_fluents or not neg_fluents and fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION:
            return None

        question = (f"{self.nl_question_prefix(plan_length)} what are the {fluent_type_negation_nl} for {obj}? "
                    f"{NONE_STATEMENT}")
        fluents = self.fluent_helper(pos_fluents, neg_fluents, True, fluent_sign_question)
        if not fluents:
            answer = 'None'
        else:
            answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, fluent_type,
                                   fluent_sign_question)

    def questions_iter_3(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            for obj in self.all_objects:
                counter += 1
                yield partial(self.questions_iter_3_helper,
                              fluent_sign_question=fluent_sign_question,
                              obj=obj,
                              question_name=question_name(counter, 'iter_3'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3())


class StateTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'state_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def helper(self, fluent_sign_question, plan_length):
        if fluent_sign_question == POS_FLUENTS_QUESTION:
            fluent_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length]
        elif fluent_sign_question == NEG_FLUENTS_QUESTION:
            fluent_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length]
        else:
            fluent_type_nl = POS_AND_NEG_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length] + self.neg_fluents_given_plan[plan_length]
        return fluent_type_nl, fluents

    def questions_iter_1_helper(self, plan_length, is_answer_true, fluent_sign_question, question_name):
        fluent_type_nl, fluents = self.helper(fluent_sign_question, plan_length)
        if not is_answer_true:
            fluents = self.corrupt_fluents(fluents)
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} are all of the following {fluent_type_nl}? {nl_fluents}. Respond with {TRUE_OR_FALSE}."
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, fluent_sign_question)

    def questions_iter_1(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_1_helper,
                              is_answer_true=is_answer_true,
                              fluent_sign_question=fluent_sign_question,
                              question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, fluent_sign_question, question_name):
        fluent_type_nl, fluents = self.helper(fluent_sign_question, plan_length)
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type_nl}. {NONE_STATEMENT}."
        return self.qa_data_object(question, nl_fluents, FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL,
                                   fluent_sign_question)

    def questions_iter_2(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          fluent_sign_question=fluent_sign_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2())


class ActionExecutabilityQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'action_executability'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, is_answer_true, question_name):
        sequence_of_actions, _random_corrupt_action_i = self.sequence_of_actions(plan_length, is_answer_true)
        nl_sequence_of_actions = asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_sequence_of_actions}. Is it possible to execute it, {TRUE_OR_FALSE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION)

    def questions_iter_1(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_1_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, is_answer_true, question_name):
        sequence_of_actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_answer_true)
        selected_action = sequence_of_actions[random_corrupt_action_i]

        nl_sequence_of_actions = self.nl_actions(sequence_of_actions)
        nl_selected_action = self.domain_class.action_to_natural_language(selected_action)
        question = (f"{INITIAL_CONDITION_PREFIX}, "
                    f"for steps 1 through {plan_length} the following actions are planned to be performed: {nl_sequence_of_actions}. "
                    f"Is the action: {nl_selected_action} executable at step {random_corrupt_action_i + 1}, "
                    f"{TRUE_OR_FALSE}?")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION)

    def questions_iter_2(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_2'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_3_helper(self, plan_length, is_answer_none, question_name):
        if is_answer_none:
            question = (
                f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. "
                f"What is the first inexecutable action in the sequence? "
                f"{NONE_STATEMENT}.")
            return self.qa_data_object(question, NONE_ANSWER, FREE_ANSWER_TYPE, question_name, plan_length,
                                       FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION)
        else:
            sequence_of_actions, random_corrupt_action_i = self.corrupt_action_sequence(plan_length)
            inexecutable_action = sequence_of_actions[random_corrupt_action_i]
            question = (
                f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. "
                f"What is the first inexecutable action in the sequence? "
                f"{NONE_STATEMENT}.")
            return self.qa_data_object(question, self.domain_class.action_to_natural_language(inexecutable_action),
                                       FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL,
                                       POS_PLUS_NEG_FLUENTS_QUESTION)

    def questions_iter_3(self):
        counter = 0
        for is_answer_none in [True, False]:
            counter += 1
            yield partial(self.questions_iter_3_helper,
                          is_answer_none=is_answer_none,
                          question_name=question_name(counter, 'iter_3'))

    def question_4(self, plan_length):
        question = (f"{self.nl_question_prefix(plan_length)} list all executable actions. "
                    f"{NONE_STATEMENT}.")
        return self.qa_data_object(question, self.nl_actions(self.executable_actions[plan_length]), FREE_ANSWER_TYPE,
                                   self.question_4.__name__, plan_length, FLUENT_TYPES_ALL,
                                   POS_PLUS_NEG_FLUENTS_QUESTION)

    def question_5(self, plan_length):
        question = (f"{self.nl_question_prefix(plan_length)} list all inexecutable actions. "
                    f"{NONE_STATEMENT}.")
        return self.qa_data_object(question, self.nl_actions(self.inexecutable_actions[plan_length]), FREE_ANSWER_TYPE,
                                   self.question_5.__name__, plan_length, FLUENT_TYPES_ALL,
                                   POS_PLUS_NEG_FLUENTS_QUESTION)

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3(),
                     [self.question_4, self.question_5])


class EffectsQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'effects'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def prefix(self, plan_length):
        if plan_length == 0:
            return f"{INITIAL_CONDITION_PREFIX},"
        else:
            return f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def questions_iter_1_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        action = self.given_plan_sequence[plan_length]
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents_current_state = set(pos_fluents).union(set(neg_fluents))

        next_pos_fluents, next_neg_fluents = self.fluents_for_fluent_type(plan_length + 1, fluent_type)
        fluents_next_state = set(next_pos_fluents).union(set(next_neg_fluents))
        fluents_new_minus_old = fluents_next_state - fluents_current_state
        if not fluents_new_minus_old:
            return None

        if is_answer_true:
            nl_fluents = self.nl_fluents(list(fluents_new_minus_old))
        else:
            fluents_all = set()
            for l in range(self.plan_length_max):
                pos_fluents, neg_fluents = self.fluents_for_fluent_type(l, fluent_type)
                fluents_all = fluents_all.union(set(pos_fluents).union(set(neg_fluents)))
            if not fluents_all:
                return None
            fluents = self.corrupt_fluents(list(fluents_all))
            fluents = list(set(fluents))
            upper = min(len(fluents), len(fluents_new_minus_old))
            rand_num_fluents = random.randint(1, upper)
            fluents = random.sample(fluents, rand_num_fluents)
            nl_fluents = self.nl_fluents(list(fluents))

        question = (f"{self.prefix(plan_length)} if {self.nl_actions([action])}, is it {TRUE_OR_FALSE} that {nl_fluents}?") #"would be valid after the action is taken?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   fluent_type, POS_PLUS_NEG_FLUENTS_QUESTION)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_1_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_1'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_2_helper(self, plan_length, fluent_sign_question, question_name):
        action = self.given_plan_sequence[plan_length]
        if fluent_sign_question == POS_PLUS_NEG_FLUENTS_QUESTION:
            fluent_negation_nl = POS_AND_NEG_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length + 1] + self.neg_fluents_given_plan[plan_length + 1]
        elif fluent_sign_question == POS_FLUENTS_QUESTION:
            fluent_negation_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length + 1]
        else:
            fluent_negation_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length + 1]
        question = (f"{self.prefix(plan_length)} if {self.nl_actions([action])}, "
                    f"what would be all of the {fluent_negation_nl}? "
                    f"{NONE_STATEMENT}.")
        return self.qa_data_object(question, self.nl_fluents(fluents), FREE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, fluent_sign_question)

    def questions_iter_2(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          fluent_sign_question=fluent_sign_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2())


class NumericalReasoningQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'numerical_reasoning'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def random_count(original_count):
        bound = int(0.2 * original_count) + 1
        number = original_count + random.choice(
            [random.randrange(-bound, 0), random.randrange(1, bound + 1)])  # excluding the zero
        return np.abs(number)

    def objects_count(self, plan_length):
        return {
            # 'objects': len(self.all_objects),
            'executable actions': len(self.executable_actions[plan_length]),
            'inexecutable actions': len(self.inexecutable_actions[plan_length]),
            'executable and inexecutable actions': len(self.inexecutable_actions[plan_length]) + len(self.executable_actions[plan_length]),
            POSITIVE_FLUENTS_NL: len(self.pos_fluents_given_plan[plan_length]),
            NEGATIVE_FLUENTS_NL: len(self.neg_fluents_given_plan[plan_length]),
            POS_AND_NEG_FLUENTS_NL: len(self.pos_fluents_given_plan[plan_length]) + len(self.neg_fluents_given_plan[plan_length]),
            # BASE_FLUENTS_NL: len(list(chain.from_iterable(self.fluents_for_fluent_type(plan_length, BASE_FLUENTS)))),
            # DERIVED_FLUENTS_NL: len(list(chain.from_iterable(self.fluents_for_fluent_type(plan_length, DERIVED_FLUENTS)))),
            # PERSISTENT_FLUENTS_NL: len(list(chain.from_iterable(self.fluents_for_fluent_type(plan_length, PERSISTENT_FLUENTS)))),
            # STATIC_FLUENTS_NL: len(list(chain.from_iterable(self.fluents_for_fluent_type(plan_length, STATIC_FLUENTS))))
        }

    @staticmethod
    def subcategories_helper(name_count):
        subcategories = []
        if name_count in (POSITIVE_FLUENTS_NL, NEGATIVE_FLUENTS_NL, POS_AND_NEG_FLUENTS_NL):
            subcategories.append(FluentTrackingQuestions.QUESTION_CATEGORY)
        elif name_count in ('executable actions', 'inexecutable actions', 'executable and inexecutable actions'):
            subcategories.append(ActionExecutabilityQuestions.QUESTION_CATEGORY)
        else:
            raise ValueError(f'Undefined name_count {name_count}')
        return subcategories

    def questions_iter_1_helper(self, plan_length, is_answer_true, name_count, question_name):
        count = self.objects_count(plan_length)[name_count]
        if is_answer_true:
            total_count = count
        else:
            total_count = self.random_count(count)

        if name_count == POSITIVE_FLUENTS_NL:
            fluent_sign_question = POS_FLUENTS_QUESTION
        elif name_count == NEGATIVE_FLUENTS_NL:
            fluent_sign_question = NEG_FLUENTS_QUESTION
        else:
            fluent_sign_question = POS_PLUS_NEG_FLUENTS_QUESTION

        question = f"{self.nl_question_prefix(plan_length)} is the number of {name_count} equal to {total_count}? {TRUE_OR_FALSE}"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, fluent_sign_question, self.subcategories_helper(name_count))

    def questions_iter_1(self):
        counter = 0
        for name_count in self.objects_count(1).keys():
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_1_helper,
                              is_answer_true=is_answer_true,
                              name_count=name_count,
                              question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, name_count, question_name):
        count = self.objects_count(plan_length)[name_count]
        question = (f"{self.nl_question_prefix(plan_length)} what is the total number of {name_count}? "
                    f"Write as an integer. {NONE_STATEMENT}.")
        return self.qa_data_object(question, count, FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL,
                                   POS_PLUS_NEG_FLUENTS_QUESTION, self.subcategories_helper(name_count))

    def questions_iter_2(self):
        counter = 0
        for name_count in self.objects_count(1).keys():
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          name_count=name_count,
                          question_name=question_name(counter, 'iter_2'))

    def questions_iter_3_helper(self, plan_length, is_answer_true, question_name):
        if is_answer_true:
            total_count = plan_length
        else:
            total_count = self.random_count(plan_length)
        question = (f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. "
                    f"Is it {TRUE_OR_FALSE} that the number of actions that led to current state in the sequence is equal to {total_count}?")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION, [ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def questions_iter_3(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_3_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_3'))

    def question_4(self, plan_length):
        sequence_of_actions, random_corrupt_action_i = self.corrupt_action_sequence(plan_length)
        question = (
            f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. "
            f"How many actions are there before the first inexecutable action? "
            f"Write as an integer. {NONE_STATEMENT}.")
        return self.qa_data_object(question, random_corrupt_action_i, FREE_ANSWER_TYPE, self.question_4.__name__,
                                   plan_length, FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION, [ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3(),
                     [self.question_4])


# class HallucinationQuestions(QuestionGenerator):
#     QUESTION_CATEGORY = 'hallucination'
#     NUMBER_REGEX = f'\d'
#
#     def __init__(self, states_actions_all, domain_class, instance_id):
#         super().__init__(states_actions_all, domain_class, instance_id)
#
#     def question_setup(self, stuff):
#         return f'some {stuff} may or may not be defined'
#
#     def hallucinated_object(self, object, other_objects_set=set()):
#         all_objects = self.all_objects_set.union(other_objects_set)
#
#         r = re.compile(self.NUMBER_REGEX)
#         object_prefix = r.sub('', object)
#         # if object == object_prefix:
#         #     print('Error: object name does not contain a number')
#         i = 1
#         hallucinated_object = object_prefix + f'{i}'
#         while hallucinated_object in all_objects and i < 100:
#             hallucinated_object = object_prefix + f'{i}'
#             i += 1
#             if i == 100:
#                 raise 'timeout'
#         return hallucinated_object
#
#     def questions_iter_1_helper(self, plan_length, is_part_of_domain, question_name):
#         obj = random.choice(self.all_objects)
#         if not is_part_of_domain:
#             obj = self.hallucinated_object(obj)
#         question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. "
#                     f"Is {obj} {PART_OF_THE_DOMAIN}? {TRUE_OR_FALSE}")
#         return self.qa_data_object(question, is_part_of_domain, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
#                                    FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_KEY)
#
#     def questions_iter_1(self):
#         counter = 0
#         for is_part_of_domain in [True, False]:
#             counter += 1
#             yield partial(self.questions_iter_1_helper,
#                           is_part_of_domain=is_part_of_domain,
#                           question_name=question_name(counter, 'iter_1'))
#
#     def questions_iter_2_helper(self, plan_length, is_answer_true, fluent_sign_question, fluent_type, question_name):
#         pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
#
#         if fluent_sign_question and pos_fluents:
#             fluent = random.choice(pos_fluents)
#         elif fluent_sign_question and neg_fluents:
#             fluent = random.choice(neg_fluents)
#         else:
#             return None
#
#         if is_answer_true:
#             nl_fluent = self.domain_class.fluent_to_natural_language(fluent)
#         else:
#             nl_fluent = self.domain_class.fluent_to_natural_language(fluent, is_hallucinated=True)
#
#         question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup(FLUENTS_NL)}. "
#                     f"Is {nl_fluent} {PART_OF_THE_STATE}? {TRUE_OR_FALSE}")
#         return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length, None,
#                                    fluent_sign_question)
#
#     def questions_iter_2(self):
#         counter = 0
#         for is_answer_true in [True, False]:
#             for fluent_sign_question in [True, False]:
#                 for fluent_type in FLUENT_TYPES_LIST:
#                     counter += 1
#                     yield partial(self.questions_iter_2_helper,
#                                   is_answer_true=is_answer_true,
#                                   fluent_sign_question=fluent_sign_question,
#                                   fluent_type=fluent_type,
#                                   question_name=question_name(counter, 'iter_2'))
#
#     def questions_iter_3_helper(self, plan_length, is_executable_action, is_answer_true, question_name):
#         if is_executable_action:
#             action = random.choice(self.executable_actions[plan_length])
#         else:
#             action = random.choice(self.inexecutable_actions[plan_length])
#
#         if is_answer_true:
#             nl_action = self.domain_class.action_to_natural_language(action)
#         else:
#             nl_action = self.domain_class.action_to_natural_language(action, is_hallucinated=True)
#
#         question = (f"{self.nl_question_prefix(plan_length, is_planned=True)} "
#                     f"is action, {nl_action}, {PART_OF_THE_DOMAIN}? {TRUE_OR_FALSE}")
#         return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_KEY)
#
#     def questions_iter_3(self):
#         counter = 0
#         for is_executable_action in [True, False]:
#             for is_answer_true in [True, False]:
#                 counter += 1
#                 yield partial(self.questions_iter_3_helper,
#                               is_executable_action=is_executable_action,
#                               is_answer_true=is_answer_true,
#                               question_name=question_name(counter, 'iter_3'))
#
#     def questions_iter_4_helper(self, plan_length, is_answer_true, question_name):
#         if len(self.all_objects) < 2:
#             print('less than 2 objects', question_name, plan_length)
#             return None
#         objects = random.sample(self.all_objects, random.randint(2, len(self.all_objects)))
#         answer = objects[0]
#         if not is_answer_true:
#             objects[0] = self.hallucinated_object(objects[0])
#             answer = objects[0]
#         random.shuffle(objects)
#         nl_objects = asp_to_nl(objects, lambda x: x)
#         question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. "
#                     f"Which of the following objects, {nl_objects}, is not {PART_OF_THE_DOMAIN}? "
#                     f"Write None if all are defined.")
#         return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_KEY)
#
#     def questions_iter_4(self):
#         counter = 0
#         for is_answer_true in [True, False]:
#             counter += 1
#             yield partial(self.questions_iter_4_helper,
#                           is_answer_true=is_answer_true,
#                           question_name=question_name(counter, 'iter_4'))
#
#     def questions_iter_5_helper(self, plan_length, fluent_sign_question, is_answer_true, fluent_type, question_name):
#         pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
#         lower_bound_rand_int = 2
#         if fluent_sign_question is True and len(pos_fluents) >= lower_bound_rand_int:
#             fluent_type_nl = POSITIVE_FLUENT_NL
#             fluents = random.sample(pos_fluents, random.randint(lower_bound_rand_int, len(pos_fluents)))
#         elif fluent_sign_question is False and len(neg_fluents) >= lower_bound_rand_int:
#             fluent_type_nl = NEGATIVE_FLUENT_NL
#             fluents = random.sample(neg_fluents, random.randint(lower_bound_rand_int, len(neg_fluents)))
#         elif fluent_sign_question is None and len(pos_fluents + neg_fluents) >= lower_bound_rand_int:
#             fluent_type_nl = FLUENTS_NL
#             fluents = random.sample(pos_fluents + neg_fluents,
#                                     random.randint(lower_bound_rand_int, len(pos_fluents + neg_fluents)))
#         else:
#             return None
#
#         if is_answer_true:
#             nl_hallucinated_fluent = NONE_ANSWER
#             nl_fluents = self.nl_fluents(fluents)
#         else:
#             nl_fluent = self.domain_class.fluent_to_natural_language(fluents[0])
#             nl_hallucinated_fluent = self.domain_class.fluent_to_natural_language(fluents[0], is_hallucinated=True)
#             random.shuffle(fluents)
#             nl_fluents = self.nl_fluents(fluents).replace(nl_fluent, nl_hallucinated_fluent)
#         question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup(f'{fluent_type_nl}')}. "
#                     f"What {fluent_type_nl} out of, {nl_fluents}, is not defined? Write None if all are defined.")
#         return self.qa_data_object(question, nl_hallucinated_fluent, FREE_ANSWER_TYPE, question_name, plan_length, None,
#                                    fluent_sign_question)
#
#     def questions_iter_5(self):
#         counter = 0
#         for fluent_sign_question in [True, False, None]:
#             for is_answer_true in [True, False]:
#                 for fluent_type in FLUENT_TYPES_LIST:
#                     counter += 1
#                     yield partial(self.questions_iter_5_helper,
#                                   fluent_sign_question=fluent_sign_question,
#                                   is_answer_true=is_answer_true,
#                                   fluent_type=fluent_type,
#                                   question_name=question_name(counter, 'iter_5'))
#
#     def questions_iter_6_helper(self, plan_length, is_answer_true, question_name):
#         postfix = 'to reach the current state. Given this sequence, what action is not defined? Write None if all are defined'
#         if is_answer_true:
#             question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} {postfix}."
#             answer = NONE_ANSWER
#         else:
#             actions = self.given_plan_sequence[:plan_length]
#             random_int = random.randint(0, len(actions) - 1)
#             nl_hallucinated_action = self.domain_class.action_to_natural_language(actions[random_int],
#                                                                                   is_hallucinated=True)
#
#             nl_actions_ls = asp_to_nl([a[len('action_'):] for a in actions],
#                                       self.domain_class.action_to_natural_language, is_sorted=False, is_list=True)
#             nl_actions_ls[random_int] = nl_hallucinated_action
#             nl_actions = add_commas_and(nl_actions_ls)
#             question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_actions} {postfix}."
#             answer = nl_hallucinated_action
#         return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_KEY)
#
#     def questions_iter_6(self):
#         counter = 0
#         for is_answer_true in [True, False]:
#             counter += 1
#             yield partial(self.questions_iter_6_helper,
#                           is_answer_true=is_answer_true,
#                           question_name=question_name(counter, 'iter_6'))
#
#     def question_iterators(self):
#         return chain(self.questions_iter_1(),
#                      self.questions_iter_2(),
#                      self.questions_iter_3(),
#                      self.questions_iter_4(),
#                      self.questions_iter_5(),
#                      self.questions_iter_6())


class CompositeQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'composite'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def nl_question_prefix_custom(self, nl_actions, is_planned=False):
        if is_planned:
            prefix = ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX
        else:
            prefix = ACTIONS_ARE_PERFORMED_PREFIX
        return f"{prefix} {nl_actions} to reach the current state."

    def questions_iter_1_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        fluents_nl = POS_AND_NEG_FLUENTS_NL
        is_correct_sequence = False
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)

        pos_fluents, neg_fluents = self.fluents_for_fluent_type(random_corrupt_action_i, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
        if not fluents:
            return None
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    f"Are the following {fluents_nl} true before the first inexecutable action in the sequence? "
                    f"{self.nl_fluents(fluents, is_capitalized=True)}. ")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   fluent_type, POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [FluentTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_1_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        is_correct_sequence = False
        fluents_nl = POS_AND_NEG_FLUENTS_NL
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)

        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(random_corrupt_action_i, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
        if not fluents:
            return None
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    f"Are the following {fluents_nl} true for {obj} before the first inexecutable action in the sequence? "
                    f"{self.nl_fluents(fluents, is_capitalized=True)}. ")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   fluent_type, POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [FluentTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY, ObjectTrackingQuestions.QUESTION_CATEGORY])

    def questions_iter_2(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_2_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_2'))

    # def questions_iter_3_helper(self, plan_length, fluent_type, is_answer_true, question_name):
    #     actions = self.given_plan_sequence[:plan_length]
    #     action_performed_nl = self.nl_actions([actions[plan_length-1]])
    #
    #     pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type)
    #     fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
    #     if not fluents:
    #         return None
    #     question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
    #                 f"If I perform action {action_performed_nl}, would the following {FLUENTS_NL} be true for {obj}? "
    #                 f"{self.nl_fluents(fluents, is_capitalized=True)}. ")
    #     return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
    #                                fluent_type)

    # def questions_iter_3(self):
    #     counter = 0
    #     for fluent_type in FLUENT_TYPES_LIST:
    #         for is_answer_true in [True, False]:
    #             counter += 1
    #             yield partial(self.questions_iter_3_helper,
    #                           fluent_type=fluent_type,
    #                           is_answer_true=is_answer_true,
    #                           question_name=question_name(counter, 'iter_3'))

    def questions_iter_4_helper(self, plan_length, is_answer_true, question_name):
        is_correct_sequence = False
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)

        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    "Some of the actions may not be executable. "
                    f"Is this the state before the first inexecutable action in the sequence? {TRUE_OR_FALSE}")
        state = self.pos_fluents_given_plan[random_corrupt_action_i] + self.neg_fluents_given_plan[random_corrupt_action_i]
        if not is_answer_true:
            state = self.corrupt_fluents(state)
        question += self.nl_fluents(state)
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER_TYPE, question_name, plan_length,
                                   FLUENT_TYPES_ALL, POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [StateTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def questions_iter_4(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_4_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_4'))

    # free answer questions

    def questions_iter_5_helper(self, plan_length, fluent_sign_question, question_name):
        fluent_type = FLUENT_TYPES_ALL
        fluent_type_negation_nl = fluents_negation_to_nl(fluent_sign_question)
        is_answer_true = random.choice([True, False])
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_answer_true)
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    f"Some of the actions may not be executable. "
                    f"What {fluent_type_negation_nl} are true before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_answer_true:
            answer = NONE_ANSWER
        else:
            pos_fluents, neg_fluents = self.fluents_for_fluent_type(random_corrupt_action_i, fluent_type)
            answer = self.pos_neg_fluent_question_helper(fluent_sign_question, pos_fluents, neg_fluents)
            if not answer:
                return None
        return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, fluent_type,
                                   POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [FluentTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def questions_iter_5(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_5_helper,
                          fluent_sign_question=fluent_sign_question,
                          question_name=question_name(counter, 'iter_5'))

    def questions_iter_6_helper(self, plan_length, fluent_sign_question, question_name):
        fluent_type = FLUENT_TYPES_ALL
        fluent_type_negation_nl = fluents_negation_to_nl(fluent_sign_question)

        is_answer_true = random.choice([True, False])
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_answer_true)

        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(random_corrupt_action_i, fluent_type=fluent_type)
        answer = self.pos_neg_fluent_question_helper(fluent_sign_question, pos_fluents, neg_fluents)
        if not answer:
            return None

        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    f"What are the {fluent_type_negation_nl} for {obj} before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_answer_true:
            answer = NONE_ANSWER
        else:
            fluents = pos_fluents + pos_fluents
            if not fluents:
                return None
            answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, fluent_type,
                                   POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [FluentTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY, ObjectTrackingQuestions.QUESTION_CATEGORY])

    def questions_iter_6(self):
        counter = 0
        for fluent_sign_question in POS_NEG_FLUENTS_KEY_LIST:
            counter += 1
            yield partial(self.questions_iter_6_helper,
                          fluent_sign_question=fluent_sign_question,
                          question_name=question_name(counter, 'iter_6'))

    # def questions_iter_7_helper(self, plan_length, fluent_type, question_name):
    #     actions = self.given_plan_sequence[:plan_length]
    #     action_performed_nl = self.nl_actions([actions[plan_length-1]])
    #
    #     pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length + 1, fluent_type)
    #     if pos_fluents is None and neg_fluents is None:
    #         return None
    #
    #     question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions))}. "
    #                 f"If I perform action {action_performed_nl}, what would be all of the {fluent_type_to_fluent_nl(fluent_type)} for {obj}? "
    #                 f"{NONE_STATEMENT}")
    #     pos_fluents, pos_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
    #     fluents = pos_fluents + pos_fluents
    #     if not fluents:
    #         return None
    #     answer = self.nl_fluents(fluents)
    #     return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, fluent_type)

    # def questions_iter_7(self):
    #     counter = 0
    #     for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
    #         counter += 1
    #         yield partial(self.questions_iter_7_helper,
    #                       fluent_type=fluent_type,
    #                       question_name=question_name(counter, 'iter_7'))

    def questions_iter_8_helper(self, plan_length, is_correct_sequence, question_name):
        actions, random_corrupt_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)} "
                    f"Some of the actions may not be executable. "
                    f"What is the state before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_correct_sequence:
            answer = NONE_ANSWER
        else:
            state = self.pos_fluents_given_plan[random_corrupt_action_i] + self.neg_fluents_given_plan[
                random_corrupt_action_i]
            answer = self.nl_fluents(state)
        return self.qa_data_object(question, answer, FREE_ANSWER_TYPE, question_name, plan_length, FLUENT_TYPES_ALL,
                                   POS_PLUS_NEG_FLUENTS_QUESTION,
                                   [StateTrackingQuestions.QUESTION_CATEGORY,
                                    ActionExecutabilityQuestions.QUESTION_CATEGORY])

    def questions_iter_8(self):
        counter = 0
        for is_correct_sequence in [True, False]:
            counter += 1
            yield partial(self.questions_iter_8_helper,
                          is_correct_sequence=is_correct_sequence,
                          question_name=question_name(counter, 'iter_8'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     # self.questions_iter_3(),
                     self.questions_iter_4(),
                     self.questions_iter_5(),
                     self.questions_iter_6(),
                     # self.questions_iter_7(),
                     self.questions_iter_8())
