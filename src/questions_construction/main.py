import json
import random
import re
import uuid
from ..common import *


class DomainMainMethods:
    def __init__(self, states_actions_jsonl_path, instance_id):
        self.states_actions_all = open_jsonl(
            states_actions_jsonl_path)  # self.data[i] defines all action->states at time i, i==0 is NULL->initial state
        self.init_state = self.states_actions_all[0][INIT_ACTION_KEY]  # initial state
        self.states_actions = self.states_actions_all[1:]
        self.instance_id = instance_id
        self.given_plan_sequence = self.extract_given_plan_sequence()
        self.plan_length_max = len(self.given_plan_sequence) - 1  # since i=0 is a NULL action
        self.executable_actions = self.extract_executable_actions()
        self.inexecutable_actions = self.extract_inexecutable_actions()
        self.fluents_from_executable_actions = self.extract_fluents_from_executable_actions()
        self.fluents_from_optimal_sequence = self.extract_fluents_from_optimal_sequence()

    def extract_given_plan_sequence(self):
        given_plan_sequence = []
        for timestep in self.states_actions:
            for action, value in timestep.items():
                if value[PART_OF_PLAN_KEY]:
                    given_plan_sequence.append(action)
        return given_plan_sequence

    def extract_actions(self, is_executable):
        """extracts the executable actions for each time step"""

        def action_executability(state_info):
            return state_info[EXECUTABLE_ACTION_BOOL_KEY] and len(state_info[FLUENTS_KEY]) > 0

        actions_for_timestep = []
        for action_state_info in self.states_actions:  # timestep is a dictionary with action as key and value as another dictionary
            actions = []
            for action, value in action_state_info.items():
                if action_executability(value) == is_executable:
                    actions.append(action)
            actions_for_timestep.append(actions)
        return actions_for_timestep

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
        while not self.inexecutable_actions[index + 1]:  # If no inexecutable action exists for that location
            index = random.randint(0, plan_length - 1)
        inexecutable_action = random.choice(self.inexecutable_actions[index + 1])
        sequence = optimal_sequence[:index] + [inexecutable_action]
        while len(sequence) < plan_length:
            sequence += [random.choice(
                self.given_plan_sequence[random.randint(0,
                                                        self.plan_length_max - 1)])]  # Adding sequence from randomly generated optimal plan
        return sequence, index

    def extract_fluents_from_executable_actions(self):
        """This function extracts the fluents
            from the executable actions which
            are not in the optimal plan from the entire plan"""

        fluents_from_executable_actions = []
        for timestep in self.states_actions:
            timestep_fluents_from_executable_actions = []
            for action, value in timestep.items():
                if not value[PART_OF_PLAN_KEY] and value[EXECUTABLE_ACTION_BOOL_KEY] and len(value[FLUENTS_KEY]) > 0:
                    # timestep_fluents_from_executable_actions.append(value[FLUENTS_KEY])
                    for fluent in value[FLUENTS_KEY]:
                        timestep_fluents_from_executable_actions.append(fluent)
            fluents_from_executable_actions.append(timestep_fluents_from_executable_actions)
        return fluents_from_executable_actions

    def extract_fluents_from_optimal_sequence(self):
        """This function extracts the fluents from the optimal sequence"""

        fluents_from_optimal_sequence = []
        for timestep in self.states_actions:
            timestep_fluents_from_optimal_sequence = []
            for action, value in timestep.items():
                if value[PART_OF_PLAN_KEY] and value[EXECUTABLE_ACTION_BOOL_KEY] and len(value[FLUENTS_KEY]) > 0:
                    # timestep_fluents_from_optimal_sequence.append(value[FLUENTS_KEY])
                    for fluent in value[FLUENTS_KEY]:
                        timestep_fluents_from_optimal_sequence.append(fluent)
            fluents_from_optimal_sequence.append(timestep_fluents_from_optimal_sequence)
        return fluents_from_optimal_sequence

    def print_all(self):
        print(self.given_plan_sequence)
        print(self.executable_actions)
        print(self.inexecutable_actions)
        print(self.fluents_from_executable_actions)
        print(self.fluents_from_optimal_sequence)


