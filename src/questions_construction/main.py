import json
import random
import re
import uuid
from ..common import *
from domains import BaseDomain, Blocksworld
from ..states_actions_generation import *
import sys

OBJ_IN_PAREN_REGEX = r'\((.*?)\)'


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
        self.domain_class = domain_class
        self.states_actions = self.states_actions_all[1:]
        self.instance_id = instance_id
        self.given_plan_sequence = self.extract_given_plan_sequence()
        self.given_fluent_sequence = self.extract_fluents_for_given_plan()
        self.given_neg_fluent_sequence = self.extract_fluents_for_given_plan(NEG_FLUENTS_KEY)
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
        states = [self.init_state[FLUENTS_KEY]]
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
    def question_phrasing_choice(questions):
        # return random.choice(questions)
        return questions[0]  # TODO add random choice

    def is_string_inside_parentheses(self, main_string, target_string):
        # TODO needs testing
        pattern = re.compile(r'\({}*\)'.format(re.escape(target_string)))
        match = pattern.search(main_string)
        return bool(match)

    def fluents_for_objects(self, obj, plan_length, is_true_fluents=True):
        # TODO needs testing
        fluents_for_object = []
        if is_true_fluents:
            fluents = self.given_fluent_sequence[plan_length + 1]
        else:
            fluents = self.given_neg_fluent_sequence[plan_length + 1]
        for fluent in fluents:
            if self.is_string_inside_parentheses(fluent, obj):
                fluents_for_object.append(fluent)
        return fluents_for_object

    def true_fluents_for_object(self, object, plan_length):
        return self.fluents_for_objects(object, plan_length, is_true_fluents=True)

    def false_fluents_for_object(self, object, plan_length):
        return self.fluents_for_objects(object, plan_length, is_true_fluents=False)

    def objects_for_fluent_one_object(self, fluent_prefix, plan_length, is_true_fluents=True):
        objects_for_fluent = []
        if is_true_fluents:
            fluents = self.given_fluent_sequence[plan_length + 1]
        else:
            fluents = self.given_neg_fluent_sequence[plan_length + 1]
        for fluent in fluents:
            if fluent_prefix in fluent:
                objects_for_fluent.append(extract_single_variable(fluent))
        return objects_for_fluent

    def random_true_fluent(self, plan_length, is_empty_fluent=True):
        fluents = self.given_fluent_sequence[plan_length + 1]
        rand_fluent = random.choice(fluents)
        if is_empty_fluent:
            while not self.is_variable_in_fluent(rand_fluent):
                rand_fluent = random.choice(fluents)
        return rand_fluent, True  # TODO change to T/F choice

    def random_false_fluent(self, plan_length, is_empty_fluent=True):
        set1 = set(self.given_neg_fluent_sequence[plan_length + 1])
        random_no = random.choice([x for x in range(0, len(self.given_fluent_sequence)) if x != plan_length + 1])
        set2 = set(self.given_neg_fluent_sequence[random_no])
        rand_fluent = random.choice(list(set2 - set1))
        if is_empty_fluent:
            while not self.is_variable_in_fluent(rand_fluent):
                rand_fluent = random.choice(rand_fluent)
        return rand_fluent, False  # TODO change to T/F choice

    def nl_actions_up_to(self, plan_length):
        return ','.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])

    def get_objects_with_true_states(self, obj, plan_length):
        true_fluents = []
        for fluent in self.given_fluent_sequence[plan_length + 1]:
            if obj in fluent:
                true_fluents.append(fluent)
        true_fluents = [self.domain_class.fluent_to_natural_language(fluent).replace('be', 'is') for fluent in true_fluents]
        return true_fluents

    def get_objects_with_false_states(self, obj, plan_length):
        false_fluents = []
        for fluent in self.given_neg_fluent_sequence[plan_length + 1]:
            if obj in fluent:
                false_fluents.append(fluent)
        false_fluents = [self.domain_class.fluent_to_natural_language(fluent).replace('be', 'is') for fluent in false_fluents]
        return false_fluents

    def object_type_by_object_name(self):
        by_object_name = {}
        for obj_type, objects in self.objects_by_type:
            for obj in objects:
                by_object_name[obj] = obj_type
        return by_object_name

    def is_variable_in_fluent(self, fluent):
        return '(' in fluent and ')' in fluent

    def blocksworld_actions_to_nl(self,plan_length):
        nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        return nl

