import json
import random
import uuid
from src.states_actions_generation import *
from collections import defaultdict

# import nltk
# nltk.download('omw-1.4')
# nltk.download('popular')
# from pattern.en import pluralize


# import sys
# from ..common import *
# import re


TRUE_OR_FALSE = 'True or False'
NONE_STATEMENT = 'Write None if there are none'
MAX_TIMEOUT = 100

OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
SUBSTRING_WITHIN_PARENTHESIS_REGEX = r'\([^)]*{}\w*[^)]*\)'
PLAN_LENGTHS = [1,5,10,15,20]


def extract_single_variable(obj):
    return re.findall(OBJ_IN_PAREN_REGEX, obj)[0]


def extract_variables(obj):
    if ',' not in obj:
        return extract_single_variable(obj)
    match = re.search(OBJ_IN_PAREN_REGEX, obj)
    return match.group(1).split(',')


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
        self.domain_class = domain_class
        self.states_actions = self.states_actions_all[1:]
        self.instance_id = instance_id
        self.given_plan_sequence = self.extract_given_plan_sequence()
        self.pos_fluents_given_plan = self.extract_fluents_for_given_plan()
        self.neg_fluent_given_plan = self.extract_fluents_for_given_plan(NEG_FLUENTS_KEY)
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

    def is_action_executable(self, state_info):
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

    def is_substring_within_parentheses(self, input_string, substring):
        pattern = re.compile(SUBSTRING_WITHIN_PARENTHESIS_REGEX.format(re.escape(substring)))
        return bool(pattern.search(input_string))

    def is_variable_in_fluent(self, fluent):
        return '(' in fluent and ')' in fluent

    def fluents_for_obj(self, obj, plan_length, is_true_fluents=True):
        fluents_for_object = []
        if is_true_fluents:
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluents = self.neg_fluent_given_plan[plan_length]
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

    def asp_to_nl(self, obj_ls, converter, fluent_subs=None):
        and_str = ' and '
        comma_str = ', '
        if not obj_ls:
            raise 'Empty list'
        if len(obj_ls) <= 1:
            nl_obj = converter(obj_ls[0])
            if fluent_subs:
                nl_obj = nl_obj.replace(fluent_subs[0], fluent_subs[1])
            return nl_obj
        nl_obj_ls = [converter(f) for f in obj_ls]
        if fluent_subs:
            nl_obj_ls = [f.replace(fluent_subs[0], fluent_subs[1]) for f in nl_obj_ls]
        return comma_str.join(nl_obj_ls[:-1]) + and_str + nl_obj_ls[-1]

    def nl_fluents(self, fluents, fluent_subs=None):
        return self.asp_to_nl(fluents, self.domain_class.fluent_to_natural_language, fluent_subs=fluent_subs)

    def nl_actions(self, actions, fluent_subs=None):
        return self.asp_to_nl(actions, self.domain_class.action_to_natural_language, fluent_subs=fluent_subs)

    def nl_question_prefix(self, plan_length):
        return f"Given the initial condition, I plan to perform {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"

    def nl_actions_up_to(self, plan_length):
        return self.nl_actions(self.given_plan_sequence[:plan_length])

    def corrupted_not_corrupted_mix(self, not_corrupted_fluents, corrupted_fluents):
        final_length = len(not_corrupted_fluents)
        if final_length == 0:
            raise 'Empty list'
        elif final_length == 1:
            num_to_be_corrupted_samples = 1
        else:
            num_to_be_corrupted_samples = random.randint(1, final_length - 1)
        corrupted_fluents_samples = random.sample(corrupted_fluents, num_to_be_corrupted_samples)
        return corrupted_fluents_samples + not_corrupted_fluents[:final_length - len(corrupted_fluents_samples)]

    def pos_neg_true_corrupted_fluents(self, is_pos_fluent_question, is_answer_true, pos_fluents, neg_fluents):
            
        if is_pos_fluent_question:
            if is_answer_true:
                fluents = pos_fluents
            else:
                fluents = self.corrupted_not_corrupted_mix(pos_fluents, [f[1:] for f in neg_fluents]) # remove the '-' sign
        else:
            if is_answer_true:
                fluents = neg_fluents
            else:
                fluents = self.corrupted_not_corrupted_mix(neg_fluents, [f"-{f}" for f in pos_fluents]) # add the '-' sign
        return fluents


