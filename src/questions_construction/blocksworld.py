from collections import defaultdict
import random
from main import DomainQuestionGen
import re


class Blocksworld(DomainQuestionGen):
    def __init__(self, data):
        super().__init__(data)
        # TODO add domain description

    def domain_name(self):
        return 'blocksworld'

    def fluent_to_natual_language(self, fluent):
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is on block {b2}'
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is clear'
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is being held'
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is on the table'
        else:
            print('all true fluents returned')
        return fluent

    def action_to_natural_language(self, action):
        # TODO test
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return f'pickup block {block_name}'
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return f'put down block {block_name}'
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return f'unstack block {b1} from block {b2}'
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return f'stack block {b1} from block {b2}'
        else:
            # TODO handle made up actions
            # action_nlp = ''
            # return f'action_nlp block {b1} from block {b2}'
            # use self.out_of_domain_action_name for translation
            raise ('action is not defined')
