from collections import defaultdict
import random
from main import DomainQuestionGen
import re
from src.states_actions_generation import StatesActionsGenerator

class BaseDomain:
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]

    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')
    
    def out_of_domain_object_name(self):
            # TODO create an out of domain action name. Has to be random, has to take random number of arguments,
            # ex: crane_lift(car1, structure2)
            # can be tricky since we are trying to tune the model later, need to make sure it's not gonna guess it easily
            # also need to return a NLP version of the action and params for self.action_to_natural_language child class
            raise ('Implement it in the child class')

    def out_of_domain_fluent_name(self):
        # TODO create an out of domain action name. Has to be random, has to take random number of arguments,
        # ex: crane_lift(car1, structure2)
        # can be tricky since we are trying to tune the model later, need to make sure it's not gonna guess it easily
        # also need to return a NLP version of the action and params for self.action_to_natural_language child class
        raise ('Implement it in the child class')

    def out_of_domain_action_name(self):
        # TODO create an out of domain action name. Has to be random, has to take random number of arguments,
        # ex: crane_lift(car1, structure2)
        # can be tricky since we are trying to tune the model later, need to make sure it's not gonna guess it easily
        # also need to return a NLP version of the action and params for self.action_to_natural_language child class
        raise ('Implement it in the child class')

class Blocksworld(BaseDomain):
    
    list_of_unknown_actions = ['action_shuffle','action_move','action_rotate','action_twist']
    
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
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is not on block {b2}'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not clear'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not being held'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not on the table'            
        else:
            #TODO handle made up fluents
            raise ('fluent is not defined')     

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
    
    def out_of_domain_action_name(self,plan_length,objects):
        random_paranthesis = f"""({random.choice(StatesActionsGenerator.parse_objects(objects))}, {random.choice(StatesActionsGenerator.parse_objects(objects))})"""
        random_action = f"""{random.choice(self.list_of_unknown_actions)}{random_paranthesis}"""
        unknown_action_index = random.randint(0,plan_length-1)
        sequences_with_unknown_actions = self.given_plan_sequence[1:plan_length+1].copy()
        sequences_with_unknown_actions.insert(unknown_action_index,random_action)
        while len(sequences_with_unknown_actions)<plan_length:
            sequences_with_unknown_actions += [random.choice(self.given_plan_sequence)]
        return sequences_with_unknown_actions, unknown_action_index    