class DomainQuestionGen(DomainMainMethods):
    """ Generates QAs * multiplicity for a given domain, init cond + plan sequence"""
    QUESTION_MULTIPLICITY = 5
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    ACTION_JOIN_STR = ', '
    FREE_ANSWER = 'free_answer'
    TRUE_FALSE_ANSWER = 'true_false_answer'

    def __init__(self, data):
        super().__init__(data)

    def domain_name(self):
        raise ('Implement it in the child class')

    def qa_data_object(self, question_class, question, answer):
        return {
            'id': uuid.uuid4(),
            'domain_name': self.domain_name(),
            'instance_id': self.instance_id,
            'action_sequence': self.given_plan_sequence,
            'question_type': question_class,
            'question': question,
            'answer': answer}

    def fluent_to_natual_language(self, fluent):
        raise ('Implement it in the child class')

    def action_to_natural_language(self, action):
        raise ('Implement it in the child class')

    def out_of_domain_action_name(self):
        # TODO create an out of domain action name. Has to be random, has to take random number of arguments,
        # ex: crane_lift(car1, structure2)
        # can be tricky since we are trying to tune the model later, need to make sure it's not gonna guess it easily
        # also need to return a NLP version of the action and params for self.action_to_natural_language child class
        pass

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]

    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')

    @staticmethod
    def unique_questions(question_generator, plan_length, multiplicity):
        # TODO implement dedup
        results = []
        for i in range(multiplicity):
            results.append(question_generator(plan_length))
        return results

    def question_constructors(self):
        return [self.composite_question_1,
                self.composite_question_2,
                self.composite_question_3,
                self.composite_question_4,
                self.sub_question_1,
                self.sub_question_2,
                self.sub_question_3,
                self.sub_question_4,
                self.sub_question_5,
                self.sub_question_6,
                self.sub_question_7,
                self.sub_question_8,
                self.sub_question_9,
                self.sub_question_10,
                self.sub_question_11,
                self.sub_question_12,
                self.sub_question_13,
                self.sub_question_14,
                self.sub_question_15]

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY):
        results = []
        for plan_length in range(1, self.plan_length_max + 1):
            for question_constructor in self.question_constructors():
                results += self.unique_questions(question_constructor, plan_length, multiplicity)
        return results

    @staticmethod
    def question_phrasing_choice(questions):
        # return random.choice(questions)
        return questions[0]  # TODO add random choice

    def composite_question_1(self, plan_length):
        inexecutable_sequence, inexecutable_action_index = self.get_random_inexecutable_sequence(plan_length)

        inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join(
            [self.action_to_natural_language(action) for action in inexecutable_sequence])
        questions = [
            f'Given the initial state, I plan to execute the following sequence of actions: {inexecutable_sequence_nlp}, what will be the state before the first inexecutable action occurs? If there are None, answer "None"',
            f'Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, what is the state before the first inexecutable action? If there are None, answer "None"',
        ]  # TODO add more question variations (if needed)
        question = self.question_phrasing_choice(questions)
        answer = self.fluents_from_optimal_sequence[inexecutable_action_index - 1]

        return self.qa_data_object(self.composite_question_1.__name__, self.FREE_ANSWER, question, answer)

    def composite_question_2(self, plan_length):
        # TODO implement
        pass

    def composite_question_3(self, plan_length):
        # TODO implement
        pass

    def composite_question_4(self, plan_length):
        # TODO implement
        pass

    def sub_question_1(self, plan_length):
        # TODO implement
        pass

    def sub_question_2(self, plan_length):
        # TODO implement
        pass

    def sub_question_3(self, plan_length):
        # TODO implement
        pass

    def sub_question_4(self, plan_length):
        # TODO implement
        pass

    def sub_question_5(self, plan_length):
        # TODO implement
        pass

    def sub_question_6(self, plan_length):
        # TODO implement
        pass

    def sub_question_7(self, plan_length):
        # TODO implement
        pass

    def sub_question_8(self, plan_length):
        # TODO implement
        pass

    def sub_question_9(self, plan_length):
        # TODO implement
        pass

    def sub_question_10(self, plan_length):
        # TODO implement
        pass

    def sub_question_11(self, plan_length):
        # TODO implement
        pass

    def sub_question_12(self, plan_length):
        # TODO implement
        pass

    def sub_question_13(self, plan_length):
        # TODO implement
        pass

    def sub_question_14(self, plan_length):
        # TODO implement
        pass

    def sub_question_15(self, plan_length):
        # TODO implement
        pass

# if __name__ == '__main__':
# all_questions = []
# for domain_class in domain_list:
#     for instance_jsonl in instance_list:
#         domain_instance = domain_class(instance_jsonl)
#         all_questions += domain_instance.create_questions()
# # TODO add batching
# with open('questions.jsonl', 'w') as f:
#     for question in all_questions:
#         f.write(json.dumps(question) + '\n')
