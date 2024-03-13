import os
import random
import re
import sys
import uuid
from collections import defaultdict
from copy import deepcopy

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from src.common import *

INITIAL_CONDITION_PREFIX = 'Given the initial condition'
ACTIONS_ARE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are performed:'
ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX = f'{INITIAL_CONDITION_PREFIX}, the following actions are planned to be performed:'
TRUE_OR_FALSE = 'True or False'
NONE_STATEMENT = 'Write None if there are none'
NONE_ANSWER = 'None'

# fluent names for QA
# POSITIVE_FLUENT = 'positive fluent'
# NEGATIVE_FLUENT = 'negative fluent'
# FLUENTS = 'fluents'
# POSITIVE_FLUENTS = 'positive fluents'
# NEGATIVE_FLUENTS = 'negative fluents'

# # fluent names for QA
# POSITIVE_FLUENT = 'true property of the world'
# NEGATIVE_FLUENT = 'true property of the world that involve a negation'
# FLUENTS = 'properties of the world that can be true or false'
# POSITIVE_FLUENTS = 'true properties of the world'
# NEGATIVE_FLUENTS = 'true properties of the world that involve a negation'

# # fluent names for QA
# POSITIVE_FLUENT = 'true property of the state'
# NEGATIVE_FLUENT = 'true property of the state that involves a negation'
# FLUENTS = 'properties of the state'
# POSITIVE_FLUENTS = 'true properties of the state'
# NEGATIVE_FLUENTS = 'true properties of the state that involve a negation'

# fluent names for QA
POSITIVE_FLUENT = 'valid property of the state'
NEGATIVE_FLUENT = 'valid property of the state that involves a negation'
FLUENTS = 'properties of the state'
POSITIVE_FLUENTS = 'valid properties of the state'
NEGATIVE_FLUENTS = 'valid properties of the state that involve negations'

PART_OF_THE_STATE = 'part of the state'
MAX_TIMEOUT = 100

OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
SUBSTRING_WITHIN_PARENTHESIS_REGEX = r'\([^)]*{}\w*[^)]*\)'

PLAN_LENGTHS = [1, 5, 10, 15, 19]
QUESTION_MULTIPLICITY = 4

# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import wordnet
# lemmatizer = WordNetLemmatizer()


def get_fluent_prefix(fluent):
    if fluent.find('(') == -1:
        return fluent
    return fluent[:fluent.find('(')]


def extract_variables(obj):
    match = re.search(OBJ_IN_PAREN_REGEX, obj)
    return match.group(1).split(',')


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


class QuestionGenerationHelpers:
    """ Generates QAs * multiplicity for a given domain, init cond + plan sequence"""
    ACTION_JOIN_STR = ', '

    def __init__(self, states_actions_all, domain_class, instance_id):
        self.states_actions_all = states_actions_all
        # self.data[i] defines all action->states at time i, i==0 is NULL->initial state
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

    def get_random_inexecutable_sequence(self, plan_length):
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

    def fluents_for_obj(self, obj, plan_length, is_true_fluents=True):
        fluents_for_object = []
        if is_true_fluents:
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluents = self.neg_fluents_given_plan[plan_length]
        for fluent in fluents:
            if self.is_substring_within_parentheses(fluent, obj):
                fluents_for_object.append(fluent)
        return fluents_for_object

    def pos_fluents_for_object(self, obj, plan_length):
        return self.fluents_for_obj(obj, plan_length, is_true_fluents=True)

    def neg_fluents_for_object(self, obj, plan_length):
        return self.fluents_for_obj(obj, plan_length, is_true_fluents=False)

    def object_type_by_object_name(self):
        by_object_name = {}
        for obj_type, objects in self.objects_by_type.items():
            for obj in objects:
                by_object_name[obj] = obj_type
        return by_object_name

    def nl_fluents(self, fluents, fluent_subs=None):
        return asp_to_nl(fluents, self.domain_class.fluent_to_natural_language, fluent_subs=fluent_subs)

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
        final_length = len(not_corrupted_fluents)
        len_corrupted_fluents = len(corrupted_fluents)

        if len_corrupted_fluents == 0:
            raise 'Empty list'
        elif final_length in (0, 1) or len_corrupted_fluents == 1:
            num_to_be_corrupted_samples = 1
        else:
            num_to_be_corrupted_samples = random.randint(1, min(len_corrupted_fluents, final_length) - 1)
        corrupted_fluents_samples = random.sample(corrupted_fluents, num_to_be_corrupted_samples)
        return corrupted_fluents_samples + not_corrupted_fluents[:final_length - len(corrupted_fluents_samples)]

    def pos_neg_true_corrupted_fluents(self, is_pos_fluent_question, is_answer_true, pos_fluents, neg_fluents):
        if is_pos_fluent_question:
            if is_answer_true:
                fluents = pos_fluents
            else:
                fluents = self.corrupted_not_corrupted_mix(pos_fluents,
                                                           [f[1:] for f in neg_fluents])  # remove the '-' sign
        else:
            if is_answer_true:
                fluents = neg_fluents
            else:
                fluents = self.corrupted_not_corrupted_mix(neg_fluents,
                                                           [f"-{f}" for f in pos_fluents])  # add the '-' sign
        return fluents


