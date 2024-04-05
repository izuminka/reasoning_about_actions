import copy
import os
import random
import re
import sys
import uuid
from copy import deepcopy
from functools import partial
from itertools import chain

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.common import *

INITIAL_CONDITION_PREFIX = 'Given the initial condition'
ACTIONS_ARE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are performed:'
ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are planned to be performed:'
TRUE_OR_FALSE = 'True or False'
NONE_STATEMENT = 'Write None if there are none'
NONE_ANSWER = 'None'

BASE_FLUENTS = 'BASE_FLUENTS'
DERIVED_FLUENTS = 'DERIVED_FLUENTS'
PERSISTENT_FLUENTS = 'PERSISTENT_FLUENTS'
STATIC_FLUENTS = 'STATIC_FLUENTS'
FLUENT_TYPES_ALL = 'all_fluents'
FLUENT_TYPES_LIST = (BASE_FLUENTS, DERIVED_FLUENTS, PERSISTENT_FLUENTS, STATIC_FLUENTS)

PART_OF_THE_STATE = 'part of the state'
MAX_TIMEOUT = 50

OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
SUBSTRING_WITHIN_PARENTHESIS_REGEX = r'\([^)]*{}\w*[^)]*\)'

PLAN_LENGTHS = (1, 5, 10, 15, 19)
QUESTION_MULTIPLICITY = 2

FRACTION_TO_CORRUPT = 0.5


def fluent_type_to_fluent_nl(fluent_type):
    if fluent_type == BASE_FLUENTS:
        return BASE_FLUENTS_NL
    elif fluent_type == DERIVED_FLUENTS:
        return DERIVED_FLUENTS_NL
    elif fluent_type == PERSISTENT_FLUENTS:
        return PERSISTENT_FLUENTS_NL
    elif fluent_type == STATIC_FLUENTS:
        return STATIC_FLUENTS_NL
    else:
        raise ValueError(f'Undefined fluent type {fluent_type}')


def exit_condition_on_fluents(pos_fluents, neg_fluents):
    return not len(pos_fluents) or not len(neg_fluents)


def asp_to_nl(obj_ls, converter, fluent_subs=None):
    and_str = ' and '
    comma_str = ', '
    if not obj_ls:
        raise 'Empty list'
    if len(obj_ls) == 1:
        nl_obj = converter(obj_ls[0])
        if fluent_subs:
            nl_obj = nl_obj.replace(fluent_subs[0], fluent_subs[1])
        return nl_obj
    nl_obj_ls = [converter(f) for f in obj_ls]
    if fluent_subs:
        nl_obj_ls = [f.replace(fluent_subs[0], fluent_subs[1]) for f in nl_obj_ls]
    return comma_str.join(nl_obj_ls[:-1]) + and_str + nl_obj_ls[-1]


def question_name(q_id, prefix=None):
    if prefix:
        return f'question_{prefix}_{q_id}'
    return f'question_{q_id}'


