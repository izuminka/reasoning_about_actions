# from collections import defaultdict
# import random
# import re
# from src.states_actions_generation import *
from src.questions_construction.main import *

class BaseDomain:
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    # def __init__(self):
    #     self.single_variable = self.extract_single_variable()
    #     self.multiple_variables = self.extract_multi_variable()

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
    list_of_unknown_fluents = ['belowtable','unclear','empty','broken','unstable','usable']
    
    def domain_name(self):
        return 'blocksworld'

    def fluent_to_natural_language(self, fluent):
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
        elif fluent.startswith('handempty'):
            return f'hand is empty'
        elif fluent.startswith('-handempty'):
            return f'hand is not empty'


        elif fluent.startswith('clear'):
            return f'clear'
        elif fluent.startswith('-clear'):
            return f'not clear'
        elif fluent.startswith('holding'):
            return f'being held'
        elif fluent.startswith('-holding'):
            return f'not being held'
        elif fluent.startswith('ontable'):
            return f'on the table'
        elif fluent.startswith('-ontable'):
            return f'not on the table'
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
    
    def out_of_domain_action_sequence(self,plan_length,objects):
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_object = random.choice(StatesActionsGenerator.parse_objects(objects)[random_key])
        random_paranthesis = f"""({random_object})"""
        random_action = f"""{random.choice(self.list_of_unknown_actions)}{random_paranthesis}"""
        unknown_action_index = random.randint(0,plan_length-1)
        sequences_with_unknown_actions = QuestionGenerator.extract_given_plan_sequence()[:unknown_action_index]+[random_action]
        while len(sequences_with_unknown_actions)<plan_length:
            sequences_with_unknown_actions += [random.choice(QuestionGenerator.extract_given_plan_sequence())]
        return sequences_with_unknown_actions, unknown_action_index   
    
    def out_of_domain_fluent_sequence(self,plan_length,objects):    
        random_key = random.choice(list(StatesActionsGenerator.parse_objects(objects).keys()))
        random_object = random.choice(StatesActionsGenerator.parse_objects(objects)[random_key])
        random_paranthesis = f"""({random_object})"""
        random_fluent = f"""{random.choice(self.list_of_unknown_fluents)}{random_paranthesis}"""
        unknown_fluent_index = random.randint(0,plan_length-1)
        sequences_with_unknown_fluents = QuestionGenerator.extract_fluents_for_given_plan()[1:unknown_fluent_index+1]+[random_fluent]
        while len(sequences_with_unknown_fluents)<plan_length:
            sequences_with_unknown_fluents += [random.choice(QuestionGenerator.extract_given_plan_sequence())]
        return sequences_with_unknown_fluents, unknown_fluent_index  
    
    def get_looping_action_sequence(self,plan,seq,key):
        fluents = seq
        last_action = plan[-1]
        # print(fluents)
        print(last_action)
        if last_action.startswith('action_unstack('):
            block = self.extract_multi_variable(last_action)[0]
            if key == True:
                string_repeat_number = random.choice([2,4,6,8,10])   
                random_action = [f"put_down({block})",f"pick_up({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                # print(actions)
                # exit()                
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                # print(action_strings)
                # exit()
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = True  
                answer_string = 'on the table'      
                question_without_result = f"will the block {block} be on table?"
                return question, answer, random_action, question_without_result,answer_string
            elif key == False:
                string_repeat_number = random.choice([3,5,7,9,11])   
                random_action = [f"put_down({block})",f"pick_up({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = False       
                answer_string = 'in the hand'
                question_without_result = f"will the block {block} be on table?"
                return question, answer, random_action, question_without_result, answer_string
        elif last_action.startswith('action_stack('):
            block1, block2 = self.extract_multi_variable(last_action)
            if key == True:
                string_repeat_number = random.choice([2,4,6,8,10])   
                random_action = [f"unstack({block1},{block2})",f"stack({block1},{block2})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block1} be on block {block2}?"
                answer = True  
                answer_string = f'on block {block2}'
                question_without_result = f"will the block {block1} be on block {block2}?"
                return question, answer, random_action, question_without_result
            elif key == False:
                string_repeat_number = random.choice([3,5,7,9,11])   
                random_action = [f"unstack({block1},{block2})",f"stack({block1},{block2})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block1} be on block {block2}?"
                answer = False        
                question_without_result = f"will the block {block1} be on block {block2}?"
                return question, answer, random_action, question_without_result
        elif last_action.startswith('action_put_down('):
            block = self.extract_single_variable(last_action)
            if key == True:
                string_repeat_number = random.choice([2,4,6,8,10])   
                random_action = [f"pick_up({block})",f"put_down({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = True        
                question_without_result = f"will the block {block} be on table?"
                return question, answer, random_action, question_without_result
            elif key == False:
                string_repeat_number = random.choice([3,5,7,9,11])   
                random_action = [f"pick_up({block})",f"put_down({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = False        
                question_without_result = f"will the block {block} be on table?"
                return question, answer, random_action, question_without_result
        elif last_action.startswith('action_pick_up('):
            block = self.extract_single_variable(last_action)
            if key == True:
                string_repeat_number = random.choice([2,4,6,8,10])   
                random_action = [f"put_down({block})",f"pick_up({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ' then' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = True        
                question_without_result = f"will the block {block} be on table?"
                return question, answer,random_action, question_without_result
            elif key == False:
                string_repeat_number = random.choice([3,5,7,9,11])   
                random_action = [f"put_down({block})",f"pick_up({block})"]
                looping_actions = []
                for i in range(0,string_repeat_number):
                    if i%2 == 0:
                        looping_actions.append(random_action[0])
                    else:
                        looping_actions.append(random_action[1])  
                actions = [self.action_to_natural_language(a) for a in looping_actions]
                action_strings = [action + ', then ' if i < len(actions) - 1 else action for i, action in enumerate(actions)]
                result = ''.join(action_strings)                     
                question = f"{result}, will the block {block} be on table?"
                answer = False        
                question_without_result = f"will the block {block} be on table?"
                return question, answer, random_action, question_without_result
                
            # else:
            #     b = random.choice(holding_list)
            #     if key == True:
            #         string_repeat_number = random.choice([2,4,6,8,10])   
            #         random_action = [f"put_down({b})",f"pick_up({b})"]
            #         looping_actions = []
            #         for i in range(0,string_repeat_number):
            #             if i%2 == 0:
            #                 looping_actions.append(random_action[0])
            #             else:
            #                 looping_actions.append(random_action[1])  
            #         actions = [self.action_to_natural_language(a) for a in looping_actions]
            #         action_strings = [action + ' then, ' if action != actions[-1] else action for action in actions]
            #         result = ''.join(action_strings)                     
            #         question = f"{result}, will the block {b} be on table and clear?"
            #         answer = True
            #         return question, answer
            #     else: 
            #         string_repeat_number = random.choice([3,5,7,9,11])   
            #         random_action = [f"put_down({b})",f"pick_up({b})"]
            #         looping_actions = []
            #         for i in range(0,string_repeat_number):
            #             if i%2 == 0:
            #                 looping_actions.append(random_action[0])
            #             else:
            #                 looping_actions.append(random_action[1])  
            #         actions = [self.action_to_natural_language(a) for a in looping_actions]
            #         action_strings = [action + ' then, ' if action != actions[-1] else action for action in actions]
            #         result = ''.join(action_strings)                     
            #         question = f"{result}, will the block {b} be on table and clear?"
            #         answer = False
            #         return question, answer                            
                
        #     if key == True:
        #         sequence = string_repeat_number*f"unstack({b1},{b2}), stack({b1},{b2})"
        #     else:
        #         sequence = string_repeat_number*f"unstack({b1},{b2}), stack({b1},{b2}), unstack({b1},{b2})"                 
        #     return sequence, string_repeat_number, b1, b2
        # elif random_fluent == 'holding':
        #     b = random.choice(holding_list)
        #     string_repeat_number = random.randint(1,plan_length-1)   
        #     if key == True:
        #         sequence = string_repeat_number*f"put_down({b}), pick_up({b})"
        #     else:
        #         sequence = string_repeat_number*f"put_down({b}), pick_up({b}), put_down({b})"                 
        #     return sequence, string_repeat_number, b

class Depots(BaseDomain):
    
    def domain_name(self):
        return 'depots'
    
    def actions_to_natural_language(self, action):
        if action.startswith('drive('):
            truck, city1, city2 = self.extract_multi_variable(action)
            return f'drive truck {truck} from city {city1} to city {city2}'
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'lift the crate {crate} from the surface {surface} with the hoist {hoist} from place {place}'
        elif action.startswith('_drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'Drop the crate {crate} on the surface {surface} with the hoist {hoist} on the place {place}'
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'load the crate {crate} by dropping it with the hoist {hoist} in the truck {truck} from the place {place}'
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'unload crate {crate} by lifting it with the hoist {hoist} from truck {truck} from the place {place}'
        else:
            raise ('action is not defined')
        
    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'truck {obj} is at place {place}'
            elif obj.startswith('crate'):
                return f'crate {obj} is at place {place}'
            else:
                return f'hoist {obj} is at place {place}'
        elif fluent.startswith('on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is on surface {obj2}'
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is in truck {obj2}'
        elif fluent.startswith('lifting('):
            hoist,crate = self.extract_multi_variable(fluent)
            return f'hoist {hoist} is lifting crate {crate}'
        elif fluent.startswith('available('):
            hoist = self.extract_single_variable(fluent)
            return f'hoist {hoist} is available'
        elif fluent.startswith('clear('):
            surface = self.extract_single_variable(fluent)
            return f'surface {surface} is clear'
        
class Driverlog(BaseDomain):
        
        def domain_name(self):
            return 'driverlog'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at('):
                obj, place = self.extract_multi_variable(fluent)
                if obj.startswith('truck'):
                    return f'truck {obj} is at place {place}'
                else:
                    return f'driver {obj} is at place {place}'
            elif fluent.startswith('in('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'package {obj1} is in truck {obj2}'
            elif fluent.startswith('driving('):
                obj1,obj2 = self.extract_multi_variable(fluent)
                return f'Driver {obj1} is driving truck {obj2}'
            elif fluent.startswith('link('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'there is a link between location {obj1} and location {obj2}'
            elif fluent.startswith('path('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'there is a path between location {obj1} and location {obj2}'
            elif fluent.startswith('empty('):
                obj = self.extract_single_variable(fluent)
                return f'truck {obj} is empty'
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('load('):
                package, truck, location = self.extract_multi_variable(action)
                return f'load package {package} in truck {truck} at location {location}'
            elif action.startswith('unload('):
                package, truck, location = self.extract_multi_variable(action)
                return f'unload package {package} from truck {truck} at location {location}'
            elif action.startswith('board('):
                driver, truck, location = self.extract_multi_variable(action)
                return f'board driver {driver} in truck {truck} at location {location}'
            elif action.startswith('disembark('):
                driver, truck, location = self.extract_multi_variable(action)
                return f'disembark driver {driver} from truck {truck} at location {location}'
            elif action.startswith('drive('):
                driver,loc_from,loc_to = self.extract_multi_variable(action)
                return f'drive driver {driver} from location {loc_from} to location {loc_to}'
            elif action.startwith('walk('):
                driver,loc_from,loc_to = self.extract_multi_variable(action)
                return f'walk driver {driver} from location {loc_from} to location {loc_to}'
            else:
                raise ('action is not defined')

class Goldminer(BaseDomain):
    
    def domain_name(self):
        return 'goldminer'
    
    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot is at location {place}'
        elif fluent.startswith('bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is at location {obj1}'
        elif fluent.startswith('laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gold is at location {obj1}'
        elif fluent.startswith('soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'soft rock is at location {obj1}'
        elif fluent.startswith('hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'hard rock is at location {obj1}'
        elif fluent.startswith('gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gold is at location {obj1}'
        elif fluent.startswith('connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is a connection between location {obj1} and location {obj2}'
        elif fluent.startswith('arms_empty('):
            return f'robot arms are empty'
        elif fluent.startswith('holds_bomb('):
            return f'robot holds bomb'
        elif fluent.startswith('holds_laser('):
            return f'robot holds laser'
        elif fluent.startswith('holds_gold('):
            return f'robot holds gold'
        elif fluent.startswith('clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is clear'
        else:
            raise ('fluent is not defined')
    
    def action_to_natural_language(self, action):
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return f'move robot from location {location1} to location {location2}'
        elif action.startswith('pickup_laser('):
            laser = self.extract_single_variable(action)
            return f'pickup laser {laser}'
        elif action.startswith('pickup_bomb('):
            bomb = self.extract_single_variable(action)
            return f'pickup bomb {bomb}'
        elif action.startswith('putdown_laser('):
            laser = self.extract_single_variable(action)
            return f'putdown laser {laser}'
        elif action.startswith('detonate_bomb('):
            bomb = self.extract_single_variable(action)
            return f'detonate bomb {bomb}'
        elif action.startswith('fire_laser('):
            laser = self.extract_single_variable(action)
            return f'fire laser {laser}'
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return f'pick gold at location {location}'
        else:
            raise ('action is not defined')
        
class Grippers(BaseDomain):
    
    def domain_name(self):
        return 'grippers'
    
    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at_robby('):
            robot,room= self.extract_multi_variable(fluent)
            return f'robot {robot} is at room {room}'
        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'object {obj} is at room {room}'
        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} has free gripper {gripper}'
        elif fluent.startswith('carry('):
            robot,obj, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} is carrying object {obj} with gripper {gripper}'
        else:
            raise ('fluent is not defined')
    
    def action_to_natural_language(self, action):
        if action.startswith('pick('):
            robot,obj,room,gripper = self.extract_multi_variable(action)
            return f'pick object {obj} from room {room} with gripper {gripper} by robot {robot}'
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'move robot {robot} from room {room_from} to room {room_to}'
        elif action.startswith('drop('):
            robot,obj,room,gripper = self.extract_multi_variable(action)
            return f'drop object {obj} in room {room} with gripper {gripper} by robot {robot}'
        else:
            raise ('action is not defined')
        
class Logistics(BaseDomain):
    
    def domain_name(self):
        return 'logistics'
    
    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is in city {city}'
        elif fluent.startswith('at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is at place {place}'
        elif fluent.startswith('in('):
            package,vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is in vehicle {vehicle}'
        else:
            raise ('fluent is not defined')
        
    def action_to_natural_language(self, action):
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'load package {package} in truck {truck} at location {location}'
        elif action.startswith('load_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'load package {package} in airplane {airplane} at location {location}'
        elif action.startswith('unload_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'unload package {package} from airplane {airplane} at location {location}'
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'unload package {package} from truck {truck} at location {location}'
        elif action.startswith('drive_truck('):
            truck,loc_from,loc_to,city = self.extract_multi_variable(action)
            return f'drive truck {truck} from location {loc_from} to location {loc_to} in city {city}'
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return f'fly airplane {airplane} from airport {airport_from} to airport {airport_to}'
        else:
            raise ('action is not defined')
        
class Miconic(BaseDomain):
    
    def domain_name(self):
        return 'miconic'
    
    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} is at floor {floor}'
        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} is at floor {floor}'
        elif fluent.startswith('above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is above floor {floor1}'
        elif fluent.startswith('boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is boarded'
        elif fluent.startswith('served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is served'
        elif fluent.startswith('lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is at floor {floor}'
        else:
            raise ('fluent is not defined')
        
    def action_to_natural_language(self, action):
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return f'board passenger {passenger} at floor {floor}'
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return f'depart passenger {passenger} at floor {floor}'
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'go up from floor {floor1} to floor {floor2}'
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'go down from floor {floor1} to floor {floor2}'
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'go down from floor {floor1} to floor {floor2}'
        else:
            raise ('action is not defined')
        
class Mystery(BaseDomain):
        
        def domain_name(self):
            return 'mystery'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at('):
                obj, room = self.extract_multi_variable(fluent)
                if obj.startswith('vehicle'):
                    return f'vehicle {obj} is at room {room}'
                else:
                    return f'cargo {obj} is at room {room}'
            elif fluent.startswith('conn('):
                location1, location2 = self.extract_multi_variable(fluent)
                return f'there is a connection between location {location1} and location {location2}'
            elif fluent.startswith('has_fuel('):
                location, fuel = self.extract_multi_variable(fluent)
                return f'location {location} has fuel {fuel}'
            elif fluent.startswith('fuel_neighbor('):
                f1,f2 = self.extract_multi_variable(fluent)
                return f'location {f1} is neighbor of location {f2}'
            elif fluent.startswith('in('):
                cargo, vehicle = self.extract_multi_variable(fluent)
                return f'cargo {cargo} is in vehicle {vehicle}'
            elif fluent.startswith('has_space('):
                vehicle, space = self.extract_multi_variable(fluent)
                return f'vehicle {vehicle} has space {space}'
            elif fluent.startswith('space_neighbor('):
                s1,s2 = self.extract_multi_variable(fluent)
                return f'space {s1} is neighbor of space {s2}'
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('move('):
                vehicle,location1,location2,fuel_level1,fuel_level2 = self.extract_multi_variable(action)
                return f'move vehicle {vehicle} from location {location1} to location {location2} with fuel level {fuel_level1} to {fuel_level2}'
            elif action.startswith('load('):
                cargo,vehicle,location,space1,space2 = self.extract_multi_variable(action)
                return f'load cargo {cargo} in vehicle {vehicle} at location {location} with space {space1} to space {space2}'
            elif action.startswith('unload('):
                cargo,vehicle,location,space1,space2 = self.extract_multi_variable(action)
                return f'unload cargo {cargo} from vehicle {vehicle} at location {location} with space {space1} to space {space2}'
            else:
                raise ('action is not defined')
            
class Npuzzle(BaseDomain):
        
        def domain_name(self):
            return 'npuzzle'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at('):
                tile, position = self.extract_multi_variable(fluent)
                return f'tile {tile} is at position {position}'
            elif fluent.startswith('neighbor('):
                position1, position2 = self.extract_multi_variable(fluent)
                return f'position {position1} is neighbor of position {position2}'
            elif fluent.startswith('empty('):
                position = self.extract_single_variable(fluent)
                return f'position {position} is empty'
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('move('):
                tile,source,destination = self.extract_multi_variable(action)
                return f'move tile {tile} from position {source} to position {destination}'
            else:
                raise ('action is not defined')
        
class Satellite(BaseDomain):
        
        def domain_name(self):
            return 'satellite'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('on_board('):
                instrument, satellite = self.extract_multi_variable(fluent)
                return f'instrument {instrument} is on board satellite {satellite}'
            elif fluent.startswith('supports('):
                instrument, mode = self.extract_multi_variable(fluent)
                return f'instrument {instrument} supports mode {mode}'
            elif fluent.startswith('pointing('):
                satellite, direction = self.extract_multi_variable(fluent)
                return f'satellite {satellite} is pointing to direction {direction}'
            elif fluent.startswith('power_avail('):
                satellite = self.extract_single_variable(fluent)
                return f'satellite {satellite} has power available'
            elif fluent.startswith('power_on('):
                instrument = self.extract_single_variable(fluent)
                return f'instrument {instrument} is powered on'
            elif fluent.startswith('calibrated('):
                instrument = self.extract_single_variable(fluent)
                return f'instrument {instrument} is calibrated'
            elif fluent.startswith('have_image('):
                direction, mode = self.extract_multi_variable(fluent)
                return f'Instrument has image of direction {direction} and mode {mode}'
            elif fluent.startswith('calibration_target('):
                instrument, direction = self.extract_multi_variable(fluent)
                return f'instrument {instrument} is calibrated to direction {direction}'
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('turn_to('):
                satellite,new_dir,old_dir = self.extract_multi_variable(action)
                return f'turn satellite {satellite} to direction {new_dir} from direction {old_dir}'
            elif action.startswith('switch_on('):
                instrument, satellite = self.extract_multi_variable(action)
                return f'switch on instrument {instrument} on satellite {satellite}'  
            elif action.startswith('switch_off('):
                instrument, satellite = self.extract_multi_variable(action)
                return f'switch off instrument {instrument} on satellite {satellite}'
            elif action.startswith('calibrate('):
                satellite, instrument, direction = self.extract_multi_variable(action)
                return f'calibrate instrument {instrument} on satellite {satellite} to direction {direction}'
            elif action.startswith('take_image('):
                satellite, direction, instrument, mode = self.extract_multi_variable(action)
                return f'take image of direction {direction} with instrument {instrument} on satellite {satellite} with mode {mode}'
            else:
                raise ('action is not defined')
    
class Spanner(BaseDomain):
        
        def domain_name(self):
            return 'spanner'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at('):
                obj, location = self.extract_multi_variable(fluent)
                if obj.startswith('man'):
                    return f"Man {obj} is at location {location}"
                elif obj.startswith('nut'):
                    return f"Nut {obj} is at location {location}"
                else:
                    return f"spanner {obj} is at location {location}"
            elif fluent.startswith('carrying('):
                man, spanner = self.extract_multi_variable(fluent)
                return f"Man {man} is carrying spanner {spanner}"
            elif fluent.startswith('useable('):
                spanner = self.extract_single_variable(fluent)
                return f"spanner {spanner} is useable"
            elif fluent.startswith('tightened('):
                nut = self.extract_single_variable(fluent)
                return f"nut {nut} is tightened"
            elif fluent.startswith('loose('):
                nut = self.extract_single_variable(fluent)
                return f"nut {nut} is loose"
            elif fluent.startswith('link('):
                location1, location2 = self.extract_multi_variable(fluent)
                return f"location {location1} is linked to location {location2}"
            else:       
                raise ('fluent is not defined')

        def action_to_natural_language(self, action):
            if action.startswith('walk'):
                start,end,man = self.extract_multi_variable(action)
                return f"walk the man {man} from location {start} to location {end}"
            elif action.startswith('pick_up_spanner('):
                loc,spanner,man = self.extract_multi_variable(action)
                return f"pick up spanner {spanner} from location {loc} by man {man}"
            elif action.startswith('tighten_nut('):
                loc, spanner, man, nut = self.extract_multi_variable(action)
                return f"tighten nut {nut} with spanner {spanner} with man {man} at location {loc}"
            else:
                raise ('action is not defined')

class Zenotravel(BaseDomain):
        
        def domain_name(self):
            return 'zenotravel'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at('):
                obj, city = self.extract_multi_variable(fluent)
                if obj.startswith('person'):
                    return f"person {obj} is at city {city}"
                else:
                    return f"aircraft {obj} is at city {city}"
            elif fluent.startswith('in('):
                person, aircraft = self.extract_multi_variable(fluent)
                return f"person {person} is in aircraft {aircraft}"
            elif fluent.startswith('fuel_level('):
                aircraft, flevel = self.extract_multi_variable(fluent)
                return f"aircraft {aircraft} has fuel level {flevel}"
            elif fluent.startswith('next('):
                fuel1,fuel2 = self.extract_multi_variable(fluent)
                return f"fuel level {fuel2} is next to fuel level {fuel1}"
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('board('):
                person, aircraft, city = self.extract_multi_variable(action)
                return f"board person {person} in airplane {aircraft} at location {city}"
            elif action.startswith('depark('):
                person, aircraft, city = self.extract_multi_variable(action)
                return f"depart passenger {person} in airplane {aircraft} at location {city}"
            elif action.startswith('fly('):
                aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
                return f"fly aircraft {aircraft} from location {city1} to location {city2} with fuel level {fleve1} to {flevel2}"
            elif action.startswith('zoom('):
                aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
                return f"zoom aircraft {aircraft} from location {city1} to location {city2} with fuel level {fleve1} to {flevel3}"
            elif action.startswith('refuel('):
                aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
                return f"refuel aircraft {aircraft} at location {city} with fuel level {flevel1} to {flevel2}"
            else:
                raise ('action is not defined')

class Visitall(BaseDomain):
        
        def domain_name(self):
            return 'visitall'
        
        def fluent_to_natural_language(self, fluent):
            if fluent.startswith('at_robot('):
                place = self.extract_multi_variable(fluent)
                return f"robot is at place {place}"
            elif fluent.startswith('connected('):
                place1, place2 = self.extract_multi_variable(fluent)
                return f"place {place1} is connected to place {place2}"
            elif fluent.startswith('visited('):
                place = self.extract_single_variable(fluent)
                return f"place {place} is visited"
            else:
                raise ('fluent is not defined')
            
        def action_to_natural_language(self, action):
            if action.startswith('move('):
                place1,place2 = self.extract_multi_variable(action)
                return f"move from place {place1} to place {place2}"
            else:
                raise ('action is not defined')
            