class QuestionGenerator(QuestionGenerationHelpers):
    digit_regex = '\d+'
    word_regex = '[a-zA-Z]+'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def qa_data_object(self, question, answer, answer_type, question_name, plan_length):
        return {OUT_OBJ_ID: str(uuid.uuid4()),
                OUT_OBJ_DOMAIN_NAME: self.domain_class.DOMAIN_NAME,
                OUT_OBJ_INSTANCE_ID: self.instance_id,
                OUT_OBJ_QUESTION_CATEGORY: self.question_category(),
                OUT_OBJ_QUESTION_NAME: question_name,
                OUT_OBJ_ANSWER_TYPE: answer_type,
                OUT_OBJ_QUESTION: question,
                OUT_OBJ_ANSWER: str(answer),
                OUT_OBJ_PLAN_LENGTH: plan_length,
                OUT_OBJ_INITIAL_STATE: self.init_state,
                OUT_OBJ_ACTION_SEQUENCE: self.given_plan_sequence}

    @staticmethod
    def question_category():
        raise 'Implement it in the child class'

    @staticmethod
    def unique_questions(question_constructor, plan_length, multiplicity, timeout=100):
        results = {}
        while (len(results) < multiplicity) and timeout > 0:
            qa_object = question_constructor(plan_length)
            if not qa_object:
                return []

            qa_id = (qa_object['question'], qa_object['answer'])
            results[qa_id] = qa_object
            timeout -= 1
        if timeout == 0:
            pass
            # warn_str = f'Timeout!!! {question_constructor} \n. plan_length: {plan_length} \n len(results): {len(results)}, \n multiplicity: {multiplicity} '
            # warnings.warn(warn_str)
        return list(results.values())

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY, plan_lengths=PLAN_LENGTHS):
        results = []
        for plan_length in plan_lengths:
            for question_constructor in self.question_constructors():
                results += self.unique_questions(question_constructor, plan_length, multiplicity)
        return results

    def question_constructors(self):
        return [self.question_1,
                self.question_2,
                self.question_3,
                self.question_4,
                self.question_5,
                self.question_6,
                self.question_7,
                self.question_8,
                self.question_9,
                self.question_10,
                self.question_11,
                self.question_12,
                self.question_13,
                self.question_14,
                self.question_15]

    def question_1(self, plan_length):
        return None

    def question_2(self, plan_length):
        return None

    def question_3(self, plan_length):
        return None

    def question_4(self, plan_length):
        return None

    def question_5(self, plan_length):
        return None

    def question_6(self, plan_length):
        return None

    def question_7(self, plan_length):
        return None

    def question_8(self, plan_length):
        return None

    def question_9(self, plan_length):
        return None

    def question_10(self, plan_length):
        return None

    def question_11(self, plan_length):
        return None

    def question_12(self, plan_length):
        return None

    def question_13(self, plan_length):
        return None

    def question_14(self, plan_length):
        return None

    def question_15(self, plan_length):
        return None


class ObjectTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'object_tracking'

    @staticmethod
    def is_variable_in_fluent(fluent):
        return ('(' in fluent) and (')' in fluent)

    @staticmethod
    def select_fluents_with_vars(fluents):
        return [f for f in fluents if ObjectTrackingQuestions.is_variable_in_fluent(f)]

    def question_1_2_helper(self, plan_length, is_pos_fluent_question, is_answer_true, min_chosen_fluents=1,
                            timeout=MAX_TIMEOUT):
        chosen_fluents = []
        while len(chosen_fluents) < min_chosen_fluents and timeout > 0:
            obj = random.choice(self.all_objects)
            pos_fluents = self.pos_fluents_for_object(obj, plan_length)
            neg_fluents = self.neg_fluents_for_object(obj, plan_length)
            if not (len(pos_fluents) and len(neg_fluents)):
                continue
            fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, pos_fluents,
                                                          neg_fluents)
            if min_chosen_fluents <= len(fluents):
                num_samples = random.randint(min_chosen_fluents, len(fluents))
                chosen_fluents = random.sample(fluents, num_samples)
            timeout -= 1
        if timeout == 0:
            raise 'Timeout error'
        nl_fluents = self.nl_fluents(chosen_fluents)
        return f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {nl_fluents}?"

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        is_answer_true = random.choice([True, False])
        question = self.question_1_2_helper(plan_length, is_pos_fluent_question, is_answer_true)
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_1.__name__, plan_length)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        is_answer_true = random.choice([True, False])
        question = self.question_1_2_helper(plan_length, is_pos_fluent_question, is_answer_true)
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_2.__name__, plan_length)

    def question_3(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        question = f"{self.nl_question_prefix(plan_length)} list all objects associated with type {random_object_type}. {NONE_STATEMENT}."
        answer = self.objects_by_type[random_object_type]
        nl_answer = asp_to_nl(sorted(answer), lambda x: x)
        return self.qa_data_object(question, nl_answer, FREE_ANSWER, self.question_3.__name__, plan_length)

    def question_4(self, plan_length):
        random_object_type = random.choice(list(self.objects_by_type.keys()))
        random_objects = random.sample(self.objects_by_type[random_object_type], random.randint(1, len(self.objects_by_type[random_object_type])))
        nl_random_objects = asp_to_nl(random_objects, lambda x: x)
        question = f"{self.nl_question_prefix(plan_length)} what is the object type for {nl_random_objects}. {NONE_STATEMENT}."
        return self.qa_data_object(question, random_object_type, FREE_ANSWER, self.question_4.__name__, plan_length)



class FluentTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'fluent_tracking'

    def qa_1_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        is_answer_true = random.choice([True, False])
        pos_fluent = random.choice(self.pos_fluents_given_plan[plan_length])
        neg_fluent = random.choice(self.neg_fluents_given_plan[plan_length])
        fluent = \
            self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, [pos_fluent], [neg_fluent])[0]
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {self.domain_class.fluent_to_natural_language(fluent)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def qa_3_4_helper(self, plan_length, is_pos_fluent_question, question_name):
        is_answer_true = random.choice([True, False])
        fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true,
                                                      self.pos_fluents_given_plan[plan_length],
                                                      self.neg_fluents_given_plan[plan_length])
        question = f"{self.nl_question_prefix(plan_length)} are all of the following {FLUENTS} {TRUE_OR_FALSE}: {self.nl_fluents(fluents)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def qa_5_6_helper(self, plan_length, is_pos_fluent_question, question_name, timeout=MAX_TIMEOUT):
        fluents = []
        while not fluents:
            obj = random.choice(self.all_objects)
            # obj_type = self.object_type_by_object_name[obj]
            if is_pos_fluent_question:
                fluent_type = POSITIVE_FLUENTS
                fluents = self.pos_fluents_for_object(obj, plan_length)
            else:
                fluent_type = NEGATIVE_FLUENTS
                fluents = self.neg_fluents_for_object(obj, plan_length)
            timeout -= 1
        if timeout == 0:
            raise 'Timeout error'
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type} that involve {obj}. {NONE_STATEMENT}."
        return self.qa_data_object(question, nl_fluents, FREE_ANSWER, question_name, plan_length)

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question, self.question_1.__name__)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question, self.question_2.__name__)

    def question_3(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question, self.question_3.__name__)

    def question_4(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question, self.question_4.__name__)

    def question_5(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_5_6_helper(plan_length, is_pos_fluent_question, self.question_5.__name__)

    def question_6(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_5_6_helper(plan_length, is_pos_fluent_question, self.question_6.__name__)


class StateTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'state_tracking'

    def qa_1_2_helper(self, plan_length, is_pos_fluent_question, question_name):
        is_answer_true = random.choice([True, False])
        pos_fluents = self.pos_fluents_given_plan[plan_length]
        neg_fluents = self.neg_fluents_given_plan[plan_length]
        fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, pos_fluents, neg_fluents)
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} are all of the following properties: {nl_fluents}, correct? Respond with {TRUE_OR_FALSE}."
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def qa_3_4_helper(self, plan_length, is_pos_fluent_question, question_name):
        if is_pos_fluent_question:
            fluent_type = POSITIVE_FLUENTS
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluent_type = NEGATIVE_FLUENTS
            fluents = self.neg_fluents_given_plan[plan_length]
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type}. {NONE_STATEMENT}."
        return self.qa_data_object(question, nl_fluents, FREE_ANSWER, question_name, plan_length)

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question, self.question_1.__name__)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question, self.question_2.__name__)

    def question_3(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question, self.question_3.__name__)

    def question_4(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question, self.question_4.__name__)


