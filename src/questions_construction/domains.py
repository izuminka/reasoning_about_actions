import re
import random
import string


def strip_action_prefix(action):
    if action.startswith('action_'):
        return action[len('action_'):]
    return action


def gen_random_str(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


class BaseDomain:
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    DOMAIN_DESC_WITHOUT_RAM = None
    DOMAIN_DESC_WITH_RAM = None
    SUBSTRINGS_TO_RAND = {}
    REPLACE_REGEX_PREFIX = r'(?<!\S)'
    REPLACE_REGEX_POSTFIX = r'(?![^\s"\'\.\,:;?!])'

    def __init__(self, is_random_sub, is_ramifications):
        self.is_random_sub = is_random_sub
        self.is_ramifications = is_ramifications
        if is_ramifications:
            self.domain_description = self.DOMAIN_DESC_WITH_RAM
        else:
            self.domain_description = self.DOMAIN_DESC_WITHOUT_RAM
        if is_random_sub:
            self.domain_description = self.replace_substrings(self.domain_description, self.SUBSTRINGS_TO_RAND)

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]

    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')

    @staticmethod
    def replace_substring(text, old_sub, new_sub):
        pattern = BaseDomain.REPLACE_REGEX_PREFIX + re.escape(old_sub) + BaseDomain.REPLACE_REGEX_POSTFIX
        return re.sub(pattern, new_sub, text)

    @staticmethod
    def replace_substrings(text, obj_dict, sentence_split_token='. '):
        result = []
        sentences = text.split(sentence_split_token)
        for sentence in sentences:
            if sentence:
                sentence = sentence.lower()
                for old_word, new_word in obj_dict.items():
                    sentence = BaseDomain.replace_substring(sentence, old_word, new_word)
                sentence = sentence[0].upper() + sentence[1:]
            result.append(sentence)
        return sentence_split_token.join(result)

    def fluent_to_natural_language_helper(self, fluent):
        raise 'Implement in child class'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        raise 'Implement in child class'

    def action_to_natural_language_helper(self, action):
        raise 'Implement in child class'

    def action_to_hallucinated_natural_language_helper(self, action):
        raise 'Implement in child class'

    def fluent_to_natural_language(self, fluent, is_hallucinated=False):
        if not is_hallucinated:
            nl_fluent = self.fluent_to_natural_language_helper(fluent)
        else:
            nl_fluent = self.fluent_to_hallucinated_natural_language_helper(fluent)

        if self.is_random_sub:
            return self.replace_substring(nl_fluent, self.SUBSTRINGS_TO_RAND)
        else:
            return nl_fluent

    def action_to_natural_language(self, action, is_hallucinated=False):
        if not is_hallucinated:
            nl_action = self.action_to_natural_language_helper(action)
        else:
            nl_action = self.action_to_hallucinated_natural_language_helper(action)

        if self.is_random_sub:
            return self.replace_substring(nl_action, self.SUBSTRINGS_TO_RAND)
        else:
            return nl_action


class Blocksworld(BaseDomain):
    DOMAIN_NAME = 'blocksworld'
    DERIVED_FLUENTS = ['clear(', 'handempty']
    DOMAIN_DESC_WITHOUT_RAM = (
        'Picking up a block is only possible if that block is clear, on the table, and the hand is empty. '
        'By picking up that block, it makes that block not present on the table and not clear. '
        'It also leads to the block being held and makes the hand not empty. '
        'Putting down the block can only be executed if the block is being held. '
        'Putting down the block causes that block to be clear and on the table. '
        'It also causes the hand to be not holding the block and makes the hand empty. '
        'A block can be stacked on the second block if it is being held and the second block is clear. '
        'By stacking the first block on the second, it causes the first block to clear and on top of the second block. '
        'Meanwhile, the second block is not clear, and the hand becomes empty as it is not holding the block. '
        'The block can also be unstacked from the top of the second block only if the hand is empty and the first block is clear and on top of the second block. '
        'Unstacking the first block from the second causes the second block to be clear. '
        'The first block is now being held, not clear, and not on top of the second block. '
        'Furthermore, the hand is not empty.')
    DOMAIN_DESC_WITH_RAM = (
        'Picking up a block is only possible if that block is clear, on the table, and the hand is empty. '
        'Picking up the block leads to the block being held. '
        "Putting down the block can only be executed if the block is being held. "
        "Putting down the block causes the block to be on the table. "
        "A block can be stacked on the second block if it is being held and the second block is clear. "
        "By stacking the first block on the second, it causes the first block to be on top of the second block. "
        "The block can also be unstacked from the top of the second block only if the hand is empty and the first block is clear and on top of the second block. "
        "Unstacking the first block from the second causes first block to be held "
        "A block is said to be clear if it is not being held and there are no blocks that are on top of it. "
        "The hand is said to be empty if and only if it is not holding any block. "
        "The block can only be at one place at a time.")

    # FOR RANDOM SUBSTITUTIONS
    OBJ_TYPE_TO_RAND = {'block': 'qbyyxzqvdh', 'blocks': 'qbyyxzqvdhs'}
    ACTION_TO_RAND = {'pick up': 'ovyuecllio', 'picking up': 'ovyuecllio', 'picked up': 'ovyuecllio',
                      'put down': 'xskgihccqt', 'puts down': 'xskgihccqt', 'putting down': 'xskgihccqt',
                      'stack': 'oscckwdtoh', 'stacks': 'oscckwdtoh', 'stacking': 'oscckwdtoh', 'stacked': 'oscckwdtoh',
                      'unstack': 'wxqdwukszo', 'unstacks': 'wxqdwukszo', 'unstacking': 'wxqdwukszo',
                      'unstacked': 'wxqdwukszo'}
    FLUENT_TO_RAND = {'table': 'zewwtdxhfs',
                      'clear': 'ormkfgqwve',
                      'holding': 'casqqrrojp', 'held': 'casqqrrojp', 'holds': 'casqqrrojp',
                      'empty': 'yqttlkcqqj',
                      'hand': 'egpbpdtalq'}
    SUBSTRINGS_TO_RAND = OBJ_TYPE_TO_RAND | ACTION_TO_RAND | FLUENT_TO_RAND

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'block {b1} is on block {b2}',
                f'block {b1} is on top of block {b2}',
                f'block {b1} is placed on top of block {b2}'
            ])
            # return f'block {b1} is on block {b2}'
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'block {b1} is not on block {b2}',
                f'block {b1} is not on top of block {b2}',
                f'block {b1} is not placed on top of block {b2}'
            ])
            # return f'block {b1} is not on block {b2}'

        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is clear'
            ])
            # return f'block {b} is clear'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not clear'
            ])
            # return f'block {b} is not clear'

        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is on the table',
                f'block {b} is located at the table'
            ])
            # return f'block {b} is on the table'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not on the table',
                f'block {b} is not located at the table'
            ])
            # return f'block {b} is not on the table'

        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is being held',
                f'the hand is holding the block {b}',
                f'block {b} is being held by the hand'
            ])
            # return f'block {b} is being held'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not being held',
                f'the hand is not holding the block {b}',
                f'block {b} is not being held by the hand'
            ])
            # return f'block {b} is not being held'

        elif fluent.startswith('handempty'):
            return random.choice([
                'hand is empty',
                'hand is not holding anything'
            ])
            # return f'hand is empty'
        elif fluent.startswith('-handempty'):
            return random.choice([
                f'hand is not empty',
                f'hand is holding some block'
            ])
            # return f'hand is not empty'
        else:
            raise Exception('fluent is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return random.choice([
                f'block {block_name} is picked up',
                f'block {block_name} is picked up by the hand',
                f'block {block_name} is picked up from the table'
            ])
            # return f'block {block_name} is picked up'
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return random.choice([
                f'block {block_name} is put down',
                f'block {block_name} is put down on the table',
                f'the hand puts down the block {block_name}'
            ])
            # return f'block {block_name} is put down'
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return random.choice([
                f'block {b1} is unstacked from block {b2}',
                f'block {b1} is unstacked from top of block {b2}',
                f'from top of block {b2}, block {b1} is unstacked'
            ])
            # return f'block {b1} is unstacked from block {b2}'
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return random.choice([
                f'block {b1} is stacked on top of block {b2}',
                f'on top of block {b2}, block {b1} is stacked'
            ])
            # return f'block {b1} is stacked on top block {b2}'
        else:
            raise Exception('action is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # under
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'block {b1} is under block {b2}',
                f'block {b1} is positioned under block {b2}'
            ])
            # return f'block {b1} is under block {b2}'
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'block {b1} is not under block {b2}',
                f'block {b1} is not positioned under block {b2}'
            ])
            # return f'block {b1} is not under block {b2}'

        # lost
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is lost',
                f'block {b} has become lost'
            ])
            # return f'block {b} is lost'
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not lost',
                f'block {b} has not been lost'
            ])
            # return f'block {b} is not lost'

        # thrown
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is being thrown',
                f'block {b} has been thrown'
            ])
            # return f'block {b} is being thrown'
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not being thrown',
                f'block {b} has not been thrown'
            ])
            # return f'block {b} is not being thrown'

        # under table
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is under the table',
                f'block {b} is positioned under the table'
            ])
            # return f'block {b} is under the table'
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return random.choice([
                f'block {b} is not under the table',
                f'block {b} is not positioned under the table'
            ])
            # return f'block {b} is not under the table'

        # hand broken
        elif fluent.startswith('handempty'):
            return random.choice([
                f'hand is broken',
                f'hand is now broken'
            ])
            # return f'hand is broken'
        elif fluent.startswith('-handempty'):
            return random.choice([
                f'hand is not broken',
                f'hand is not broken anymore'
            ])
            # return f'hand is not broken'
        else:
            raise Exception('fluent is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return random.choice([
                f'block {block_name} is lifted',
                f'block {block_name} is lifted by the hand',
                f'the hand lifts the block {block_name}'
            ])
            # return f'block {block_name} is lifted'  # lift
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return random.choice([
                f'block {block_name} is lowered',
                f'block {block_name} is lowered by the hand',
                f'block {block_name} is lowered to the table'
            ])
            # return f'block {block_name} is lowered'  # lower
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return random.choice([
                f'block {b1} is removed from block {b2}',
                f'block {b1} is removed from top of block {b2}'
                f'from top of block {b2}, block {b1} is removed'
            ])
            # return f'block {b1} is removed from from block {b2}'  # remove
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return random.choice([
                f'block {b1} is crashed from block {b2}'
                f'block {b1} is crashed from top of block {b2}',
                f'from top of block {b2}, block {b1} is crashed'
            ])
            # return f'block {b1} is crashed from block {b2}'  # crashed
        else:
            raise Exception('action is not defined')


