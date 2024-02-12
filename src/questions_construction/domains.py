import re


def strip_action_prefix(action):
    if action.startswith('action_'):
        return action[len('action_'):]
    return action


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
    DOMAIN_NAME = 'blocksworld'

    def __init__(self):
        self.domain_description_without_ram = self.domain_description_without_ram()

    @staticmethod
    def domain_description_without_ram():
        domain_description = ('Picking up a block is only possible if that block is clear, on the table, and the hand '
                              'is empty. By picking up that block, it makes that block not present on the table and '
                              'not clear. It also leads to the block being held and makes the hand not empty. Putting '
                              'down the block can only be executed if the block is being held. Putting down the block '
                              'causes that block to be clear and on the table. It also causes the hand to be not '
                              'holding the block and makes the hand empty. A block can be stacked on the second block '
                              'if it is being held and the second block is clear. By stacking the first block on the '
                              'second, it causes the first block to clear and on top of the second block. Meanwhile, '
                              'the second block is not clear, and the hand becomes empty as it is not holding the '
                              'block. The block can also be unstacked from the top of the second block only if the '
                              'hand is empty and the first block is clear and on top of the second block. Unstacking '
                              'the first block from the second causes the second block to be clear. The first block '
                              'is now being held, not clear, and not on top of the second block. Furthermore, '
                              'the hand is not empty.')
        return domain_description

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is on block {b2}'
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is not on block {b2}'
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is clear'
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is being held'
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is on the table'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not clear'
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is being held'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not being held'
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is on the table'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not on the table'
        elif fluent.startswith('handempty'):
            return f'hand is empty'
        elif fluent.startswith('-handempty'):
            return f'hand is not empty'
        else:
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
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
            raise ('action is not defined')

    def fluent_to_hallucinated_natural_language(self, fluent):
        # under
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is under block {b2}'
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return f'block {b1} is not under block {b2}'

        # broken
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is broken'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not broken'

        # thrown
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is being thrown'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not being thrown'

        # under table
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is under the table'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not under the table'

        # hand full
        elif fluent.startswith('handempty'):
            return f'hand is full'
        elif fluent.startswith('-handempty'):
            return f'hand is not full'
        else:
            raise ('fluent is not defined')

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return f'lift block {block_name}'  # lift
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return f'lower block {block_name}'  # lower
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return f'remove block {b1} from block {b2}'  # remove
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return f'load block {b1} from block {b2}'  # load
        else:
            raise ('action is not defined')