def unique_id(data):
    import base64
    import hashlib
    hasher = hashlib.sha1(str(data).encode('ascii'))
    return base64.urlsafe_b64encode(hasher.digest())


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

    def nl_fluents(self, fluents, fluent_subs=None, is_sorted=True):
        nl = asp_to_nl(fluents, self.domain_class.fluent_to_natural_language, fluent_subs=fluent_subs)
        if is_sorted:
            return nl
        return nl

    def nl_actions(self, actions, fluent_subs=None):
        actions = [a[len('action_'):] for a in actions]
        return asp_to_nl(actions, self.domain_class.action_to_natural_language, fluent_subs=fluent_subs)

    def nl_question_prefix(self, plan_length, is_planned=False):
        if is_planned:
            prefix = ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX
        else:
            prefix = ACTIONS_ARE_PERFORMED_PREFIX
        return f"{prefix} {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def nl_actions_up_to(self, plan_length):
        return self.nl_actions(self.given_plan_sequence[:plan_length])

    @staticmethod
    def corrupted_not_corrupted_mix(not_corrupted_fluents, corrupted_fluents):
        # TODO double check this function, maybe replace with corrupt_fluents
        final_length = len(not_corrupted_fluents)
        len_corrupted_fluents = len(corrupted_fluents)

        if len_corrupted_fluents == 0:
            raise 'Empty list'
        elif final_length in (0, 1) or len_corrupted_fluents == 1:
            num_to_be_corrupted_samples = 1
        else:
            num_to_be_corrupted_samples = random.randint(1, min(len_corrupted_fluents, final_length) - 1)
        corrupted_fluents_samples = random.sample(corrupted_fluents, num_to_be_corrupted_samples)
        final = corrupted_fluents_samples + not_corrupted_fluents[:final_length - len(corrupted_fluents_samples)]
        final.shuffle()
        return final

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
            num_samples_to_corrupt = int(fraction_to_corrupt * len(fluents))
            samples_to_corrupt_inds = random.sample(range(0, len(fluents)), num_samples_to_corrupt)
            for i in samples_to_corrupt_inds:
                corrupted_fluents[i] = corrupt_fluent(fluents[i])
            return corrupted_fluents

    def corrupt_action_sequence(self, plan_length):
        corrupted_actions = deepcopy(self.given_plan_sequence[:plan_length])
        random_break_ind = random.randint(0, plan_length - 1)
        random_inxecutable_action = random.choice(self.inexecutable_actions[random_break_ind])
        corrupted_actions[random_break_ind] = random_inxecutable_action
        return corrupted_actions, random_break_ind

    def sequence_of_actions(self, plan_length, is_correct_sequence):
        if not is_correct_sequence:
            sequence_of_actions, random_break_ind = self.corrupt_action_sequence(plan_length)
        else:
            sequence_of_actions = self.given_plan_sequence[:plan_length]
            random_break_ind = random.randint(0, plan_length - 1)
        return sequence_of_actions, random_break_ind

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
        else:
            raise ValueError(f'Undefined fluent type {fluent_type}')
        return pos_fluents, neg_fluents

    def fluents_for_random_obj(self, plan_length, fluent_type, min_chosen_fluents=1, timeout=MAX_TIMEOUT):
        pos_fluents, neg_fluents = [], []
        while (len(pos_fluents) + len(neg_fluents)) < min_chosen_fluents and timeout > 0:
            obj = random.choice(self.all_objects)
            pos_fluents, neg_fluents = self.fluents_for_object_tracking(obj, plan_length, fluent_type)
            if len(pos_fluents) and len(neg_fluents):
                return pos_fluents, neg_fluents, obj
            timeout -= 1
        return None, None, None

    def sample_fluents(self, fluents):
        if len(fluents) == 0:
            raise ValueError('Empty list')
        elif len(fluents) == 1:
            num_samples = 1
        else:
            num_samples = random.randint(1, len(fluents) - 1)
        fluents = random.sample(fluents, num_samples)
        return self.corrupt_fluents(fluents)

    def fluent_helper(self, pos_fluents, neg_fluents, is_answer_true, is_pos_fluent_question=None):
        # TODO add sampling
        if not pos_fluents and not neg_fluents:
            return None

        if is_answer_true:
            if is_pos_fluent_question is True:
                return pos_fluents
            elif is_pos_fluent_question is False:
                return neg_fluents
            else:
                return pos_fluents + neg_fluents
        else:
            if is_pos_fluent_question is None:
                return self.corrupt_fluents(pos_fluents + neg_fluents)
            else:
                if not pos_fluents or not neg_fluents:
                    return None
                fluents = self.corrupt_fluents(pos_fluents) + self.corrupt_fluents(neg_fluents)
                if is_pos_fluent_question is True:
                    return [f if f[0] != '-' else f[1:] for f in fluents]
                else:
                    return [f if f[0] == '-' else '-' + f for f in fluents]