def corrupt_action_sequence(true_actions, inexecutable_actions_timestep, plan_length):
    corrupted_actions = deepcopy(true_actions)
    random_break_ind = random.randint(0, plan_length - 1)
    random_inxecutable_action = random.choice(inexecutable_actions_timestep[random_break_ind])
    corrupted_actions[random_break_ind] = random_inxecutable_action
    return corrupted_actions, random_break_ind


class ActionExecutabilityQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'action_executability'

    def qa_1_2_helper(self, nl_sequence_of_actions):
        return

    def question_1(self, plan_length):
        is_answer_true = random.choice([True, False])
        if not is_answer_true:
            sequence_of_actions, random_break_ind = corrupt_action_sequence(self.given_plan_sequence[:plan_length],
                                                                            self.inexecutable_actions, plan_length)
        else:
            sequence_of_actions = self.given_plan_sequence[:plan_length]
        nl_sequence_of_actions = asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_sequence_of_actions}. Is it possible to execute it, {TRUE_OR_FALSE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_1.__name__, plan_length)

    def question_2(self, plan_length):
        is_answer_true = random.choice([True, False])
        if not is_answer_true:
            sequence_of_actions, random_break_ind = corrupt_action_sequence(self.given_plan_sequence[:plan_length], self.inexecutable_actions, plan_length)
        else:
            sequence_of_actions = self.given_plan_sequence[:plan_length]
            random_break_ind = random.randint(0, plan_length - 1)
        selected_action = sequence_of_actions[random_break_ind]

        nl_sequence_of_actions = self.nl_actions(sequence_of_actions)
        nl_selected_action = self.domain_class.action_to_natural_language(selected_action)
        question = f"{INITIAL_CONDITION_PREFIX}, for steps 1 through {plan_length} the following actions are planned to be performed: {nl_sequence_of_actions}. Is the action: {nl_selected_action} executable at step {random_break_ind + 1}, {TRUE_OR_FALSE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_2.__name__, plan_length)

    def question_3(self, plan_length):
        question = f"{self.nl_question_prefix(plan_length)} list all executable actions. {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_actions(self.executable_actions[plan_length]), FREE_ANSWER,
                                   self.question_3.__name__, plan_length)

    def question_4(self, plan_length):
        question = f"{self.nl_question_prefix(plan_length)} list all inexecutable actions. {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_actions(self.inexecutable_actions[plan_length]), FREE_ANSWER,
                                   self.question_4.__name__, plan_length)

    def question_5(self, plan_length):
        is_answer_true = random.choice([True, False])
        if not is_answer_true:
            question = f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. What is the first inexecutable action in the sequence? {NONE_STATEMENT}."
            return self.qa_data_object(question, NONE_ANSWER, FREE_ANSWER, self.question_5.__name__, plan_length)
        else:
            sequence_of_actions, random_break_ind = corrupt_action_sequence(self.given_plan_sequence[:plan_length],
                                                                            self.inexecutable_actions, plan_length)
            inexecutable_action = sequence_of_actions[random_break_ind]
            question = f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. What is the first inexecutable action in the sequence? {NONE_STATEMENT}."
            return self.qa_data_object(question, self.domain_class.action_to_natural_language(inexecutable_action),
                                       FREE_ANSWER, self.question_5.__name__, plan_length)


class EffectsQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'effects'

    def prefix(self, plan_length):
        if plan_length == 0:
            return f"{INITIAL_CONDITION_PREFIX},"
        else:
            return f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def qa_1_2_helper(self, plan_length, is_answer_true, question_name):
        action = self.given_plan_sequence[plan_length]
        fluents_current_state = set(self.pos_fluents_given_plan[plan_length]).union(set(self.neg_fluents_given_plan[plan_length]))
        fluents_next_state = set(self.pos_fluents_given_plan[plan_length + 1]).union(set(self.neg_fluents_given_plan[plan_length + 1]))
        fluents_new_minus_old = fluents_next_state - fluents_current_state
        if is_answer_true:
            fluents = fluents_new_minus_old
        else:
            fluents_all = self.pos_fluents_given_plan + self.neg_fluents_given_plan
            corrupted_fluents = set([l for ls in fluents_all for l in ls]) - fluents_new_minus_old
            fluents = self.corrupted_not_corrupted_mix(list(fluents_new_minus_old), list(corrupted_fluents))
            fluents = random.sample(fluents, len(fluents_new_minus_old))

        fluents = list(fluents)
        random.shuffle(fluents)
        question = f"{self.prefix(plan_length)} if {self.nl_actions([action])}, is it {TRUE_OR_FALSE} that {self.nl_fluents(fluents)}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def qa_3_4_helper(self, plan_length, is_positive_fluents_question, question_name):
        action = self.given_plan_sequence[plan_length]
        if is_positive_fluents_question:
            fluents_type = POSITIVE_FLUENTS
            fluents = self.pos_fluents_given_plan[plan_length + 1]
        else:
            fluents_type = NEGATIVE_FLUENTS
            fluents = self.neg_fluents_given_plan[plan_length + 1]
        question = f"{self.prefix(plan_length)} if {self.nl_actions([action])}, what would be all of the {fluents_type}? {NONE_STATEMENT}."
        return self.qa_data_object(question, self.nl_fluents(fluents), FREE_ANSWER, question_name, plan_length)

    def question_1(self, plan_length):
        return self.qa_1_2_helper(plan_length, True, self.question_1.__name__)

    def question_2(self, plan_length):
        return self.qa_1_2_helper(plan_length, False, self.question_2.__name__)

    def question_3(self, plan_length):
        is_positive_fluents_question = True
        return self.qa_3_4_helper(plan_length, is_positive_fluents_question, self.question_3.__name__)

    def question_4(self, plan_length):
        is_positive_fluents_question = False
        return self.qa_3_4_helper(plan_length, is_positive_fluents_question, self.question_4.__name__)


class NumericalReasoningQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'numerical_reasoning'

    @staticmethod
    def random_count(original_count):
        bound = int(0.2 * original_count) + 1
        return original_count + random.choice([random.randrange(-bound, 0), random.randrange(1, bound + 1)])

    def true_false_qa_helper(self, plan_length, is_answer_true, name_count, count, question_name):
        if is_answer_true:
            total_count = count
        else:
            total_count = self.random_count(count)
        question = f"{self.nl_question_prefix(plan_length)} is the number of {name_count} equal to {total_count}? {TRUE_OR_FALSE}"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def free_answer_qa_helper(self, plan_length, name_count, count, question_name, is_planned=False):
        question = f"{self.nl_question_prefix(plan_length, is_planned=is_planned)} what is the total number of {name_count}? Write as a decimal. {NONE_STATEMENT}."
        return self.qa_data_object(question, count, FREE_ANSWER, question_name, plan_length)

    def question_1(self, plan_length):
        is_answer_true = random.choice([True, False])
        total_objects = len(self.all_objects)
        return self.true_false_qa_helper(plan_length, is_answer_true, 'objects', total_objects, self.question_1.__name__)

    def question_2(self, plan_length):
        is_answer_true = random.choice([True, False])
        actions_count = len(self.executable_actions[plan_length])
        return self.true_false_qa_helper(plan_length, is_answer_true, 'executable actions', actions_count, self.question_2.__name__)

    def question_3(self, plan_length):
        is_answer_true = random.choice([True, False])
        actions_count = len(self.inexecutable_actions[plan_length])
        return self.true_false_qa_helper(plan_length, is_answer_true, 'inexecutable actions', actions_count, self.question_3.__name__)

    def question_4(self, plan_length):
        is_answer_true = random.choice([True, False])
        if is_answer_true:
            total_count = plan_length
        else:
            total_count = self.random_count(plan_length)
        question = f"{ACTIONS_ARE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} to reach the current state. Is it {TRUE_OR_FALSE} that the number of actions that led to current state in the sequence is equal to {total_count}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_4.__name__, plan_length)

    def question_5(self, plan_length):
        name_count = 'objects'
        count = len(self.all_objects)
        return self.free_answer_qa_helper(plan_length, name_count, count, self.question_5.__name__)

    def question_6(self, plan_length):
        name_count = POSITIVE_FLUENTS
        count = len(self.pos_fluents_given_plan[plan_length])
        return self.free_answer_qa_helper(plan_length, name_count, count, self.question_6.__name__)

    def question_7(self, plan_length):
        name_count = NEGATIVE_FLUENTS
        count = len(self.neg_fluents_given_plan[plan_length])
        return self.free_answer_qa_helper(plan_length, name_count, count, self.question_7.__name__)

    def question_8(self, plan_length):
        name_count = 'executable actions'
        count = len(self.executable_actions[plan_length])
        return self.free_answer_qa_helper(plan_length, name_count, count, self.question_8.__name__, is_planned=True)

    def question_9(self, plan_length):
        name_count = 'inexecutable actions'
        count = len(self.inexecutable_actions[plan_length])
        return self.free_answer_qa_helper(plan_length, name_count, count, self.question_9.__name__, is_planned=True)

    def question_10(self, plan_length):
        sequence_of_actions, random_break_ind = corrupt_action_sequence(self.given_plan_sequence[:plan_length],
                                                                        self.inexecutable_actions, plan_length)
        prefix = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions(sequence_of_actions)} to reach the current state. In this state,"
        question = f"{prefix} what is the number of actions that led to the current state in the sequence before the first inexecutable action? Write as a decimal. {NONE_STATEMENT}."

        return self.qa_data_object(question, random_break_ind, FREE_ANSWER, self.question_10.__name__, plan_length)