class QuestionGenerator(QuestionGenerationHelpers):
    QUESTION_MULTIPLICITY = 5
    FREE_ANSWER = 'free_answer'
    TRUE_FALSE_ANSWER = 'true_false_answer'
    digit_regex = '\d+'
    word_regex = '[a-zA-Z]+'

    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def qa_data_object(self, anwswer_type, question, answer):
        return {
            'id': uuid.uuid4(),
            'domain_name': self.domain_class.domain_name(),
            'instance_id': self.instance_id,
            'action_sequence': self.given_plan_sequence,
            'question_type': self.question_category(),
            'question': question,
            'anwswer_type': anwswer_type,
            'answer': answer}

    def question_category(self):
        raise 'Implement it in the child class'

    @staticmethod
    def unique_questions(question_constructor, plan_length, multiplicity, timeout=100):
        results = {}
        while (len(results) < multiplicity) and timeout > 0:
            qa_object = question_constructor(plan_length)
            if qa_object:  # can be None
                qa_id = (qa_object['question'], qa_object['answer'])
                results[qa_id] = qa_object
            timeout -= 1
        if timeout == 0:
            raise ('Timeout error')
        return list(results.values())

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY):
        results = []
        for plan_length in range(1, self.plan_length_max + 1):
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
        # TODO insure the same format for all question_categories
        return 'object_tracking'

    def question_1_2_helper(self, plan_length, is_true_fluents=True, min_object_fluent_pair=2):
        object_fluent_pair = []
        while len(object_fluent_pair) <= min_object_fluent_pair:
            object = random.choice(self.objects_by_type.values())
            if is_true_fluents:
                fluents = self.true_fluents_for_object(object, plan_length)
            else:
                fluents = self.false_fluents_for_object(object, plan_length)
            num_samples = random.randint(min_object_fluent_pair, len(fluents))
            object_fluent_pair = random.sample(fluents, num_samples)
        return f"Given the initial condition, I perform {self.nl_actions_up_to(plan_length)}. Is {object_fluent_pair} after my actions?"

    def question_1(self, plan_length):
        question = self.question_1_2_helper(plan_length, is_true_fluents=True)
        answer_type = self.TRUE_FALSE_ANSWER
        return self.qa_data_object(answer_type, question, True)

    def question_2(self, plan_length):
        question = self.question_1_2_helper(plan_length, is_true_fluents=False)
        answer_type = self.TRUE_FALSE_ANSWER
        return self.qa_data_object(answer_type, question, False)

    def question_3_4_helper(self, plan_length, is_true_fluents=True):
        # NOTE: only fluents for single objects, ex: ontable(block1)
        chosen_fluent = None
        while not self.is_variable_in_fluent(chosen_fluent) and ',' not in chosen_fluent:
            if is_true_fluents:
                chosen_fluent = random.choice(self.given_fluent_sequence[plan_length + 1])
            else:
                chosen_fluent = random.choice(self.given_neg_fluent_sequence[plan_length + 1])
        objects_for_fluent = self.objects_for_fluent_one_object(chosen_fluent[:chosen_fluent.find('(')], plan_length)
        by_object_name = self.object_type_by_object_name()
        object_types = set([by_object_name[obj] for obj in objects_for_fluent])
        return object_types, objects_for_fluent, chosen_fluent

    def question_3(self, plan_length):
        # NOTE: only fluents for single objects, ex: ontable(block1)
        object_types, objects_for_fluent, chosen_fluent = self.question_3_4_helper(plan_length, is_true_fluents=True)
        question = f"Given the initial condition, I perform {self.nl_actions_up_to(plan_length)}. What {object_types} are {chosen_fluent} after my actions?"
        answer_type = self.FREE_ANSWER
        return self.qa_data_object(answer_type, question, objects_for_fluent)

    def question_4(self, plan_length):
        # NOTE: only fluents for single objects, ex: -ontable(block1)
        object_types, objects_for_fluent, chosen_fluent = self.question_3_4_helper(plan_length, is_true_fluents=False)
        question = f"Given the initial condition, I perform {self.nl_actions_up_to(plan_length)}. What {object_types} are {chosen_fluent} after my actions?"
        answer_type = self.FREE_ANSWER
        return self.qa_data_object(answer_type, question, objects_for_fluent)


class FluentTrackingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'fluent_tracking'

    def question_1(self, plan_length):
        # TODO implement
        fluent, answer = self.random_true_fluent(plan_length)
        question = f"I plan to perform the following sequence of actions: { self.nl_actions_up_to(plan_length)}, is the condition:{self.domain_class.fluent_to_natural_language(fluent)} True/False?"
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO implement
        fluent, answer = self.random_false_fluent(plan_length)
        question = f"I plan to perform the following sequence of actions: { self.nl_actions_up_to(plan_length)}, is the condition:{self.domain_class.fluent_to_natural_language(fluent)} True/False?"
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length):
        # TODO implement
        # pass
        random_length = random.randint(2, plan_length - 1)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, in this are all the following {random.sample(self.given_fluent_sequence[plan_length + 1], random_length)} True/False?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_4(self, plan_length):
        # TODO implement
        random_length = random.randint(2, plan_length - 1)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, in this are all the following {random.sample(self.given_fluent_sequence[plan_length], random_length)} True/False?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_5(self, plan_length):
        # TODO implement
        unique_object = random.choice(StatesActionsGenerator.parse_objects())
        true_states = self.get_objects_with_true_states(unique_object, plan_length)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, can you specify all the true fluents for {unique_object}?"
        return self.qa_data_object(self.FREE_ANSWER, question, true_states)

    def question_6(self, plan_length):
        # TODO implement
        unique_object = random.choice(StatesActionsGenerator.parse_objects())
        false_states = self.get_objects_with_false_states(unique_object, plan_length)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, can you specify all the true fluents for {unique_object}?"
        return self.qa_data_object(self.FREE_ANSWER, question, false_states)


class StateTracking(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'state_tracking'

    def question_1(self, plan_length):
        question = f"I plan to perform the actions {self.nl_actions_up_to(plan_length)}, to reach the current state. Do the following fluents {self.given_fluent_sequence[plan_length + 1]} represent the state completely?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO implement
        return None

    def question_3(self, plan_length):
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, list all the conditions that will be true when I perform the sequence of actions?"
        answer = self.ACTION_JOIN_STR.join(
            [self.domain_class.fluent_to_natural_language(fluent) for fluent in self.given_fluent_sequence[plan_length + 1]])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)

    def question_4(self, plan_length):
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, list all the conditions that will not be true when I perform the sequence of actions?"
        answer = self.ACTION_JOIN_STR.join(
            [self.domain_class.fluent_to_natural_language(fluent) for fluent in self.given_neg_fluent_sequence[plan_length + 1]])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)


class ActionExecutabilityQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'action_executability'

    def question_1(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}, are all the actions in the sequence executable?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.get_random_inexecutable_sequence(plan_length)}, are all the actions in the sequence executable?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)} to reach the current state, specify all the actions which are executable in the current state?"
        answer = self.ACTION_JOIN_STR.join(
            [self.domain_class.fluent_to_natural_language(action) for action in self.executable_actions[plan_length + 1]])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)

    def question_4(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)} to reach the current state, specify all the actions which are inexecutable in the current state?"
        answer = self.ACTION_JOIN_STR.join(
            [self.domain_class.fluent_to_natural_language(action) for action in self.inexecutable_actions[plan_length + 1]])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)

    def question_5(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.get_random_inexecutable_sequence(plan_length)} to reach the current state, what is the first inexecutable action in the sequence of actions?"
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        answer = inexecutable_action
        return self.qa_data_object(self.FREE_ANSWER, question, answer)


class EffectsQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'effects'

    def question_1(self, plan_length):
        action = self.given_plan_sequence[plan_length-1]  #TODO doube check
        fluents_current_state = set(self.given_fluent_sequence[plan_length-1]) #TODO doube check
        fluents_next_state = set(self.given_fluent_sequence[plan_length])

        affected_fluents = fluents_next_state - fluents_current_state
        num_samples = len(affected_fluents)
        sampled_fluents = random.sample(affected_fluents, num_samples)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}. In this state, if I {action} will {sampled_fluents}? True/False"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        action = self.given_plan_sequence[plan_length-1]  #TODO doube check
        fluents_current_state = set(self.given_fluent_sequence[plan_length-1]) #TODO doube check
        fluents_next_state = set(self.given_fluent_sequence[plan_length])

        unaffected_fluents = fluents_next_state.intersection(fluents_current_state)
        num_samples = len(unaffected_fluents)
        sampled_fluents = random.sample(unaffected_fluents, num_samples)
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}. In this state, if I {action} will {sampled_fluents}? True/False"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length):
        action = self.given_plan_sequence[plan_length-1]  #TODO doube check
        fluents_next_state = self.given_fluent_sequence[plan_length] #TODO doube check
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}. In this state, if I {action} which fluents will be true"
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, fluents_next_state)

    def question_4(self, plan_length):
        action = self.given_plan_sequence[plan_length-1]  #TODO doube check
        neg_fluents_next_state = self.given_neg_fluent_sequence[plan_length] #TODO doube check
        question = f"I plan to perform the following sequence of actions: {self.nl_actions_up_to(plan_length)}. In this state, if I {action} which fluents will be false"
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, neg_fluents_next_state)


class LoopingQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'looping'

    def question_1(self, plan_length):
        sequence, string_repeat_number, b1, b2 = Blocksworld.get_looping_action_sequence(self,plan_length)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]}, to reach the current state. In the currents state if I perform :{sequence}  Will the block {b1} be on top of block{b2}?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

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


class NumericalReasoningQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'numerical_reasoning'

    def question_1(self, plan_length):
        # TODO implement
        # obj, no_of_unique_objects = StatesActionsGenerator.parse_objects(objects)
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})   
        len_of_unique_blocks = len(unique_blocks)        
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])        
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the current number of objects {len_of_unique_blocks}?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_2(self, plan_length):
        # TODO implement
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})       
        len_of_unique_blocks_corrupted = len(unique_blocks)+random.randint(1, 10) 
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        # print(self.given_plan_sequence[:plan_length])
        # sys.exit(0)
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of objects {len_of_unique_blocks_corrupted}?"
        # return None
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length):
        # TODO implement
        no_of_executable_actions = len(self.executable_actions[plan_length])
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of executable actions {no_of_executable_actions}?"
        answer = True
        print("self.executable_actions[plan_length]---->",self.executable_actions[plan_length])
        print("fluents---->",self.given_fluent_sequence[plan_length])
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_4(self, plan_length):
        # TODO implement
        no_of_executable_actions = len(self.executable_actions[plan_length]) + random.randint(1, 10)
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the number of executable actions {no_of_executable_actions}?"
        print("self.executable_actions[plan_length]---->",self.executable_actions[plan_length])
        print("fluents---->",self.given_fluent_sequence[plan_length])
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_5(self, plan_length):
        # TODO implement
        total_no_of_actions = plan_length
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the total number of actions {total_no_of_actions}?"
        answer = True
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)
        # return None

    def question_6(self, plan_length):
        # TODO implement
        total_no_of_actions = plan_length + random.randint(1, 10)
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state is the total number of actions {total_no_of_actions}?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)        
    
    def question_7(self, plan_length):
        # TODO implement
        # no_of_unique_objects = sum([len(instances) for instances in StatesActionsGenerator.parse_objects(objects).values()]) 
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})       
        len_of_unique_blocks = len(unique_blocks)   
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])         
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. In current state what is the total number of objects?" 
        answer = len_of_unique_blocks
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_8(self, plan_length):
        # TODO implement
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. How many true fluents are there in the current state?"
        answer = len(self.given_fluent_sequence[plan_length])
        print("self.given_fluent_sequence[plan_length]---->",self.given_fluent_sequence[plan_length])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_9(self, plan_length):
    # TODO implement
        actions_to_nl = ', '.join([self.domain_class.action_to_natural_language(a) for a in self.given_plan_sequence[:plan_length]])
        question = f"I plan to perform the following sequence of actions: {actions_to_nl} to reach the current state. How many false fluents are there in the current state?"
        answer = len(self.given_neg_fluent_sequence[plan_length])
        print("self.given_neg_fluent_sequence[plan_length]---->",self.given_neg_fluent_sequence[plan_length])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)   
    
    def question_10(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.blocksworld_actions_to_nl(plan_length)} to reach the current state. How many executable actions are there from the current state?"
        answer = len(self.executable_actions[plan_length])
        print("self.executable_actions[plan_length]---->",self.executable_actions[plan_length])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)   
    
    def question_11(self, plan_length):
        # TODO implement
        question = f"I plan to perform the following sequence of actions: {self.blocksworld_actions_to_nl(plan_length)} to reach the current state. How many inexecutable actions are there from the current state?"
        answer = len(self.inexecutable_actions[plan_length])
        print("self.inexecutable_actions[plan_length]---->",self.inexecutable_actions[plan_length])
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_12(self, plan_length):
        # TODO implement
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        question = f"I plan to perform the following sequence of actions: {inexecutable_action} to reach the current state. What is the first inexecutable action in the sequence of actions?"
        answer = inexecutable_action[index]
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_13(self, plan_length):
        # TODO implement
        inexecutable_action, index = self.get_random_inexecutable_sequence(plan_length)
        question = f"I plan to perform the following sequence of actions: {inexecutable_action} to reach the current state. How many actions are there before the first inexecutable action?"
        print("inexecutable_action---->",inexecutable_action)
        answer = index
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
        
