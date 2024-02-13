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
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not clear'

        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is on the table'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not on the table'

        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is being held'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not being held'

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
            return f'stack block {b1} on block {b2}'
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

        # lost
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is lost'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return f'block {b} is not lost'

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

        # hand broken
        elif fluent.startswith('handempty'):
            return f'hand is broken'
        elif fluent.startswith('-handempty'):
            return f'hand is not broken'
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
                return f'{obj} is at {place}'
            elif obj.startswith('crate'):
                return f'{obj} is at {place}'
            elif obj.startswith('hoist'):
                return f'{obj} is at {place}'
            elif obj.startswith('pallet'):
                return f'{obj} is at {place}'
            else:
                raise ('fluent is not defined')

        elif fluent.startswith('-at('):
            obj, place = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'{obj} is not at {place}'
            elif obj.startswith('crate'):
                return f'{obj} is not at {place}'
            elif obj.startswith('hoist'):
                return f'{obj} is not at {place}'
            elif obj.startswith('pallet'):
                return f'{obj} is not at {place}'
            else:
                raise ('fluent is not defined')

        elif fluent.startswith('on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is on {obj2}'
        elif fluent.startswith('-on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not on {obj2}'

        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is in {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not in {obj2}'

        elif fluent.startswith('lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return f'{hoist} is lifting {crate}'
        elif fluent.startswith('-lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return f'{hoist} is not lifting {crate}'

        elif fluent.startswith('available('):
            hoist = self.extract_single_variable(fluent)
            return f'{hoist} is available'
        elif fluent.startswith('-available('):
            hoist = self.extract_single_variable(fluent)
            return f'{hoist} is not available'

        elif fluent.startswith('clear('):
            surface = self.extract_single_variable(fluent)
            return f'{surface} is clear'
        elif fluent.startswith('-clear('):
            surface = self.extract_single_variable(fluent)
            return f'{surface} is not clear'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return f'the {truck} is driven from the {distributor1} to the {distributor2}'
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the {crate} is lifted from the {surface} with the {hoist} from {place}'
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the {crate} drops on the {surface} with the {hoist} on the {place}'
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the {crate} is loaded by dropping it with the {hoist} in the {truck} from the {place}'
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the {crate} is unloaded by lifting it with the {hoist} from the {truck} from the {place}'
        else:
            raise ('action is not defined')

    def fluent_to_hallucinated_natural_language(self, fluent):
        flag = True
        for prefix_asp, prefix_nl in [('-', 'not'), ('', '')]:
            if fluent.startswith(f'{prefix_asp}at('):
                obj, place = self.extract_multi_variable(fluent)
                if obj.startswith('truck'):
                    return f'the {obj} is {prefix_nl} maintained at the {place}'  # maintained
                elif obj.startswith('crate'):
                    return f'the {obj} is {prefix_nl} stranded at the {place}'  # stranded
                elif obj.startswith('hoist'):
                    return f'the {obj} is {prefix_nl} near the {place}'  # near
                elif obj.startswith('pallet'):
                    return f'the {obj} is {prefix_nl} on top of the {place}'  #  on top of
                else:
                    raise ('fluent is not defined')
            elif fluent.startswith(f'{prefix_asp}on('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'the {obj1} is {prefix_nl} within the {obj2}'  # within
            elif fluent.startswith(f'{prefix_asp}in('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return f'the {obj1} is {prefix_nl} next to the {obj2}'  # next to
            elif fluent.startswith(f'{prefix_asp}lifting('):
                hoist, crate = self.extract_multi_variable(fluent)
                return f'the {hoist} is {prefix_nl} transporting the {crate}'  # transporting
            elif fluent.startswith(f'{prefix_asp}available('):
                hoist = self.extract_single_variable(fluent)
                return f'the {hoist} is {prefix_nl} free'  # free
            elif fluent.startswith(f'{prefix_asp}clear('):
                surface = self.extract_single_variable(fluent)
                return f'the {surface} is {prefix_nl} free'  # free
        if flag:
            raise ('fluent is not defined')

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return f'the {truck} is inspected at the {distributor1} and at the {distributor2}'  # inspected
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the {crate} is lowered from the {surface} with the {hoist} from the {place}'  # lowered
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return f'the {crate} is released to the {surface} with the {hoist} on the the {place}' #released
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the {crate} is transported with the {hoist} in the {truck} from the {place}' # transports
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return f'the {crate} is maneuvered with the {hoist} from the {truck} from the {place}' # stacked
        else:
            raise ('action is not defined')


class Driverlog(BaseDomain):
    DOMAIN_NAME = 'driverlog'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'the {obj} is at the {location}'
            elif obj.startswith('driver'):
                return f'the {obj} is at the {location}'
            else:
                return f'the {obj} is at the {location}'
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'the {obj} is not at the {location}'
            elif obj.startswith('driver'):
                return f'the {obj} is not at the {location}'
            else:
                return f'the {obj} is not at the {location}'
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is in the {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is not in the {obj2}'
        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is driving the {obj2}'
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is not driving the {obj2}'
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
            return f'the {obj} is empty'
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return f'the {obj} is not empty'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'load the {package} in the {truck} at location {location}'
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'unload the {package} from the {truck} at location {location}'
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'the {driver} boards the {truck} at location {location}'
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'the {driver} disembarks from the {truck} at location {location}'
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'the {driver} drives the {truck} from location {loc_from} to location {loc_to}'
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'the {driver} walks from location {loc_from} to location {loc_to}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'the {obj} is parked at location {location}' # parked at
            else:
                return f'the {obj} is near location {location}' # near
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'the {obj} is not parked at location {location}' # parked at
            else:
                return f'the {obj} is not near location {location}'  # near

        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is placed into the {obj2}' # placed
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is not  placed into the {obj2}' # near

        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is steering the {obj2}' # steering
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'the {obj1} is not steering the {obj2}'

        elif fluent.startswith('link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}' # neighbors
        elif fluent.startswith('-link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}' # neighbors
        elif fluent.startswith('-path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('empty('):
            obj = self.extract_single_variable(fluent)
            return f'the {obj} is overloaded' # overloaded
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return f'the {obj} is not overloaded'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'return the {package} in the {truck} at location {location}' # return
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'deliver the {package} from the {truck} at location {location}' # deliver
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'the {driver} inspects the {truck} at location {location}' # inspect
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'the {driver} repairs the {truck} at location {location}' # repairs
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'the {driver} checks the {truck} at location {loc_from} and location {loc_to}' # checks
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'the {driver} rests at location {loc_from} and at location {loc_to}' # rests
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
            return f'laser is at location {obj1}'
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
        else:
            raise 'fluent is not defined'

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
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot communicates at location {place}' # communicates
        elif fluent.startswith('-robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot does not communicates at location {place}' # communicates

        elif fluent.startswith('bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is detonated at location {obj1}' # detonated
        elif fluent.startswith('-bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is not detonated at location {obj1}'

        elif fluent.startswith('laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gear is at location {obj1}' # gear
        elif fluent.startswith('-laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gear is not at location {obj1}'

        elif fluent.startswith('soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'sand is at location {obj1}' # sand
        elif fluent.startswith('-soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'sand is not at location {obj1}'

        elif fluent.startswith('hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'granite is at location {obj1}' # granite
        elif fluent.startswith('-hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'granite is not at location {obj1}' #granite

        elif fluent.startswith('gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'treasure is at location {obj1}' # treasure
        elif fluent.startswith('-gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'treasure is not at location {obj1}'

        elif fluent.startswith('connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}' #neighbors
        elif fluent.startswith('-connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('arm_empty'):
            return f"robot's gripper is empty" # gripper
        elif fluent.startswith('-arm_empty'):
            return f"robot's gripper is not empty"

        elif fluent.startswith('holds_bomb'):
            return f'robot holds an explosive' # explosive
        elif fluent.startswith('-holds_bomb'):
            return f'robot does not hold an explosive'

        elif fluent.startswith('holds_laser'):
            return f'robot holds tools' # tools
        elif fluent.startswith('-holds_laser'):
            return f'robot does not hold tools'

        elif fluent.startswith('holds_gold'):
            return f'robot holds reward' # reward
        elif fluent.startswith('-holds_gold'):
            return f'robot does not hold reward'

        elif fluent.startswith('clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is not occupied' # not occupied
        elif fluent.startswith('-clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is occupied'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return f'robot rolls from location {location1} to location {location2}' # rolls
        elif action.startswith('pickup_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is ready to fire' # ready to fire
        elif action.startswith('pickup_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is set up' # set up
        elif action.startswith('putdown_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is disposed of' # disposed of
        elif action.startswith('detonate_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is malfunctions' # malfunctions
        elif action.startswith('fire_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is missing' # missing
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
            return f'the {robot} is at the {room}'
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'the {robot} is not at the {room}'

        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'the {obj} is at the {room}'
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'the {obj} is not at the {room}'

        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"the {gripper} of the {robot} is free"
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"the {gripper} of the {robot} is not free"

        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'the {robot} is carrying the {obj} with the {gripper}'
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'robot {robot} is not carrying the {obj} with the {gripper}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'the {obj} is picked from the {room} with the {gripper} by the {robot}'
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'the {robot} moves from the {room_from} to the {room_to}'
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'the {obj} is dropped in the {room} with the {gripper} by the {robot}'
        else:
            raise 'action is not defined'


    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'the {robot} is engaged in the {room}' # is engaged
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'the {robot} is not engaged in the {room}'

        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'the {obj} is transported to the {room}' # transported to
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'the {obj} is not transported to the {room}'

        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"the {gripper} of the {robot} is broken"
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"the {gripper} of the {robot} is not broken"

        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'the {robot} is loading the {obj} with the {gripper}' # loading
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'the {robot} is not loading the {obj} with the {gripper}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'the {obj} is inspected in the {room} with the {gripper} by the {robot}' # inspected
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'the {robot} checks the {room_from} and then checks the {room_to}' # checks
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'the {obj} is collected in the {room} with the {gripper} by the {robot}' # collected
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
            raise 'fluent is not defined'

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

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is outside the city {city}' # outside
        elif fluent.startswith('-in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is not outside the city {city}'

        elif fluent.startswith('at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is scanned at place {place}' # scanned
        elif fluent.startswith('-at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is not scanned at place {place}'

        elif fluent.startswith('in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is transported in vehicle {vehicle}' # transported
        elif fluent.startswith('-in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is not transported in vehicle {vehicle}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} in truck {truck} is inspected at location {location}' # inspected
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} in truck {truck} is stuck at location {location}' # stuck
        elif action.startswith('load_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} from the airplane {airplane} is inspected at location {location}' # inspected
        elif action.startswith('unload_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} unloaded from airplane {airplane} is lost at location {location}' # lost
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return f'truck {truck} is inspected at {loc_from} and refueled at {loc_to} in city {city}' # inspected, refueled
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return f'airplane {airplane} is refueled at {airport_from} and at airport {airport_to}' # refueled
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
            raise 'fluent is not defined'

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

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} waits at floor {floor}' #waits
        elif fluent.startswith('-origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not wait at floor {floor}'

        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} evacuates at floor {floor}' #evacuates
        elif fluent.startswith('-destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not evacuates at floor {floor}'

        elif fluent.startswith('above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is cleaner than floor {floor1}' # cleaner
        elif fluent.startswith('-above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is not cleaner than floor {floor1}'

        elif fluent.startswith('boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} walks' #walks
        elif fluent.startswith('-boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} does not walk'

        elif fluent.startswith('served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} rides' #rides
        elif fluent.startswith('-served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is not ride'

        elif fluent.startswith('lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is stuck at floor {floor}' # stuck
        elif fluent.startswith('-lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is not stuck at floor {floor}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} waits at floor {floor}' # waits
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} walks out at floor {floor}' # walks out
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'elevator is stuck between floor {floor1} and floor {floor2}' # stuck
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'elevator navigates from floor {floor1} to floor {floor2}' #navigates
        else:
            raise 'action is not defined'


class Mystery(BaseDomain):
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
            return f'location {location1} is connected to location {location2}'
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
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return f'vehicle {vehicle} moves from location {location1} to location {location2} with fuel level {fuel_level1} and {fuel_level2}'
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is loaded in vehicle {vehicle} with space {space1} and space {space2} at location {location}'
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is unloaded from vehicle {vehicle} with space {space1} and space {space2} at location {location}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is being maintained at location {location}' # maintained
            else:
                return f'cargo {obj} is inspected at location {location}' # inspected
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is not being maintained at location {location}'  # maintained
            else:
                return f'cargo {obj} is not inspected at location {location}' # inspected
        elif fluent.startswith('conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'location {location1} is far from location {location2}' # far
        elif fluent.startswith('-conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'location {location1} is not far from location {location2}'

        elif fluent.startswith('has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} sells fuel {fuel}' # sells
        elif fluent.startswith('-has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} does not sell fuel {fuel}'

        elif fluent.startswith('fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} and location {f2} are secure' # secure
        elif fluent.startswith('-fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} and location {f2} are not secure'

        elif fluent.startswith('in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is secured in vehicle {vehicle}' # not secured
        elif fluent.startswith('-in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is not secured in vehicle {vehicle}'

        elif fluent.startswith('has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} parks in space {space}' # parks in
        elif fluent.startswith('-has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} does not parks in space {space}'

        elif fluent.startswith('space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is in the same city as space {s2}' # is the same city as
        elif fluent.startswith('-space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is not in the same city as space {s2}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return f'vehicle {vehicle} gets pulled over at {location1}' # gets pulled over
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is transported into vehicle {vehicle} at location {location} with space {space1} to space {space2}' # transported
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} and vehicle {vehicle} are inspected at location {location}' # inspected
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
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return f'tile {tile} moves from position {source} to position {destination}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is stuck at position {position}' # stuck
        elif fluent.startswith('-at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is not stuck at position {position}'

        elif fluent.startswith('neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is far from of position {position2}' # far from
        elif fluent.startswith('-neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is not far from position {position2}'

        elif fluent.startswith('empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} exists' # does not exist
        elif fluent.startswith('-empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} does not exist'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return f'tile {tile} slides diagonally from position {source} to position {destination}' # slides diagonally
        else:
            raise 'action is not defined'


class Satellite(BaseDomain):
    DOMAIN_NAME = 'satellite'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'the {instrument} is on board the {satellite}'
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'the {instrument} is not on board the {satellite}'
        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'the {instrument} supports mode {mode}'
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'the {instrument} does not support mode {mode}'
        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'the {satellite} is pointing to the {direction}'
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'the {satellite} is not pointing to the {direction}'
        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'the {satellite} has power available'
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'the {satellite} does not have power available'
        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is powered on'
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is not powered on'
        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is calibrated'
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is not calibrated'
        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the has image of {direction} with mode {mode}'
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the does not have image of direction {direction} with mode {mode}'
        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'the {instrument} is calibrated for the {direction}'
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'the {instrument} is not calibrated for the {direction}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return f'the {satellite} turns to the {new_dir} from the {old_dir}'
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'the {instrument} is switched on the {satellite}'
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'the {instrument} is switched off on the {satellite}'
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return f'the {instrument} is calibrated on the {satellite} to the {direction}'
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return f'image of the {direction} is taken with the {instrument} on the {satellite} with mode {mode}'
        else:
            raise 'action is not defined'


    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'the {instrument} is out of order on the {satellite}' # out of order
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'the {instrument} is not out of order on the {satellite}'

        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'the {instrument} lacks mode {mode}' # lacks
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'the {instrument} does not lack mode {mode}'

        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'the {satellite} is moving to the {direction}' # moving
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'the {satellite} is not moving to the {direction}'

        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'the {satellite} is orbiting' # is orbiting
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'the {satellite} is not orbiting'

        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is functioning' # not functioning
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is not functioning'

        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is broken' # is broken
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'the {instrument} is not broken'

        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the instrument is inspecting {direction}' # inspecting
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the instrument is not inspecting {direction}'

        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'the {instrument} needs maintenance' # needs maintenance
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'the {instrument} is not need maintenance'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return f'the {satellite} cannot be pointed towards {new_dir}' #cannot be pointed towards
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'the {instrument} is being fixed' # being fixed
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'the {instrument} is dead' # dead
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return f'the {satellite} transmits the information to the {instrument}' # transmits information
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return f'the {direction} is scanned with the {instrument} on the {satellite} with a calibrated camera' # scanned calibrated camera
        else:
            raise 'action is not defined'


class Spanner(BaseDomain):
    DOMAIN_NAME = 'spanner'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is at the {location}"
            elif obj.startswith('nut'):
                return f"{obj} is at the {location}"
            else:
                return f"the {obj} is at the {location}"
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is not at the {location}"
            elif obj.startswith('nut'):
                return f"{obj} is not at the {location}"
            else:
                return f"the {obj} is not at the {location}"
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f"{man} is carrying the {spanner}"
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f'{man} is not carrying the {spanner}'
        elif fluent.startswith('useable('):
            spanner = self.extract_single_variable(fluent)
            return f"the {spanner} is usable"
        elif fluent.startswith('-useable('):
            spanner = self.extract_single_variable(fluent)
            return f"the {spanner} is not usable"
        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is tightened"
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is not tightened"
        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is loose"
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is not loose"
        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"the {location1} is linked to the {location2}"
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"the {location1} is not linked to the {location2}"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return f"{man} walks from the {start} to the {end}"
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return f"{man} picks up the {spanner} from the {loc}"
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return f"{man} tightens the the {nut} with the {spanner} at the {loc}"
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is sleeping" #sleeping
            elif obj.startswith('nut'):
                return f"{obj} is screwed" #screwed
            else:
                return f"the {obj} is at the store" #is at the store
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is not sleeping" #not sleeping
            elif obj.startswith('nut'):
                return f"the {obj} is not screwed" #not screwed
            else:
                return f"the {obj} is not at the store" #is not at the store
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f"the {spanner} is working" #working
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f'the {man} is not working'

        elif fluent.startswith('useable('):
            spanner = self.extract_single_variable(fluent)
            return f"the {spanner} is not needed"   #not needed
        elif fluent.startswith('-useable('):
            spanner = self.extract_single_variable(fluent)
            return f"the {spanner} is needed"  #needed

        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is lost" # lost
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is not lost"

        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is too small"
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return f"the {nut} is not too small"

        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"the {location1} is far away from the {location2}"
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"the {location1} is not far away from the {location2}"
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return f"{man} eats at the {start} and sleeps at the {end}" # eats, sleeps
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return f"{man} loses the {spanner} at the {loc}" #loses
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return f"{man} forgets the the {spanner} at the {loc}" # forgets
        else:
            raise 'action is not defined'


class Zenotravel(BaseDomain):
    DOMAIN_NAME = 'zenotravel'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is at the {city}"
            else:
                return f"the {obj} is at the {city}"
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is not at the {city}"
            else:
                return f"the {obj} is not at the {city}"
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is in the {aircraft}"
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is not in the {aircraft}"
        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"the {aircraft} has fuel level {flevel}"
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"the {aircraft} does not have fuel level {flevel}"
        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is next to fuel level {fuel1}"
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is not next to fuel level {fuel1}"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} boards the the {aircraft} at the {city}"
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} departs the the {aircraft} at the {city}"
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return f"the {aircraft} flies from the {city1} to the {city2} with fuel level {fleve1} to {flevel2}"
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return f"the {aircraft} zooms from the {city1} to the {city2} with fuel level {fleve1} to {flevel3}"
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return f"the {aircraft} gets refueled at the {city} with fuel level {flevel1} to {flevel2}"
        else:
            raise 'action is not defined'


    def fluent_to_hallucination_natural_language(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} explores the the {city}" # explores
            else:
                return f"the {obj} is maintained" # is maintained
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is not explore the {city}"
            else:
                return f"{obj} is not maintained"
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is boarding the the {aircraft}" # boarding
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is not boarding the the {aircraft}"

        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"the {aircraft} has a fuel leak" #leak
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"the {aircraft} does not have a fuel leak"

        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"the fuel level {fuel2} is smaller than {fuel1}" # smaller than
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"the fuel level {fuel2} is not is smaller than fuel level {fuel1}"
        else:
            raise 'fluent is not defined'

    def action_to_hallucination_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} changes the the {aircraft} at the {city}" #changes
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} forgets to board the the {aircraft} at the {city}" # forgets
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return f"the {aircraft} is in the {city1} then flies for maintenance to the {city2}" # maintenance
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return f"the {aircraft} consumes the fuel level {fleve1} and {flevel3}" # consumes
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return f"the {aircraft} goes for maitnance at location {city} and refueled with fuel {flevel1}" # maintained and refueled
        else:
            raise 'action is not defined'


class Visitall(BaseDomain):
    DOMAIN_NAME = 'visitall'

    def fluent_to_natural_language(self, fluent):
        if fluent.startswith('at_robot('):
            place = self.extract_single_variable(fluent)
            return f"robot is at the {place}"
        elif fluent.startswith('-at_robot('):
            place = self.extract_single_variable(fluent)
            return f"robot is not at the {place}"
        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"the {place1} is connected to the {place2}"
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"the {place1} is not connected to the {place2}"
        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return f"the {place} is visited"
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return f"the {place} is not visited"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return f"move from the {place1} to the {place2}"
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language(self, fluent):
        if fluent.startswith('at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is stuck at the {place}" # stuck
        elif fluent.startswith('-at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is not stuck at the {place}"

        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"the {place1} is far from to the {place2}" #far from
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"the {place1} is not far from to the {place2}"

        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return f"the {place} is observed" # observed
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return f"the {place} is not observed"

        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return f"jump from the {place1} to the {place2}" # jump
        else:
            raise 'action is not defined'


ALL_DOMAIN_CLASSES = [Blocksworld, Depots, Driverlog, Goldminer, Grippers, Logistics, Miconic, Mystery, Npuzzle, Satellite, Spanner, Visitall, Zenotravel]