class HallucinationQuestions(QuestionGenerator):
    NUMBER_REGEX = f'\d'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    @staticmethod
    def question_category():
        return 'hallucination'

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

    def question_1(self, plan_length):
        is_answer_true = random.choice([True, False])
        object = random.choice(self.all_objects)
        if not is_answer_true:
            object = self.hallucinated_object(object)
        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. Is it {TRUE_OR_FALSE} that {object} is {PART_OF_THE_STATE}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, self.question_1.__name__, plan_length)

    def qa_2_3_helper(self, plan_length, is_pos_fluent_question, question_name):
        if is_pos_fluent_question:
            fluent = random.choice(self.pos_fluents_given_plan[plan_length])
        else:
            fluent = random.choice(self.neg_fluents_given_plan[plan_length])

        is_answer_true = random.choice([True, False])
        if is_answer_true:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluent)
        else:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluent, is_hallucinated=True)

        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup(FLUENTS)}. Is it {TRUE_OR_FALSE} that {nl_fluent}?"
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def qa_4_5_helper(self, plan_length, is_executable_action, question_name):
        is_answer_true = random.choice([True, False])
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
        return self.qa_data_object(question, is_answer_true, TRUE_FALSE_ANSWER, question_name, plan_length)

    def question_2(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_2_3_helper(plan_length, is_pos_fluent_question, self.question_2.__name__)

    def question_3(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_2_3_helper(plan_length, is_pos_fluent_question, self.question_3.__name__)

    def question_4(self, plan_length):
        is_executable_action = True
        return self.qa_4_5_helper(plan_length, is_executable_action, self.question_4.__name__)

    def question_5(self, plan_length):
        is_executable_action = False
        return self.qa_4_5_helper(plan_length, is_executable_action, self.question_5.__name__)

    def question_6(self, plan_length):
        is_answer_true = random.choice([True, False])
        if len(self.all_objects) < 2:
            print('less than 2 objects', self.question_6.__name__, plan_length)
            return None
        objects = random.sample(self.all_objects, random.randint(2, len(self.all_objects)))
        answer = objects[0]
        if not is_answer_true:
            objects[0] = self.hallucinated_object(objects[0])
            answer = objects[0]
        random.shuffle(objects)
        nl_objects = asp_to_nl(objects, lambda x: x)
        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup('objects')}. Which of the following objects, {nl_objects}, is not defined? Write None if all are defined."
        return self.qa_data_object(question, answer, FREE_ANSWER, self.question_6.__name__, plan_length)

    def qa_7_8_helper(self, plan_length, is_pos_fluent_question, is_answer_true, question_name):
        if is_pos_fluent_question:
            fluent_type = POSITIVE_FLUENT
            fluents = random.sample(self.pos_fluents_given_plan[plan_length],
                                    random.randint(2, len(self.pos_fluents_given_plan[plan_length])))
        else:
            fluent_type = NEGATIVE_FLUENT
            fluents = random.sample(self.neg_fluents_given_plan[plan_length],
                                    random.randint(2, len(self.neg_fluents_given_plan[plan_length])))
        if is_answer_true:
            nl_hallucinated_fluent = NONE_ANSWER
            nl_fluents = self.nl_fluents(fluents)
        else:
            nl_fluent = self.domain_class.fluent_to_natural_language(fluents[0])
            nl_hallucinated_fluent = self.domain_class.fluent_to_natural_language(fluents[0], is_hallucinated=True)
            random.shuffle(fluents)
            nl_fluents = self.nl_fluents(fluents).replace(nl_fluent, nl_hallucinated_fluent)
        question = f"{self.nl_question_prefix(plan_length)} {self.question_setup(f'{fluent_type}')}. What {fluent_type} out of, {nl_fluents}, is not defined? Write None if all are defined."
        return self.qa_data_object(question, nl_hallucinated_fluent, FREE_ANSWER, question_name, plan_length)

    def question_7(self, plan_length):
        is_pos_fluent_question = True
        is_answer_true = random.choice([True, False])
        return self.qa_7_8_helper(plan_length, is_pos_fluent_question, is_answer_true, self.question_7.__name__)

    def question_8(self, plan_length):
        is_pos_fluent_question = False
        is_answer_true = random.choice([True, False])
        return self.qa_7_8_helper(plan_length, is_pos_fluent_question, is_answer_true, self.question_8.__name__)

    def question_9(self, plan_length):
        is_answer_true = random.choice([True, False])
        postfix = 'to reach the current state. Given this sequence, what action is not defined? Write None if all are defined'
        if is_answer_true:
            question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {self.nl_actions_up_to(plan_length)} {postfix}."
            answer = "None"
        if not is_answer_true:
            actions = self.given_plan_sequence[:plan_length]
            random_int = random.randint(0, len(actions) - 1)
            nl_selected_action = self.domain_class.action_to_natural_language(actions[random_int])
            nl_hallucinated_action = self.domain_class.action_to_natural_language(actions[random_int], is_hallucinated=True)
            nl_actions = self.nl_actions(actions).replace(nl_selected_action, nl_hallucinated_action)
            question = f"{ACTIONS_ARE_PLANNED_TO_BE_PERFORMED_PREFIX} {nl_actions} {postfix}."
            answer = nl_hallucinated_action
        return self.qa_data_object(question, answer, FREE_ANSWER, self.question_8.__name__, plan_length)

# class LoopingQuestions(QuestionGenerator):
#     def __init__(self, states_actions_all, domain_class, instance_id):
#         super().__init__(states_actions_all, domain_class, instance_id)
#
#     @staticmethod
#     def question_category():
#         return 'looping'
#
#     def get_looping_action_sequence(self, plan, seq, key):
#         fluents = seq
#         last_action = plan[-1]
#         # print(fluents)
#         print(last_action)
#         if last_action.startswith('action_unstack('):
#             block = self.extract_multi_variable(last_action)[0]
#             if key == True:
#                 string_repeat_number = random.choice([2, 4, 6, 8, 10])
#                 random_action = [f"put_down({block})", f"pick_up({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 # print(actions)
#                 # exit()
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 # print(action_strings)
#                 # exit()
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = True
#                 answer_string = 'on the table'
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result, answer_string
#             elif key == False:
#                 string_repeat_number = random.choice([3, 5, 7, 9, 11])
#                 random_action = [f"put_down({block})", f"pick_up({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = False
#                 answer_string = 'in the hand'
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result, answer_string
#         elif last_action.startswith('action_stack('):
#             block1, block2 = self.extract_multi_variable(last_action)
#             if key == True:
#                 string_repeat_number = random.choice([2, 4, 6, 8, 10])
#                 random_action = [f"unstack({block1},{block2})", f"stack({block1},{block2})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block1} be on block {block2}?"
#                 answer = True
#                 answer_string = f'on block {block2}'
#                 question_without_result = f"will the block {block1} be on block {block2}?"
#                 return question, answer, random_action, question_without_result
#             elif key == False:
#                 string_repeat_number = random.choice([3, 5, 7, 9, 11])
#                 random_action = [f"unstack({block1},{block2})", f"stack({block1},{block2})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block1} be on block {block2}?"
#                 answer = False
#                 question_without_result = f"will the block {block1} be on block {block2}?"
#                 return question, answer, random_action, question_without_result
#         elif last_action.startswith('action_put_down('):
#             block = self.extract_single_variable(last_action)
#             if key == True:
#                 string_repeat_number = random.choice([2, 4, 6, 8, 10])
#                 random_action = [f"pick_up({block})", f"put_down({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = True
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result
#             elif key == False:
#                 string_repeat_number = random.choice([3, 5, 7, 9, 11])
#                 random_action = [f"pick_up({block})", f"put_down({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = False
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result
#         elif last_action.startswith('action_pick_up('):
#             block = self.extract_single_variable(last_action)
#             if key == True:
#                 string_repeat_number = random.choice([2, 4, 6, 8, 10])
#                 random_action = [f"put_down({block})", f"pick_up({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ' then' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = True
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result
#             elif key == False:
#                 string_repeat_number = random.choice([3, 5, 7, 9, 11])
#                 random_action = [f"put_down({block})", f"pick_up({block})"]
#                 looping_actions = []
#                 for i in range(0, string_repeat_number):
#                     if i % 2 == 0:
#                         looping_actions.append(random_action[0])
#                     else:
#                         looping_actions.append(random_action[1])
#                 actions = [self.action_to_natural_language(a) for a in looping_actions]
#                 action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in
#                                   enumerate(actions)]
#                 result = ''.join(action_strings)
#                 question = f"{result}, will the block {block} be on table?"
#                 answer = False
#                 question_without_result = f"will the block {block} be on table?"
#                 return question, answer, random_action, question_without_result
#

# class CompositeQuestions(DomainQuestionGen):
#         def __init__(self, states_actions_jsonl_path, instance_id):
#             super().__init__(states_actions_jsonl_path, instance_id)

#         @staticmethod
#     def question_category():
#             return 'ObjectTracking'

#         def question_1(self, plan_length):

#           true_fluents = self.given_fluent_sequence[plan_length+1]
# random_index = random.randint(0, true_fluents - 1)
#             inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join(
#                 [self.action_to_natural_language(action) for action in inexecutable_sequence])
#             questions = [
#                 f'Given the initial state, I plan to execute the following sequence of actions: {inexecutable_sequence_nlp}, what will be the state before the first inexecutable action occurs? If there are None, answer "None"',
#                 f'Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, what is the state before the first inexecutable action? If there are None, answer "None"',
#             ]
#             question = self.question_phrasing_choice(questions)
#             answer = self.fluents_from_optimal_sequence[inexecutable_action_index - 1]

#             return self.qa_data_object(self.composite_question_1.__name__, FREE_ANSWER, question, answer)