class Depots(BaseDomain):
    DOMAIN_NAME = 'depots'
    DOMAIN_DESC_WITHOUT_RAM = (
        'A surface can be a pallet or a crate. '
        'A truck can be driven from one location to another only if it is present at the first location. '
        'Driving the truck makes the truck to be present at the final destination and not at the starting location. '
        'A hoist can lift a crate from a surface only when the hoist and the crate are present in the same location, the hoist is available, the crate is present on the surface, and the crate is clear. '
        'Lifting causes the hoist to lift the crate, the crate to be not in that location, not clear, and not on top of the previous surface, which is now clear. '
        'Moreover, lifting the crate causes the hoist to be not available. '
        'Dropping the crate is possible only if the hoist, crate, and surface are present in the same location, the hoist is lifting the crate, and the surface is clear. '
        'Dropping the crate causes it to be on top of the surface, be present in the location where it was dropped, and be clear. '
        'It also causes the hoist to become available, and not lift the crate. The surface on which the crate was dropped becomes not clear. '
        'Loading the crate on a truck can be executed only when the crate and truck are present in the same location, and the hoist is lifting the crate. '
        'Loading the crate onto the truck causes the hoist to be available and not lifting the crate, and crate to be in the truck. '
        'Unloading the crate from the truck can be done only if the hoist and truck are in the same place, the hoist is available, and the crate is present in the truck. '
        'Unloading the crate from the truck causes the crate to be not in the truck, and the hoist to be lifting the crate and not available.')
    DOMAIN_DESC_WITH_RAM = (
        'A surface can be a pallet or a crate. '
        "A truck can be driven from one location to another only if it is present at the first location. "
        "Driving the truck makes the truck to be present at the final destination. "
        "A hoist can lift a crate from a surface only when the hoist and the crate are present in the same location, the hoist is available, the crate is present on the surface, and the crate is clear."
        "Lifting causes the hoist to lift the crate. "
        "Dropping the crate is possible only if the hoist, crate, and surface are present in the same location, the hoist is lifting the crate, and the surface is clear. "
        "Dropping the crate causes it to be on top of the surface and be present at the location where it was dropped. It also causes the hoist to not lift the crate. "
        "Loading the crate on a truck can be executed only when the crate and truck are present in the same location and the hoist is lifting the crate. "
        "Loading the crate onto the truck causes the hoist to be not lifting the crate, and the crate to be in the truck. "
        "Unloading the crate from the truck can be done only if the hoist and truck are in the same place, the hoist is available, and the crate is present in the truck. "
        "Unloading the crate from the truck causes the crate to be not in the truck, and the hoist to be lifting the crate. "
        "A hoist is available if and only if it does not lift anything (any crate). "
        "A surface  is clear if and only if no crates are on top of that surface. "
        "A crate is clear if and only if no hoist is lifting that crate. "
        "A truck can be only at one location. "
        "A crate can only be at one location. "
        "A crate can only be on top of one surface. ")
    DERIVED_FLUENTS = ['clear(', 'available(']

    SUBSTRINGS_TO_RAND = {
        'surface': 'fshxjwxean', 'surfaces': 'fshxjwxean',
        'pallet': 'tzrwjuotxz', 'pallets': 'tzrwjuotxz',
        'crate': 'pjrluufopq', 'crates': 'pjrluufopq',
        'truck': 'nblmdziyqf', 'trucks': 'nblmdziyqf',
        'location': 'eejxtwabwx', 'locations': 'eejxtwabwx',
        'clear': 'sypgozifms',
        'available': 'xlhhnyciys',
        'hoist': 'suhmddooyi', 'hoists': 'suhmddooyi',
        'driven': 'jzmscukkyy', 'drive': 'jzmscukkyy', 'driving': 'jzmscukkyy', 'drove': 'jzmscukkyy',
        'lift': 'aeaygzpsjc', 'lifting': 'aeaygzpsjc', 'lifts': 'aeaygzpsjc', 'lifted': 'aeaygzpsjc',
        'drop': 'uckhudtpif', 'drops': 'uckhudtpif', 'dropping': 'uckhudtpif', 'dropped': 'uckhudtpif',
        'load': 'gjqgfjtbnf', 'loads': 'gjqgfjtbnf', 'loading': 'gjqgfjtbnf', 'loaded': 'gjqgfjtbnf',
        'unload': 'gpztfzvsux', 'unloads': 'gpztfzvsux', 'unloading': 'gpztfzvsux', 'unloaded': 'gpztfzvsux'}

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, place = self.extract_multi_variable(fluent)
            if (obj.startswith('truck') or obj.startswith('crate')
                    or obj.startswith('hoist') or obj.startswith('pallet')):
                return random.choice([
                    f'{obj} is at {place}',
                    f'{obj} is located at {place}',
                    f'{place} is where {obj} is located',
                    f'{obj} can be found located at {place}'
                ])
                # return f'{obj} is at {place}'
            else:
                raise Exception('fluent is not defined')

        elif fluent.startswith('-at('):
            obj, place = self.extract_multi_variable(fluent)
            if (obj.startswith('truck') or obj.startswith('crate')
                    or obj.startswith('hoist') or obj.startswith('pallet')):
                return random.choice([
                    f'{obj} is not at {place}',
                    f'{obj} is not located at {place}',
                    f'{place} is where {obj} is not located',
                    f'{obj} cannot be found located at {place}'
                ])
                # return f'{obj} is not at {place}'
            else:
                raise Exception('fluent is not defined')

        elif fluent.startswith('on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'{obj1} is on {obj2}',
                f'{obj2} has {obj1} on it',
                f'{obj1} is on top of {obj2}'
            ])
            # return f'{obj1} is on {obj2}'
        elif fluent.startswith('-on('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'{obj1} is not on {obj2}',
                f'{obj2} does not have {obj1} on it',
                f'{obj1} is not on top of {obj2}'
            ])
            # return f'{obj1} is not on {obj2}'

        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'{obj1} is in {obj2}',
                f'{obj2} contains {obj1}',
                f'{obj1} is inside {obj2}'
            ])
            # return f'{obj1} is in {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return random.choice([
                f'{obj1} is not in {obj2}',
                f'{obj2} does not contain {obj1}',
                f'{obj1} is not inside {obj2}'
            ])
            # return f'{obj1} is not in {obj2}'

        elif fluent.startswith('lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return random.choice([
                f'{hoist} is lifting {crate}',
                f'{hoist} is raising {crate}',
                f'{hoist} is elevating {crate}'
            ])
            # return f'{hoist} is lifting {crate}'
        elif fluent.startswith('-lifting('):
            hoist, crate = self.extract_multi_variable(fluent)
            return random.choice([
                f'{hoist} is not lifting {crate}',
                f'{hoist} is not raising {crate}',
                f'{hoist} is not elevating {crate}'
            ])
            # return f'{hoist} is not lifting {crate}'

        elif fluent.startswith('available('):
            hoist = self.extract_single_variable(fluent)
            return random.choice([
                f'{hoist} is available',
                f'{hoist} is accessible',
                f'{hoist} is available for work'
            ])
            # return f'{hoist} is available'
        elif fluent.startswith('-available('):
            hoist = self.extract_single_variable(fluent)
            return random.choice([
                f'{hoist} is not available',
                f'{hoist} is not accessible',
                f'{hoist} is not available for work'
            ])
            # return f'{hoist} is not available'

        elif fluent.startswith('clear('):
            surface = self.extract_single_variable(fluent)
            return random.choice([
                f'{surface} is clear',
                f'{surface} is clear of any crates'
            ])
            # return f'{surface} is clear'
        elif fluent.startswith('-clear('):
            surface = self.extract_single_variable(fluent)
            return random.choice([
                f'{surface} is not clear',
                f'{surface} is not clear of any crates'
            ])
            # return f'{surface} is not clear'
        else:
            raise Exception('fluent is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return random.choice([
                f'{truck} is driven from {distributor1} to {distributor2}',
                f'{truck} is driven to {distributor2} from {distributor1}',
                f'from {distributor1}, {truck} is driven to {distributor2}'
            ])
            # return f'{truck} is driven from {distributor1} to {distributor2}'
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return random.choice([
                f'{hoist} lifts {crate} from {surface} at {place}',
                f'{crate} is lifted from {surface} at {place} by {hoist}',
                f'at {place}, {hoist} lifts {crate} off {surface}'
            ])
            # return f'{hoist} lifts {crate} from {surface} at {place}'
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return random.choice([
                f'{hoist} drops {crate} on {surface} at {place}',
                f'{crate} is dropped on {surface} at {place} by {hoist}',
                f'at {place}, {hoist} drops {crate} on {surface}'
            ])
            # return f'{hoist} drops {crate} on {surface} at {place}'
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is loaded by {hoist} into {truck} at {place}',
                f'{hoist} loads {crate} into {truck} at {place}',
                f'at {place}, {hoist} loads {crate} into {truck}'
            ])
            # return f'{crate} is loaded by {hoist} into {truck} at {place}'
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is unloaded by {hoist} from {truck} at {place}',
                f'{hoist} unloads {crate} from {truck} at {place}',
                f'at {place}, {hoist} unloads {crate} from {truck}'
            ])
            # return f'{crate} is unloaded by {hoist} from {truck} at {place}'
        else:
            raise Exception('action is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        flag = True
        for prefix_asp, prefix_nl in [('-', 'not '), ('', '')]:
            if fluent.startswith(f'{prefix_asp}at('):
                obj, place = self.extract_multi_variable(fluent)
                if obj.startswith('truck'):
                    return random.choice([
                        f'{obj} is {prefix_nl}maintained at {place}',
                        f'at {place}, {obj} is {prefix_nl}is maintained'
                    ])
                    # return f'{obj} is {prefix_nl} maintained at {place}'  # maintained
                elif obj.startswith('crate'):
                    return random.choice([
                        f'{obj} is {prefix_nl}stranded at {place}',
                        f'at {place}, {obj} is {prefix_nl}stranded'
                    ])
                    # return f'{obj} is {prefix_nl} stranded at {place}'  # stranded
                elif obj.startswith('hoist'):
                    return random.choice([
                        f'{obj} is {prefix_nl}near {place}',
                        f'{obj} is {prefix_nl}located near {place}'
                    ])
                    # return f'{obj} is {prefix_nl} near {place}'  # near
                elif obj.startswith('pallet'):  ############## On is a defined fluent in this domain
                    return random.choice([
                        f'{obj} is {prefix_nl}on top of {place}'
                    ])
                    # return f'{obj} is {prefix_nl} on top of {place}'  # on top of
                else:
                    raise Exception('fluent is not defined')
            elif fluent.startswith(f'{prefix_asp}on('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return random.choice([
                    f'{obj1} is {prefix_nl}within {obj2}',
                    f'{obj1} does {prefix_nl}exists within {obj2}'
                ])
                # return f'{obj1} is {prefix_nl} within {obj2}'  # within
            elif fluent.startswith(f'{prefix_asp}in('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                return random.choice([
                    f'{obj1} is {prefix_nl}next to {obj2}',
                    f'{obj1} is {prefix_nl}situated next to {obj2}'
                ])
                # return f'{obj1} is {prefix_nl} next to {obj2}'  # next to
            elif fluent.startswith(f'{prefix_asp}lifting('):
                hoist, crate = self.extract_multi_variable(fluent)
                return random.choice([
                    f'{hoist} is {prefix_nl}transporting {crate}',
                    f'{crate} is {prefix_nl}being transported by {hoist}'
                ])
                # return f'{hoist} is {prefix_nl} transporting {crate}'  # transporting
            elif fluent.startswith(f'{prefix_asp}available('):  ############### Free means the same thing as available
                hoist = self.extract_single_variable(fluent)
                return random.choice([
                    f'{hoist} is {prefix_nl} free',
                ])
                # return f'{hoist} is {prefix_nl} free'  # free
            elif fluent.startswith(f'{prefix_asp}clear('):  ############### Free means the same thing as clear
                surface = self.extract_single_variable(fluent)
                return random.choice([
                    f'{surface} is {prefix_nl} free'
                ])
                # return f'{surface} is {prefix_nl} free'  # free
        if flag:
            raise Exception('fluent is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return random.choice([
                f'{truck} is inspected at {distributor1} and at {distributor2}',
                f'inspection of {truck} occurs at {distributor1} and {distributor2}'
            ])
            # return f'{truck} is inspected at {distributor1} and at {distributor2}'  # inspected
        elif action.startswith('lift('):  ############### Lowered means the same thing as drop
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is lowered from {surface} with {hoist} from {place}'
            ])
            # return f'{crate} is lowered from {surface} with {hoist} from {place}'  # lowered
        elif action.startswith('drop('):  ############### Released can mean the same thing as drop
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is released to {surface} with {hoist} on {place}'
            ])
            # return f'{crate} is released to {surface} with {hoist} on {place}'  # released
        elif action.startswith('load('):  ############### Trnsported can mean the same thing as Load
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is transported with {hoist} in {truck} from {place}'
            ])
            # return f'{crate} is transported with {hoist} in {truck} from {place}'  # transports
        elif action.startswith('unload('):  ############### Maneuvered can mean the same thing as Unload
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return random.choice([
                f'{crate} is maneuvered with {hoist} from {truck} from {place}'
            ])
            # return f'{crate} is maneuvered with {hoist} from {truck} from {place}'  # stacked
        else:
            raise Exception('action is not defined')


