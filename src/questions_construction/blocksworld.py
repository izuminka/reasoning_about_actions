from collections import defaultdict
import random
from main import DomainQuestionGen
import re

class Blocksworld(DomainQuestionGen):
    def __init__(self, data):
        super().__init__(data)
        #TODO add domain description

    def domain_name(self):
        return 'blocksworld'

    def fluent_to_natual_language(self, fluent):
        #TODO add logic to convert fluents to natural language
        return fluent
    
    def action_to_natural_language(self, action):
        # TODO test
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return f'pickup block {block_name}'
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return f'put down block {block_name}'
        elif 'stack(' in action:
            b1, b2 =  self.extract_multi_variable(action)
            return f'stack block {b1} from block {b2}'
        elif 'unstack(' in action:
            b1, b2 =  self.extract_multi_variable(action)
            return f'unstack block {b1} from block {b2}'
        else:
            #TODO handle made up actions
            # action_nlp = ''
            # return f'action_nlp block {b1} from block {b2}'
            # use self.out_of_domain_action_name for translation
            raise('action is not defined')


        # sequence_length = 1

        # for i in range(3):
        #     custom_valid_action_sequences = self.optimal_sequence.copy()
        #     custom_valid_action_sequences = custom_valid_action_sequences[:sequence_length]
        #     select_random_inexecutable_action = random.choice(self.inexecutable_actions[i + 1])
        #     random_index = random.choice(range(len(custom_valid_action_sequences) + 1))
        #     custom_valid_action_sequences.insert(random_index, select_random_inexecutable_action)
        #     if random_index == 0:
        #         sequence_before_first_infeasible_action = self.fluents_from_optimal_sequence[
        #             self.optimal_sequence.index(custom_valid_action_sequences[random_index + 1])]
        #     else:
        #         sequence_before_first_infeasible_action = self.fluents_from_optimal_sequence[
        #             self.optimal_sequence.index(custom_valid_action_sequences[random_index - 1])]
        #     question = f"""Given the sequence of actions: {custom_valid_action_sequences},what is the state before the first infeasible action in the sequence??"""
        #     composite_question_answers[question] = sequence_before_first_infeasible_action
        #     sequence_length += 1
        # return composite_question_answers