class QuestionGenerator(QuestionGenerationHelpers):
    digit_regex = '\d+'
    word_regex = '[a-zA-Z]+'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def qa_data_object(self, question, answer, answer_type, question_name, plan_length, fluent_type):
        return {OUT_OBJ_ID: str(uuid.uuid4()),
                OUT_OBJ_DOMAIN_NAME: self.domain_class.DOMAIN_NAME,
                OUT_OBJ_INSTANCE_ID: self.instance_id,
                OUT_OBJ_QUESTION_CATEGORY: self.QUESTION_CATEGORY,
                OUT_OBJ_QUESTION_NAME: question_name,
                OUT_OBJ_FLUENT_TYPE: fluent_type,
                OUT_OBJ_ANSWER_TYPE: answer_type,
                OUT_OBJ_QUESTION: question,
                OUT_OBJ_ANSWER: str(answer),
                OUT_OBJ_PLAN_LENGTH: plan_length,
                OUT_OBJ_INITIAL_STATE: self.init_state,
                OUT_OBJ_ACTION_SEQUENCE: self.given_plan_sequence}
        # OBOUT_OBJ_QUESTION_ID: question_id}

    @staticmethod
    def question_category():
        raise 'Implement it in the child class'

    @staticmethod
    def unique_questions(question_constructor, plan_length, multiplicity, timeout_outer=20, timeout_inner=3):
        results = {}
        while (len(results) < multiplicity) and timeout_outer > 0:
            qa_object = question_constructor(plan_length)
            while (qa_object is None) and timeout_inner > 0:
                qa_object = question_constructor(plan_length)
                timeout_inner -= 1
            if not qa_object:
                return []

            qa_id = (qa_object['question'], qa_object['answer'])
            results[qa_id] = qa_object
            timeout_outer -= 1
        if timeout_outer == 0:
            pass
            # warn_str = f'Timeout!!! {question_constructor} \n. plan_length: {plan_length} \n len(results): {len(results)}, \n multiplicity: {multiplicity} '
            # warnings.warn(warn_str)
        return list(results.values())

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY, plan_lengths=PLAN_LENGTHS):
        results = []
        for plan_length in plan_lengths:
            for question_constructor in self.question_iterators():
                results += self.unique_questions(question_constructor, plan_length, multiplicity)
        return results

    def question_iterators(self):
        # return []
        raise ValueError('Implement it in the child class')


class ObjectTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'object_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, fluent_type, is_pos_fluent_question, is_answer_true, question_name):
        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true, is_pos_fluent_question)
        if not fluents:
            return None
        nl_fluents = self.nl_fluents(fluents)
        # TODO add
        # q_id = unique_id((fluents, is_answer_true, question_name, is_answer_true))
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that the following {FLUENTS_NL} are correct for {obj}: {nl_fluents}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_pos_fluent_question in [True, False, None]:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_1_helper,
                                  fluent_type=fluent_type,
                                  is_pos_fluent_question=is_pos_fluent_question,
                                  is_answer_true=is_answer_true,
                                  question_name=question_name(counter, 'iter_1'))

    ########## Free Answer questions ##########

    def question_1(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        question = f"{self.nl_question_prefix(plan_length)} list all objects associated with type {random_object_type}. {NONE_STATEMENT}."
        answer = self.objects_by_type[random_object_type]
        nl_answer = asp_to_nl(sorted(answer), lambda x: x)
        return self.qa_data_object(question, nl_answer, FREE_ANSWER, self.question_1.__name__, plan_length,
                                   fluent_type=None)

    def question_2(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        random_objects = random.sample(self.objects_by_type[random_object_type],
                                       random.randint(1, len(self.objects_by_type[random_object_type])))
        nl_random_objects = asp_to_nl(random_objects, lambda x: x)
        question = f"{self.nl_question_prefix(plan_length)} what is the object type for {nl_random_objects}. {NONE_STATEMENT}."
        return self.qa_data_object(question, random_object_type, FREE_ANSWER, self.question_2.__name__, plan_length,
                                   fluent_type=None)

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     [self.question_1, self.question_2])


class FluentTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'fluent_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, fluent_type, is_pos_fluent_question, is_answer_true, question_name):
        pos_fluent, neg_fluent = self.fluents_for_fluent_type(plan_length, fluent_type)
        if len(pos_fluent) == 0 or len(neg_fluent) == 0:
            return None
        else:
            pos_fluent = random.choice(pos_fluent)
            neg_fluent = random.choice(neg_fluent)

        if is_pos_fluent_question and is_answer_true:
            fluent = pos_fluent
        elif is_pos_fluent_question and not is_answer_true:
            fluent = '-' + pos_fluent
        elif not is_pos_fluent_question and is_answer_true:
            fluent = neg_fluent
        else:
            fluent = neg_fluent[1:]
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {self.domain_class.fluent_to_natural_language(fluent)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_pos_fluent_question in [True, False, None]:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_1_helper,
                                  fluent_type=fluent_type,
                                  is_pos_fluent_question=is_pos_fluent_question,
                                  is_answer_true=is_answer_true,
                                  question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, fluent_type, is_pos_fluent_question, is_answer_true, question_name):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true, is_pos_fluent_question)
        if not fluents:
            return None
        question = f"{self.nl_question_prefix(plan_length)} are all of the following {FLUENTS_NL} {TRUE_OR_FALSE}: {self.nl_fluents(fluents)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_2(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_pos_fluent_question in [True, False, None]:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_2_helper,
                                  fluent_type=fluent_type,
                                  is_pos_fluent_question=is_pos_fluent_question,
                                  is_answer_true=is_answer_true,
                                  question_name=question_name(counter, 'iter_2'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_3_helper(self, plan_length, fluent_type, is_pos_fluent_question, question_name):
        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type=fluent_type)
        if pos_fluents is None and neg_fluents is None:
            return None

        question = (f"{self.nl_question_prefix(plan_length)}. "
                    f"What are the {fluent_type_to_fluent_nl(fluent_type)} for {obj}? "
                    f"{NONE_STATEMENT}")
        fluents = self.fluent_helper(pos_fluents, neg_fluents, True, is_pos_fluent_question)
        if not fluents:
            answer = 'None'
        else:
            answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_3(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_pos_fluent_question in [True, False, None]:
                counter += 1
                yield partial(self.questions_iter_3_helper,
                              fluent_type=fluent_type,
                              is_pos_fluent_question=is_pos_fluent_question,
                              question_name=question_name(counter, 'iter_3'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3())


class StateTrackingQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'state_tracking'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, is_answer_true, question_name):
        pos_fluents, neg_fluents = self.pos_fluents_given_plan[plan_length], self.neg_fluents_given_plan[plan_length]
        if exit_condition_on_fluents(pos_fluents, neg_fluents):
            return None
        fluents = pos_fluents + neg_fluents
        if not is_answer_true:
            fluents = self.corrupt_fluents(fluents)
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} are all of the following properties: {nl_fluents}, correct? Respond with {TRUE_OR_FALSE}."
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_1(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_1_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        if is_pos_fluent_question:
            fluent_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluent_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length]
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type_nl}. {NONE_STATEMENT}."
        return self.qa_data_object(question, nl_fluents, FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_2(self):
        counter = 0
        for is_pos_fluent_question in [True, False, None]:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_pos_fluent_question=is_pos_fluent_question,
                          question_name=question_name(counter, 'iter_2'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2())


class ActionExecutabilityQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'action_executability'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def questions_iter_1_helper(self, plan_length, is_answer_true, question_name):
        sequence_of_actions, _random_break_ind = self.sequence_of_actions(plan_length, is_answer_true)
        nl_sequence_of_actions = asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_sequence_of_actions}. Is it possible to execute it, {TRUE_OR_FALSE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_1(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_1_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, is_answer_true, question_name):
        sequence_of_actions, random_break_ind = self.sequence_of_actions(plan_length, is_answer_true)
        selected_action = sequence_of_actions[random_break_ind]

        nl_sequence_of_actions = self.nl_actions(sequence_of_actions)
        nl_selected_action = self.domain_class.action_to_natural_language(selected_action)
        question = f"{INITIAL_CONDITION_PREFIX}, for steps 1 through {plan_length} the following actions are planned to be performed: {nl_sequence_of_actions}. Is the action: {nl_selected_action} executable at step {random_break_ind + 1}, {TRUE_OR_FALSE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_2(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_2'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_3_helper(self, plan_length, is_answer_true, question_name):
        if not is_answer_true:
            question = (
                f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. "
                f"What is the first inexecutable action in the sequence? {NONE_STATEMENT}.")
            return self.qa_data_object(question, NONE_ANSWER, FREE_ANSWER, question_name, plan_length, None)
        else:
            sequence_of_actions, random_break_ind = self.corrupt_action_sequence(plan_length)
            inexecutable_action = sequence_of_actions[random_break_ind]
            question = (
                f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. "
                f"What is the first inexecutable action in the sequence? {NONE_STATEMENT}.")
            return self.qa_data_object(question, self.domain_class.action_to_natural_language(inexecutable_action),
                                       FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_3(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_3_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_3'))

    def question_4(self, plan_length):
        question = f"{self.nl_question_prefix(plan_length)} list all executable actions. {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_actions(self.executable_actions[plan_length]), FREE_ANSWER,
                                   self.question_4.__name__, plan_length, None)

    def question_5(self, plan_length):
        question = f"{self.nl_question_prefix(plan_length)} list all inexecutable actions. {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_actions(self.inexecutable_actions[plan_length]), FREE_ANSWER,
                                   self.question_5.__name__, plan_length, None)

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

    def questions_iter_1_helper(self, plan_length, fluent_type, is_answer_true, is_same_sample, question_name):
        action = self.given_plan_sequence[plan_length]
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents_current_state = set(pos_fluents).union(set(neg_fluents))

        next_pos_fluents, next_neg_fluents = self.fluents_for_fluent_type(plan_length + 1, fluent_type)
        fluents_next_state = set(next_pos_fluents).union(set(next_neg_fluents))
        fluents_new_minus_old = fluents_next_state - fluents_current_state

        if is_answer_true:
            fluents = fluents_new_minus_old
        else:
            if is_same_sample and fluents_new_minus_old:
                fluents = self.corrupt_fluents(list(fluents_new_minus_old))
            else:
                fluents_all = self.pos_fluents_given_plan + self.neg_fluents_given_plan
                fluents = self.corrupt_fluents([l for ls in fluents_all for l in ls])
                fluents = list(set(fluents) - fluents_new_minus_old)
                fluents = random.sample(fluents, len(fluents_new_minus_old))
        fluents = list(fluents)
        if not fluents:
            nl_fluents = f'no {FLUENTS_NL} change'
        else:
            nl_fluents = self.nl_fluents(fluents)
        question = f"{self.prefix(plan_length)} if {self.nl_actions([action])}, is it {TRUE_OR_FALSE} that {nl_fluents}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:
            for is_same_sample in [True, False]:
                for is_answer_true in [True, False]:
                    counter += 1
                    yield partial(self.questions_iter_1_helper,
                                  fluent_type=fluent_type,
                                  is_answer_true=is_answer_true,
                                  is_same_sample=is_same_sample,
                                  question_name=question_name(counter, 'iter_1'))

    #### FREE ANSWER QUESTIONS ####

    def questions_iter_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        action = self.given_plan_sequence[plan_length]
        if is_pos_fluent_question:
            fluents_type_nl = POSITIVE_FLUENTS_NL
            fluents = self.pos_fluents_given_plan[plan_length + 1]
        else:
            fluents_type_nl = NEGATIVE_FLUENTS_NL
            fluents = self.neg_fluents_given_plan[plan_length + 1]
        question = f"{self.prefix(plan_length)} if {self.nl_actions([action])}, what would be all of the {fluents_type_nl}? {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_fluents(fluents), FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_2(self):
        counter = 0
        for is_pos_fluent_question in [True, False, None]:
            counter += 1
            yield partial(self.questions_iter_2_helper,
                          is_pos_fluent_question=is_pos_fluent_question,
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
        return original_count + random.choice([random.randrange(-bound, 0), random.randrange(1, bound + 1)])

    def objects_count(self, plan_length):
        return {
            'objects': len(self.all_objects),
            'executable actions': len(self.executable_actions[plan_length]),
            'inexecutable actions': len(self.inexecutable_actions[plan_length]),
            POSITIVE_FLUENTS_NL: len(self.pos_fluents_given_plan[plan_length]),
            NEGATIVE_FLUENTS_NL: len(self.neg_fluents_given_plan[plan_length]),
            BASE_FLUENTS_NL: len(list(chain(self.fluents_for_fluent_type(plan_length, BASE_FLUENTS)))),
            DERIVED_FLUENTS_NL: len(list(chain(self.fluents_for_fluent_type(plan_length, DERIVED_FLUENTS)))),
            PERSISTENT_FLUENTS_NL: len(list(chain(self.fluents_for_fluent_type(plan_length, PERSISTENT_FLUENTS)))),
            STATIC_FLUENTS_NL: len(list(chain(self.fluents_for_fluent_type(plan_length, STATIC_FLUENTS))))
        }

    def questions_iter_1_helper(self, plan_length, is_answer_true, name_count, question_name):
        count = self.objects_count(plan_length)[name_count]
        if is_answer_true:
            total_count = count
        else:
            total_count = self.random_count(count)
        question = f"{self.nl_question_prefix(plan_length)} is the number of {name_count} equal to {total_count}? {TRUE_OR_FALSE}"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

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
        question = f"{self.nl_question_prefix(plan_length, is_planned=False)} what is the total number of {name_count}? Write as a decimal. {NONE_STATEMENT}."
        return self.qa_data_object(question, count, FREE_ANSWER, question_name, plan_length, None)

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
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_3(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_3_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_3'))

    def question_4(self, plan_length):
        sequence_of_actions, random_break_ind = self.corrupt_action_sequence(plan_length)
        prefix = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. In this state,"
        question = f"{prefix} what is the number of actions that led to the current state in the sequence before the first inexecutable action? Write as a decimal. {NONE_STATEMENT}."
        return self.qa_data_object(question, random_break_ind, FREE_ANSWER, self.question_4.__name__, plan_length, None)

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3(),
                     [self.question_4])


class HallucinationQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'hallucination'
    NUMBER_REGEX = f'\d'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_setup(self, stuff):
        return f'some {stuff} may or may not be defined'

    def hallucinated_object(self, object, other_objects_set=set()):
        all_objects = self.all_objects_set.union(other_objects_set)

        r = re.compile(self.NUMBER_REGEX)
        object_prefix = r.sub('', object)
        # if object == object_prefix:
        #     print('Error: object name does not contain a number')
        i = 1
        hallucinated_object = object_prefix + f'{i}'
        while hallucinated_object in all_objects and i < 100:
            hallucinated_object = object_prefix + f'{i}'
            i += 1
            if i == 100:
                raise 'timeout'
        return hallucinated_object

    def questions_iter_1_helper(self, plan_length, is_answer_true, question_name):
        object = random.choice(self.all_objects)
        if not is_answer_true:
            object = self.hallucinated_object(object)
        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. Is it {TRUE_OR_FALSE} that {object} is {PART_OF_THE_STATE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_1(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_1_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, is_answer_true, is_pos_fluent_question, fluent_type, question_name):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)

        if is_pos_fluent_question and pos_fluents:
            fluent = random.choice(pos_fluents)
        elif is_pos_fluent_question and neg_fluents:
            fluent = random.choice(neg_fluents)
        else:
            return None

        if is_answer_true:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluent)
        else:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluent, is_hallucinated=True)

        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup(FLUENTS_NL)}. Is it {TRUE_OR_FALSE} that {nl_fluent}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_2(self):
        counter = 0
        for is_answer_true in [True, False]:
            for is_pos_fluent_question in [True, False]:
                for fluent_type in FLUENT_TYPES_LIST:
                    counter += 1
                    yield partial(self.questions_iter_2_helper,
                                  is_answer_true=is_answer_true,
                                  is_pos_fluent_question=is_pos_fluent_question,
                                  fluent_type=fluent_type,
                                  question_name=question_name(counter, 'iter_2'))

    def questions_iter_3_helper(self, plan_length, is_executable_action, is_answer_true, question_name):
        if is_executable_action:
            action_type = 'executable'
            action = random.choice(self.executable_actions[plan_length])
        else:
            action_type = 'inexecutable'
            action = random.choice(self.inexecutable_actions[plan_length])

        if is_answer_true:
            nl_action = self.domain_class.action_to_natural_language(action)
        else:
            nl_action = self.domain_class.action_to_natural_language(action, is_hallucinated=True)

        question_setup = self.question_setup(f'{action_type} actions')
        question = f"{self.nl_question_prefix(plan_length, is_planned=True)} {question_setup}. Is it {TRUE_OR_FALSE} that action, {nl_action}, is defined?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_3(self):
        counter = 0
        for is_executable_action in [True, False]:
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_3_helper,
                              is_executable_action=is_executable_action,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_3'))

    def questions_iter_4_helper(self, plan_length, is_answer_true, question_name):
        if len(self.all_objects) < 2:
            print('less than 2 objects', question_name, plan_length)
            return None
        objects = random.sample(self.all_objects, random.randint(2, len(self.all_objects)))
        answer = objects[0]
        if not is_answer_true:
            objects[0] = self.hallucinated_object(objects[0])
            answer = objects[0]
        random.shuffle(objects)
        nl_objects = asp_to_nl(objects, lambda x: x)
        question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. "
                    f"Which of the following objects, {nl_objects}, is not defined? Write None if all are defined.")
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_4(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_4_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_4'))

    def questions_iter_5_helper(self, plan_length, is_pos_fluent_question, is_answer_true, fluent_type, question_name):
        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        lower_bound_rand_int = 2
        if is_pos_fluent_question is True and len(pos_fluents) >= lower_bound_rand_int:
            fluent_type_nl = POSITIVE_FLUENT_NL
            fluents = random.sample(pos_fluents, random.randint(lower_bound_rand_int, len(pos_fluents)))
        elif is_pos_fluent_question is False and len(neg_fluents) >= lower_bound_rand_int:
            fluent_type_nl = NEGATIVE_FLUENT_NL
            fluents = random.sample(neg_fluents, random.randint(lower_bound_rand_int, len(neg_fluents)))
        elif is_pos_fluent_question is None and len(pos_fluents + neg_fluents) >= lower_bound_rand_int:
            fluent_type_nl = FLUENTS_NL
            fluents = random.sample(pos_fluents + neg_fluents,
                                    random.randint(lower_bound_rand_int, len(pos_fluents + neg_fluents)))
        else:
            return None

        if is_answer_true:
            nl_hallucinated_fluent = NONE_ANSWER
            nl_fluents = self.nl_fluents(fluents)
        else:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluents[0])
            nl_hallucinated_fluent = self.domain_class.fluent_to_natural_language(fluents[0], is_hallucinated=True)
            random.shuffle(fluents)
            nl_fluents = self.nl_fluents(fluents).replace(nl_fluent, nl_hallucinated_fluent)
        question = (f"{self.nl_question_prefix(plan_length)} {self.question_setup(f'{fluent_type_nl}')}. "
                    f"What {fluent_type_nl} out of, {nl_fluents}, is not defined? Write None if all are defined.")
        return self.qa_data_object(question, nl_hallucinated_fluent, FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_5(self):
        counter = 0
        for is_pos_fluent_question in [True, False]:
            for is_answer_true in [True, False]:
                for fluent_type in FLUENT_TYPES_LIST:
                    counter += 1
                    yield partial(self.questions_iter_5_helper,
                                  is_pos_fluent_question=is_pos_fluent_question,
                                  is_answer_true=is_answer_true,
                                  fluent_type=fluent_type,
                                  question_name=question_name(counter, 'iter_5'))

    def questions_iter_6_helper(self, plan_length, is_answer_true, question_name):
        postfix = 'to reach the current state. Given this sequence, what action is not defined? Write None if all are defined'
        if is_answer_true:
            question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} {postfix}."
            answer = "None"
        else:
            actions = self.given_plan_sequence[:plan_length]
            random_int = random.randint(0, len(actions) - 1)
            nl_selected_action = self.domain_class.action_to_natural_language(actions[random_int])
            nl_hallucinated_action = self.domain_class.action_to_natural_language(actions[random_int],
                                                                                  is_hallucinated=True)
            nl_actions = self.nl_actions(actions).replace(nl_selected_action, nl_hallucinated_action)
            question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_actions} {postfix}."
            answer = nl_hallucinated_action
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, None)

    def questions_iter_6(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_6_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_6'))

    def question_iterators(self):
        return chain(self.questions_iter_1(),
                     self.questions_iter_2(),
                     self.questions_iter_3(),
                     self.questions_iter_4(),
                     self.questions_iter_5(),
                     self.questions_iter_6())


class CompositeQuestions(QuestionGenerator):
    QUESTION_CATEGORY = 'composite_questions'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def nl_question_prefix_custom(self, nl_actions, is_planned=False):
        if is_planned:
            prefix = ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX
        else:
            prefix = ACTIONS_ARE_PERFORMED_PREFIX
        return f"{prefix} {nl_actions} to reach the current state."

    def questions_iter_1_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        is_correct_sequence = False  # random.choice([True, False])
        actions, random_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)

        pos_fluents, neg_fluents = self.fluents_for_fluent_type(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
        if not fluents:
            return None
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"Are the following {FLUENTS_NL} true before the first infeasible action in the sequence? "
                    f"{self.nl_fluents(fluents)}. ")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_1(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_1_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_1'))

    def questions_iter_2_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        is_correct_sequence = False
        actions, random_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)
        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
        if not fluents:
            return None
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"Are the following {FLUENTS_NL} true for {obj} before the first infeasible action in the sequence? "
                    f"{self.nl_fluents(fluents)}. ")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_2(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_2_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_2'))

    def questions_iter_3_helper(self, plan_length, fluent_type, is_answer_true, question_name):
        actions = self.given_plan_sequence[:plan_length]
        action_performed = actions[plan_length]

        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type)
        fluents = self.fluent_helper(pos_fluents, neg_fluents, is_answer_true)
        if not fluents:
            return None
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"If I perform action {action_performed}, would the following {FLUENTS_NL} be true for {obj}? "
                    f"{self.nl_fluents(fluents)}. ")
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_3(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            for is_answer_true in [True, False]:
                counter += 1
                yield partial(self.questions_iter_3_helper,
                              fluent_type=fluent_type,
                              is_answer_true=is_answer_true,
                              question_name=question_name(counter, 'iter_3'))

    def questions_iter_4_helper(self, plan_length, is_answer_true, question_name):
        is_correct_sequence = False  # random.choice([True, False])
        actions, random_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)

        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    "Some of the actions may not be executable. "
                    f"Is this the state before the first infeasible action in the sequence? {TRUE_OR_FALSE}")
        state = self.pos_fluents_given_plan[random_action_i] + self.neg_fluents_given_plan[random_action_i]
        if not is_answer_true:
            state = self.corrupt_fluents(state)
        question += self.nl_fluents(state)
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length, None)

    def questions_iter_4(self):
        counter = 0
        for is_answer_true in [True, False]:
            counter += 1
            yield partial(self.questions_iter_4_helper,
                          is_answer_true=is_answer_true,
                          question_name=question_name(counter, 'iter_4'))

    # free answer questions

    def questions_iter_5_helper(self, plan_length, fluent_type, question_name):
        is_answer_true = random.choice([True, False])
        actions, random_action_i = self.sequence_of_actions(plan_length, is_answer_true)
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"Some of the actions may not be executable. "
                    f"What {fluent_type_to_fluent_nl(fluent_type)} are true before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_answer_true:
            answer = NONE_ANSWER
        else:
            fluents = self.fluents_for_fluent_type(random_action_i, fluent_type)
            answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_5(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            counter += 1
            yield partial(self.questions_iter_5_helper,
                          fluent_type=fluent_type,
                          question_name=question_name(counter, 'iter_5'))

    def questions_iter_6_helper(self, plan_length, fluent_type, question_name):
        is_answer_true = random.choice([True, False])
        actions, random_action_i = self.sequence_of_actions(plan_length, is_answer_true)

        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length, fluent_type=fluent_type)
        if pos_fluents is None and neg_fluents is None:
            return None

        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"What are the {fluent_type_to_fluent_nl(fluent_type)} for {obj} before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_answer_true:
            answer = NONE_ANSWER
        else:
            fluents = pos_fluents + pos_fluents
            answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_6(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            counter += 1
            yield partial(self.questions_iter_6_helper,
                          fluent_type=fluent_type,
                          question_name=question_name(counter, 'iter_6'))

    def questions_iter_7_helper(self, plan_length, fluent_type, question_name):
        actions = self.given_plan_sequence[:plan_length]
        action_performed = actions[plan_length]

        pos_fluents, neg_fluents, obj = self.fluents_for_random_obj(plan_length + 1, fluent_type)
        if pos_fluents is None and neg_fluents is None:
            return None

        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions))}. "
                    f"If I perform action {action_performed}, what would be all of the {fluent_type_to_fluent_nl(fluent_type)} for {obj}? "
                    f"{NONE_STATEMENT}")
        pos_fluents, pos_fluents = self.fluents_for_fluent_type(fluent_type)
        fluents = pos_fluents + pos_fluents
        answer = self.nl_fluents(fluents)
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, fluent_type)

    def questions_iter_7(self):
        counter = 0
        for fluent_type in FLUENT_TYPES_LIST:  # STATIC_FLUENTS
            counter += 1
            yield partial(self.questions_iter_7_helper,
                          fluent_type=fluent_type,
                          question_name=question_name(counter, 'iter_7'))

    def questions_iter_8_helper(self, plan_length, is_correct_sequence, question_name):
        actions, random_action_i = self.sequence_of_actions(plan_length, is_correct_sequence)
        question = (f"{self.nl_question_prefix_custom(self.nl_actions(actions), is_planned=True)}. "
                    f"Some of the actions may not be executable. "
                    f"What is the state before the first infeasible action in the sequence? "
                    f"{NONE_STATEMENT}")
        if is_correct_sequence:
            answer = NONE_ANSWER
        else:
            state = self.pos_fluents_given_plan[random_action_i] + self.neg_fluents_given_plan[random_action_i]
            answer = self.nl_fluents(state)
        return self.qa_data_object(question, answer, FREE_ANSWER, question_name, plan_length, None)

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
                     self.questions_iter_3(),
                     self.questions_iter_4(),
                     self.questions_iter_5(),
                     self.questions_iter_6(),
                     self.questions_iter_7(),
                     self.questions_iter_8())