class Driverlog(BaseDomain):
    DOMAIN_NAME = 'driverlog'
    DOMAIN_DESC_WITHOUT_RAM = (
        'To load an object onto a truck at a location, the truck and the object must be at the same location. '
        'Loading the object onto the truck causes the object to not be at its initial location and to be inside the truck. '
        'To unload an object from a truck at a location, the truck must be at the specified location and the object should be in the truck. '
        'Unloading the object from the truck causes the object to not be inside the truck and to be at the specified location. '
        'To board a truck, the driver and the truck must be at the same location, and the truck must be empty. '
        'Boarding the truck makes the driver not be at the initial location, to be driving the truck, and the truck becomes not empty. '
        'Disembarking from a truck is only possible when the driver is driving the truck and the truck is at the location. '
        'Disembarking from the truck causes the driver to stop driving the truck, be at the specified location, and the truck to be empty. '
        'To drive a truck from one location to another, the truck must be at the initial location, the driver must be driving the truck, and there must be a link between the initial and final locations. '
        'Driving the truck causes it to no longer be at the initial location but to be at the final location. '
        'To walk from one location to another, the driver must be at the initial location, and there must be a path between the initial and final locations. '
        'Walking causes the driver to no longer be at the initial location but to be at the final location.')
    DOMAIN_DESC_WITH_RAM = (
        'To load an object onto a truck at a location, the truck and the object must be at the same location. '
        'Loading the object onto the truck causes the object to be inside the truck. '
        'To unload an object from a truck at a location, the truck must be at the same location and the object should be in the truck. '
        'Unloading the object from the truck causes the object to be at the specified location. '
        "To board a truck, the driver and the truck must be at the same location, and the truck must be empty. Boarding the truck causes the driver to be driving the truck. "
        "Disembarking from a truck is only possible when the driver is driving the truck and the truck is at the location. "
        "Disembarking from the truck causes the driver to be at the specified location. "
        "To drive a truck from one location to another, the truck must be at the initial location, the driver must be driving the truck, and there must be a link between the initial and final locations. "
        "Driving the truck causes it to be at the final location. "
        "To walk from one location to another, the driver must be at the initial location, and there must be a path between the initial and final locations. "
        "Walking from inital location to final location, causes the driver to be at the final location. "
        "A truck is empty if and only if it is not driven by anyone (any driver). "
        "A driver is driving the truck if and only if the driver is not at a location "
        "An object can only be at one location. "
        "A driver can only be at one location.")
    DERIVED_FLUENTS = ['empty']

    SUBSTRINGS_TO_RAND = {
        'truck': 'zkkizjecwh', 'trucks': 'zkkizjecwh',
        'location': 'iatympbexj', 'locations': 'iatympbexj',
        'object': 'omkfkvxwrg', 'objects': 'omkfkvxwrg',
        'driver': 'fxwdnwxasu', 'drivers': 'fxwdnwxasu',
        'link': 'umwttodbts', 'links': 'umwttodbts',
        'path': 'zgbnmmdljx', 'paths': 'zgbnmmdljx',
        'empty': 'fgrxzszxhm',
        'load': 'yvlcghamlt', 'loads': 'yvlcghamlt', 'loading': 'yvlcghamlt', 'loaded': 'yvlcghamlt',
        'unload': 'zfjywbftzj', 'unloads': 'zfjywbftzj', 'unloading': 'zfjywbftzj',
        'unloaded': 'zfjywbftzj',
        'board': 'kqrkdhivua', 'boards': 'kqrkdhivua', 'boarding': 'kqrkdhivua',
        'boarded': 'kqrkdhivua',
        'disembark': 'qstuhdgygm', 'disembarks': 'qstuhdgygm', 'disembarking': 'qstuhdgygm',
        'disembarked': 'qstuhdgygm',
        'drive': 'wqfrddftie', 'drives': 'wqfrddftie', 'driving': 'wqfrddftie', 'drove': 'wqfrddftie',
        'driven': 'wqfrddftie',
        'walk': 'elasopyqsh', 'walks': 'elasopyqsh', 'walking': 'elasopyqsh', 'walked': 'elasopyqsh',
    }

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            return f'{obj} is at loaction {location}'
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            return f'{obj} is not at location {location}'
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is in {obj2}'
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not in {obj2}'
        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is driving {obj2}'
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not driving {obj2}'
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
            return f'{obj} is empty'
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return f'{obj} is not empty'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'{package} is loaded in {truck} at location {location}'
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'{package} is unload from {truck} at location {location}'
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'{driver} boards {truck} at location {location}'
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'{driver} disembarks from {truck} at location {location}'
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'{driver} drives {truck} from location {loc_from} to location {loc_to}'
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'{driver} walks from location {loc_from} to location {loc_to}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'{obj} is parked at location {location}'  # parked at
            else:
                return f'{obj} is near location {location}'  # near
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                return f'{obj} is not parked at location {location}'  # parked at
            else:
                return f'{obj} is not near location {location}'  # near

        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is placed into {obj2}'  # placed
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not  placed into {obj2}'  # near

        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is steering {obj2}'  # steering
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'{obj1} is not steering {obj2}'

        elif fluent.startswith('link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}'  # neighbors
        elif fluent.startswith('-link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}'  # neighbors
        elif fluent.startswith('-path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('empty('):
            obj = self.extract_single_variable(fluent)
            return f'{obj} is overloaded'  # overloaded
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return f'{obj} is not overloaded'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'{package} is returned at location {location}'  # return
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'{package} is delivered at location {location}'  # deliver
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'{driver} inspects {truck} at location {location}'  # inspect
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return f'{driver} repairs {truck} at location {location}'  # repairs
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'{driver} checks {truck} at location {loc_from} and location {loc_to}'  # checks
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return f'{driver} rests at location {loc_from} and at location {loc_to}'  # rests
        else:
            raise 'action is not defined'


class Goldminer(BaseDomain):
    DOMAIN_NAME = 'goldminer'
    DOMAIN_DESC_WITHOUT_RAM = (
        'A robot can move from one location to another if it is currently at the starting location, the locations are connected, and the destination is clear. '
        'Moving causes the robot to be at the new location, and it is no longer at the previous location. '
        'The robot is capable of picking up a laser at a specific location if it is at that location, the laser is present at that location, and the robot\'s arm is empty. '
        'Picking up the laser results in the robot\'s arm being no longer empty, holding the laser, and the laser no longer being at that location. '
        'Similarly, the robot can pick up a bomb at a particular location if it is at that location, the bomb is present at that location, and the robot\'s arm is empty. Picking up the bomb results in the robot\'s arm being no longer empty, and it now holds the bomb. '
        'The robot can put down a laser at a specific location if it is at that location and currently holds the laser. '
        'Putting down the laser results in the robot\'s arm being empty, not holding the laser, and the laser being at that location. '
        'A robot that is present at one location, can detonate the bomb at another location only if the robot is holding a bomb, the locations are connected and there is a soft rock at the second location. '
        'Detonating the bomb results in the robot\'s arm becoming empty and not holding the bomb anymore. The second location becomes clear and the soft rock is destroyed. '
        'Firing a laser from one location to another is executable only if the robot is at the starting location, holds a laser, and the locations are connected. '
        'Firing the laser results in the destination being clear, with no soft rocks, no gold, and no hard rocks at the destination. '
        'Finally, the robot can pick up gold at a specific location if it is at that location, the robot\'s arm is empty, and there is gold at that location. '
        'Picking up gold results in the robot\'s arm no longer being empty, and it now holds the gold.')
    DOMAIN_DESC_WITH_RAM = (
        'A robot can move from one location to another if it is currently at the starting location, the locations are connected, and the destination is clear. '
        "Moving causes the robot to be at the new location. "

        "The robot can pick up a laser at a specific location only if it is at that location, the laser is present at that location, and the robot's arm is empty. "
        "Picking up the laser results in the robot holding the laser. "

        "Similarly, the robot can pick up a bomb at a particular location if it is at that location, the bomb is present at that location, and the robot's arm is empty. "
        "Picking up the bomb results in the robot holding the bomb. "

        "The robot can put down a laser at a specific location if it is at that location and currently holds the laser. Putting down the laser results in the laser being at that location. "

        "A robot that is present at one location, can detonate the bomb at another location only if the robot is holding a bomb, the locations are connected and there is a soft rock at the second location. "
        "Detonating the bomb results in the robot not holding the bomb anymore and the soft rock being destroyed. "

        "Firing a laser from one location to another is executable only if the robot is at the starting location, holds a laser, and the locations are connected. "
        "Firing the laser results in the destination having no soft rocks, no gold, and no hard rocks. "

        "Finally, the robot can pick up gold at a specific location if it is at that location, the robot's arm is empty, and there is gold at that location. "
        "Picking up gold results in the robot holding the gold. "

        "A robot cannot be in two places at once. "
        "The arm is said to be empty if and only if it is not holding a laser and not holding a bomb and not holding gold. "
        "The place is clear if and only if it does not contain any soft rock, gold, or hard rock. "
        "The robot is holding a laser if and only if the laser is not at a location. ")

    DERIVED_FLUENTS = ['arm_empty', 'clear(']
    SUBSTRINGS_TO_RAND = {
        'robot': 'oiycijmjmo',
        'location': 'cltqghvirt', 'locations': 'cltqghvirt',
        'laser': 'jaakaxcemj',
        'clear': 'qvnmedqflj',
        'arm': 'jawtollkbp', 'arms': 'jawtollkbp',
        'empty': 'kqtvognkhw',
        'bomb': 'ojyinshkhj',
        'gold': 'gbxztwroqz',
        'soft rock': 'erzvzboobp', 'soft rocks': 'erzvzboobp',
        'hard rock': 'vcybvdqmgp', 'hard rocks': 'vcybvdqmgp',
        'detonate': 'vputhhsycf', 'detonates': 'vputhhsycf', 'detonating': 'vputhhsycf',
        'find': 'qwyadblmhl', 'finds': 'qwyadblmhl', 'finding': 'qwyadblmhl', 'found': 'qwyadblmhl',
        'move': 'zdmlakgkqc', 'moves': 'zdmlakgkqc', 'moving': 'zdmlakgkqc', 'moved': 'zdmlakgkqc',
        'pick up': 'wlcfexwxse', 'picks up': 'wlcfexwxse', 'picking up': 'wlcfexwxse', 'picked up': 'wlcfexwxse',
        'put down': 'lrlcipamts', 'puts down': 'lrlcipamts', 'putting down': 'lrlcipamts',
        'fire': 'arvmgimcpi', 'fires': 'arvmgimcpi', 'firing': 'arvmgimcpi', 'fired': 'arvmgimcpi'}

    def fluent_to_natural_language_helper(self, fluent):
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

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return f'robot moves from location {location1} to location {location2}'
        elif action.startswith('pickup_laser('):
            location = self.extract_single_variable(action)
            return f'laser is picked up at location {location}'
        elif action.startswith('pickup_bomb('):
            location = self.extract_single_variable(action)
            return f'bomb is picked up at location {location}'
        elif action.startswith('putdown_laser('):
            location = self.extract_single_variable(action)
            return f'robot puts down laser at location {location}'
        elif action.startswith('detonate_bomb('):
            location1, location2 = self.extract_multi_variable(action)
            return f'bomb is detontaed at location {location2} from location {location1}'
        elif action.startswith('fire_laser('):
            location1, location2 = self.extract_multi_variable(action)
            return f'laser is fired at location {location2} from location {location1}'
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return f'gold is picked up at location {location}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot communicates at location {place}'  # communicates
        elif fluent.startswith('-robot_at('):
            place = self.extract_single_variable(fluent)
            return f'robot does not communicates at location {place}'  # communicates

        elif fluent.startswith('bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is detonated at location {obj1}'  # detonated
        elif fluent.startswith('-bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'bomb is not detonated at location {obj1}'

        elif fluent.startswith('laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gear is at location {obj1}'  # gear
        elif fluent.startswith('-laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'gear is not at location {obj1}'

        elif fluent.startswith('soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'sand is at location {obj1}'  # sand
        elif fluent.startswith('-soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'sand is not at location {obj1}'

        elif fluent.startswith('hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'granite is at location {obj1}'  # granite
        elif fluent.startswith('-hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'granite is not at location {obj1}'  # granite

        elif fluent.startswith('gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'treasure is at location {obj1}'  # treasure
        elif fluent.startswith('-gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return f'treasure is not at location {obj1}'

        elif fluent.startswith('connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} neighbors location {obj2}'  # neighbors
        elif fluent.startswith('-connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return f'location {obj1} does not neighbor location {obj2}'

        elif fluent.startswith('arm_empty'):
            return f"robot's gripper is empty"  # gripper
        elif fluent.startswith('-arm_empty'):
            return f"robot's gripper is not empty"

        elif fluent.startswith('holds_bomb'):
            return f'robot holds an explosive'  # explosive
        elif fluent.startswith('-holds_bomb'):
            return f'robot does not hold an explosive'

        elif fluent.startswith('holds_laser'):
            return f'robot holds tools'  # tools
        elif fluent.startswith('-holds_laser'):
            return f'robot does not hold tools'

        elif fluent.startswith('holds_gold'):
            return f'robot holds reward'  # reward
        elif fluent.startswith('-holds_gold'):
            return f'robot does not hold reward'

        elif fluent.startswith('clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is not occupied'  # not occupied
        elif fluent.startswith('-clear('):
            location = self.extract_single_variable(fluent)
            return f'location {location} is occupied'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return f'robot rolls from location {location1} to location {location2}'  # rolls
        elif action.startswith('pickup_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is ready to fire'  # ready to fire
        elif action.startswith('pickup_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is set up'  # set up
        elif action.startswith('putdown_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is disposed of'  # disposed of
        elif action.startswith('detonate_bomb('):
            bomb = self.extract_single_variable(action)
            return f'bomb {bomb} is malfunctions'  # malfunctions
        elif action.startswith('fire_laser('):
            laser = self.extract_single_variable(action)
            return f'laser {laser} is missing'  # missing
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return f'gold is picked up at location {location}'
        else:
            raise ('action is not defined')


class Grippers(BaseDomain):
    DOMAIN_NAME = 'grippers'
    DERIVED_FLUENTS = ['free']
    DOMAIN_DESC_WITHOUT_RAM = (
        'A robot can move from a specified room if it is in that room. '
        'Moving the robot causes it to be not in the said room but in the destination room. '
        'A robot can pick up the object using a gripper only when the object and the robot are in the same room and the mentioned gripper is free. '
        'Picking up the object causes the robot to carry that object using its gripper, the object to be not in that room, and the said gripper not free. '
        'Dropping the object in a specified room is only executable when the robot is carrying that object using its gripper, and the robot is in the said room. '
        'Dropping an object in a room makes the object be in that room, the gripper be free and the robot not carrying the object anymore.')
    DOMAIN_DESC_WITH_RAM = (
        "A robot can move from a specified room if it is in that room. "
        "Moving the robot causes  it to be in the destination room. "

        "A robot can pick up the object using a gripper only when the object and the robot are in the same room and the mentioned gripper is free. "
        "Picking up the object causes the robot to carry the object via its gripper. "

        "Dropping the object in a specified room is executable if and only if the robot is carrying the object using its gripper, and the robot is in the room. "
        "Dropping the object causes the robot to not carry the object. "

        "A robot's gripper is said to be free if the robot is not carrying any of the objects with a gripper. "
        "If the robot is carrying the object then the object is not in the room. "
        "If the robot is not carrying the object then the object a in the room. "
        "Robot can only be at one place. ")

    SUBSTRINGS_TO_RAND = {
        'robot': 'jjjrptnvkh', 'robots': 'jjjrptnvkh',
        'room': 'ixokqrvnqn', 'rooms': 'ixokqrvnqn',
        'destination': 'ezrqqoajas', 'destinations': 'ezrqqoajas',
        'object': 'wtdcrmrabz', 'objects': 'wtdcrmrabz',
        'gripper': 'yegitqlmuq', 'grippers': 'yegitqlmuq',
        'move': 'zucvbghqwl', 'moves': 'zucvbghqwl', 'moving': 'zucvbghqwl', 'moved': 'zucvbghqwl',
        'pick': 'angmkdpvfb', 'picks': 'angmkdpvfb', 'picking': 'angmkdpvfb', 'picked': 'angmkdpvfb',
        'drop': 'qhfmsjkotn', 'drops': 'qhfmsjkotn', 'dropping': 'qhfmsjkotn',
        'dropped': 'qhfmsjkotn',
        'transport': 'kseqanhkzt', 'transports': 'kseqanhkzt', 'transporting': 'kseqanhkzt',
        'transported': 'kseqanhkzt',
        'carry': 'rwgciavjpj', 'carries': 'rwgciavjpj', 'carrying': 'rwgciavjpj',
        'carried': 'rwgciavjpj'}

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'{robot} is at {room}'
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'{robot} is not at {room}'

        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'{obj} is at {room}'
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'{obj} is not at {room}'

        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"{gripper} of {robot} is free"
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"{gripper} of {robot} is not free"

        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'{robot} is carrying {obj} with {gripper}'
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'{robot} is not carrying {obj} with {gripper}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'{obj} is picked from {room} with {gripper} by {robot}'
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'{robot} moves from {room_from} to {room_to}'
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'{obj} is dropped in {room} with {gripper} by {robot}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'{robot} is engaged in {room}'  # is engaged
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return f'{robot} is not engaged in {room}'

        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'{obj} is transported to {room}'  # transported to
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return f'{obj} is not transported to {room}'

        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"{gripper} of {robot} is broken"
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return f"{gripper} of {robot} is not broken"

        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'{robot} is loading {obj} with {gripper}'  # loading
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return f'{robot} is not loading {obj} with {gripper}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'{obj} is inspected in {room} with {gripper} by {robot}'  # inspected
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return f'{robot} checks {room_from} and then checks {room_to}'  # checks
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return f'{obj} is collected in {room} with {gripper} by {robot}'  # collected
        else:
            raise 'action is not defined'


class Logistics(BaseDomain):
    DOMAIN_NAME = 'logistics'
    DOMAIN_DESC_WITHOUT_RAM = (
        'Loading a package onto a truck is only possible if both the package and the truck are in the same location. '
        'Loading the package onto the truck causes the package not to be at that location but to be in the truck. '
        'Loading a package onto an airplane is possible if and only if both the package and the airplane are in the same location. '
        'Loading the package onto the airplane causes the package to not be at the location but in the airplane. '
        'Unloading from a truck is executable if the truck is in a location and the package is in the truck. '
        'Unloading the package from the truck causes the package to be not in the truck anymore, but be present in that location. '
        'Unloading a package from an airplane is possible only when the package is in the airplane and the plane is in a location. '
        'Unloading from the airplane makes the package present in that location and not in the plane anymore. '
        'Driving a truck is possible only when the truck is in a location where the source and destination are in the same city. '
        'Driving the truck causes it to be at the destination and not at the source. Flying an airplane is possible if and only if the airplane is at a location. '
        'Flying the airplane causes it to be not at the source location but at the destination location.')
    DOMAIN_DESC_WITH_RAM = (
        'Loading a package onto a truck is only possible if both the package and the truck are in the same location. Loading the package onto the truck causes the package to be in the truck. '
        "Loading a package onto an airplane is possible if and only if both the package and the airplane are in the same location. "
        "Loading the package onto the airplane causes the package to be in the airplane. "

        "Unloading from a truck is executable if the truck is in a location and the package is in the truck. "
        "Unloading the package from the truck causes the package to be present in that location. "
        "Unloading a package from an airplane is possible only when the package is in the airplane and the plane is in the location. "
        "Unloading from the airplane makes the package present in that location. "

        "Driving a truck is possible only when the truck is in a location where the source and destination are in the same city. "
        "Driving the truck causes it to be at the destination. "

        "Flying an airplane is possible if and only if the airplane is at a location. "
        "Flying the airplane causes it to be at the destination location. "

        "If a package is in a truck or a plane, it is not at any location. If a package is not in a truck or an airplane then it is at some location. "
        "A truck can only be at one location at a time. A plane can only be in one location at a time.")
    DERIVED_FLUENTS = []  # kept this empty because no derived fluents for this domain
    SUBSTRINGS_TO_RAND = {
        'package': 'tnzistccqp', 'packages': 'tnzistccqp',
        'truck': 'pvcuetihtl', 'trucks': 'pvcuetihtl',
        'airplane': 'xmyqeckfwm', 'airplanes': 'xmyqeckfwm',
        'airport': 'qpplrkefyr', 'airports': 'qpplrkefyr',
        'location': 'wesxmnrgzy', 'locations': 'wesxmnrgzy',
        'object': 'causdnkeoz', 'objects': 'causdnkeoz',
        'vehicle': 'qmgahdodkq', 'vehicles': 'qmgahdodkq',
        'city': 'bpzwevlomd', 'cities': 'bpzwevlomd',
        'load': 'nxrnxkjybr', 'loads': 'nxrnxkjybr', 'loading': 'nxrnxkjybr', 'loaded': 'nxrnxkjybr',
        'unload': 'bdfszwzdpi', 'unloads': 'bdfszwzdpi', 'unloading': 'bdfszwzdpi',
        'unloaded': 'bdfszwzdpi',
        'drive': 'umcjrdgfyn', 'drives': 'umcjrdgfyn', 'driving': 'umcjrdgfyn', 'drove': 'umcjrdgfyn',
        'driven': 'umcjrdgfyn',
        'fly': 'umnkjqinar', 'flies': 'umnkjqinar', 'flying': 'umnkjqinar', 'flied': 'umnkjqinar', 'flown': 'umnkjqinar'
    }

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('in_city('):
            airport, city = self.extract_multi_variable(fluent)
            return f'airport {airport} is in city {city}'
        elif fluent.startswith('-in_city('):
            airport, city = self.extract_multi_variable(fluent)
            return f'airport {airport} is not in city {city}'
        elif fluent.startswith('at('):
            physical_object, airport = self.extract_multi_variable(fluent)
            return f'object {physical_object} is at airport {airport}'
        elif fluent.startswith('-at('):
            physical_object, airport = self.extract_multi_variable(fluent)
            return f'object {physical_object} is not at airport {airport}'
        elif fluent.startswith('in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is in vehicle {vehicle}'
        elif fluent.startswith('-in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is not in vehicle {vehicle}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, airport = self.extract_multi_variable(action)
            return f'package {package} is loaded in truck {truck} at airport {airport}'
        elif action.startswith('unload_truck('):
            package, truck, airport = self.extract_multi_variable(action)
            return f'package {package} is unloaded from truck {truck} at airport {airport}'
        elif action.startswith('load_airplane('):
            package, airplane, airport = self.extract_multi_variable(action)
            return f'package {package} is loaded into airplane {airplane} at airport {airport}'
        elif action.startswith('unload_airplane('):
            package, airplane, airport = self.extract_multi_variable(action)
            return f'package {package} is unloaded from airplane {airplane} at airport {airport}'
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return f'truck {truck} is driven from airport {loc_from} to airport {loc_to} in city {city}'
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return f'airplane {airplane} is flown from airport {airport_from} to airport {airport_to}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is outside the city {city}'  # outside
        elif fluent.startswith('-in_city('):
            place, city = self.extract_multi_variable(fluent)
            return f'place {place} is not outside the city {city}'

        elif fluent.startswith('at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is scanned at place {place}'  # scanned
        elif fluent.startswith('-at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return f'object {physical_object} is not scanned at place {place}'

        elif fluent.startswith('in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is transported in vehicle {vehicle}'  # transported
        elif fluent.startswith('-in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return f'package {package} is not transported in vehicle {vehicle}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} in truck {truck} is inspected at location {location}'  # inspected
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return f'package {package} in truck {truck} is stuck at location {location}'  # stuck
        elif action.startswith('load_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} from the airplane {airplane} is inspected at location {location}'  # inspected
        elif action.startswith('unload_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return f'package {package} unloaded from airplane {airplane} is lost at location {location}'  # lost
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return f'truck {truck} is inspected at {loc_from} and refueled at {loc_to} in city {city}'  # inspected, refueled
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return f'airplane {airplane} is refueled at {airport_from} and at airport {airport_to}'  # refueled
        else:
            raise 'action is not defined'


class Miconic(BaseDomain):
    DOMAIN_NAME = 'miconic'
    DOMAIN_DESC_WITHOUT_RAM = (
        'A passenger can board the lift on a floor only if the lift is on that floor and the passenger\'s travel originates from that floor. '
        'Boarding the lift causes the passenger to be boarded. Departing from the lift is executable only when the lift is on the floor, the passenger is boarded, and the passenger\'s destination is on that floor. '
        'Departing from the lift causes the passenger to be served and not boarded. A lift can go up from one floor to another if and only if it is currently on the floor and the destination floor is above the source floor. '
        'Going up makes the lift on the destination floor. A lift can go down from one floor to another if and only if it is currently on a floor and the source floor is above the destination floor. '
        'Going down makes the lift on the destination floor.')
    DOMAIN_DESC_WITH_RAM = (
        "A passenger can board the lift on a floor only if the lift is on that floor and the passenger's travel originates from that floor. "
        "Boarding the lift causes the passenger to be boarded. "

        "Departing from the lift is executable only when the lift is on the floor, the passenger is boarded, and the passenger's destination is on that floor. "
        "Departing from the lift causes the passenger to be served. "

        "A lift can go up from one floor to another if and only if it is currently on the floor and the destination floor is above the source floor. "
        "Going up makes the lift on the destination floor. A lift can go down from one floor to another if and only if it is currently on a floor and the source floor is above the destination floor. "
        "Going down makes the lift on the destination floor. "

        "A lift can only be on one floor at a time. "
        "If the passenger is served, then the passenger is not boarded.")
    DERIVED_FLUENTS = []  # TODO double check
    SUBSTRINGS_TO_RAND = {
        'up': 'lfapuhgnsn',
        'down': 'mmphaaxcri',
        'source': 'outpkddlno',
        'above': 'idfiasmopc',
        'served': 'vpdiuemmjp',
        'elevator': 'jbbturclrd', 'elevators': 'jbbturclrd',
        'passenger': 'tucyshtaky', 'passengers': 'tucyshtaky',
        'destination': 'gqrormjdyu', 'destinations': 'gqrormjdyu',
        'lift': 'ywjmmwrawz', 'lifts': 'ywjmmwrawz',
        'floor': 'rhwfsepbez', 'floors': 'rhwfsepbez',
        'board': 'bidmuazwal', 'boards': 'bidmuazwal', 'boarding': 'bidmuazwal', 'boarded': 'bidmuazwal',
        'depart': 'jbctpepaja', 'departs': 'jbctpepaja', 'departing': 'jbctpepaja','departed': 'jbctpepaja'
    }

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} enters at floor {floor}'
        elif fluent.startswith('-origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not enter at floor {floor}'
        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'destination of passenger {passenger} is floor {floor}'
        elif fluent.startswith('-destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'destination of passenger {passenger} is not floor {floor}'
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

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} boards at floor {floor}'
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} departs at floor {floor}'
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'the elevator goes up from floor {floor1} to floor {floor2}'
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'the elevator goes down from floor {floor1} to floor {floor2}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} waits at floor {floor}'  # waits
        elif fluent.startswith('-origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not wait at floor {floor}'

        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} evacuates at floor {floor}'  # evacuates
        elif fluent.startswith('-destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return f'passenger {passenger} does not evacuates at floor {floor}'

        elif fluent.startswith('above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is cleaner than floor {floor1}'  # cleaner
        elif fluent.startswith('-above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return f'floor {floor2} is not cleaner than floor {floor1}'

        elif fluent.startswith('boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} walks'  # walks
        elif fluent.startswith('-boarded('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} does not walk'

        elif fluent.startswith('served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} rides'  # rides
        elif fluent.startswith('-served('):
            passenger = self.extract_single_variable(fluent)
            return f'passenger {passenger} is not ride'

        elif fluent.startswith('lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is stuck at floor {floor}'  # stuck
        elif fluent.startswith('-lift_at('):
            floor = self.extract_single_variable(fluent)
            return f'lift is not stuck at floor {floor}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} waits at floor {floor}'  # waits
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return f'passenger {passenger} walks out at floor {floor}'  # walks out
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'the elevator is stuck between floor {floor1} and floor {floor2}'  # stuck
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return f'the elevator navigates from floor {floor1} to floor {floor2}'  # navigates
        else:
            raise 'action is not defined'


class Mystery(BaseDomain):
    DOMAIN_NAME = 'mystery'
    DOMAIN_DESC_WITHOUT_RAM = (
        'A vehicle has a set of spaces inside next to each other for carrying cargo. '
        'Locations can have sets of fuel that neighbor each other. '
        'A vehicle can move from the initial to the final location if it is currently at the initial location, the initial and final locations are connected, the initial location has fuel, and there is an additional fuel next to it. '
        'As a result, a vehicle is no longer at the original location, it is at the destination, there is no first set of fuel at the initial location, but a second set of fuel is present at the initial location. '
        'A vehicle can be loaded if cargo is at a location, the vehicle is at the same location, the vehicle has space, and there is an additional space in the vehicle. '
        'When cargo is loaded into the vehicle, cargo is no longer at a location, cargo is now in the vehicle, the first space in the vehicle is occupied, but the vehicle has a secondary space. '
        'A vehicle can be unloaded if the cargo is in the vehicle, the vehicle is at a location, the vehicle has space, and there is an additional space next to it. '
        'When a vehicle is unloaded, cargo is no longer in the vehicle, cargo is at a location, the vehicle no longer has the initial space, and there is a secondary space.')
    DOMAIN_DESC_WITH_RAM = (
        "Moving a vehicle from source location to destination location is executable if the vehicle is at source location, there is a connection between the source location and destination location, and the location's fuel level has some neighboring level. "
        "Moving a vehicle from source location to destination location causes the vehicle to be present at the destination location and decreases the location's fuel level to its next level. "

        "A cargo can be loaded onto a vehicle if the cargo and the vehicle are at the same location and the vehicle has some space. "
        "When a cargo is loaded into the vehicle, it is in the vehicle. It also decreases the vehicle's space to its next level. "

        "A cargo can be unloaded from a vehicle if the cargo is in the vehicle. "
        "When a cargo is unloaded from the vehicle, it is at the same location as that of the vehicle. It also increases the vehicle's space to its next higher level. "

        "Vehicle can only be at one location at a time. "
        "Cargo can only be at one place at a time. "
        "The location's fuel level is unique. "
        "The vehicle's amount of space is unique. ")
    DERIVED_FLUENTS = []  # TODO double check
    SUBSTRINGS_TO_RAND = {
        'vehicle': 'xduwfabpov', 'vehicles': 'xduwfabpov',
        'cargo': 'mrxzbljtex', 'cargos': 'mrxzbljtex',
        'location': 'wrbrffbbsf', 'locations': 'wrbrffbbsf',
        'fuel': 'vyumzovixm', 'fuels': 'vyumzovixm',
        'space': 'kiurijzhmd', 'spaces': 'kiurijzhmd',
        'connect': 'qqqxlayhxq', 'connects': 'qqqxlayhxq', 'connecting': 'qqqxlayhxq', 'connected': 'qqqxlayhxq'}

    def fluent_to_natural_language_helper(self, fluent):
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
            return f'fuel level {f1} neighbours fuel level {f2}'
        elif fluent.startswith('-fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'fuel level {f1} does not neighbour fuel level {f2}'

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
            return f'space {s1} neighbours space {s2}'
        elif fluent.startswith('-space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} does not neighbour space {s2}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return f'vehicle {vehicle} moves to location {location2} from location {location1} that has fuel level {fuel_level1} and {fuel_level2}'
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is loaded in vehicle {vehicle} with space {space1} and space {space2} at location {location}'
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is unloaded from vehicle {vehicle} with space {space1} and space {space2} at location {location}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is being maintained at location {location}'  # maintained
            else:
                return f'cargo {obj} is inspected at location {location}'  # inspected
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return f'vehicle {obj} is not being maintained at location {location}'  # maintained
            else:
                return f'cargo {obj} is not inspected at location {location}'  # inspected
        elif fluent.startswith('conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'location {location1} is far from location {location2}'  # far
        elif fluent.startswith('-conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f'location {location1} is not far from location {location2}'

        elif fluent.startswith('has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} sells fuel {fuel}'  # sells
        elif fluent.startswith('-has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return f'location {location} does not sell fuel {fuel}'

        elif fluent.startswith('fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} and location {f2} are secure'  # secure
        elif fluent.startswith('-fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return f'location {f1} and location {f2} are not secure'

        elif fluent.startswith('in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is secured in vehicle {vehicle}'  # not secured
        elif fluent.startswith('-in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return f'cargo {cargo} is not secured in vehicle {vehicle}'

        elif fluent.startswith('has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} parks in space {space}'  # parks in
        elif fluent.startswith('-has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return f'vehicle {vehicle} does not parks in space {space}'

        elif fluent.startswith('space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is in the same city as space {s2}'  # is the same city as
        elif fluent.startswith('-space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return f'space {s1} is not in the same city as space {s2}'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return f'vehicle {vehicle} gets pulled over at {location1}'  # gets pulled over
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} is transported into vehicle {vehicle} at location {location} with space {space1} to space {space2}'  # transported
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return f'cargo {cargo} and vehicle {vehicle} are inspected at location {location}'  # inspected
        else:
            raise 'action is not defined'


class Npuzzle(BaseDomain):
    DOMAIN_NAME = 'npuzzle'
    DERIVED_FLUENTS = ['empty']
    DOMAIN_DESC_WITHOUT_RAM = (
        'Moving a tile from source position to destination position is executable if source position and destination positions are neighbors i.e next to each other, destination position is empty and initially the tile is at source position. '
        'Moving a tile from source position to destination position causes the tile to be present at destination position, destination position to be not empty, and causes source position to be empty.')
    DOMAIN_DESC_WITH_RAM = (
        'Moving a tile from source position to destination position is executable if source position and destination positions are neighbors i.e next to each other, destination position is empty and initially the tile is at source position. '
        "A position is not empty if the tile is at that position. A tile cannot be on multiple positions at the same time.")
    SUBSTRINGS_TO_RAND = {
        'tile': 'gkxiurkpij', 'tiles': 'gkxiurkpij',
        'move': 'edclnosigi', 'moves': 'edclnosigi', 'moving': 'edclnosigi', 'moved': 'edclnosigi',
        'source': 'dfqdjcpgle',
        'destination': 'jfyxocsjve',
        'empty': 'vigzxelnpn',
        'neighbor': 'wbsxhcqjhh', 'neighbors': 'wbsxhcqjhh'}

    def fluent_to_natural_language_helper(self, fluent):
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

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return f'tile {tile} is moved from position {source} to position {destination}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is stuck at position {position}'  # stuck
        elif fluent.startswith('-at('):
            tile, position = self.extract_multi_variable(fluent)
            return f'tile {tile} is not stuck at position {position}'

        elif fluent.startswith('neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is far from of position {position2}'  # far from
        elif fluent.startswith('-neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return f'position {position1} is not far from position {position2}'

        elif fluent.startswith('empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} exists'  # does not exist
        elif fluent.startswith('-empty('):
            position = self.extract_single_variable(fluent)
            return f'position {position} does not exist'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return f'tile {tile} is slid diagonally from position {source} to position {destination}'  # slides diagonally
        else:
            raise 'action is not defined'


class Satellite(BaseDomain):
    DOMAIN_NAME = 'satellite'
    DOMAIN_DESC_WITHOUT_RAM = (
        'Turning a satellite to the intended direction from the source direction is executable if the satellite is facing to the source direction initially. '
        'Turning a satellite to the intended direction from the source direction causes the satellite to point to the intended direction, it also causes the satellite to not point at the source direction. '
        'Switching on the instrument on a satellite is executable if the instrument is onboard with the satellite and power is available on the satellite. '
        'Switching on the instrument on a satellite causes the instrument to power on but not calibrated. '
        'Switching on the instrument causes the satellite to not have power available. '
        'Switching off the instrument on a satellite is executable if the instrument is onboard with the satellite and the instrument is powered on. '
        'Switching off the instrument on the satellite causes the instrument to power off, and causes the satellite to have power available. '
        'Calibrating the instrument on the satellite to the intended direction is executable if the instrument is onboard with the satellite, calibration target of the instrument is set to the intended direction, the satellite is pointing to the intended direction and the instrument is powered on. '
        'Calibrating the instrument on the satellite to the intended direction causes the instrument to be calibrated. '
        'Taking an image on the satellite with the instrument set to a mode which is facing to the intended direction is executable if the instrument is calibrated, instrument is onboard with the satellite, the instrument supports the mode to which it is set to, the instrument is powered on and the satellite is pointing to the intended direction. '
        'Taking an image on the satellite with the instrument set to a mode facing to the intended direction causes it to capture an image of the intended direction with the mode with which the instrument was set to.')
    DOMAIN_DESC_WITH_RAM = (
        'Turning a satellite to the intended direction from the source direction is executable if the satellite is facing to the source direction initially. '
        "Turning a satellite to the intended direction from the source direction causes the satellite to point to the intended direction. The satellite cannot point to two different directions simultaneously. "

        "Switching on the instrument on a satellite is executable if the instrument is onboard with the satellite and power is available on the satellite. "
        "Switching on the instrument on a satellite causes the instrument to be powered on but not calibrated. If the instrument is powered on then the satellite does not have power. "

        "Switching off the instrument on a satellite is executable if the instrument is onboard with the satellite and the instrument is powered on. "
        "Switching off the instrument on the satellite causes the instrument to be powered off. If the instrument is not powered on then power is available on the satellite. "

        "Calibrating the instrument on the satellite to the intended direction is executable if the instrument is onboard with the satellite, calibration target of the instrument is set to the intended direction, the satellite is pointing to the intended direction and the instrument is powered on. "
        "Calibrating the instrument on the satellite to the intended direction causes the instrument to be calibrated. "

        "Taking an image on the satellite with the instrument set to a mode which is facing to the intended direction is executable if the instrument is calibrated, instrument is onboard with the satellite, the instrument supports the mode to which it is set to, the instrument is powered on and the satellite is pointing to the intended direction. "
        "Taking an image on the satellite with the instrument set to a mode facing to the intended direction causes it to capture an image of the intended direction with the mode with which the instrument was set to. ")
    DERIVED_FLUENTS = ['power_avail(']
    SUBSTRINGS_TO_RAND = {
        'satellite': 'zzofnkbesk', 'satellites': 'zzofnkbesk',
        'source': 'uuwgcgehnr',
        'mode': 'kegmrmllim', 'modes': 'kegmrmllim',
        'destination': 'izwwbtklpt',
        'direction': 'apdptereua', 'directions': 'apdptereua',
        'instrument': 'rstzlaxvor', 'instruments': 'rstzlaxvor',
        'onboard': 'icafejchri',
        'image': 'fetzcryvyb', 'images': 'fetzcryvyb',
        'turn': 'gwuqwrsowb', 'turns': 'gwuqwrsowb', 'turning': 'gwuqwrsowb', 'turned': 'gwuqwrsowb',
        'switch': 'sqsicvmhrn', 'switches': 'sqsicvmhrn', 'switching': 'sqsicvmhrn', 'switched': 'sqsicvmhrn',
        'calibrate': 'dymysndcxa', 'calibrates': 'dymysndcxa', 'calibrating': 'dymysndcxa', 'calibrated': 'dymysndcxa',
        'take': 'idrpvqprlo', 'takes': 'idrpvqprlo', 'taking': 'idrpvqprlo', 'taken': 'idrpvqprlo',
        'power': 'ymikwvufrq', 'powers': 'ymikwvufrq', 'powering': 'ymikwvufrq', 'powered': 'ymikwvufrq'}

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'{instrument} is on board {satellite}'
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'{instrument} is not on board {satellite}'
        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'{instrument} supports {mode}'
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'{instrument} does not support {mode}'
        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'{satellite} is pointing to {direction}'
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'{satellite} is not pointing to {direction}'
        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'{satellite} has power available'
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'{satellite} does not have power available'
        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is powered on'
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is not powered on'
        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is calibrated'
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is not calibrated'
        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'there is an image of {direction} in {mode}'
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'there is no image of direction {direction} in {mode}'
        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'{instrument} is calibrated for {direction}'
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'{instrument} is not calibrated for {direction}'
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return f'{satellite} turns to {new_dir} from {old_dir}'
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'{instrument} on {satellite} is switched on'
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'{instrument} on {satellite} is switched off'
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return f'{instrument} is calibrated on {satellite} to {direction}'
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return f'image of {direction} is taken with {instrument} on {satellite} in {mode}'
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'{instrument} is out of order on {satellite}'  # out of order
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return f'{instrument} is not out of order on {satellite}'

        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'{instrument} lacks mode {mode}'  # lacks
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return f'{instrument} does not lack mode {mode}'

        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'{satellite} is moving to {direction}'  # moving
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return f'{satellite} is not moving to {direction}'

        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'{satellite} is orbiting'  # is orbiting
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return f'{satellite} is not orbiting'

        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is functioning'  # not functioning
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is not functioning'

        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is broken'  # is broken
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return f'{instrument} is not broken'

        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the instrument is inspecting {direction}'  # inspecting
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return f'the instrument is not inspecting {direction}'

        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'{instrument} needs maintenance'  # needs maintenance
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return f'{instrument} is not need maintenance'
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return f'{satellite} cannot be pointed towards {new_dir}'  # cannot be pointed towards
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'{instrument} is being fixed'  # being fixed
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return f'{instrument} is dead'  # dead
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return f'{satellite} transmits the information to {instrument}'  # transmits information
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return f'{direction} is scanned with {instrument} on {satellite} with a calibrated camera'  # scanned calibrated camera
        else:
            raise 'action is not defined'


class Spanner(BaseDomain):
    DOMAIN_NAME = 'spanner'
    DOMAIN_DESC_WITHOUT_RAM = (
        'Walking from start location to destination location is executable if the man is at the start location and there is a link between start and the destination location. '
        'Walking from start location to destination location causes the man to be at the destination location and not be at the start location. '
        'Picking up a spanner from a location is executable if the man and the spanner is at the same location. '
        'Picking up a spanner from a location causes the man to carry the spanner, and the spanner to be not at any location. '
        'Tightening the nut at a location with a spanner is executable if the man and the nut are at the same location, the man is carrying the spanner, the spanner is usable, and the nut is loose. '
        'Tightening the nut at a location with a spanner causes the nut to be not loose, the spanner to be unusable and the nut to be tightened.')
    DOMAIN_DESC_WITH_RAM = (
        'Walking from start location to destination location is executable if the man is at the start location initially and there is a link between start and the destination location. '
        "Walking from start location to destination location causes the man to be at the destination location after the walk action from start location to destination location is executed. "

        "Picking up a spanner from start location is executable if the man is at start location and spanner is at start location. Picking up a spanner from the start location causes the man to carry the spanner. "

        "Tightening the nut at start location with a spanner is executable if the man is at start location, nut is at the start location, the man is carrying the spanner, the spanner is usable and the nut is loose. "
        "Tightening the nut at start location with a spanner causes the nut to be tightened. "

        "A man cannot be at two different places at the same time. "
        "The spanner is not at a location if it is being hold by the man. "
        "The nut is not loose if and only if it is tightened. "
        "The spanner is not usable if and only if the nut is tightened. ")
    DERIVED_FLUENTS = ['useable(']
    SUBSTRINGS_TO_RAND = {
        'nut': 'uwdhnrpile', 'nuts': 'uwdhnrpile',
        'man': 'bmojqrwpdg',
        'usable': 'fgbcjqnbgp',
        'spanner': 'ujzeqlcecc', 'spanners': 'ujzeqlcecc',
        'location': 'pyliwxfzrf', 'locations': 'pyliwxfzrf',
        'link': 'qzylwqxpoq', 'links': 'qzylwqxpoq', 'linking': 'qzylwqxpoq', 'linked': 'qzylwqxpoq',
        'walk': 'fvuxqntacz', 'walks': 'fvuxqntacz', 'walking': 'fvuxqntacz', 'walked': 'fvuxqntacz',
        'pick': 'rcholfpyyj', 'picks': 'rcholfpyyj', 'picking': 'rcholfpyyj', 'picked': 'rcholfpyyj',
        'tighten': 'xvxccombol', 'tightens': 'xvxccombol', 'tightening': 'xvxccombol', 'tightened': 'xvxccombol',
    }

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            return f"{obj} is at {location}"
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            return f"{obj} is not at {location}"
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f"{man} is carrying {spanner}"
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f'{man} is not carrying {spanner}'
        elif fluent.startswith('useable('):
            spanner = self.extract_single_variable(fluent)
            return f"{spanner} is usable"
        elif fluent.startswith('-useable('):
            spanner = self.extract_single_variable(fluent)
            return f"{spanner} is not usable"
        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is tightened"
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is not tightened"
        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is loose"
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is not loose"
        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"{location1} is linked to {location2}"
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"{location1} is not linked to {location2}"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return f"{man} walks from {start} to {end}"
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return f"{man} picks up {spanner} from {loc}"
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return f"{man} tightens {nut} with {spanner} at {loc}"
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is sleeping"  # sleeping
            elif obj.startswith('nut'):
                return f"{obj} is screwed"  # screwed
            else:
                return f"{obj} is at the store"  # is at the store
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('man'):
                return f"{obj} is not sleeping"  # not sleeping
            elif obj.startswith('nut'):
                return f"{obj} is not screwed"  # not screwed
            else:
                return f"{obj} is not at the store"  # is not at the store
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f"{spanner} is working"  # working
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return f'{man} is not working'

        elif fluent.startswith('useable('):
            spanner = self.extract_single_variable(fluent)
            return f"{spanner} is not needed"  # not needed
        elif fluent.startswith('-useable('):
            spanner = self.extract_single_variable(fluent)
            return f"{spanner} is needed"  # needed

        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is lost"  # lost
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is not lost"

        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is too small"
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return f"{nut} is not too small"

        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"{location1} is far away from {location2}"
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return f"{location1} is not far away from {location2}"
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return f"{man} eats at {start} and sleeps at {end}"  # eats, sleeps
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return f"{man} loses {spanner} at {loc}"  # loses
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return f"{man} forgets {spanner} at {loc}"  # forgets
        else:
            raise 'action is not defined'


class Zenotravel(BaseDomain):
    DOMAIN_NAME = 'zenotravel'
    DOMAIN_DESC_WITHOUT_RAM = (
        'Boarding a person in a city is executable if the person and the aircraft are both present in the city. '
        'Boarding a person in the city causes the person to be in the aircraft and not present in the city. '
        'Debarking a person in a city is executable if the person is in the aircraft and the aircraft is present in the city. '
        'Debarking a person in the city causes the person to be present in the city and not present in the aircraft. '
        'Flying an aircraft from a city to another city is executable if the aircraft is present in the city and has an initial fuel level that is next to (i.e., higher than) some fuel level. '
        'Flying the aircraft from a city to a destination city causes the aircraft to be present in the destination city and not present in the original city. '
        'It also decreases the fuel level of the aircraft to the next level. '
        'Zooming the aircraft from a city to a destination city is executable if the aircraft is present in the city and has some initial fuel level that is at least two levels up compared to the lowest possible fuel level. '
        'It causes the aircraft to be present in the destination city and not present in the original city. It also decreases the fuel level of the aircraft two levels down. '
        'Refueling the aircraft in a city is executable if the aircraft is in the city. '
        'It changes the current fuel level to its next level.')
    DOMAIN_DESC_WITH_RAM = (
        'Boarding a person in a city is executable if the person and the aircraft are both present in the city. '
        "Boarding a person in the city causes the person to be in the aircraft. "

        "Debarking a person in a city is executable if the person is in the aircraft and the aircraft is present in the city. "
        "Debarking a person in the city causes the person to be present in the city. "

        "Flying an aircraft from a city to another city is executable if the aircraft is present in the city and has some initial fuel level that is more than the lowest possible fuel level. "
        "Flying the aircraft from a city to a destination city causes the aircraft to be present in the destination city. It also decreases the fuel level of the aircraft to the next level. "

        "Zooming the aircraft from a city to a destination city is executable if the aircraft is present in the city and has some initial fuel level that is at least two levels up compared to the lowest possible fuel level. "
        "It causes the aircraft to be present in the destination city. It also decreases the fuel level of the aircraft two levels down. "

        "Refueling the aircraft in a city is executable if the aircraft is in the city. It changes the current fuel level to its next level. "

        "A person is not present in a city if the person is in some aircraft. "
        "The aircraft cannot be in two different cities at the same time. "
        "An aircraft cannot have two different fuel levels. "
        "Person can only be at one place.")
    DERIVED_FLUENTS = []  # TODO double check
    SUBSTRINGS_TO_RAND = {
        'board': 'jxfvtxvzgh', 'boards': 'jxfvtxvzgh', 'boarding': 'jxfvtxvzgh', 'boarded': 'jxfvtxvzgh',
        'debark': 'jnjwzqrpms', 'debarks': 'jnjwzqrpms', 'debarking': 'jnjwzqrpms', 'debarked': 'jnjwzqrpms',
        'fly': 'gartdizjnu', 'flies': 'gartdizjnu', 'flying': 'gartdizjnu', 'flown': 'gartdizjnu',
        'zoom': 'rqdfjbixnz', 'zooms': 'rqdfjbixnz', 'zooming': 'rqdfjbixnz', 'zoomed': 'rqdfjbixnz',
        'refuel': 'egufeqdcrz', 'refuels': 'egufeqdcrz', 'refueling': 'egufeqdcrz', 'refueled': 'egufeqdcrz',
        'fuel': 'njzcihffcg', 'fuels': 'njzcihffcg', 'fueling': 'njzcihffcg', 'fueled': 'njzcihffcg',

        'person': 'ihpgygxfoe', 'persons': 'ihpgygxfoe', 'people': 'ihpgygxfoe',
        'city': 'uibqqmoerq', 'cities': 'uibqqmoerq',
        'aircraft': 'psjemaawdi', 'aircrafts': 'psjemaawdi',
        'airport': 'vuvceigmai', 'airports': 'vuvceigmai',
        'source': 'xfdqznnlrs',
        'destination': 'ohytkfeoay', 'destinations': 'ohytkfeoay',
        'level': 'ndozmmwian', 'levels': 'ndozmmwian'}

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is at {city}"
            else:
                return f"{obj} is at {city}"
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is not at {city}"
            else:
                return f"{obj} is not at {city}"
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is in {aircraft}"
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is not in {aircraft}"
        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"{aircraft} has fuel level {flevel}"
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"{aircraft} does not have fuel level {flevel}"
        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is next to fuel level {fuel1}"
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"fuel level {fuel2} is not next to fuel level {fuel1}"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} boards {aircraft} at {city}"
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} departs {aircraft} at {city}"
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return f"{aircraft} flies from {city1} to {city2} with fuel level {fleve1} to {flevel2}"
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return f"{aircraft} zooms from {city1} to {city2} with fuel level {fleve1} to {flevel3}"
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return f"{aircraft} gets refueled at {city} with fuel level {flevel1} to {flevel2}"
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} explores {city}"  # explores
            else:
                return f"{obj} is maintained"  # is maintained
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            if obj.startswith('person'):
                return f"{obj} is not explore {city}"
            else:
                return f"{obj} is not maintained"
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is boarding {aircraft}"  # boarding
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return f"{person} is not boarding {aircraft}"

        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"{aircraft} has a fuel leak"  # leak
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return f"{aircraft} does not have a fuel leak"

        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"the fuel level {fuel2} is smaller than {fuel1}"  # smaller than
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return f"the fuel level {fuel2} is not is smaller than fuel level {fuel1}"
        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} changes {aircraft} at {city}"  # changes
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return f"{person} forgets to board {aircraft} at {city}"  # forgets
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return f"{aircraft} is in {city1} then flies for maintenance to {city2}"  # maintenance
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return f"{aircraft} consumes the fuel level {fleve1} and {flevel3}"  # consumes
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return f"{aircraft} goes for maitnance at location {city} and refueled with fuel {flevel1}"  # maintained and refueled
        else:
            raise 'action is not defined'


class Visitall(BaseDomain):
    DOMAIN_NAME = 'visitall'
    DOMAIN_DESC_WITHOUT_RAM = (
        'A robot can move from its current position to the next position if the robot is at its current position and the current position is connected to the next position. '
        'Moving from the current position to the next position causes the robot to be at the next position, not at the current position anymore, and marks the next position as visited.')
    DOMAIN_DESC_WITH_RAM = (
        'A robot can only move from its current position to the next position if the robot is at its current position and the current position is connected to the next position. '
        "Moving from a current position to the next position causes the robot to be present at the next position. "

        "A robot cannot be at two places at the same time. A place is marked as visited if a robot has been at that place. ")
    DERIVED_FLUENTS = ['visited(']
    SUBSTRINGS_TO_RAND = {
        'robot': 'xtjpivjhco', 'robots': 'xtjpivjhco',
        'position': 'puxuduuqen', 'positions': 'puxuduuqen',
        'connect': 'dlipeeieju', 'connects': 'dlipeeieju', 'connecting': 'dlipeeieju', 'connected': 'dlipeeieju',
        'move': 'pkjjnojvly', 'moves': 'pkjjnojvly', 'moving': 'pkjjnojvly', 'moved': 'pkjjnojvly',
        'visit': 'lknwwwkrbf', 'visits': 'lknwwwkrbf', 'visiting': 'lknwwwkrbf', 'visited': 'lknwwwkrbf',
    }

    def fluent_to_natural_language_helper(self, fluent):
        if fluent.startswith('at_robot('):
            place = self.extract_single_variable(fluent)
            return f"robot is at {place}"
        elif fluent.startswith('-at_robot('):
            place = self.extract_single_variable(fluent)
            return f"robot is not at {place}"
        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"{place1} is connected to {place2}"
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"{place1} is not connected to {place2}"
        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return f"{place} is visited"
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return f"{place} is not visited"
        else:
            raise 'fluent is not defined'

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return f"moves from {place1} to {place2}"
        else:
            raise 'action is not defined'

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is stuck at {place}"  # stuck
        elif fluent.startswith('-at_robot('):
            place = self.extract_multi_variable(fluent)
            return f"robot is not stuck at {place}"

        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"{place1} is far from to {place2}"  # far from
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return f"{place1} is not far from to {place2}"

        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return f"{place} is observed"  # observed
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return f"{place} is not observed"

        else:
            raise 'fluent is not defined'

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return f"jump from {place1} to {place2}"  # jump
        else:
            raise 'action is not defined'


ALL_DOMAIN_CLASSES = [Blocksworld, Depots, Driverlog, Goldminer, Grippers, Logistics, Miconic, Mystery, Npuzzle,
                      Satellite, Spanner, Visitall, Zenotravel]

if __name__ == '__main__':
    dom = Blocksworld(is_random_sub=False, is_ramifications=True)
    print(dom.domain_description)
    dom = Blocksworld(is_random_sub=True, is_ramifications=True)
    print(dom.domain_description)