class Depots(BaseDomain):
    DOMAIN_NAME = 'depots'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'truck {obj} is at place {place}'
            elif obj.startswith('crate'):
                return f'crate {obj} is at place {place}'
            elif obj.startswith('hoist'):
                return f'hoist {obj} is at place {place}'
            elif obj.startswith('pallet'):
                return f'pallet {obj} is at place {place}'
            else:
                raise ('fluent is not defined')
        elif fluent.startswith('-at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'truck {obj} is not at place {place}'
            elif obj.startswith('crate'):
                return f'crate {obj} is not at place {place}'
            elif obj.startswith('hoist'):
                return f'hoist {obj} is not at place {place}'
            elif obj.startswith('pallet'):
                return f'pallet {obj} is not at place {place}'
            else:
                raise ('fluent is not defined')
        elif fluent.startswith('on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is on surface {obj2}'
        elif fluent.startswith('-on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is not on surface {obj2}'
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is in truck {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'crate {obj1} is not in truck {obj2}'
        elif fluent.startswith('lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return f'hoist {hoist} is lifting crate {crate}'
        elif fluent.startswith('-lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return f'hoist {hoist} is not lifting crate {crate}'
        elif fluent.startswith('available('):
            hoist = self.extract_single_variable(fluent)
            return f'hoist {hoist} is available'
        elif fluent.startswith('-available('):
            hoist = self.extract_single_variable(fluent)
            return f'hoist {hoist} is not available'
        elif fluent.startswith('clear('):
            surface = self.extract_single_variable(fluent)
            return f'surface {surface} is clear'
        elif fluent.startswith('-clear('):
            surface = self.extract_single_variable(fluent)
            return f'surface {surface} is not clear'
        else:
            raise ('fluent is not defined')

    def fluent_to_hallucinated_natural_language(self, fluent):
        flag = True
        for prefix_asp, prefix_nl in [('-', 'not'), ('', '')]:
            if fluent.startswith(f'{prefix_asp}at('):
                obj, place = self.extract_multi_variable(fluent)
                if obj.startswith('truck'):
                    return f'truck {obj} is {prefix_nl} crashed into place {place}'  # crashed into
                elif obj.startswith('crate'):
                    return f'crate {obj} is {prefix_nl} stranded at place {place}'  # stranded
                elif obj.startswith('hoist'):
                    return f'hoist {obj} is {prefix_nl} at near {place}'  # near
                elif obj.startswith('pallet'):
                    return f'pallet {obj} is {prefix_nl} within place {place}'  # within
                else:
                    raise ('fluent is not defined')
            elif fluent.startswith(f'{prefix_asp}on('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'crate {obj1} is {prefix_nl} within surface {obj2}'  # within
            elif fluent.startswith(f'{prefix_asp}in('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'crate {obj1} is {prefix_nl} under the truck {obj2}'  # under
            elif fluent.startswith(f'{prefix_asp}lifting('):
                hoist, crate = self.extract_multi_variable(fluent)
                return f'hoist {hoist} is {prefix_nl} transporting crate {crate}'  # transporting
            elif fluent.startswith(f'{prefix_asp}available('):
                hoist = self.extract_single_variable(fluent)
                return f'hoist {hoist} is {prefix_nl} free'  # free
            elif fluent.startswith(f'{prefix_asp}clear('):
                surface = self.extract_single_variable(fluent)
                return f'surface {surface} is {prefix_nl} free'  # free
        if flag:
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, city1, city2 = self.extract_multi_variable(action)
            return f'truck {truck} is driven from city {city1} to city {city2}'
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the crate {crate} is lifted from the surface {surface} with the hoist {hoist} from place {place}'
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the crate {crate} drops on the surface {surface} with the hoist {hoist} on the place {place}'
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the crate {crate} is loaded by dropping it with the hoist {hoist} in the truck {truck} from the place {place}'
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the crate {crate} is unloaded by lifting it with the hoist {hoist} from truck {truck} from the place {place}'
        else:
            raise ('action is not defined')

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, city1, city2 = self.extract_multi_variable(action)
            return f'truck {truck} crashes on a way from city {city1} to city {city2}'  # crashes
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the crate {crate} is lowered from the surface {surface} with the hoist {hoist} from place {place}'  # lowered
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the crate {crate} drops on the surface {surface} with the hoist {hoist} on the place {place}'  # drops
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the crate {crate} is loaded by dropping it with the hoist {hoist} in the truck {truck} from the place {place}'
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the crate {crate} is unloaded by lifting it with the hoist {hoist} from truck {truck} from the place {place}'
        else:
            raise ('action is not defined')


class Driverlog(BaseDomain):
    DOMAIN_NAME = 'driverlog'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'truck {obj} is at place {place}'
            else:
                return f'driver {obj} is at place {place}'
        elif fluent.startswith('-at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'truck {obj} is not at place {place}'
            else:
                return f'driver {obj} is not at place {place}'
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'package {obj1} is in truck {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'package {obj1} is not in truck {obj2}'
        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'driver {obj1} is driving truck {obj2}'
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'driver {obj1} is not driving truck {obj2}'
        elif fluent.startswith('link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is a link between location {obj1} and location {obj2}'
        elif fluent.startswith('-link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is no link between location {obj1} and location {obj2}'
        elif fluent.startswith('path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is a path between location {obj1} and location {obj2}'
        elif fluent.startswith('-path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is no path between location {obj1} and location {obj2}'
        elif fluent.startswith('empty('):
            obj = self.extract_single_variable(fluent)
            return f'truck {obj} is empty'
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return f'truck {obj} is not empty'
        else:
            # TODO for hallucination
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'load package {package} in truck {truck} at location {location}'
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'unload package {package} from truck {truck} at location {location}'
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'driver {driver} boards truck {truck} at location {location}'
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'driver {driver} disembarks from truck {truck} at location {location}'
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'driver {driver} drives truck {truck} from location {loc_from} to location {loc_to}'
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'driver {driver} walks from location {loc_from} to location {loc_to}'
        else:
            raise 'action is not defined'


class Goldminer(BaseDomain):
    DOMAIN_NAME = 'goldminer'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot is at location {place}'
        elif fluent.startswith('-robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot is not at location {place}'
        elif fluent.startswith('bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is at location {obj1}'
        elif fluent.startswith('-bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is not at location {obj1}'
        elif fluent.startswith('laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gold is at location {obj1}'
        elif fluent.startswith('-laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'laser is not at location {obj1}'
        elif fluent.startswith('soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'soft rock is at location {obj1}'
        elif fluent.startswith('-soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'soft rock is not at location {obj1}'
        elif fluent.startswith('hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'hard rock is at location {obj1}'
        elif fluent.startswith('-hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'hard rock is not at location {obj1}'
        elif fluent.startswith('gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gold is at location {obj1}'
        elif fluent.startswith('-gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gold is not at location {obj1}'
        elif fluent.startswith('connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is a connection between location {obj1} and location {obj2}'
        elif fluent.startswith('-connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'there is no connection between location {obj1} and location {obj2}'
        elif fluent.startswith('arm_empty'):
            return f"robot's arm is empty"
        elif fluent.startswith('-arm_empty'):
            return f"robot's arm is not empty"
        elif fluent.startswith('holds_bomb'):
            return f'robot holds a bomb'
        elif fluent.startswith('-holds_bomb'):
            return f'robot does not hold a bomb'
        elif fluent.startswith('holds_laser'):
            return f'robot holds laser'
        elif fluent.startswith('-holds_laser'):
            return f'robot does not hold laser'
        elif fluent.startswith('holds_gold'):
            return f'robot holds gold'
        elif fluent.startswith('-holds_gold'):
            return f'robot does not hold gold'
        elif fluent.startswith('clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is clear'
        elif fluent.startswith('-clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is not clear'

        # TODO for object detection
        elif fluent == 'robot_at':
            return f'robot is at'
        elif fluent == 'bomb_at':
            return f'bomb is at'
        elif fluent == 'laser_at':
            return f'laser is at'
        elif fluent == 'soft_rock_at':
            return f'soft rock is at'
        elif fluent == 'hard_rock_at':
            return f'hard rock is at'
        elif fluent == 'gold_at':
            return f'gold is at'
        elif fluent == 'connected':
            return f'connected'
        else:
            # TODO for hallucination
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return f'robot moves from location {location1} to location {location2}'
        elif action.startswith('pickup_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is picked up'
        elif action.startswith('pickup_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is picked up'
        elif action.startswith('putdown_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is put down'
        elif action.startswith('detonate_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is detonated'
        elif action.startswith('fire_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is fired'
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return f'gold is picked up at location {location}'
        else:
            raise ('action is not defined')


class Grippers(BaseDomain):
    DOMAIN_NAME = 'grippers'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'robot {robot} is at room {room}'
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'robot {robot} is not at room {room}'
        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'object {obj} is at room {room}'
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'object {obj} is not at room {room}'
        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} has free gripper {gripper}'
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} does not have free gripper {gripper}'
        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} is carrying object {obj} with gripper {gripper}'
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} is not carrying object {obj} with gripper {gripper}'
        else:
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'object {obj} is picked from room {room} with gripper {gripper} by robot {robot}'
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'robot {robot} moves from room {room_from} to room {room_to}'
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'object {obj} is dropped in room {room} with gripper {gripper} by robot {robot}'
        else:
            raise 'action is not defined'


class Logistics(BaseDomain):
    DOMAIN_NAME = 'logistics'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is in city {city}'
        elif fluent.startswith('-in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is not in city {city}'
        elif fluent.startswith('at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is at place {place}'
        elif fluent.startswith('-at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is not at place {place}'
        elif fluent.startswith('in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is in vehicle {vehicle}'
        elif fluent.startswith('-in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is not in vehicle {vehicle}'
        else:
            # TODO for hallucination
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} is loaded in truck {truck} at location {location}'
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} is unloaded from truck {truck} at location {location}'
        elif action.startswith('load_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} is loaded into airplane {airplane} at location {location}'
        elif action.startswith('unload_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} is unloaded from airplane {airplane} at location {location}'
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return f'truck {truck} is driven from location {loc_from} to location {loc_to} in city {city}'
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return f'airplane {airplane} is flown from airport {airport_from} to airport {airport_to}'
        else:
            raise 'action is not defined'


class Miconic(BaseDomain):
    DOMAIN_NAME = 'miconic'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} enters at floor {floor}'
        elif fluent.startswith('-origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not enter at floor {floor}'
        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} exits at floor {floor}'
        elif fluent.startswith('-destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not exit at floor {floor}'
        elif fluent.startswith('above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is above floor {floor1}'
        elif fluent.startswith('-above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is not above floor {floor1}'
        elif fluent.startswith('boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is boarded'
        elif fluent.startswith('-boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is not boarded'
        elif fluent.startswith('served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is served'
        elif fluent.startswith('-served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is not served'
        elif fluent.startswith('lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is at floor {floor}'
        elif fluent.startswith('-lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is not at floor {floor}'
        else:
            # TODO for hallucination
            raise ('fluent is not defined')

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} boards at floor {floor}'
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} departs at floor {floor}'
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'elevator goes up from floor {floor1} to floor {floor2}'
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'elevator goes down from floor {floor1} to floor {floor2}'
        else:
            raise 'action is not defined'


class Mystery(BaseDomain):
    # TODO: double check NL for this domain
    DOMAIN_NAME = 'mystery'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is at location {location}'
            else:
                return f'cargo {obj} is at location {location}'
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is not at location {location}'
            else:
                return f'cargo {obj} is not at location {location}'
        elif fluent.startswith('conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'{location1} is connected to location {location2}'
        elif fluent.startswith('-conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'location {location1} is not connected to location {location2}'
        elif fluent.startswith('has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} has fuel {fuel}'
        elif fluent.startswith('-has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} does not have fuel {fuel}'
        elif fluent.startswith('fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} is neighbor of location {f2}'
        elif fluent.startswith('-fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} is not neighbor of location {f2}'
        elif fluent.startswith('in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is in vehicle {vehicle}'
        elif fluent.startswith('-in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is not in vehicle {vehicle}'
        elif fluent.startswith('has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} has space {space}'
        elif fluent.startswith('-has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} does not have space {space}'
        elif fluent.startswith('space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is neighbor of space {s2}'
        elif fluent.startswith('-space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is not neighbor of space {s2}'
        else:
            # TODO for hallucination
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return f'vehicle {vehicle} moves from location {location1} to location {location2} with fuel level {fuel_level1} to {fuel_level2}'
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is loaded in vehicle {vehicle} at location {location} with space {space1} to space {space2}'
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is unloaded from vehicle {vehicle} at location {location} with space {space1} to space {space2}'
        else:
            raise 'action is not defined'


class Npuzzle(BaseDomain):
    DOMAIN_NAME = 'npuzzle'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is at position {position}'
        elif fluent.startswith('-at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is not at position {position}'
        elif fluent.startswith('neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is a neighbor of position {position2}'
        elif fluent.startswith('-neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is not a neighbor of position {position2}'
        elif fluent.startswith('empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} is empty'
        elif fluent.startswith('-empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} is not empty'
        else:
            # TODO for hallucination
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return f'tile {tile} moves from position {source} to position {destination}'
        else:
            raise 'action is not defined'


class Satellite(BaseDomain):
    DOMAIN_NAME = 'satellite'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'instrument {instrument} is on board satellite {satellite}'
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'instrument {instrument} is not on board satellite {satellite}'
        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'instrument {instrument} supports mode {mode}'
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'instrument {instrument} does not support mode {mode}'
        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'satellite {satellite} is pointing to direction {direction}'
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'satellite {satellite} is not pointing to direction {direction}'
        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'satellite {satellite} has power available'
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'satellite {satellite} does not have power available'
        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'instrument {instrument} is powered on'
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'instrument {instrument} is not powered on'
        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'instrument {instrument} is calibrated'
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'instrument {instrument} is not calibrated'
        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'Instrument has image of direction {direction} and mode {mode}'
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'Instrument does not have image of direction {direction} and mode {mode}'
        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'instrument {instrument} is calibrated to direction {direction}'
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'instrument {instrument} is not calibrated to direction {direction}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return f'satellite {satellite} turns to direction {new_dir} from direction {old_dir}'
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'instrument {instrument} is switched on on satellite {satellite}'
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return f' instrument {instrument} is switched off on satellite {satellite}'
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return f'instrument {instrument} is calibrated on satellite {satellite} to direction {direction}'
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return f'image of direction {direction} is taken with instrument {instrument} on satellite {satellite} with mode {mode}'
        else:
            raise ('action is not defined')


class Spanner(BaseDomain):
    DOMAIN_NAME = 'spanner'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"man {obj} is at location {location}"
            elif obj.startswith('nut'):
                return f"nut {obj} is at location {location}"
            else:
                return f"spanner {obj} is at location {location}"
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"man {obj} is not at location {location}"
            elif obj.startswith('nut'):
                return f"nut {obj} is not at location {location}"
            else:
                return f"spanner {obj} is not at location {location}"
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f"man {man} is carrying spanner {spanner}"
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f'man {man} is not carrying spanner {spanner}'
        elif fluent.startswith('usable('):
            spanner = self.extract_single_variable(fluent)
            return f"spanner {spanner} is usable"
        elif fluent.startswith('-usable('):
            spanner = self.extract_single_variable(fluent)
            return f"spanner {spanner} is not usable"
        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return f"nut {nut} is tightened"
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return f"nut {nut} is not tightened"
        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return f"nut {nut} is loose"
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return f"nut {nut} is not loose"
        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"location {location1} is linked to location {location2}"
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"location {location1} is not linked to location {location2}"

        # TODO for object detection
        elif fluent == 'at':
            return f'at'
        elif fluent == 'carrying':
            return f'carrying'
        elif fluent == 'useable':
            return f'useable'
        elif fluent == 'tightened':
            return f'tightened'
        elif fluent == 'loose':
            return f'loose'
        elif fluent == 'link':
            return f'link'
        else:
            # TODO for hallucination
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return f"man {man} walks from location {start} to location {end}"
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return f"man {man} picks up spanner {spanner} from location {loc}"
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return f"man {man} tightens the nut {nut} with spanner {spanner} at location {loc}"
        else:
            raise 'action is not defined'


class Zenotravel(BaseDomain):
    DOMAIN_NAME = 'zenotravel'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"person {obj} is at city {city}"
            else:
                return f"aircraft {obj} is at city {city}"
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"person {obj} is not at city {city}"
            else:
                return f"aircraft {obj} is not at city {city}"
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"person {person} is in aircraft {aircraft}"
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"person {person} is not in aircraft {aircraft}"
        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"aircraft {aircraft} has fuel level {flevel}"
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"aircraft {aircraft} does not have fuel level {flevel}"
        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is next to fuel level {fuel1}"
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is not next to fuel level {fuel1}"

        # TODO for object detection
        elif fluent == 'at':
            return f'at'
        elif fluent == 'in':
            return f'in'
        elif fluent == 'fuel_level':
            return f'fuel level'
        elif fluent == 'next':
            return f'next'
        else:
            # TODO for hallucination
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"person {person} boards the aircraft {aircraft} at location {city}"
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"passenger {person} depart the aircraft {aircraft} at location {city}"
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return f"aircraft {aircraft} flies from location {city1} to location {city2} with fuel level {fleve1} to {flevel2}"
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return f"aircraft {aircraft} zooms from location {city1} to location {city2} with fuel level {fleve1} to {flevel3}"
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return f"aircraft {aircraft} gets refueled at location {city} with fuel level {flevel1} to {flevel2}"
        else:
            raise 'action is not defined'


class Visitall(BaseDomain):
    DOMAIN_NAME = 'visitall'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is at place {place}"
        elif fluent.startswith('-at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is not at place {place}"
        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"place {place1} is connected to place {place2}"
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"place {place1} is not connected to place {place2}"
        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return f"place {place} is visited"
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return f"place {place} is not visited"
        else:
            # TODO for hallucination
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return f"move from place {place1} to place {place2}"
        else:
            raise 'action is not defined'


ALL_DOMAIN_CLASSES = [Blocksworld, Depots, Driverlog, Goldminer, Grippers, Logistics, Miconic, Mystery, Npuzzle,
                      Satellite, Spanner, Zenotravel, Visitall]