class QuestionGenerator(QuestionGenerationHelpers):
    QUESTION_MULTIPLICITY = 5
    digit_regex = '\d+'
    word_regex = '[a-zA-Z]+'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)
    
    def qa_data_object(self, anwswer_type, question, answer):
        return {
            OUT_OBJ_ID: str(uuid.uuid4()),
            OUT_OBJ_DOMAIN_NAME: self.domain_class.domain_name(),
            OUT_OBJ_INSTANCE_ID: self.instance_id,
            OUT_OBJ_ACTION_SEQUENCE: self.given_plan_sequence,
            OUT_OBJ_QUESTION_TYPE: self.question_category(),
            OUT_OBJ_QUESTION: question,
            OUT_OBJ_ANSWER_TYPE: anwswer_type,
            OUT_OBJ_ANSWER: answer}

    def question_category(self):
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
            raise 'Timeout error'
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
                self.question_10]

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


class ObjectTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'object_tracking'

    def objects_for_fluent_one_object(self, fluent_prefix, plan_length, is_true_fluents=True):
        objects_for_fluent = []
        if is_true_fluents:
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluents = self.neg_fluent_given_plan[plan_length]
        for fluent in fluents:
            if fluent_prefix in fluent:
                objects_for_fluent.append(extract_single_variable(fluent))
        return objects_for_fluent

    def question_1_2_helper(self, plan_length, is_pos_fluent_question, is_answer_true, min_chosen_fluents=2,
                            timeout=MAX_TIMEOUT):
        chosen_fluents = []
        while len(chosen_fluents) < min_chosen_fluents and timeout > 0:
            obj = random.choice(self.all_objects)
            fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, self.pos_fluents_for_object(obj, plan_length),  self.neg_fluents_for_object(obj, plan_length))
            if min_chosen_fluents <= len(fluents):
                num_samples = random.randint(min_chosen_fluents, len(fluents))
                chosen_fluents = random.sample(fluents, num_samples)
            timeout -= 1
        if timeout == 0:
            raise 'Timeout error'
        nl_fluents = self.nl_fluents(chosen_fluents)
        return f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {nl_fluents}?"

    def question_3_4_helper(self, plan_length, is_pos_fluents=True, timeout=MAX_TIMEOUT):

        def is_break_condition(chosen_fluent, objects_for_fluent):
            return self.is_variable_in_fluent(chosen_fluent) and (',' not in chosen_fluent) and (
                    '(' in chosen_fluent) and len(objects_for_fluent) >= 1

        # NOTE: only fluents for single objects, ex: ontable(block1),  NOT on(block1, block2)
        chosen_fluent = ''
        objects_for_fluent = []
        while not is_break_condition(chosen_fluent, objects_for_fluent) and timeout > 0:
            if is_pos_fluents:
                chosen_fluent = random.choice(self.pos_fluents_given_plan[plan_length])
            else:
                chosen_fluent = random.choice(self.neg_fluent_given_plan[plan_length])
            if '(' not in chosen_fluent: # associated with object
                continue
            fluent_prefix = chosen_fluent[:chosen_fluent.find('(')]
            objects_for_fluent = self.objects_for_fluent_one_object(fluent_prefix, plan_length, is_pos_fluents)
            timeout -= 1
        if timeout == 0:
            raise 'Timeout error'

        objects_by_type = defaultdict(list)
        for obj in objects_for_fluent:
            objects_by_type[self.object_type_by_object_name[obj]].append(obj)

        nl_object_types = 's, '.join(list(objects_by_type.keys())) + 's'
        nl_fluents = self.nl_fluents([chosen_fluent[:chosen_fluent.find('(')]])
        question = f"{self.nl_question_prefix(plan_length)} what {nl_object_types} are {nl_fluents}? {NONE_STATEMENT}."

        answer = []
        for obj_type, objects in objects_by_type.items():
            for obj in objects:
                answer.append(f"{obj_type} {obj}")
        answer = self.asp_to_nl(sorted(answer), lambda x: x)

        return question, answer

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        is_answer_true = random.choice([True, False])
        question = self.question_1_2_helper(plan_length, 1, is_answer_true)
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        is_answer_true = random.choice([True, False])
        question = self.question_1_2_helper(plan_length, 2, is_answer_true)
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def question_3(self, plan_length):
        # NOTE: only fluents for single objects, ex: ontable(block1)
        question, answer = self.question_3_4_helper(plan_length, is_pos_fluents=True)
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_4(self, plan_length):
        # NOTE: only fluents for single objects, ex: -ontable(block1)
        question, answer = self.question_3_4_helper(plan_length, is_pos_fluents=False)
        return self.qa_data_object(FREE_ANSWER, question, answer)


class FluentTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'fluent_tracking'

    def qa_1_2_helper(self, plan_length, is_pos_fluent_question):
        is_answer_true = random.choice([True, False])
        pos_fluent = random.choice(self.pos_fluents_given_plan[plan_length])
        neg_fluent = random.choice(self.neg_fluent_given_plan[plan_length])
        fluent = \
            self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, [pos_fluent], [neg_fluent])[0]
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that {self.domain_class.fluent_to_natural_language(fluent)}?"
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def qa_3_4_helper(self, plan_length, is_pos_fluent_question):
        is_answer_true = random.choice([True, False])
        fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true,
                                                      self.pos_fluents_given_plan[plan_length],
                                                      self.neg_fluent_given_plan[plan_length])
        question = f"{self.nl_question_prefix(plan_length)} are all of the following fluents {TRUE_OR_FALSE}: {self.nl_fluents(fluents)}? {NONE_STATEMENT}"
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def qa_5_6_helper(self, plan_length, is_pos_fluent_question):
        obj = random.choice(self.all_objects)
        obj_type = self.object_type_by_object_name[obj]
        if is_pos_fluent_question:
            fluent_type = 'positive'
            fluents = self.pos_fluents_for_object(obj, plan_length)
        else:
            fluent_type = 'negative'
            fluents = self.neg_fluents_for_object(obj, plan_length)
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type} fluents for {obj_type} {obj}. {NONE_STATEMENT}."
        return self.qa_data_object(FREE_ANSWER, question, nl_fluents.capitalize())

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question)

    def question_3(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question)

    def question_4(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question)

    def question_5(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_5_6_helper(plan_length, is_pos_fluent_question)

    def question_6(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_5_6_helper(plan_length, is_pos_fluent_question)


class StateTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'state_tracking'

    def qa_1_2_helper(self, plan_length, is_pos_fluent_question):
        is_answer_true = random.choice([True, False])
        pos_fluents = self.pos_fluents_given_plan[plan_length]
        neg_fluents = self.neg_fluent_given_plan[plan_length]
        fluents = self.pos_neg_true_corrupted_fluents(is_pos_fluent_question, is_answer_true, pos_fluents, neg_fluents)
        nl_fluents = self.nl_fluents(fluents)
        if is_pos_fluent_question:
            fluent_type = 'positive'
        else:
            fluent_type = 'negative'
        question = f"{self.nl_question_prefix(plan_length)} is it {TRUE_OR_FALSE} that the following {fluent_type} fluents represent the state completely: {nl_fluents}?"
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def qa_3_4_helper(self, plan_length, is_pos_fluent_question):
        if is_pos_fluent_question:
            fluent_type = 'positive'
            fluents = self.pos_fluents_given_plan[plan_length]
        else:
            fluent_type = 'negative'
            fluents = self.neg_fluent_given_plan[plan_length]
        nl_fluents = self.nl_fluents(fluents)
        question = f"{self.nl_question_prefix(plan_length)} list all {fluent_type} fluents for this state. {NONE_STATEMENT}."
        return self.qa_data_object(FREE_ANSWER, question, nl_fluents.capitalize())

    def question_1(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question)

    def question_2(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_1_2_helper(plan_length, is_pos_fluent_question)

    def question_3(self, plan_length):
        is_pos_fluent_question = True
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question)

    def question_4(self, plan_length):
        is_pos_fluent_question = False
        return self.qa_3_4_helper(plan_length, is_pos_fluent_question)


class ActionExecutabilityQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'action_executability'

    def qa_1_2_helper(self, nl_sequence_of_actions):
        return f"Given the initial condition, I plan to perform {nl_sequence_of_actions}. Is it possible to execute it, {TRUE_OR_FALSE}?"

    def question_1(self, plan_length):
        nl_sequence_of_actions = self.asp_to_nl(self.given_plan_sequence[:plan_length],
                                                self.domain_class.action_to_natural_language)
        question = self.qa_1_2_helper(nl_sequence_of_actions)
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, True)

    def question_2(self, plan_length):
        is_answer_true = random.choice([True, False])
        sequence_of_actions = self.given_plan_sequence[:plan_length]
        if not is_answer_true:
            random_break_ind = random.randint(0, plan_length - 1)
            random_inxecutable_action = random.choice(self.inexecutable_actions[random_break_ind])
            sequence_of_actions[random_break_ind] = random_inxecutable_action
        nl_sequence_of_actions = self.asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        question = self.qa_1_2_helper(nl_sequence_of_actions)
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, False)

    def question_3(self, plan_length):
        is_answer_true = random.choice([True, False])
        sequence_of_actions = self.given_plan_sequence[:plan_length]
        random_break_ind = random.randint(0, plan_length - 1)
        if not is_answer_true:
            random_inxecutable_action = random.choice(self.inexecutable_actions[random_break_ind])
            sequence_of_actions[random_break_ind] = random_inxecutable_action
        selected_action = sequence_of_actions[random_break_ind]

        nl_sequence_of_actions = self.asp_to_nl(sequence_of_actions, self.domain_class.action_to_natural_language)
        nl_selected_action = self.domain_class.action_to_natural_language(selected_action)
        question = f"Given the initial condition, for steps 1 through {plan_length} I plan to perform: {nl_sequence_of_actions}. Is it possible to execute {nl_selected_action} at step {random_break_ind+1}, {TRUE_OR_FALSE}?"
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def question_4(self, plan_length):
        # TODO validate
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)} to reach the current state, specify all the actions which are inexecutable in the current state?"
        answer = self.ACTION_JOIN_STR.join(
            [self.domain_class.fluent_to_natural_language(action) for action in
             self.inexecutable_actions[plan_length + 1]])
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_5(self, plan_length):
        # TODO validate
        question = f"I plan to perform the following sequence of actions: {self.get_random_inexecutable_sequence(plan_length)} to reach the current state, what is the first inexecutable action in the sequence of actions?"
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        answer = inexecutable_action
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_6(self, plan_length):
        # TODO validate
        question = f"I plan to perform the following sequence of actions: {self.get_random_inexecutable_sequence(plan_length)} to reach the current state, what is the first inexecutable action in the sequence of actions?"
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        answer = inexecutable_action
        return self.qa_data_object(FREE_ANSWER, question, answer)


class EffectsQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'effects'

    def prefix(self, plan_length):
        if plan_length == 0:
            return f"Given the initial condition,"
        else:
            return f"Given the initial condition, I plan to perform {self.nl_actions_up_to(plan_length)} to reach the current state. In this state,"


    def qa_1_2_helper(self, plan_length, is_affected_fluents_question, is_answer_true):
        plan_length -= 1  # since we are taking an action in this question
        action = self.given_plan_sequence[plan_length]
        fluents_current_state = set(self.pos_fluents_given_plan[plan_length])
        fluents_next_state = set(self.pos_fluents_given_plan[plan_length + 1])

        fluents_from_action = list(fluents_next_state - fluents_current_state)
        unaffected_fluents = list(fluents_next_state.intersection(fluents_current_state))
        if is_affected_fluents_question:
            if is_answer_true:
                fluents = fluents_from_action
            else:
                fluents = self.corrupted_not_corrupted_mix(fluents_from_action, unaffected_fluents)
        else:
            if is_answer_true:
                fluents = unaffected_fluents
            else:
                fluents = self.corrupted_not_corrupted_mix(unaffected_fluents, fluents_from_action)
        sampled_fluents = random.sample(fluents, random.randint(1, len(fluents)))

        nl_fluents = self.nl_fluents(sampled_fluents, )
        question = f"{self.prefix(plan_length)} if I perform {self.nl_actions([action])}, is it {TRUE_OR_FALSE} that {nl_fluents}?"
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, is_answer_true)

    def qa_3_4_helper(self, plan_length, is_positive_fluents_question):
        plan_length -= 1  # since we are taking an action in this question
        action = self.given_plan_sequence[plan_length]
        if is_positive_fluents_question:
            fluents = self.pos_fluents_given_plan[plan_length + 1]
        else:
            fluents = self.neg_fluent_given_plan[plan_length + 1]
        question = f"{self.prefix(plan_length)} I perform {self.nl_actions([action])}, list all fluents that would be {is_positive_fluents_question}"
        return self.qa_data_object(FREE_ANSWER, question,  self.nl_fluents(fluents))

    def question_1(self, plan_length):
        is_affected_fluents_question = True
        is_answer_true = random.choice([True, False])
        return self.qa_1_2_helper(plan_length, is_affected_fluents_question, is_answer_true)

    def question_2(self, plan_length):
        is_affected_fluents_question = False
        is_answer_true = random.choice([True, False])
        return self.qa_1_2_helper(plan_length, is_affected_fluents_question, is_answer_true)

    def question_3(self, plan_length):
        is_positive_fluents_question = True
        return self.qa_3_4_helper(plan_length, is_positive_fluents_question)

    def question_4(self, plan_length):
        is_positive_fluents_question = True
        return self.qa_3_4_helper(plan_length, is_positive_fluents_question)

class NumericalReasoningQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'numerical_reasoning'

    def question_1(self, plan_length):
        # TODO validate
        # obj, no_of_unique_objects = StatesActionsGenerator.parse_objects(objects)
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})
        len_of_unique_blocks = len(unique_blocks)
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the current number of objects {len_of_unique_blocks}?"
        answer = True
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO validate
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})
        len_of_unique_blocks_corrupted = len(unique_blocks) + random.randint(1, 10)
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        # print(self.given_plan_sequence[:plan_length])
        # sys.exit(0)
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of objects {len_of_unique_blocks_corrupted}?"
        # return None
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length):
        # TODO validate
        no_of_executable_actions = len(self.executable_actions[plan_length])
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of executable actions {no_of_executable_actions}?"
        answer = True
        print("self.executable_actions[plan_length]---->", self.executable_actions[plan_length])
        print("fluents---->", self.pos_fluents_given_plan[plan_length])
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_4(self, plan_length):
        # TODO validate
        no_of_executable_actions = len(self.executable_actions[plan_length]) + random.randint(1, 10)
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of executable actions {no_of_executable_actions}?"
        print("self.executable_actions[plan_length]---->", self.executable_actions[plan_length])
        print("fluents---->", self.pos_fluents_given_plan[plan_length])
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_5(self, plan_length):
        # TODO validate
        total_no_of_actions = plan_length
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the total number of actions {total_no_of_actions}?"
        answer = True
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)
        # return None

    def question_6(self, plan_length):
        # TODO validate
        total_no_of_actions = plan_length + random.randint(1, 10)
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the total number of actions {total_no_of_actions}?"
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_7(self, plan_length):
        # TODO validate
        # no_of_unique_objects = sum([len(instances) for instances in StatesActionsGenerator.parse_objects(objects).values()]) 
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})
        len_of_unique_blocks = len(unique_blocks)
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state what is the total number of objects?"
        answer = len_of_unique_blocks
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_8(self, plan_length):
        # TODO validate
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. How many true fluents are there in the current state?"
        answer = len(self.pos_fluents_given_plan[plan_length])
        print("self.given_fluent_sequence[plan_length]---->", self.pos_fluents_given_plan[plan_length])
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_9(self, plan_length):
        # TODO validate
        actions_to_nl = ', '.join(
            [self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. How many false fluents are there in the current state?"
        answer = len(self.neg_fluent_given_plan[plan_length])
        print("self.given_neg_fluent_sequence[plan_length]---->", self.neg_fluent_given_plan[plan_length])
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_10(self, plan_length):
        # TODO validate
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)} to reach the current state. How many executable actions are there from the current state?"
        answer = len(self.executable_actions[plan_length])
        print("self.executable_actions[plan_length]---->", self.executable_actions[plan_length])
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_11(self, plan_length):
        # TODO validate
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)} to reach the current state. How many inexecutable actions are there from the current state?"
        answer = len(self.inexecutable_actions[plan_length])
        print("self.inexecutable_actions[plan_length]---->", self.inexecutable_actions[plan_length])
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_12(self, plan_length):
        # TODO validate
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        question = f"I plan to perform the following sequence of actions: {inexecutable_action} to reach the current state. What is the first inexecutable action in the sequence of actions?"
        answer = inexecutable_action[index]
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_13(self, plan_length):
        # TODO validate
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        question = f"I plan to perform the following sequence of actions: {inexecutable_action} to reach the current state. How many actions are there before the first inexecutable action?"
        print("inexecutable_action---->", inexecutable_action)
        answer = index
        return self.qa_data_object(FREE_ANSWER, question, answer)


class HallucinationQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'hallucination'

    def question_1(self, plan_length, objects):
        # TODO validate
        # return None
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_object = random.choice(StatesActionsGenerator.parse_objects(objects)[random_key])
        object_name = re.findall(self.word_regex, random_object)[0]
        object_number = re.findall(self.digit_regex, random_object)[0]
        hallucinated_object = object_name + str(random.randint(int(object_number), int(object_number) + 10))
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state, is the object {hallucinated_object} part of the objects in the current state?"
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length, objects):
        # TODO validate
        # return None
        out_of_domain_action_seq, index = self.domain_class.out_of_domain_action_sequence(plan_length, objects)
        question = f"I plan to perform the following sequence of actions: {out_of_domain_action_seq} to reach the current state, is the action {out_of_domain_action_seq[index]} a defined action in the domain?"
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length, objects):
        # TODO validate
        out_of_domain_fluent_seq, index = self.domain_class.out_of_domain_fluent_sequence(plan_length, objects)
        question = f"I plan to perform the following sequence of actions: {out_of_domain_fluent_seq} to reach the current state, is the fluent {out_of_domain_fluent_seq[index]} a defined fluent in the domain?"
        answer = False
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_4(self, plan_length, objects):
        # TODO validate
        # return None
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_objects = StatesActionsGenerator.parse_objects(objects)[random_key]
        object_name = re.findall(self.word_regex, random_objects)[0]
        object_number = re.findall(self.digit_regex, random_objects)[0]
        hallucinated_object = object_name + str(random.randint(int(object_number), int(object_number) + 10))
        random_index = random.randint(0, len(random_objects) - 1)
        random_objects.pop(random_index)
        random_objects.insert(random_index, hallucinated_object)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state, which object is not defined in the problem?"
        answer = hallucinated_object
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_5(self, plan_length, objects):
        # TODO validate
        corrupted_fluent_sequence, index = self.domain_class.out_of_domain_fluent_sequence(plan_length, objects)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state. Given the fluents for a current_state: {corrupted_fluent_sequence} which fluent is not defined in the problem?"
        answer = corrupted_fluent_sequence[index]
        return self.qa_data_object(FREE_ANSWER, question, answer)

    def question_6(self, plan_length, objects):
        # TODO validate
        corrupted_action_sequence, index = self.domain_class.out_of_domain_action_sequence(plan_length, objects)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state. Given the actions for a current_state: {corrupted_action_sequence} which action is not defined in the problem?"
        answer = corrupted_action_sequence[index]
        return self.qa_data_object(FREE_ANSWER, question, answer)


class LoopingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'looping'

    def question_1(self, plan_length):
        # TODO validate
        sequence, string_repeat_number, b1, b2 = self.domain_class.get_looping_action_sequence(self, plan_length)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]}, to reach the current state. In the currents state if I perform :{sequence}  Will the block {b1} be on top of block{b2}?"
        answer = True
        return self.qa_data_object(TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO implement
        return None

    def question_3(self, plan_length):
        # TODO implement
        return None

    def question_4(self, plan_length):
        # TODO implement
        return None

    def question_5(self, plan_length):
        # TODO implement
        return None

    def question_6(self, plan_length):
        # TODO implement
        return None


# class CompositeQuestions(DomainQuestionGen):
#         def __init__(self, states_actions_jsonl_path, instance_id):
#             super().__init__(states_actions_jsonl_path, instance_id)

#         def question_category(self):
#             return 'ObjectTracking'

#         def question_1(self, plan_length):

#           true_fluents = self.given_fluent_sequence[plan_length+1]
# random_index = random.randint(0, true_fluents - 1)
#             inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join(
#                 [self.action_to_natural_language(action) for action in inexecutable_sequence])
#             questions = [
#                 f'Given the initial state, I plan to execute the following sequence of actions: {inexecutable_sequence_nlp}, what will be the state before the first inexecutable action occurs? If there are None, answer "None"',
#                 f'Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, what is the state before the first inexecutable action? If there are None, answer "None"',
#             ]  # TODO add more question variations (if needed)
#             question = self.question_phrasing_choice(questions)
#             answer = self.fluents_from_optimal_sequence[inexecutable_action_index - 1]

#             return self.qa_data_object(self.composite_question_1.__name__, FREE_ANSWER, question, answer)

#         def question_2(self, plan_length):
#             # TODO implement
#             pass

#         def question_3(self, plan_length):
#             # TODO implement
#             pass

#         def question_4(self, plan_length):
#             # TODO implement
#             pass


class AllQuestions:
    def __init__(self, jsonl_instance, domain_class, instance_id):
        with open(jsonl_instance, 'r') as f:
            data = f.readlines()
        jsonl_instance = [json.loads(d) for d in data]
        self.domain_asp_to_nlp = domain_class
        self.jsonl_instance = jsonl_instance
        self.q_types = [ObjectTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        FluentTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        StateTrackingQuestions(jsonl_instance, domain_class, instance_id),
                        ActionExecutabilityQuestions(jsonl_instance, domain_class, instance_id),
                        EffectsQuestions(jsonl_instance, domain_class, instance_id),
                        LoopingQuestions(jsonl_instance, domain_class, instance_id),
                        NumericalReasoningQuestions(jsonl_instance, domain_class, instance_id),
                        HallucinationQuestions(jsonl_instance, domain_class, instance_id)]

    def generate_all_questions(self):
        all_questions = []
        for q_type in self.q_types:
            all_questions += q_type.create_questions()

# if __name__ == '__main__':
#     all_questions = []
#     for domain_class in domain_list:
#         for instance_jsonl in instance_list:
#             domain_instance = domain_class(instance_jsonl)
#             all_questions += domain_instance.create_questions()
#     # TODO add batching
#     with open('questions.jsonl', 'w') as f:
#         for question in all_questions:
#             f.write(json.dumps(question) + '\n')