class HallucinationQuestions(QuestionGenerator):
    def __init__(self, states_actions_all, domain_class, instance_id):
        super().__init__(states_actions_all, domain_class, instance_id)

    def question_category(self):
        return 'hallucination'

    def question_1(self, plan_length,objects):
        # TODO implement
        # return None
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_object = random.choice(StatesActionsGenerator.parse_objects(objects)[random_key])
        object_name = re.findall(self.word_regex, random_object)[0]
        object_number = re.findall(self.digit_regex, random_object)[0]
        hallucinated_object = object_name+str(random.randint(int(object_number), int(object_number)+10))
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state, is the object {hallucinated_object} part of the objects in the current state?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)
    
    def question_2(self, plan_length,objects):
        # TODO implement
        # return None
        out_of_domain_action_seq,index = self.domain_class.out_of_domain_action_sequence(plan_length,objects)
        question = f"I plan to perform the following sequence of actions: {out_of_domain_action_seq} to reach the current state, is the action {out_of_domain_action_seq[index]} a defined action in the domain?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_3(self, plan_length,objects):
        # TODO implement
        out_of_domain_fluent_seq,index = self.domain_class.out_of_domain_fluent_sequence(plan_length,objects)
        question = f"I plan to perform the following sequence of actions: {out_of_domain_fluent_seq} to reach the current state, is the fluent {out_of_domain_fluent_seq[index]} a defined fluent in the domain?"
        answer = False
        return self.qa_data_object(self.TRUE_FALSE_ANSWER, question, answer)

    def question_4(self, plan_length,objects):
        # TODO implement
        # return None
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_objects = StatesActionsGenerator.parse_objects(objects)[random_key]
        object_name = re.findall(self.word_regex, random_objects)[0]
        object_number = re.findall(self.digit_regex, random_objects)[0]
        hallucinated_object = object_name+str(random.randint(int(object_number), int(object_number)+10))        
        random_index = random.randint(0, len(random_objects) - 1)
        random_objects.pop(random_index)
        random_objects.insert(random_index,hallucinated_object)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state, which object is not defined in the problem?"
        answer = hallucinated_object
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_5(self, plan_length,objects):
        corrupted_fluent_sequence , index = self.domain_class.out_of_domain_fluent_sequence(plan_length,objects)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state. Given the fluents for a current_state: {corrupted_fluent_sequence} which fluent is not defined in the problem?"
        answer = corrupted_fluent_sequence[index]
        return self.qa_data_object(self.FREE_ANSWER, question, answer)
    
    def question_6(self, plan_length,objects):
        corrupted_action_sequence , index = self.domain_class.out_of_domain_action_sequence(plan_length,objects)
        question = f"I plan to perform the following sequence of actions: {self.given_plan_sequence[:plan_length]} to reach the current state. Given the actions for a current_state: {corrupted_action_sequence} which action is not defined in the problem?"
        answer = corrupted_action_sequence[index]
        return self.qa_data_object(self.FREE_ANSWER, question, answer)


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

#             return self.qa_data_object(self.composite_question_1.__name__, self.FREE_ANSWER, question, answer)

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
    def __init__(self, jsonl_instance,domain_class, instance_id):
        with open(jsonl_instance, 'r') as f:
            data = f.readlines()
        jsonl_instance = [json.loads(d) for d in data]    
        self.domain_asp_to_nlp = domain_class
        self.jsonl_instance = jsonl_instance
        self.q_types = [ObjectTrackingQuestions(jsonl_instance,domain_class, instance_id),
                        FluentTrackingQuestions(jsonl_instance,domain_class, instance_id),
                        StateTracking(jsonl_instance,domain_class, instance_id),
                        ActionExecutabilityQuestions(jsonl_instance,domain_class, instance_id),
                        EffectsQuestions(jsonl_instance,domain_class, instance_id),
                        LoopingQuestions(jsonl_instance,domain_class, instance_id),
                        NumericalReasoningQuestions(jsonl_instance,domain_class, instance_id),
                        HallucinationQuestions(jsonl_instance,domain_class, instance_id)]

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
