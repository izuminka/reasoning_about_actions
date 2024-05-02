import re
import random
import string

import sys
sys.path.insert(0,'../../')
from src.common import *
from copy import deepcopy

def strip_action_prefix(action):
    if action.startswith('action_'):
        return action[len('action_'):]
    return action


def gen_random_str(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

REGEX_CACHE = {}

class BaseDomain:
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    DOMAIN_DESC_WITHOUT_RAM = ''
    DOMAIN_DESC_WITH_RAM = ''
    SUBSTRINGS_TO_RAND = {}
    REPLACE_REGEX_PREFIX = r'(?<!\S)'
    REPLACE_REGEX_POSTFIX = r'(?![^\s"\'\.\,:;?!])'

    BASE_FLUENTS = []
    DERIVED_FLUENTS = []
    PERSISTENT_FLUENTS = []
    STATIC_FLUENTS = []

    def __init__(self, is_random_sub, is_ramifications, is_with_fluent_info=True):
        self.is_random_sub = is_random_sub
        self.is_ramifications = is_ramifications
        self.domain_description = self.DOMAIN_DESC_WITH_RAM if is_ramifications else self.DOMAIN_DESC_WITHOUT_RAM
        self.fluent_info_for_domain = self.construct_fluent_info_for_domain()
        if is_with_fluent_info:
            self.domain_description += '\n\n' + self.fluent_info_for_domain
        if is_random_sub:
            self.domain_description = self.to_random_substring(self.domain_description)

    def asp_to_nl(self, obj_ls):
        if not obj_ls:
            return None
        and_str = ' and '
        comma_str = ', '
        if len(obj_ls) == 1:
            nl_obj = self.fluent_to_natural_language_helper(obj_ls[0], is_without_object=True)[0]
            return nl_obj
        nl_obj_ls = [self.fluent_to_natural_language_helper(f, is_without_object=True)[0] for f in obj_ls]
        return comma_str.join(nl_obj_ls[:-1]) + and_str + nl_obj_ls[-1]

    def to_random_substring(self, text):
        return self.replace_substrings(text, self.SUBSTRINGS_TO_RAND)


    def construct_fluent_info_for_domain(self):
        def add_fluents(fluent_ls, fluent_type_nl):
            result = ''
            if fluent_ls:
                result += f"In this domain, they are: {self.asp_to_nl(fluent_ls)}. "
            else:
                result += f"There are no {fluent_type_nl} in this domain. "
            return result

        result = f'A state is a set of valid properties. Properties may or may not involve negations. '
        result += f'{capitalize_first_letter(FLUENTS_NL)} can be of 4 types: base, derived, persistent, and static. '

        result += f"{capitalize_first_letter(BASE_FLUENTS_NL)} are properties that don't depend on other properties. "
        result += add_fluents(self.BASE_FLUENTS, BASE_FLUENTS_NL)

        result += f"{capitalize_first_letter(DERIVED_FLUENTS_NL)} are properties that depend on other properties. "
        result += add_fluents(self.DERIVED_FLUENTS, DERIVED_FLUENTS_NL)

        result += f"{capitalize_first_letter(PERSISTENT_FLUENTS_NL)} are properties that depend on themselves. "
        result += add_fluents(self.PERSISTENT_FLUENTS, PERSISTENT_FLUENTS_NL)

        result += f"{capitalize_first_letter(STATIC_FLUENTS_NL)} are properties that don't change under any action. "
        result += add_fluents(self.STATIC_FLUENTS, STATIC_FLUENTS_NL)

        return result

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]

    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')

    @staticmethod
    def replace_substring(text, old_sub, new_sub):
        def case_preserving_replace(new_sub):
            def replace(match):
                original = match.group()
                if original.islower():
                    return new_sub.lower()
                elif original.isupper():
                    return new_sub.upper()
                elif original.istitle():
                    return new_sub.title()
                else:
                    return new_sub  # default to the original new_sub case
            return replace

        if old_sub not in REGEX_CACHE:
            pattern = BaseDomain.REPLACE_REGEX_PREFIX + re.escape(old_sub) + BaseDomain.REPLACE_REGEX_POSTFIX
            REGEX_CACHE[old_sub] = re.compile(pattern, re.IGNORECASE)
        return re.sub(REGEX_CACHE[old_sub], case_preserving_replace(new_sub), text)

    @staticmethod
    def replace_substrings(text, obj_dict):
        text_new = deepcopy(text)
        for old_word, new_word in obj_dict.items():
            text_new = BaseDomain.replace_substring(text_new, old_word, new_word)
        return text_new

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        raise Exception('Implement in child class')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        raise Exception('Implement in child class')

    def action_to_natural_language_helper(self, action):
        raise Exception('Implement in child class')

    def action_to_hallucinated_natural_language_helper(self, action):
        raise Exception('Implement in child class')

    def fluent_to_natural_language(self, fluent, is_hallucinated=False):
        if not is_hallucinated:
            nl_fluent_list = self.fluent_to_natural_language_helper(fluent)
        else:
            nl_fluent_list = self.fluent_to_hallucinated_natural_language_helper(fluent)

        if self.is_random_sub:
            nl_fluent_list = [self.replace_substrings(ele, self.SUBSTRINGS_TO_RAND) for ele in nl_fluent_list]

        return random.choice(nl_fluent_list)

    def action_to_natural_language(self, action, is_hallucinated=False):
        if not is_hallucinated:
            nl_action_list = self.action_to_natural_language_helper(action)
        else:
            nl_action_list = self.action_to_hallucinated_natural_language_helper(action)

        if self.is_random_sub:
            nl_action_list = [self.replace_substrings(ele, self.SUBSTRINGS_TO_RAND) for ele in nl_action_list]

        return random.choice(nl_action_list)


class Blocksworld(BaseDomain):
    DOMAIN_NAME = 'blocksworld'
    
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
        'Furthermore, the hand is not empty.'
    )
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
        "The block can only be at one place at a time."
    )
    
    BASE_POS_FLUENTS = ['ontable(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['clear(', 'handempty']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['holding(', 'on(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_FLUENTS = []
    STATIC_POS_FLUENTS = []
    STATIC_NEG_FLUENTS = []
    
    SUBSTRINGS_TO_RAND = {
        # Object types
        'block': 'qbyyxzqvdh', 'blocks': 'qbyyxzqvdhs',
        'hand': 'egpbpdtalq',
        'table': 'gcbwvwyvkv',

        # Fluents
        'on':'wtuwjwbuja', 'on top of': 'wtuwjwbuja', 'placed on top': 'wtuwjwbuja',
        'on the table': 'zewwtdxhfs', 'located on the table': 'zewwtdxhfs',
        # 'clear': 'ormkfgqwve',
        'hold': 'casqqrrojp', 'holding': 'casqqrrojp', 'held': 'casqqrrojp', 'holds': 'casqqrrojp', 'being held': 'casqqrrojp',
        # 'empty': 'yqttlkcqqj',
        
        # Actions
        'pick up': 'ovyuecllio', 'picking up': 'ovyuecllio', 'picked up': 'ovyuecllio',
        'put down': 'xskgihccqt', 'puts down': 'xskgihccqt', 'putting down': 'xskgihccqt',
        'stack': 'oscckwdtoh', 'stacks': 'oscckwdtoh', 'stacking': 'oscckwdtoh', 'stacked': 'oscckwdtoh',
        'unstack': 'wxqdwukszo', 'unstacks': 'wxqdwukszo', 'unstacking': 'wxqdwukszo', 'unstacked': 'wxqdwukszo',
        
        # Hallucinated Fluents
        'switched': 'pueupbojkz', 'swapped': 'pueupbojkz', 'exchanged': 'pueupbojkz',
        'lost': 'xzeywfsucg', 'become lost': 'xzeywfsucg',
        'being thrown': 'zjzqfzjvqz', 'been thrown': 'zjzqfzjvqz',
        'under the table': 'iqvpbljrxy', 'positioned under the table': 'iqvpbljrxy',
        'broken': 'jmqpdsymid', 'now broken': 'jmqpdsymid', 'broken anymore': 'jmqpdsymid',
        
        # Hallucinated Actions
        'crushed': 'qvyqxotjqc', 'crushes': 'qvyqxotjqc',
        'glued': 'infnjzlsvf',
        'placed inside': 'erhgolynpo', 'inserted inside': 'erhgolynpo', 'put inside': 'erhgolynpo',
        'crashed': 'yqyqjvzjxw',
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('on('):
            if is_without_object:
                return ['a block is on another block']
            b1, b2 = self.extract_multi_variable(fluent)
            return [
                f'block {b1} is on block {b2}',
                f'block {b1} is on top of block {b2}',
                f'block {b1} is placed on top of block {b2}'
            ]
        elif fluent.startswith('-on('):
            if is_without_object:
                return ['a block is not on another block']
            b1, b2 = self.extract_multi_variable(fluent)
            return [
                f'block {b1} is not on block {b2}',
                f'block {b1} is not on top of block {b2}',
                f'block {b1} is not placed on top of block {b2}'
            ]

        elif fluent.startswith('clear('):
            if is_without_object:
                return ['a block is clear']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is clear'
            ]
        elif fluent.startswith('-clear('):
            if is_without_object:
                return ['a block is not clear']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not clear'
            ]

        elif fluent.startswith('ontable('):
            if is_without_object:
                return ['a block is on the table']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is on the table',
                f'block {b} is located on the table'
            ]
        elif fluent.startswith('-ontable('):
            if is_without_object:
                return ['a block is not on the table']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not on the table',
                f'block {b} is not located on the table'
            ]

        elif fluent.startswith('holding('):
            if is_without_object:
                return ['a block is being held']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is being held',
                f'the hand is holding the block {b}',
                f'block {b} is being held by the hand'
            ]
        elif fluent.startswith('-holding('):
            if is_without_object:
                return ['a block is not being held']
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not being held',
                f'the hand is not holding the block {b}',
                f'block {b} is not being held by the hand'
            ]

        elif fluent.startswith('handempty'):
            return [
                'hand is empty',
                'hand is not holding anything'
            ]
        elif fluent.startswith('-handempty'):
            return [
                f'hand is not empty',
                f'hand is holding some block'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return [
                f'block {block_name} is picked up',
                f'block {block_name} is picked up by the hand',
                f'block {block_name} is picked up from the table'
            ]
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return [
                f'block {block_name} is put down',
                f'block {block_name} is put down on the table',
                f'the hand puts down the block {block_name}'
            ]
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return [
                f'block {b1} is unstacked from block {b2}',
                f'block {b1} is unstacked from top of block {b2}',
                f'from top of block {b2}, block {b1} is unstacked'
            ]
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return [
                f'block {b1} is stacked on top of block {b2}',
                f'on top of block {b2}, block {b1} is stacked'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # switched
        if fluent.startswith('on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return [
                f'block {b1} is switched with block {b2}',
                f'block {b1} is swapped with block {b2}',
                f'block {b2} is exhanged with block {b1}'
            ]
        elif fluent.startswith('-on('):
            b1, b2 = self.extract_multi_variable(fluent)
            return [
                f'block {b1} is not switched with block {b2}',
                f'block {b1} is not swapped with block {b2}',
                f'block {b2} is not exchanged with block {b1}'
            ]

        # lost
        elif fluent.startswith('clear('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is lost',
                f'block {b} has become lost'
            ]
        elif fluent.startswith('-clear('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not lost',
                f'block {b} has not become lost'
            ]

        # thrown
        elif fluent.startswith('holding('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is being thrown',
                f'block {b} has been thrown'
            ]
        elif fluent.startswith('-holding('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not being thrown',
                f'block {b} has not been thrown'
            ]

        # under table
        elif fluent.startswith('ontable('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is under the table',
                f'block {b} is positioned under the table'
            ]
        elif fluent.startswith('-ontable('):
            b = self.extract_single_variable(fluent)
            return [
                f'block {b} is not under the table',
                f'block {b} is not positioned under the table'
            ]

        # hand broken
        elif fluent.startswith('handempty'):
            return [
                f'hand is broken',
                f'hand is now broken'
            ]
        elif fluent.startswith('-handempty'):
            return [
                f'hand is not broken',
                f'hand is not broken anymore'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        
        # crush
        if 'pick_up(' in action:
            block_name = self.extract_single_variable(action)
            return [
                f'block {block_name} is crushed',
                f'block {block_name} is crushed by the hand',
                f'the hand crushes the block {block_name}'
            ]
        
        # glue
        elif 'put_down(' in action:
            block_name = self.extract_single_variable(action)
            return [
                f'block {block_name} is glued',
                f'block {block_name} is glued by the hand',
                f'block {block_name} is glued to the table'
            ]
        
        # inside
        elif 'unstack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return [
                f'block {b1} is placed inside block {b2}',
                f'block {b1} is inserted inside block {b2}',
                f'block {b1} is put inside block {b2}'
            ]

        # crashed
        elif 'stack(' in action:
            b1, b2 = self.extract_multi_variable(action)
            return [
                f'block {b1} is crashed from block {b2}'
                f'block {b1} is crashed from top of block {b2}',
                f'from top of block {b2}, block {b1} is crashed'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'Unloading the crate from the truck causes the crate to be not in the truck, and the hoist to be lifting the crate and not available.'
    )
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
        "A crate can only be on top of one surface. "
    )
  
    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['clear(', 'available(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(', 'on(', 'in(', 'lifting(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_FLUENTS = []
    STATIC_NEG_FLUENTS = []
    STATIC_POS_FLUENTS = []

    SUBSTRINGS_TO_RAND = {
        # Object types
        'depot': 'viwwhelzlg', 'depots': 'viwwhelzlg',
        'distributor': 'vjbtrtgdsx', 'distributors': 'vjbtrtgdsx',
        'surface': 'fshxjwxean', 'surfaces': 'fshxjwxean',
        'pallet': 'tzrwjuotxz', 'pallets': 'tzrwjuotxz',
        'crate': 'pjrluufopq', 'crates': 'pjrluufopq',
        'truck': 'nblmdziyqf', 'trucks': 'nblmdziyqf',
        'hoist': 'suhmddooyi', 'hoists': 'suhmddooyi',
        
        # Fluents
        'at': 'cmgnqlveog', 'located at': 'cmgnqlveog',
        'on': 'fpqyitbzqq', 'on top of': 'fpqyitbzqq',
        'in': 'qxkqlxlezx', 'contains': 'qxkqlxlezx', 'inside': 'qxkqlxlezx',
        'lifting': 'uzsyubjcdy', 'raising': 'uzsyubjcdy', 'elevating': 'uzsyubjcdy',
        # 'available': 'xlhhnyciys', 'accessible': 'xlhhnyciys', 'available for work': 'xlhhnyciys',
        # 'clear': 'sypgozifms',
        
        # Actions
        'driven': 'jzmscukkyy', 'drive': 'jzmscukkyy', 'driving': 'jzmscukkyy', 'drove': 'jzmscukkyy',
        'lift': 'aeaygzpsjc', 'lifting': 'aeaygzpsjc', 'lifts': 'aeaygzpsjc', 'lifted': 'aeaygzpsjc',
        'drop': 'uckhudtpif', 'drops': 'uckhudtpif', 'dropping': 'uckhudtpif', 'dropped': 'uckhudtpif',
        'load': 'gjqgfjtbnf', 'loads': 'gjqgfjtbnf', 'loading': 'gjqgfjtbnf', 'loaded': 'gjqgfjtbnf',
        'unload': 'gpztfzvsux', 'unloads': 'gpztfzvsux', 'unloading': 'gpztfzvsux', 'unloaded': 'gpztfzvsux',
        
        # Hallucinated Fluents
        'maintained': 'ytvcrjybec',
        'stranded': 'jjlqbocvnz',
        'near': 'ginalixply',
        'delivered': 'myywdvcitn', 'delivery': 'myywdvcitn',
        'within': 'cxigqletvk', 'exist within': 'cxigqletvk',
        'next to': 'fwhnkxhpvg', 'situated next to': 'fwhnkxhpvg',
        'transporting': 'fmiayxdllr', 'transported': 'fmiayxdllr',
        'malfunctioning': 'ikvdhtgkxv', 'experiencing a malfunciton': 'ikvdhtgkxv',
        'expensive': 'wcjwdipviu', 'valuable': 'wcjwdipviu', 'costly': 'wcjwdipviu',
        
        # Hallucinated Actions
        'inspected': 'amxudankts', 'inspection': 'amxudankts',
        'broken': 'jnhkhfkmzz', 'breaks': 'jnhkhfkmzz',
        'stuck': 'uotbvdpsft',
        'packed': 'uijtrascvl', 'packs': 'uijtrascvl',
        'hoisted': 'ahlymciwax', 'hoisting': 'ahlymciwax',
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['at']
            obj, place = self.extract_multi_variable(fluent)
            if (obj.startswith('truck') or
                    obj.startswith('crate') or
                    obj.startswith('hoist') or
                    obj.startswith('pallet')):
                return [
                    f'{obj} is at {place}',
                    f'{obj} is located at {place}',
                    f'{place} is where {obj} is located',
                    f'{obj} can be found located at {place}'
                ]
            else:
                raise Exception(f'fluent: {fluent} is not defined')
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['not at']
            obj, place = self.extract_multi_variable(fluent)
            if (obj.startswith('truck') or
                    obj.startswith('crate') or
                    obj.startswith('hoist') or
                    obj.startswith('pallet')):
                return [
                    f'{obj} is not at {place}',
                    f'{obj} is not located at {place}',
                    f'{place} is where {obj} is not located',
                    f'{obj} cannot be found located at {place}'
                ]
            else:
                raise Exception(f'fluent: {fluent} is not defined')

        elif fluent.startswith('on('):
            if is_without_object:
                return ['on']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is on {obj2}',
                f'{obj2} has {obj1} on it',
                f'{obj1} is on top of {obj2}'
            ]
        elif fluent.startswith('-on('):
            if is_without_object:
                return ['not on']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not on {obj2}',
                f'{obj2} does not have {obj1} on it',
                f'{obj1} is not on top of {obj2}'
            ]

        elif fluent.startswith('in('):
            if is_without_object:
                return ['in']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is in {obj2}',
                f'{obj2} contains {obj1}',
                f'{obj1} is inside {obj2}'
            ]
        elif fluent.startswith('-in('):
            if is_without_object:
                return ['not in']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not in {obj2}',
                f'{obj2} does not contain {obj1}',
                f'{obj1} is not inside {obj2}'
            ]

        elif fluent.startswith('lifting('):
            if is_without_object:
                return ['a hoist is lifting a crate']
            hoist, crate = self.extract_multi_variable(fluent)
            return [
                f'{hoist} is lifting {crate}',
                f'{hoist} is raising {crate}',
                f'{hoist} is elevating {crate}'
            ]
        elif fluent.startswith('-lifting('):
            if is_without_object:
                return ['a hoist is not lifting a crate']
            hoist, crate = self.extract_multi_variable(fluent)
            return [
                f'{hoist} is not lifting {crate}',
                f'{hoist} is not raising {crate}',
                f'{hoist} is not elevating {crate}'
            ]

        elif fluent.startswith('available('):
            if is_without_object:
                return ['hoist is available']
            hoist = self.extract_single_variable(fluent)
            return [
                f'{hoist} is available',
                f'{hoist} is accessible',
                f'{hoist} is available for work'
            ]
        elif fluent.startswith('-available('):
            if is_without_object:
                return ['hoist is not available']
            hoist = self.extract_single_variable(fluent)
            return [
                f'{hoist} is not available',
                f'{hoist} is not accessible',
                f'{hoist} is not available for work'
            ]

        elif fluent.startswith('clear('):
            if is_without_object:
                return ['a surface is clear']
            surface = self.extract_single_variable(fluent)
            return [
                f'{surface} is clear',
                f'{surface} is clear of any crates'
            ]
        elif fluent.startswith('-clear('):
            if is_without_object:
                return ['a surface is not clear']
            surface = self.extract_single_variable(fluent)
            return [
                f'{surface} is not clear',
                f'{surface} is not clear of any crates'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return [
                f'{truck} is driven from {distributor1} to {distributor2}',
                f'{truck} is driven to {distributor2} from {distributor1}',
                f'from {distributor1}, {truck} is driven to {distributor2}'
            ]
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return [
                f'{hoist} lifts {crate} from {surface} at {place}',
                f'{crate} is lifted from {surface} at {place} by {hoist}',
                f'at {place}, {hoist} lifts {crate} off {surface}'
            ]
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return [
                f'{hoist} drops {crate} on {surface} at {place}',
                f'{crate} is dropped on {surface} at {place} by {hoist}',
                f'at {place}, {hoist} drops {crate} on {surface}'
            ]
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return [
                f'{crate} is loaded by {hoist} into {truck} at {place}',
                f'{hoist} loads {crate} into {truck} at {place}',
                f'at {place}, {hoist} loads {crate} into {truck}'
            ]
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return [
                f'{crate} is unloaded by {hoist} from {truck} at {place}',
                f'{hoist} unloads {crate} from {truck} at {place}',
                f'at {place}, {hoist} unloads {crate} from {truck}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        flag = True
        for prefix_asp, prefix_nl in [('-', 'not '), ('', '')]:
            if fluent.startswith(f'{prefix_asp}at('):
                obj, place = self.extract_multi_variable(fluent)
                # maintained
                if obj.startswith('truck'):
                    return [
                        f'{obj} is {prefix_nl}maintained at {place}',
                        f'at {place}, {obj} is {prefix_nl}is maintained'
                    ]
                # stranded
                elif obj.startswith('crate'):
                    return [
                        f'{obj} is {prefix_nl}stranded at {place}',
                        f'at {place}, {obj} is {prefix_nl}stranded'
                    ]
                # near
                elif obj.startswith('hoist'):
                    return [
                        f'{obj} is {prefix_nl}near {place}',
                        f'{obj} is {prefix_nl}located near {place}'
                    ]
                # delivered (changed from 'on top of')
                elif obj.startswith('pallet'):
                    return [
                        f'{obj} is {prefix_nl}delivered to {place}',
                        f'{place} does {prefix_nl}receive delivery of {obj}'
                    ]
                else:
                    raise Exception(f'fluent: {fluent} is not defined')

            elif fluent.startswith(f'{prefix_asp}on('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                # within
                return [
                    f'{obj1} is {prefix_nl}within {obj2}',
                    f'{obj1} does {prefix_nl}exist within {obj2}'
                ]

            elif fluent.startswith(f'{prefix_asp}in('):
                obj1, obj2 = self.extract_multi_variable(fluent)
                # next to
                return [
                    f'{obj1} is {prefix_nl}next to {obj2}',
                    f'{obj1} is {prefix_nl}situated next to {obj2}'
                ]

            elif fluent.startswith(f'{prefix_asp}lifting('):
                hoist, crate = self.extract_multi_variable(fluent)
                # transporting
                return [
                    f'{hoist} is {prefix_nl}transporting {crate}',
                    f'{crate} is {prefix_nl}being transported by {hoist}'
                ]

            elif fluent.startswith(f'{prefix_asp}available('):
                hoist = self.extract_single_variable(fluent)
                # malfunction (changed from 'free')
                return [
                    f'{hoist} is {prefix_nl}malfunctioning',
                    f'{hoist} is {prefix_nl}experiencing a malfunciton'
                ]

            elif fluent.startswith(f'{prefix_asp}clear('):
                surface = self.extract_single_variable(fluent)
                # expensive (changed from 'free')
                return [
                    f'{surface} is {prefix_nl}expensive',
                    f'{surface} is {prefix_nl}valuable',
                    f'{surface} is {prefix_nl}costly'
                ]
        if flag:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)

        # inspected
        if action.startswith('drive('):
            truck, distributor1, distributor2 = self.extract_multi_variable(action)
            return [
                f'{truck} is inspected at {distributor1} and at {distributor2}',
                f'inspection of {truck} occurs at {distributor1} and {distributor2}'
            ]
        # breaks (changed from 'lowered')
        elif action.startswith('lift('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return [
                f'{crate} breaks {surface} at {place}',
                f'at {place}, {surface} is broken by placing {crate}',
                f'{surface} is broken at {place} by placing {crate}'
            ]
        # stuck (changed from 'released')
        elif action.startswith('drop('):
            hoist, crate, surface, place = self.extract_multi_variable(action)
            return [
                f'{crate} is stuck on {hoist} at {place}',
                f'at {place}, {crate} is stuck on {hoist}',
                f'{hoist} has {crate} stuck at {place}'
            ]
        # packed (changed from 'transports')
        elif action.startswith('load('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return [
                f'{truck} is packed in {crate} by {hoist} at {place}',
                f'{hoist} packs {truck} in {crate} at {place}',
                f'at {place}, {hoist} packs {truck} in {crate}'
            ]
        # hoisted (changed from 'maneuvered')
        elif action.startswith('unload('):
            hoist, crate, truck, place = self.extract_multi_variable(action)
            return [
                f'{truck} is hoisted with {hoist} at {place}',
                f'at {place}, {truck} is hoisted with {hoist}',
                f'{hoist} is hoisting {truck} at {place}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'Walking causes the driver to no longer be at the initial location but to be at the final location.'
    )
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
        "Walking from initial location to final location, causes the driver to be at the final location. "
        "A truck is empty if and only if it is not driven by anyone (any driver). "
        "A driver is driving the truck if and only if the driver is not at a location "
        "An object can only be at one location. "
        "A driver can only be at one location."
    )
    
    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['empty(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(', 'in(', 'driving(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['link(', 'path(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        # 'location': 'iatympbexj', 'locations': 'iatympbexj',
        'truck': 'zkkizjecwh', 'trucks': 'zkkizjecwh',
        'object': 'omkfkvxwrg', 'objects': 'omkfkvxwrg',
        'driver': 'fxwdnwxasu', 'drivers': 'fxwdnwxasu',
        
        # Fluents
        'at': 'yceafumfdp', 'present at': 'yceafumfdp', 'currently at': 'yceafumfdp',
        'in': 'qhkipqlxfx', 'placed in': 'qhkipqlxfx', 'located in': 'qhkipqlxfx',
        'driving': 'qvpnltnffy', 'being driven by': 'qvpnltnffy',
        'link': 'umwttodbts', 'links': 'umwttodbts',
        'path': 'zgbnmmdljx', 'paths': 'zgbnmmdljx',
        # 'empty': 'fgrxzszxhm', 'nothing': 'fgrxzszxhm',
        
        # Actions
        'load': 'yvlcghamlt', 'loads': 'yvlcghamlt', 'loading': 'yvlcghamlt', 'loaded': 'yvlcghamlt',
        'unload': 'zfjywbftzj', 'unloads': 'zfjywbftzj', 'unloading': 'zfjywbftzj', 'unloaded': 'zfjywbftzj',
        'board': 'kqrkdhivua', 'boards': 'kqrkdhivua', 'boarding': 'kqrkdhivua', 'boarded': 'kqrkdhivua',
        'disembark': 'qstuhdgygm', 'disembarks': 'qstuhdgygm', 'disembarking': 'qstuhdgygm', 'disembarked': 'qstuhdgygm',
        'drive': 'wqfrddftie', 'drives': 'wqfrddftie', 'driving': 'wqfrddftie', 'drove': 'wqfrddftie', 'driven': 'wqfrddftie',
        'walk': 'elasopyqsh', 'walks': 'elasopyqsh', 'walking': 'elasopyqsh', 'walked': 'elasopyqsh',
        
        # Hallucinated Fluents
        'parked at': 'ffbivspbrs', 'parked': 'ffbivspbrs',
        'near': 'drvlxsqrlz', 'located near': 'drvlxsqrlz',
        'above': 'lnhfycnrbd', 'placed above': 'lnhfycnrbd', 'located above': 'lnhfycnrbd',
        'sleeping': 'otwcyyzroo', 'currently sleeping': 'otwcyyzroo', 'taking a nap': 'otwcyyzroo',
        'neighbors': 'fgutxzbccy', 'neighbor': 'fgutxzbccy',
        'overloaded': 'ashjotasqz',
        
        # Hallucinated Actions
        'returned': 'jrnajvctur', 'returned back': 'jrnajvctur',
        'delivered': 'aaxcanwktt',
        'inspects': 'mpfmwjioxq', 'inspected': 'mpfmwjioxq',
        'repairs': 'dwunyofrzp', 'repaired': 'dwunyofrzp',
        'checks': 'sxzlmtkqcl', 'checked': 'sxzlmtkqcl', 'checking': 'sxzlmtkqcl',
        'rests': 'anaefeatxi', 'rest': 'anaefeatxi',
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['an object is obj is at a location']
            obj, location = self.extract_multi_variable(fluent)
            return [
                f'{obj} is at location {location}',
                f'{obj} is present at location {location}',
                f'{obj} is currently at location {location}'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['an object is obj is not at a location']
            obj, location = self.extract_multi_variable(fluent)
            return [
                f'{obj} is not at location {location}',
                f'{obj} is not present at location {location}',
                f'{obj} is not currently at location {location}'
            ]

        elif fluent.startswith('in('):
            if is_without_object:
                return ['in']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is in {obj2}',
                f'{obj1} is placed in {obj2}',
                f'{obj1} is located in {obj2}'
            ]
        elif fluent.startswith('-in('):
            if is_without_object:
                return ['not in']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not in {obj2}',
                f'{obj1} is not placed in {obj2}',
                f'{obj1} is not located in {obj2}'
            ]

        elif fluent.startswith('driving('):
            if is_without_object:
                return ['driving']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is driving {obj2}',
                f'{obj2} is being driven by {obj1}',
                f'{obj1} is driving {obj2} currently'
            ]
        elif fluent.startswith('-driving('):
            if is_without_object:
                return ['not driving']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not driving {obj2}',
                f'{obj2} is not being driven by {obj1}',
                f'{obj1} is not driving {obj2} currently'
            ]

        elif fluent.startswith('link('):
            if is_without_object:
                return ['locations are linked']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is a link between location {obj1} and location {obj2}',
                f'there exists a link between the locations {obj1} and {obj2}',
                f'locations {obj1} and {obj2} have a link between them'
            ]
        elif fluent.startswith('-link('):
            if is_without_object:
                return ['locations are not linked']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is no link between location {obj1} and location {obj2}',
                f'there doesn\'t exist a link between the locations {obj1} and {obj2}',
                f'locations {obj1} and {obj2} does not have a link between them'
            ]

        elif fluent.startswith('path('):
            if is_without_object:
                return ['there is a path between locations']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is a path between location {obj1} and location {obj2}',
                f'there exists a path between the locations {obj1} and {obj2}',
                f'locations {obj1} and {obj2} have a path between them'
            ]
        elif fluent.startswith('-path('):
            if is_without_object:
                return ['there is no a path between locations']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is no path between location {obj1} and location {obj2}',
                f'there doesn\'t exist a path between the locations {obj1} and {obj2}',
                f'locations {obj1} and {obj2} does not have a path between them'
            ]

        elif fluent.startswith('empty('):
            if is_without_object:
                return ['empty']
            obj = self.extract_single_variable(fluent)
            return [
                f'{obj} is empty',
                f'{obj} contains nothing'
            ]
        elif fluent.startswith('-empty('):
            if is_without_object:
                return ['not empty']
            obj = self.extract_single_variable(fluent)
            return [
                f'{obj} is not empty',
                f'{obj} contains some package'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'{package} is loaded in {truck} at location {location}',
                f'{truck} is loaded with {package} at location {location}',
                f'at location {location}, {package} is loaded in {truck}'
            ]
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'{package} is unloaded from {truck} at location {location}',
                f'{truck} is unloaded with {package} at location {location}',
                f'at location {location}, {package} is unloaded in {truck}'
            ]
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return [
                f'{driver} boards {truck} at location {location}',
                f'{truck} is boarded by {driver} at location {location}',
                f'at location {location}, {driver} boards {truck}'
            ]
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return [
                f'{driver} disembarks from {truck} at location {location}',
                f'at location {location}, {driver} disembarks from {truck}',
                f'from {truck}, {driver} disembarks at location {location}'
            ]
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return [
                f'{driver} drives {truck} from location {loc_from} to location {loc_to}',
                f'{truck} is driven from location {loc_from} to {loc_to} by {driver}',
                f'{driver} drives {truck} to location {loc_to} from location {loc_from}'
            ]
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return [
                f'{driver} walks from location {loc_from} to location {loc_to}',
                f'{driver} walks to location {loc_to} from location {loc_from}',
                f'{driver} walks from location {loc_from} to {loc_to}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                # parked at
                return [
                    f'{obj} is parked at location {location}',
                    f'at location {location}, {obj} is parked'
                ]
            else:
                # near
                return [
                    f'{obj} is near location {location}',
                    f'{obj} is located near location {location}'
                ]
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('truck'):
                # parked at
                return [
                    f'{obj} is not parked at location {location}',
                    f'at location {location}, {obj} is not parked'
                ]
            else:
                # near
                return [
                    f'{obj} is not near location {location}',
                    f'{obj} is not located near location {location}'
                ]

        # above
        elif fluent.startswith('in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is placed above {obj2}',
                f'{obj1} is located above {obj2}',
                f'{obj1} is above {obj2}'
            ]
        elif fluent.startswith('-in('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not placed above {obj2}',
                f'{obj1} is not located above {obj2}',
                f'{obj1} is not above {obj2}'
            ]

        # sleeping
        elif fluent.startswith('driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is sleeping in {obj2}',
                f'{obj1} is currently sleeping in {obj2}',
                f'{obj1} is taking a nap in {obj2}'
            ]
        elif fluent.startswith('-driving('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'{obj1} is not sleeping in {obj2}',
                f'{obj1} is not currently sleeping in {obj2}',
                f'{obj1} is not taking a nap in {obj2}'
            ]

        # neighbors
        elif fluent.startswith('link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} neighbors location {obj2}',
                f'locations {obj1} and {obj2} are neighbors',
                f'location {obj1} and location {obj2} are neighbors'
            ]
        elif fluent.startswith('-link('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} does not neighbor location {obj2}',
                f'locations {obj1} and {obj2} are not neightbors',
                f'location {obj1} and location {obj2} are not neighbors'
            ]

        # neighbors
        elif fluent.startswith('path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} neighbors location {obj2}',
                f'locations {obj1} and {obj2} are neighbors',
                f'location {obj1} and location {obj2} are neighbors'
            ]
        elif fluent.startswith('-path('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} does not neighbor location {obj2}',
                f'locations {obj1} and {obj2} are not neightbors',
                f'location {obj1} and location {obj2} are not neighbors'
            ]

        # overloaded
        elif fluent.startswith('empty('):
            obj = self.extract_single_variable(fluent)
            return [
                f'{obj} is overloaded',
                f'{obj} is overloaded with packages'
            ]
        elif fluent.startswith('-empty('):
            obj = self.extract_single_variable(fluent)
            return [
                f'{obj} is not overloaded',
                f'{obj} is not overloaded with packages'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # return
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'{package} is returned at location {location}',
                f'{package} is returned to lcoation {location}',
                f'{package} is returned back to location {location}'
            ]
        # deliver
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'{package} is delivered at location {location}',
                f'{package} is delivered to customer at location {location}'
            ]
        # inspect
        elif action.startswith('board_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return [
                f'{driver} inspects {truck} at location {location}',
                f'{truck} is inspected by {driver} at location {location}',
                f'at location {location}, {driver} inspects {truck}'
            ]
        # repairs
        elif action.startswith('disembark_truck('):
            driver, truck, location = self.extract_multi_variable(action)
            return [
                f'{driver} repairs {truck} at location {location}',
                f'{truck} is repaired by {driver} at location {location}',
                f'at location {location}, {driver} repairs {truck}'
            ]
        # checks
        elif action.startswith('drive_truck('):
            truck, driver, loc_from, loc_to = self.extract_multi_variable(action)
            return [
                f'{driver} checks {truck} at location {loc_from} and location {loc_to}',
                f'{truck} is checked by {driver} at locations {loc_from} and {loc_to}',
                f'checking of {truck} is conducted at locations {loc_from} and {loc_to} by {driver}'
            ]
        # rests
        elif action.startswith('walk('):
            driver, loc_from, loc_to = self.extract_multi_variable(action)
            return [
                f'{driver} rests at location {loc_from} and at location {loc_to}',
                f'at locations {loc_from} and {loc_to}, {driver} takes a rest',
                f'{driver} rests at locations {loc_from} and {loc_to}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'Picking up gold results in the robot\'s arm no longer being empty, and it now holds the gold.'
    )
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
        "The robot is holding a laser if and only if the laser is not at a location. "
    )

    BASE_POS_FLUENTS = ['bomb_at(', 'laser_at(', 'soft_rock_at(', 'hard_rock_at(', 'holds_bomb(', 'holds_laser(',
                        'holds_gold(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['arm_empty', 'clear(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['robot_at(', 'gold_at(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['connected(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS
    
    SUBSTRINGS_TO_RAND = {
        # Object types
        'robot': 'oiycijmjmo', 'robot\'s': 'oiycijmjmo',
        # 'location': 'cltqghvirt', 'locations': 'cltqghvirt',
        'bomb': 'ojyinshkhj',
        'laser': 'jaakaxcemj',
        'soft rock': 'erzvzboobp', 'soft rocks': 'erzvzboobp',
        'hard rock': 'vcybvdqmgp', 'hard rocks': 'vcybvdqmgp',
        'gold': 'gbxztwroqz',
        'arm': 'jawtollkbp', 'arms': 'jawtollkbp',

        # Fluents
        'at': 'ihzolltlau', 'present at': 'ihzolltlau', 'located at': 'ihzolltlau',
        'connected': 'vkeayseeni', 'connection': 'vkeayseeni',
        # 'empty': 'kqtvognkhw', 'contains nothing': 'kqtvognkhw', 'contains something': 'not kqtvognkhw',
        'holds': 'fxfwyzfzar', 'held': 'fxfwyzfzar', 'holding': 'fxfwyzfzar',
        # 'clear': 'qvnmedqflj', 'has nothing': 'qvnmedqflj', 'has something': 'not qvnmedqflj',

        # Actions
        'move': 'zdmlakgkqc', 'moves': 'zdmlakgkqc', 'moving': 'zdmlakgkqc', 'moved': 'zdmlakgkqc',
        'pick up': 'wlcfexwxse', 'picks up': 'wlcfexwxse', 'picking up': 'wlcfexwxse', 'picked up': 'wlcfexwxse',
        'put down': 'lrlcipamts', 'puts down': 'lrlcipamts', 'putting down': 'lrlcipamts',
        'detonate': 'vputhhsycf', 'detonates': 'vputhhsycf', 'detonating': 'vputhhsycf', 'detonated': 'vputhhsycf',
        'fire': 'arvmgimcpi', 'fires': 'arvmgimcpi', 'firing': 'arvmgimcpi', 'fired': 'arvmgimcpi',

        # Hallucinated Fluents
        'communicates': 'mjyqffezpe', 'communicating': 'mjyqffezpe',
        'defused': 'vizuneyana', 'defuses': 'vizuneyana', 'defuse': 'vizuneyana',
        'gear': 'vlzaxhwuea',
        'sand': 'bcgycaqwqo',
        'granite': 'ehpwetoajj',
        'treasure': 'hjfltlgacl',
        'bigger': 'mosinwuhak', 'larger': 'mosinwuhak', 'not smaller': 'mosinwuhak', 'smaller': 'not mosinwuhak',
        'recharging': 'buwihxwpho', 'currently recharging': 'buwihxwpho', 'process of recharging': 'buwihxwpho',
        'deploys its solar-panels': 'tsmjqaiugb', 'deploying its solar-panels': 'tsmjqaiugb', 'deployed by robot': 'tsmjqaiugb', 'deploy its solar-panels': 'tsmjqaiugb',
        'tools': 'vgxoxqvrde',
        'reward': 'zkhwvjaxso',
        'spikes': 'wducbjthlg', 'spiked': 'wducbjthlg',

        # Hallucinated Actions
        'rolls': 'cluquubese',
        'ready to fire': 'yzrwmffzzb', 'prepared for firing': 'yzrwmffzzb', 'ready to be fired': 'yzrwmffzzb',
        'set up': 'gisfsluxlg',
        'disposed': 'qhjxfpoxkj', 'disposes': 'qhjxfpoxkj',
        'malfunctions': 'omwyipcewn', 'malfunctioned during detonation': 'omwyipcewn',
        'missing': 'gkmajqzggr', 'reported missing': 'gkmajqzggr', 'lost': 'gkmajqzggr',
        'melted': 'mizxhuksan', 'melts': 'mizxhuksan'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('robot_at('):
            if is_without_object:
                return ['a robot is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'robot is at location {place}',
                f'robot is present at location {place}',
                f'robot is located at {place}'
            ]
        elif fluent.startswith('-robot_at('):
            if is_without_object:
                return ['a robot is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'robot is not at location {place}',
                f'robot is not present at location {place}',
                f'robot is not located at {place}'
            ]

        elif fluent.startswith('bomb_at('):
            if is_without_object:
                return ['a bomb is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'bomb is at location {place}',
                f'bomb is present at location {place}',
                f'bomb is located at {place}'
            ]
        elif fluent.startswith('-bomb_at('):
            if is_without_object:
                return ['a bomb is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'bomb is not at location {place}',
                f'bomb is not present at location {place}',
                f'bomb is not located at {place}'
            ]

        elif fluent.startswith('laser_at('):
            if is_without_object:
                return ['a laser is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'laser is at location {place}',
                f'laser is present at location {place}',
                f'laser is located at {place}'
            ]
        elif fluent.startswith('-laser_at('):
            if is_without_object:
                return ['a laser is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'laser is not at location {place}',
                f'laser is not present at location {place}',
                f'laser is not located at {place}'
            ]

        elif fluent.startswith('soft_rock_at('):
            if is_without_object:
                return ['a soft rock is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'soft rock is at location {place}',
                f'soft rock is present at location {place}',
                f'soft rock is located at {place}'
            ]
        elif fluent.startswith('-soft_rock_at('):
            if is_without_object:
                return ['a soft rock is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'soft rock is not at location {place}',
                f'soft rock is not present at location {place}',
                f'soft rock is not located at {place}'
            ]

        elif fluent.startswith('hard_rock_at('):
            if is_without_object:
                return ['a hard rock is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'hard rock is at location {place}',
                f'hard rock is present at location {place}',
                f'hard rock is located at {place}'
            ]
        elif fluent.startswith('-hard_rock_at('):
            if is_without_object:
                return ['a hard rock is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'hard rock is not at location {place}',
                f'hard rock is not present at location {place}',
                f'hard rock is not located at {place}'
            ]

        elif fluent.startswith('gold_at('):
            if is_without_object:
                return ['gold is at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'gold is at location {place}',
                f'gold is present at location {place}',
                f'gold is located at {place}'
            ]
        elif fluent.startswith('-gold_at('):
            if is_without_object:
                return ['gold is not at a location']
            place = self.extract_single_variable(fluent)
            return [
                f'gold is not at location {place}',
                f'gold is not present at location {place}',
                f'gold is not located at {place}'
            ]

        elif fluent.startswith('connected('):
            if is_without_object:
                return ['locations are connected']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is a connection between location {obj1} and location {obj2}',
                f'location {obj1} and location {obj2} are connected',
                f'locations {obj1} and {obj2} are connected'
            ]
        elif fluent.startswith('-connected('):
            if is_without_object:
                return ['locations are not connected']
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'there is no connection between location {obj1} and location {obj2}',
                f'location {obj1} and location {obj2} are not connected',
                f'locations {obj1} and {obj2} are not connected'
            ]

        elif fluent.startswith('arm_empty'):
            return [
                f"robot's arm is empty",
                f'arm of robot is empty',
                f'robot\'s arm contains nothing'
            ]
        elif fluent.startswith('-arm_empty'):
            return [
                f"robot's arm is not empty",
                f'arm of robot is not empty',
                f'robot\'s arm contains something'
            ]

        elif fluent.startswith('holds_bomb'):
            return [
                f'robot holds a bomb',
                f'bomb is held by robot'
            ]
        elif fluent.startswith('-holds_bomb'):
            return [
                f'robot does not hold a bomb',
                f'bomb is not held by robot'
            ]

        elif fluent.startswith('holds_laser'):
            return [
                f'robot holds laser',
                f'laser is held by robot'
            ]
        elif fluent.startswith('-holds_laser'):
            return [
                f'robot does not hold laser',
                f'laser is not held by robot'
            ]

        elif fluent.startswith('holds_gold'):
            return [
                f'robot holds gold',
                f'gold is held by robot'
            ]
        elif fluent.startswith('-holds_gold'):
            return [
                f'robot does not hold gold',
                f'gold is not held by robot'
            ]

        elif fluent.startswith('clear('):
            if is_without_object:
                return ['a location is clear']
            location = self.extract_single_variable(fluent)
            return [
                f'location {location} is clear',
                f'location {location} has nothing'
            ]
        elif fluent.startswith('-clear('):
            if is_without_object:
                return ['a location is not clear']
            location = self.extract_single_variable(fluent)
            return [
                f'location {location} is not clear',
                f'location {location} has something'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return [
                f'robot moves from location {location1} to location {location2}',
                f'robot moves from locations {location1} to {location2}',
                f'robot moves to location {location2} from location {location1}'
            ]
        elif action.startswith('pickup_laser('):
            location = self.extract_single_variable(action)
            return [
                f'laser is picked up at location {location}',
                f'at location {location}, laser is picked up',
                f'robot picks up laser at location {location}'
            ]
        elif action.startswith('pickup_bomb('):
            location = self.extract_single_variable(action)
            return [
                f'bomb is picked up at location {location}',
                f'at location {location}, bomb is picked up',
                f'robot picks up bomb at location {location}'
            ]
        elif action.startswith('putdown_laser('):
            location = self.extract_single_variable(action)
            return [
                f'robot puts down laser at location {location}',
                f'at location {location}, robot puts down the laser',
                f'laser is put down at location {location}'
            ]
        elif action.startswith('detonate_bomb('):
            location1, location2 = self.extract_multi_variable(action)
            return [
                f'bomb is detontaed at location {location2} from location {location1}',
                f'from location {location1}, bomb is detonated at location {location2}',
                f'robot detonates bomb at location {location2} from location {location1}'
            ]
        elif action.startswith('fire_laser('):
            location1, location2 = self.extract_multi_variable(action)
            return [
                f'laser is fired at location {location2} from location {location1}',
                f'from location {location1}, laser is fired at location {location2}',
                f'robot fires laser at location {location2} from location {location1}'
            ]
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return [
                f'gold is picked up at location {location}',
                f'at location {location}, gold is picked up',
                f'robot picks up gold at location {location}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # communicates
        if fluent.startswith('robot_at('):
            place = self.extract_single_variable(fluent)
            return [
                f'robot communicates to location {place}',
                f'at location {place}, robot communicates',
                f'robot is communicating at location {place}'
            ]
        elif fluent.startswith('-robot_at('):
            place = self.extract_single_variable(fluent)
            return [
                f'robot does not communicates at location {place}',
                f'at location {place}, the robot does not communicates',
                f'robot is not communicating at location {place}'
            ]

        # defused
        elif fluent.startswith('bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'bomb is defused at location {obj1}',
                f'at location {obj1}, bomb is defused',
                f'robot defuses bomb at location {obj1}'
            ]
        elif fluent.startswith('-bomb_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'bomb is not defused at location {obj1}',
                f'at location {obj1}, bomb is not defused',
                f'robot does not defuse bomb at location {obj1}'
            ]

        # gear
        elif fluent.startswith('laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'gear is at location {obj1}',
                f'gear is present at location {obj1}',
                f'gear is currently at location {obj1}'
            ]
        elif fluent.startswith('-laser_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'gear is not at location {obj1}',
                f'gear is not present at location {obj1}',
                f'gear is not currently at location {obj1}'
            ]

        # sand
        elif fluent.startswith('soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'sand is at location {obj1}',
                f'sand is present at location {obj1}',
                f'sand is currently at location {obj1}'
            ]
        elif fluent.startswith('-soft_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'sand is not at location {obj1}',
                f'sand is not present at location {obj1}',
                f'sand is not currently at location {obj1}'
            ]

        # granite
        elif fluent.startswith('hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'granite is at location {obj1}',
                f'granite is present at location {obj1}',
                f'granite is currently at location {obj1}'
            ]
        elif fluent.startswith('-hard_rock_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'granite is not at location {obj1}',
                f'granite is not present at location {obj1}',
                f'granite is not currently at location {obj1}'
            ]

        # treasure
        elif fluent.startswith('gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'treasure is at location {obj1}',
                f'treasure is present at location {obj1}',
                f'treasure is currently at location {obj1}'
            ]
        elif fluent.startswith('-gold_at('):
            obj1 = self.extract_single_variable(fluent)
            return [
                f'treasure is not at location {obj1}',
                f'treasure is not present at lcoation {obj1}',
                f'treasure is not currently at location {obj1}'
            ]

        # bigger
        elif fluent.startswith('connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} is bigger than location {obj2}',
                f'location {obj1} is larger than location {obj2}',
                f'location {obj2} is smaller than location {obj1}'
            ]
        elif fluent.startswith('-connected('):
            obj1, obj2 = self.extract_multi_variable(fluent)
            return [
                f'location {obj1} is not bigger than location {obj2}',
                f'location {obj1} is not larger than location {obj2}',
                f'location {obj2} is not smaller than location {obj1}'
            ]

        # recharging
        elif fluent.startswith('arm_empty'):
            return [
                f"robot is recharging",
                f'robot is currently recharging',
                f'robot is in the process of recharging'
            ]
        elif fluent.startswith('-arm_empty'):
            return [
                f"robot is not recharging",
                f'robot is currently not recharging',
                f'robot is not in the process of recharging'
            ]

        # solar-panel
        elif fluent.startswith('holds_bomb'):
            return [
                f'robot deploys its solar-panels',
                f'robot is deploying its solar-panels',
                f'solar-panels are being deployed by robot'
            ]
        elif fluent.startswith('-holds_bomb'):
            return [
                f'robot does not deploy its solar-panels',
                f'robot is not deploying its solar-panels',
                f'solar-panels are not being deployed by robot'
            ]

        # tools
        elif fluent.startswith('holds_laser'):
            return [
                f'robot holds tools',
                f'tools are being held by robot',
                f'robot is currently holding tools'
            ]
        elif fluent.startswith('-holds_laser'):
            return [
                f'robot does not hold tools',
                f'robot is not holding any tools',
                f'robot is currently not holding any tools'
            ]

        # reward
        elif fluent.startswith('holds_gold'):
            return [
                f'robot holds reward',
                f'reward is being held by robot',
                f'robot is currently holding reward'
            ]
        elif fluent.startswith('-holds_gold'):
            return [
                f'robot does not hold reward',
                f'reward is not being held by robot',
                f'robot is currently not holding reward'
            ]

        # spikes
        elif fluent.startswith('clear('):
            location = self.extract_single_variable(fluent)
            return [
                f'location {location} contains spikes',
                f'spikes are present at location {location}',
                f'location {location} is spiked'
            ]
        elif fluent.startswith('-clear('):
            location = self.extract_single_variable(fluent)
            return [
                f'location {location} does not contain spikes',
                f'spikes are not present at location {location}',
                f'location {location} is not spiked'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # rolls
        if action.startswith('move('):
            location1, location2 = self.extract_multi_variable(action)
            return [
                f'robot rolls from location {location1} to location {location2}',
                f'robot rolls from locations {location1} to {location2}',
                f'from location {location1}, robot rolls to location {location2}'
            ]
        # ready to fire
        elif action.startswith('pickup_laser('):
            laser = self.extract_single_variable(action)
            return [
                f'laser {laser} is ready to fire',
                f'laser {laser} is prepared for firing',
                f'laser {laser} is ready to be fired'
            ]
        # set up
        elif action.startswith('pickup_bomb('):
            bomb = self.extract_single_variable(action)
            return [
                f'bomb {bomb} is set up',
                f'bomb {bomb} is set up for use',
                f'bomb {bomb} is set up for detonation'
            ]
        # disposed of
        elif action.startswith('putdown_laser('):
            laser = self.extract_single_variable(action)
            return [
                f'laser {laser} is disposed of',
                f'laser {laser} is disposed of by robot',
                f'robot disposes of laser {laser}'
            ]
        # malfunctions
        elif action.startswith('detonate_bomb('):
            bomb = self.extract_single_variable(action)
            return [
                f'bomb {bomb} malfunctions',
                f'bomb {bomb} malfunctioned during detonation'
            ]
        # missing
        elif action.startswith('fire_laser('):
            laser = self.extract_single_variable(action)
            return [
                f'laser {laser} is missing',
                f'laser {laser} is reported missing',
                f'laser {laser} is lost'
            ]
        # melted
        elif action.startswith('pick_gold('):
            location = self.extract_single_variable(action)
            return [
                f'gold is melted at location {location}',
                f'at location {location}, gold is melted',
                f'robot melts gold at location {location}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


class Grippers(BaseDomain):
    DOMAIN_NAME = 'grippers'
    
    DOMAIN_DESC_WITHOUT_RAM = (
        'A robot can move from a specified room if it is in that room. '
        'Moving the robot causes it to be not in the said room but in the destination room. '
        'A robot can pick up the object using a gripper only when the object and the robot are in the same room and the mentioned gripper is free. '
        'Picking up the object causes the robot to carry that object using its gripper, the object to be not in that room, and the said gripper not free. '
        'Dropping the object in a specified room is only executable when the robot is carrying that object using its gripper, and the robot is in the said room. '
        'Dropping an object in a room makes the object be in that room, the gripper be free and the robot not carrying the object anymore.'
    )
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
        "Robot can only be at one place. "
    )

    BASE_POS_FLUENTS = ['carry(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['free(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at_robby(', 'at(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = []
    STATIC_NEG_FLUENTS = []
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'robot': 'jjjrptnvkh', 'robots': 'jjjrptnvkh', 'robot\'s': 'jjjrptnvkh',
        'room': 'ixokqrvnqn', 'rooms': 'ixokqrvnqn',
        'gripper': 'rfqqokqouf', 'grippers': 'rfqqokqouf',
        
        # Fluents
        'at': 'dsbkgjtckb', 'present at': 'dsbkgjtckb', 'located at': 'dsbkgjtckb',
        'free': 'gburhntwol', 'available': 'gburhntwol',
        'carry': 'rwgciavjpj', 'carries': 'rwgciavjpj', 'carrying': 'rwgciavjpj', 'carried': 'rwgciavjpj',

        # Actions
        'pick': 'angmkdpvfb', 'picks': 'angmkdpvfb', 'picking': 'angmkdpvfb', 'picked': 'angmkdpvfb',
        'move': 'zucvbghqwl', 'moves': 'zucvbghqwl', 'moving': 'zucvbghqwl', 'moved': 'zucvbghqwl',
        'drop': 'qhfmsjkotn', 'drops': 'qhfmsjkotn', 'dropping': 'qhfmsjkotn','dropped': 'qhfmsjkotn',

        # Hallucinated Fluents
        'engaged': 'vymmedxpiu',
        'transport': 'kseqanhkzt', 'transports': 'kseqanhkzt', 'transporting': 'kseqanhkzt', 'transported': 'kseqanhkzt',
        'broken': 'wlylmjkbyt',
        'loading': 'kruldgryji', 'loaded': 'kruldgryji', 'load': 'kruldgryji',

        # Hallucinated Actions
        'inspected': 'ewyaiaclhl', 'inspects': 'ewyaiaclhl',
        'checks': 'zvgsdawjsn', 'checked': 'zvgsdawjsn',
        'destroyed': 'sjejpbrezk', 'destroys': 'sjejpbrezk',

        # 'destination': 'ezrqqoajas', 'destinations': 'ezrqqoajas',
        'object': 'wtdcrmrabz', 'objects': 'wtdcrmrabz',
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at_robby('):
            if is_without_object:
                return ['a robot is at a room']
            robot, room = self.extract_multi_variable(fluent)
            return [
                f'{robot} is at {room}',
                f'{robot} is present in {room}',
                f'{robot} is located at {room}'
            ]
        elif fluent.startswith('-at_robby('):
            if is_without_object:
                return ['a robot is not at a room']
            robot, room = self.extract_multi_variable(fluent)
            return [
                f'{robot} is not at {room}',
                f'{robot} is not present in {room}',
                f'{robot} is not located at {room}'
            ]

        elif fluent.startswith('at('):
            if is_without_object:
                return ['an object is at a room']
            obj, room = self.extract_multi_variable(fluent)
            return [
                f'{obj} is at {room}',
                f'{obj} is located at {room}',
                f'{obj} is present at {room}'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['an object is not at a room']
            obj, room = self.extract_multi_variable(fluent)
            return [
                f'{obj} is not at {room}',
                f'{obj} is not located at {room}',
                f'{obj} is not present at {room}'
            ]

        elif fluent.startswith('free('):
            if is_without_object:
                return ['a gripper is free']
            robot, gripper = self.extract_multi_variable(fluent)
            return [
                f"{gripper} of {robot} is free",
                f'{robot}\'s {gripper} is free',
                f'{robot}\'s {gripper} is available'
            ]
        elif fluent.startswith('-free('):
            if is_without_object:
                return ['a gripper is not free']
            robot, gripper = self.extract_multi_variable(fluent)
            return [
                f"{gripper} of {robot} is not free",
                f'{robot}\'s {gripper} is not free',
                f'{robot}\'s {gripper} is not available'
            ]

        elif fluent.startswith('carry('):
            if is_without_object:
                return ['a robot is carrying an object with a gripper']
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return [
                f'{robot} is carrying {obj} with {gripper}',
                f'{obj} is being carried by {robot}\'s {gripper}',
                f'{gripper} of {robot} is carrying {obj}'
            ]
        elif fluent.startswith('-carry('):
            if is_without_object:
                return ['a robot is not carrying an object with a gripper']
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return [
                f'{robot} is not carrying {obj} with {gripper}',
                f'{obj} is not being carried by {robot}\'s {gripper}',
                f'{gripper} of {robot} is not carrying {obj}'
            ]
        else:
            raise Exception(f'fluent: "{fluent}" is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return [
                f'{obj} is picked from {room} with {gripper} by {robot}',
                f'from {room}, {robot}\'s {gripper} picks up {obj}',
                f'{gripper} of {robot} picks up {obj} in {room}'
            ]
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return [
                f'{robot} moves from {room_from} to {room_to}',
                f'{robot} moves to {room_to} from {room_from}',
                f'from {room_from}, {robot} moves to {room_to}'
            ]
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return [
                f'{obj} is dropped in {room} with {gripper} by {robot}',
                f'in {room}, {robot}\'s {gripper} drops {obj}',
                f'{gripper} of {robot} drops {obj} in {room}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # engaged
        if fluent.startswith('at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return [
                f'{robot} is engaged in {room}',
                f'in {room}, {robot} is engaged',
                f'{robot} is currently engaged in {room}'
            ]
        elif fluent.startswith('-at_robby('):
            robot, room = self.extract_multi_variable(fluent)
            return [
                f'{robot} is not engaged in {room}',
                f'in {room}, {robot} isn\'t engaged',
                f'{robot} is not currently engaged in {room}'
            ]

        # transported to
        elif fluent.startswith('at('):
            obj, room = self.extract_multi_variable(fluent)
            return [
                f'{obj} is transported to {room}',
                f'{obj} is moved to {room}'
            ]
        elif fluent.startswith('-at('):
            obj, room = self.extract_multi_variable(fluent)
            return [
                f'{obj} is not transported to {room}',
                f'{obj} isn\'t moved to {room}'
            ]

        # broken
        elif fluent.startswith('free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return [
                f"{gripper} of {robot} is broken",
                f'{robot}\'s {gripper} is broken'
            ]
        elif fluent.startswith('-free('):
            robot, gripper = self.extract_multi_variable(fluent)
            return [
                f"{gripper} of {robot} is not broken",
                f'{robot}\'s {gripper} is not broken'
            ]

        # loading
        elif fluent.startswith('carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return [
                f'{robot} is loading {obj} with {gripper}',
                f'{obj} is loaded using {robot}\'s {gripper}',
                f'{robot} is using {gripper} to load {obj}'
            ]
        elif fluent.startswith('-carry('):
            robot, obj, gripper = self.extract_multi_variable(fluent)
            return [
                f'{robot} is not loading {obj} with {gripper}',
                f'{obj} is not loaded using {robot}\'s {gripper}',
                f'{robot} is not using {gripper} to load {obj}'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # inspected
        if action.startswith('pick('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return [
                f'{obj} is inspected in {room} with {gripper} by {robot}',
                f'in {room}, {obj} is inspected using {robot}\'s {gripper}',
                f'{gripper} of {robot} inspects the {obj} in {room}'
            ]
        # checks
        elif action.startswith('move('):
            robot, room_from, room_to = self.extract_multi_variable(action)
            return [
                f'{robot} checks {room_from} and then checks {room_to}',
                f'{robot} checks {room_from} and {room_to}',
                f'{room_from} and {room_to} are checked by {robot}'
            ]
        # destroyed (changed from "collected")
        elif action.startswith('drop('):
            robot, obj, room, gripper = self.extract_multi_variable(action)
            return [
                f'{obj} is destroyed in {room} with {gripper} by {robot}',
                f'in {room}, {obj} is destroyed using {robot}\'s {gripper}',
                f'{gripper} of {robot} destroys {obj} in {room}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'Flying the airplane causes it to be not at the source location but at the destination location.'
    )
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
        "A truck can only be at one location at a time. A plane can only be in one location at a time."
    )
   
    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = []
    DERIVED_NEG_FLUENTS = []
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(', 'in(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['in_city(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'truck': 'pvcuetihtl', 'trucks': 'pvcuetihtl',
        'airplane': 'xmyqeckfwm', 'airplanes': 'xmyqeckfwm',
        'package': 'tnzistccqp', 'packages': 'tnzistccqp',
        'vehicle': 'qmgahdodkq', 'vehicles': 'qmgahdodkq',
        'airport': 'qpplrkefyr', 'airports': 'qpplrkefyr',
        'city': 'bpzwevlomd', 'cities': 'bpzwevlomd',
        'object': 'causdnkeoz', 'objects': 'causdnkeoz',
        # 'location': 'wesxmnrgzy', 'locations': 'wesxmnrgzy',
        
        # Fluents
        'in city': 'cppjrnvvpl', 'located in city': 'cppjrnvvpl', 'contains': 'cppjrnvvpl', 'contain': 'cppjrnvvpl',
        'at': 'lyfgdjkunc', 'located at': 'lyfgdjkunc',
        'in': 'kfhraifzlu', 'present in': 'kfhraifzlu', 'located in': 'kfhraifzlu',

        # Actions
        'load': 'nxrnxkjybr', 'loads': 'nxrnxkjybr', 'loading': 'nxrnxkjybr', 'loaded': 'nxrnxkjybr',
        'unload': 'bdfszwzdpi', 'unloads': 'bdfszwzdpi', 'unloading': 'bdfszwzdpi', 'unloaded': 'bdfszwzdpi',
        'drive': 'umcjrdgfyn', 'drives': 'umcjrdgfyn', 'driving': 'umcjrdgfyn', 'drove': 'umcjrdgfyn', 'driven': 'umcjrdgfyn',
        'fly': 'umnkjqinar', 'flies': 'umnkjqinar', 'flying': 'umnkjqinar', 'flied': 'umnkjqinar', 'flown': 'umnkjqinar',

        # Hallucinated Fluents
        'capital': 'jmddqentke',
        'scanned': 'xaijmlivhh',
        'heavy': 'vnuzugdjib', 'exceeds the weight limit': 'vnuzugdjib', 'exceed the weight limit': 'vnuzugdjib',
        
        # Hallucinated Actions
        'inspected': 'ywvxawjyhr', 'inspection': 'ywvxawjyhr',
        'stuck': 'nvhbcjejlg',
        'lost': 'wuvrtakvnb',
        'refueled': 'lcgnljujin'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('in_city('):
            if is_without_object:
                return ['an airport is in a city']
            airport, city = self.extract_multi_variable(fluent)
            return [
                f'airport {airport} is in city {city}',
                f'airport {airport} is located in city {city}',
                f'city {city} contains airport {airport}'
            ]
        elif fluent.startswith('-in_city('):
            if is_without_object:
                return ['an airport is not in a city']
            airport, city = self.extract_multi_variable(fluent)
            return [
                f'airport {airport} is not in city {city}'
                f'airport {airport} is not located in city {city}',
                f'city {city} does not contain airport {airport}'
            ]

        elif fluent.startswith('at('):
            if is_without_object:
                return ['an object is at an airport']
            physical_object, airport = self.extract_multi_variable(fluent)
            return [
                f'object {physical_object} is at airport {airport}',
                f'object {physical_object} is located at airport {airport}',
                f'at airport {airport}, object {physical_object} is located'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['an object is not at an airport']
            physical_object, airport = self.extract_multi_variable(fluent)
            return [
                f'object {physical_object} is not at airport {airport}',
                f'object {physical_object} is not located at airport {airport}',
                f'at airport {airport}, object {physical_object} is not located'
            ]

        elif fluent.startswith('in('):
            if is_without_object:
                return ['a package is in a vehicle']
            package, vehicle = self.extract_multi_variable(fluent)
            return [
                f'package {package} is in vehicle {vehicle}',
                f'package {package} is present in vehicle {vehicle}',
                f'package {package} is located in vehicle {vehicle}'
            ]
        elif fluent.startswith('-in('):
            if is_without_object:
                return ['a package is not in a vehicle']
            package, vehicle = self.extract_multi_variable(fluent)
            return [
                f'package {package} is not in vehicle {vehicle}',
                f'package {package} is not present in vehicle {vehicle}',
                f'package {package} is not located in vehicle {vehicle}'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('load_truck('):
            package, truck, airport = self.extract_multi_variable(action)
            return [
                f'package {package} is loaded in truck {truck} at airport {airport}',
                f'at airport {airport}, package {package} is loaded in truck {truck}',
                f'truck {truck} is loaded with package {package} at airport {airport}'
            ]
        elif action.startswith('unload_truck('):
            package, truck, airport = self.extract_multi_variable(action)
            return [
                f'package {package} is unloaded from truck {truck} at airport {airport}',
                f'at airport {airport}, package {package} is unloaded from truck {truck}',
                f'from truck {truck} package {package} is unloaded at airport {airport}'
            ]
        elif action.startswith('load_airplane('):
            package, airplane, airport = self.extract_multi_variable(action)
            return [
                f'package {package} is loaded into airplane {airplane} at airport {airport}',
                f'at airport {airport}, package {package} is loaded in airplane {airplane}',
                f'airplane {airplane} is loaded with package {package} at airport {airport}'
            ]
        elif action.startswith('unload_airplane('):
            package, airplane, airport = self.extract_multi_variable(action)
            return [
                f'package {package} is unloaded from airplane {airplane} at airport {airport}',
                f'at airport {airport}, package {package} is unloaded from airplane {airplane}',
                f'from airplane {airplane} package {package} is unloaded at airport {airport}'
            ]
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return [
                f'truck {truck} is driven from airport {loc_from} to airport {loc_to} in city {city}',
                f'truck {truck} is driven to airport {loc_to} from airport {loc_from} in city {city}',
                f'in city {city}, truck is driven from airports {loc_from} to {loc_to}',
            ]
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return [
                f'airplane {airplane} is flown from airport {airport_from} to airport {airport_to}',
                f'airplane {airplane} is flown to airport {airport_to} from airport {airport_from}',
                f'airplane {airplane} flies from airports {airport_from} to {airport_to}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # capital
        if fluent.startswith('in_city('):
            place, city = self.extract_multi_variable(fluent)
            return [
                f'place {place} is the capital the city {city}',
                f'city {city}\'s capital is place {place}'
            ]
        elif fluent.startswith('-in_city('):
            place, city = self.extract_multi_variable(fluent)
            return [
                f'place {place} is not the capital the city {city}',
                f'city {city}\'s capital is not place {place}'
            ]

        # scanned
        elif fluent.startswith('at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return [
                f'object {physical_object} is scanned at place {place}',
                f'at place {place}, object {physical_object} is scanned'
            ]
        elif fluent.startswith('-at('):
            physical_object, place = self.extract_multi_variable(fluent)
            return [
                f'object {physical_object} is not scanned at place {place}',
                f'at place {place}, object {physical_object} is not scanned'
            ]

        # heavy
        elif fluent.startswith('in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return [
                f'package {package} is heavy for vehicle {vehicle}',
                f'package {package} exceeds the weight limit for vehicle {vehicle}'
            ]
        elif fluent.startswith('-in('):
            package, vehicle = self.extract_multi_variable(fluent)
            return [
                f'package {package} is not heavy for vehicle {vehicle}',
                f'package {package} does not exceed the weight limit for vehicle {vehicle}'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # inspected
        if action.startswith('load_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'package {package} in truck {truck} is inspected at location {location}',
                f'at location {location}, package {package} is inspected in truck {truck}',
                f'inspection of package {package} takes place in truck {truck} at location {location}'
            ]
        # stuck
        elif action.startswith('unload_truck('):
            package, truck, location = self.extract_multi_variable(action)
            return [
                f'package {package} in truck {truck} is stuck at location {location}',
                f'at location {location}, package {package} in truck {truck} is stuck'
            ]
        # inspected
        elif action.startswith('load_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return [
                f'package {package} from the airplane {airplane} is inspected at location {location}',
                f'at location {location}, package {package} is inspected in airplane {airplane}',
                f'inspection of package {package} takes place in airplane {airplane} at location {location}'
            ]
        # lost
        elif action.startswith('unload_airplane('):
            package, airplane, location = self.extract_multi_variable(action)
            return [
                f'package {package} unloaded from airplane {airplane} is lost at location {location}',
                f'at location {location}, package {package} is lost from airplane {airplane}'
            ]
        # inspected, refueled
        elif action.startswith('drive_truck('):
            truck, loc_from, loc_to, city = self.extract_multi_variable(action)
            return [
                f'truck {truck} is inspected at {loc_from} and refueled at {loc_to} in city {city}',
                f'in city {city}, truck {truck} is inspected at {loc_from} and refueled at {loc_to}'
            ]
        # refueled
        elif action.startswith('fly_airplane('):
            airplane, airport_from, airport_to = self.extract_multi_variable(action)
            return [
                f'airplane {airplane} is refueled at {airport_from} and at airport {airport_to}',
                f'at airports {airport_from} and {airport_to}, airplane {airplane} is refueled'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


class Miconic(BaseDomain):
    DOMAIN_NAME = 'miconic'

    DOMAIN_DESC_WITHOUT_RAM = (
        'A passenger can board the lift on a floor only if the lift is on that floor and the passenger\'s travel originates from that floor. '
        'Boarding the lift causes the passenger to be boarded. Departing from the lift is executable only when the lift is on the floor, the passenger is boarded, and the passenger\'s destination is on that floor. '
        'Departing from the lift causes the passenger to be served and not boarded. A lift can go up from one floor to another if and only if it is currently on the floor and the destination floor is above the source floor. '
        'Going up makes the lift on the destination floor. A lift can go down from one floor to another if and only if it is currently on a floor and the source floor is above the destination floor. '
        'Going down makes the lift on the destination floor.'
    )
    DOMAIN_DESC_WITH_RAM = (
        "A passenger can board the lift on a floor only if the lift is on that floor and the passenger's travel originates from that floor. "
        "Boarding the lift causes the passenger to be boarded. "

        "Departing from the lift is executable only when the lift is on the floor, the passenger is boarded, and the passenger's destination is on that floor. "
        "Departing from the lift causes the passenger to be served. "

        "A lift can go up from one floor to another if and only if it is currently on the floor and the destination floor is above the source floor. "
        "Going up makes the lift on the destination floor. A lift can go down from one floor to another if and only if it is currently on a floor and the source floor is above the destination floor. "
        "Going down makes the lift on the destination floor. "

        "A lift can only be on one floor at a time. "
        "If the passenger is served, then the passenger is not boarded."
    )
    
    BASE_POS_FLUENTS = ['boarded(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['served(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['lift_at(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['origin(', 'destin(', 'above(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'passenger': 'tucyshtaky', 'passengers': 'tucyshtaky',
        'floor': 'rhwfsepbez', 'floors': 'rhwfsepbez', 'level': 'rhwfsepbez', 'levels': 'rhwfsepbez',
        'lift': 'ywjmmwrawz', 'lifts': 'ywjmmwrawz', 'elevator': 'ywjmmwrawz', 'elevators': 'ywjmmwrawz',

        # Fluents
        'board': 'bidmuazwal', 'boards': 'bidmuazwal', 'boarding': 'bidmuazwal', 'boarded': 'bidmuazwal', 'enters': 'bidmuazwal', 'enter': 'bidmuazwal',
        # 'destination': 'gqrormjdyu', 'destinations': 'gqrormjdyu',
        # 'above': 'idfiasmopc', 'located above': 'idfiasmopc', 'not below': 'idfiasmopc', 'below': 'not idfiasmopc',
        'served': 'vpdiuemmjp', 'attended to': 'vpdiuemmjp',
        'at': 'vunbrpfgtb', 'positioned at': 'vunbrpfgtb',

        # Actions
        'depart': 'jbctpepaja', 'departs': 'jbctpepaja', 'departing': 'jbctpepaja','departed': 'jbctpepaja',
        # 'up': 'lfapuhgnsn',
        # 'down': 'mmphaaxcri',
        
        # Hallucinated Fluents
        'stairs': 'wecfuexbsn',
        'evacuates': 'ftrcwxtscd', 'evacuate': 'ftrcwxtscd',
        'cleaner': 'vxzirxndzr', 'clean': 'vxzirxndzr', 'not dirtier': 'vxzirxndzr', 'dirtier': 'not vxzirxndzr',
        'walks': 'avucqtzrgw', 'walk': 'avucqtzrgw',
        'ride': 'bwpgkgoesk', 'rides': 'bwpgkgoesk',
        'stuck': 'ovwhyqdjic', 'trapped': 'ovwhyqdjic',

        # Hallucinated Actions
        'lives': 'joqnheevqm',
        'shouts': 'hlzcqdfogl',
        'windows': 'apymbdlzvk'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('origin('):
            if is_without_object:
                return ['a passenger boards at a floor']
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} enters at floor {floor}',
                f'passenger {passenger} boards at floor {floor}',
                f'passenger {passenger} boards on level {floor}'
            ]
        elif fluent.startswith('-origin('):
            if is_without_object:
                return ['a passenger does not board at a floor']
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} does not enter at floor {floor}',
                f'passenger {passenger} does not boards at floor {floor}',
                f'passenger {passenger} does not boards on level {floor}'
            ]

        elif fluent.startswith('destin('):
            if is_without_object:
                return ['a destination']
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'destination of passenger {passenger} is floor {floor}',
                f'floor {floor} is the destination of the passenger {passenger}',
                f'destination of passenger {passenger} is level {floor}'
            ]
        elif fluent.startswith('-destin('):
            if is_without_object:
                return ['not a destination']
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'destination of passenger {passenger} is not floor {floor}',
                f'floor {floor} is not the destination of passenger {passenger}',
                f'destination of passenger {passenger} is not level {floor}',
            ]

        elif fluent.startswith('above('):
            if is_without_object:
                return ['one floor is above another']
            floor1, floor2 = self.extract_multi_variable(fluent)
            return [
                f'floor {floor2} is above floor {floor1}',
                f'floor {floor2} is located above floor {floor1}',
                f'floor {floor1} is below floor {floor2}'
            ]
        elif fluent.startswith('-above('):
            if is_without_object:
                return ['one floor is not above another']
            floor1, floor2 = self.extract_multi_variable(fluent)
            return [
                f'floor {floor2} is not above floor {floor1}',
                f'floor {floor2} is not located above floor {floor1}',
                f'floor {floor1} is not below floor {floor2}'
            ]
        
        elif fluent.startswith('boarded('):
            if is_without_object:
                return ['a passenger is boarded']
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} is boarded',
                f'passenger {passenger} has boarded the lift'
            ]
        elif fluent.startswith('-boarded('):
            if is_without_object:
                return ['a passenger is not boarded']
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} is not boarded',
                f'passenger {passenger} has not boarded the lift'
            ]

        elif fluent.startswith('served('):
            if is_without_object:
                return ['a passenger is served']
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} is served',
                f'passenger {passenger} is attended to'
            ]
        elif fluent.startswith('-served('):
            if is_without_object:
                return ['a passenger is not served']
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} is not served',
                f'passenger {passenger} is not attended to'
            ]

        elif fluent.startswith('lift_at('):
            if is_without_object:
                return ['a lift is at floor']
            floor = self.extract_single_variable(fluent)
            return [
                f'lift is at floor {floor}',
                f'lift is positioned at level {floor}'
            ]
        elif fluent.startswith('-lift_at('):
            if is_without_object:
                return ['a lift is not at floor']
            floor = self.extract_single_variable(fluent)
            return [
                f'lift is not at floor {floor}',
                f'lift is not positioned at level {floor}'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return [
                f'passenger {passenger} boards at floor {floor}',
                f'passenger {passenger} boards at level {floor}',
                f'at floor {floor}, passenger {passenger} boards the lift'
            ]
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return [
                f'passenger {passenger} departs at floor {floor}',
                f'passenger {passenger} departs at level {floor}',
                f'at floor {floor}, passenger {passenger} departs the lift'
            ]
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return [
                f'the elevator goes up from floor {floor1} to floor {floor2}',
                f'the lift goes up to floor {floor2} from floor {floor1}',
                f'elevator goes from level {floor1} up to level {floor2}'
            ]
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return [
                f'the elevator goes down from floor {floor1} to floor {floor2}',
                f'the lift goes down to floor {floor2} from floor {floor1}',
                f'elevator goes from level {floor1} down to level {floor2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # stairs
        if fluent.startswith('origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} takes the stairs at floor {floor}',
                f'passenger {passenger} takes the stairs at level {floor}',
                f'at floor {floor}, passenger {passenger} takes the stairs'
            ]
        elif fluent.startswith('-origin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} does not take the stairs at floor {floor}',
                f'passenger {passenger} does not take the stairs at level {floor}',
                f'at floor {floor}, passenger {passenger} does not take the stairs'
            ]

        # evacuates
        elif fluent.startswith('destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} evacuates at floor {floor}',
                f'passenger {passenger} evacuates the lift at floor {floor}',
                f'at level {floor}, passenger {passenger} evacuates the elevator'
            ]
        elif fluent.startswith('-destin('):
            passenger, floor = self.extract_multi_variable(fluent)
            return [
                f'passenger {passenger} does not evacuate at floor {floor}',
                f'passenger {passenger} does not evacuate the lift at floor {floor}',
                f'at level {floor}, passenger {passenger} does not evacuate the elevator'
            ]

        # cleaner
        elif fluent.startswith('above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return [
                f'floor {floor2} is cleaner than floor {floor1}',
                f'level {floor2} is more clean than level {floor1}',
                f'floor {floor1} is dirtier than floor {floor2}',
            ]
        elif fluent.startswith('-above('):
            floor1, floor2 = self.extract_multi_variable(fluent)
            return [
                f'floor {floor2} is not cleaner than floor {floor1}',
                f'level {floor2} is less clean than level {floor1}',
                f'floor {floor1} is not dirtier than floor {floor2}',
            ]

        # walks
        elif fluent.startswith('boarded('):
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} walks',
                f'passenger {passenger} takes a walk',
                f'passenger {passenger} walks around'
            ]
        elif fluent.startswith('-boarded('):
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} does not walk'
                f'passenger {passenger} does not take a walk',
                f'passenger {passenger} does not walk around'
            ]

        # rides
        elif fluent.startswith('served('):
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} rides',
                f'passenger {passenger} takes a ride'
            ]
        elif fluent.startswith('-served('):
            passenger = self.extract_single_variable(fluent)
            return [
                f'passenger {passenger} does not ride',
                f'passenger {passenger} does not take a ride'
            ]

        # stuck
        elif fluent.startswith('lift_at('):
            floor = self.extract_single_variable(fluent)
            return [
                f'lift is stuck at floor {floor}',
                f'elevator is stuck at level {floor}',
                f'at floor {floor}, elevator is stuck'
            ]
        elif fluent.startswith('-lift_at('):
            floor = self.extract_single_variable(fluent)
            return [
                f'lift is not stuck at floor {floor}',
                f'elevator is not stuck at level {floor}',
                f'at floor {floor}, elevator is not stuck'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # lives
        if action.startswith('board('):
            floor, passenger = self.extract_multi_variable(action)
            return [
                f'passenger {passenger} lives at floor {floor}',
                f'passenger {passenger} lives at level {floor}',
                f'at floor {floor}, passenger {passenger} lives'
            ]
        # shouting
        elif action.startswith('depart('):
            floor, passenger = self.extract_multi_variable(action)
            return [
                f'passenger {passenger} shouts at floor {floor}',
                f'passenger {passenger} shouts at level {floor}',
                f'at floor {floor}, passenger {passenger} shouts'
            ]
        # stuck
        elif action.startswith('up('):
            floor1, floor2 = self.extract_multi_variable(action)
            return [
                f'the elevator is stuck between floor {floor1} and floor {floor2}',
                f'lift is trapped between levels {floor1} and {floor2}',
                f'elevator is stuck between level {floor1} and level {floor2}'
            ]
        # windows
        elif action.startswith('down('):
            floor1, floor2 = self.extract_multi_variable(action)
            return [
                f'floors {floor1} and {floor2} have windows',
                f'levels {floor1} and {floor2} have windows',
                f'windows are present at floors {floor1} and {floor2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'When a vehicle is unloaded, cargo is no longer in the vehicle, cargo is at a location, the vehicle no longer has the initial space, and there is a secondary space.'
    )
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
        "The vehicle's amount of space is unique. "
    )
   
    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = []
    DERIVED_NEG_FLUENTS = []
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(', 'in(', 'has_space(', 'has_fuel(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['space_neighbor(', 'fuel_neighbor(', 'conn(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'space': 'kiurijzhmd', 'spaces': 'kiurijzhmd',
        'fuel': 'vyumzovixm', 'fuels': 'vyumzovixm',
        # 'location': 'wrbrffbbsf', 'locations': 'wrbrffbbsf',
        'vehicle': 'xduwfabpov', 'vehicles': 'xduwfabpov',
        'cargo': 'mrxzbljtex', 'cargos': 'mrxzbljtex',

        # Fluents
        'at': 'ubukdzgtdo', 'present at': 'ubukdzgtdo', 'situated at': 'ubukdzgtdo',
        'connect': 'qqqxlayhxq', 'connects': 'qqqxlayhxq', 'connection': 'qqqxlayhxq', 'connected': 'qqqxlayhxq',
        # 'has fuel': 'wtiirvdcva', 'have fuel': 'wtiirvdcva', 'has a fuel-level': 'wtiirvdcva', 'have a fuel-level': 'wtiirvdcva', 'exists': 'wtiirvdcva', 'exist': 'wtiirvdcva',
        'neighbors': 'vayiiathfq', 'neighbor': 'vayiiathfq',
        'in': 'aubryvcpjj', 'located in': 'aubryvcpjj', 'contains': 'aubryvcpjj', 'contain': 'aubryvcpjj',
        # 'has space': 'qwbslpmcpd', 'contains space': 'qwbslpmcpd', 'have space': 'qwbslpmcpd', 'contain space': 'qwbslpmcpd',

        # Actions
        'move': 'eszobwszrw', 'moves': 'eszobwszrw',
        'load': 'kzcowqkyya', 'loaded': 'kzcowqkyya',
        'unload': 'voxfehpkwm', 'unloaded': 'voxfehpkwm',

        # Hallucinated Fluents
        'maintained': 'czdukanscj', 'maintenance': 'czdukanscj',
        'inspected': 'mhhzfbljxv', 'inspection': 'mhhzfbljxv',
        'far': 'fzzodpjusq',
        'sells': 'wxpeehyavy', 'sold': 'wxpeehyavy', 'sell': 'wxpeehyavy',
        'gas station': 'kgivlnmjjk',
        'secured': 'mjajlixuhe',
        'parks in': 'vukazaisyk', 'parked in': 'vukazaisyk',
        'same city': 'scrwfacwjy',

        # Hallucinated Actions
        'pulled over': 'zqhccxnqxc',
        'breaks': 'ttmllhlahl',

    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['a vehicle is at a location']
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return [
                    f'vehicle {obj} is at location {location}',
                    f'vehicle {obj} is present at location {location}',
                    f'vehicle {obj} is situated at location {location}'
                ]
            else:
                return [
                    f'cargo {obj} is at location {location}',
                    f'cargo {obj} is present at location {location}',
                    f'cargo {obj} is situated at location {location}'
                ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['a vehicle is not at a location']
            obj, location = self.extract_multi_variable(fluent)
            if obj.startswith('vehicle'):
                return [
                    f'vehicle {obj} is not at location {location}',
                    f'vehicle {obj} is not present at location {location}',
                    f'vehicle {obj} is not situated at location {location}'
                ]
            else:
                return [
                    f'cargo {obj} is not at location {location}'
                    f'cargo {obj} is not present at location {location}',
                    f'cargo {obj} is not situated at location {location}'
                ]

        elif fluent.startswith('conn('):
            if is_without_object:
                return ['locations are connected']
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f'location {location1} is connected to location {location2}',
                f'there is a connection between locations {location1} and {location2}',
                f'location {location1} and location {location2} are connected'
            ]
        elif fluent.startswith('-conn('):
            if is_without_object:
                return ['locations are not connected']
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f'location {location1} is not connected to location {location2}',
                f'there is no connection between locations {location1} and {location2}',
                f'location {location1} and location {location2} are not connected'
            ]

        elif fluent.startswith('has_fuel('):
            if is_without_object:
                return ['location has fuel']
            location, fuel = self.extract_multi_variable(fluent)
            return [
                f'location {location} has fuel {fuel}',
                f'location {location} has a fuel-level of {fuel}',
                f'fuel {fuel} exists in location {location}'
            ]
        elif fluent.startswith('-has_fuel('):
            if is_without_object:
                return ['location does not have fuel']
            location, fuel = self.extract_multi_variable(fluent)
            return [
                f'location {location} does not have fuel {fuel}',
                f'location {location} does not have a fuel-level of {fuel}',
                f'fuel {fuel} does not exist in location {location}'
            ]

        elif fluent.startswith('fuel_neighbor('):
            if is_without_object:
                return ['fuel level neighbours another fuel level']
            f1, f2 = self.extract_multi_variable(fluent)
            return [
                f'fuel level {f1} neighbors fuel level {f2}',
                f'fuel-levels {f1} and {f2} are neighbors'
            ]
        elif fluent.startswith('-fuel_neighbor('):
            if is_without_object:
                return ['fuel level does not neighbour another fuel level']
            f1, f2 = self.extract_multi_variable(fluent)
            return [
                f'fuel level {f1} does not neighbour fuel level {f2}',
                f'fuel-levels {f1} and {f2} are not neighbors'
            ]

        elif fluent.startswith('in('):
            if is_without_object:
                return ['cargo is in a vehicle']
            cargo, vehicle = self.extract_multi_variable(fluent)
            return [
                f'cargo {cargo} is in vehicle {vehicle}',
                f'cargo {cargo} is located in vehicle {vehicle}',
                f'vehicle {vehicle} contains cargo {cargo}'
            ]
        elif fluent.startswith('-in('):
            if is_without_object:
                return ['cargo is not in a vehicle']
            cargo, vehicle = self.extract_multi_variable(fluent)
            return [
                f'cargo {cargo} is not in vehicle {vehicle}',
                f'cargo {cargo} is not located in vehicle {vehicle}',
                f'vehicle {vehicle} does not contain cargo {cargo}'
            ]

        elif fluent.startswith('has_space('):
            if is_without_object:
                return ['a vehicle has space']
            vehicle, space = self.extract_multi_variable(fluent)
            return [
                f'vehicle {vehicle} has space {space}',
                f'vehicle {vehicle} contains space {space}'
            ]
        elif fluent.startswith('-has_space('):
            if is_without_object:
                return ['a vehicle does not have space']
            vehicle, space = self.extract_multi_variable(fluent)
            return [
                f'vehicle {vehicle} does not have space {space}',
                f'vehicle {vehicle} does not contain space {space}'
            ]

        elif fluent.startswith('space_neighbor('):
            if is_without_object:
                return ['space neighbours another space']
            s1, s2 = self.extract_multi_variable(fluent)
            return [
                f'space {s1} neighbors space {s2}',
                f'spaces {s1} and {s2} are neighbors'
            ]
        elif fluent.startswith('-space_neighbor('):
            if is_without_object:
                return ['space does not neighbour another space']
            s1, s2 = self.extract_multi_variable(fluent)
            return [
                f'space {s1} does not neighbour space {s2}',
                f'spaces {s1} and {s2} are not neighbors'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return [
                f'vehicle {vehicle} moves to location {location2} from location {location1} that has fuel level {fuel_level1} and {fuel_level2}',
                f'vehicle {vehicle} moves from location {location1} which has fuel-levels {fuel_level1} and {fuel_level2} to location {location2}'
            ]
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return [
                f'cargo {cargo} is loaded in vehicle {vehicle} with space {space1} and space {space2} at location {location}',
                f'at location {location}, cargo {cargo} is loaded in vehicle {vehicle} with spaces {space1} and {space2}'
            ]
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return [
                f'cargo {cargo} is unloaded from vehicle {vehicle} with space {space1} and space {space2} at location {location}',
                f'at location {location}, cargo {cargo} is unloaded from vehicle {vehicle} with spaces {space1} and {space2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            # maintained
            if obj.startswith('vehicle'):
                return [
                    f'vehicle {obj} is being maintained at location {location}',
                    f'at location {location}, vehicle {obj} is maintained',
                    f'maintenance of vehicle {obj} occurs at location {location}'
                ]
            # inspected
            else:
                return [
                    f'cargo {obj} is inspected at location {location}',
                    f'at location {location}, cargo {obj} is inspected',
                    f'inspection of cargo {obj} occurs at location {location}'
                ]
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            # maintained
            if obj.startswith('vehicle'):
                return [
                    f'vehicle {obj} is not being maintained at location {location}',
                    f'at location {location}, vehicle {obj} is not maintained',
                    f'maintenance of vehicle {obj} does not occur at location {location}'
                ]
            # inspected
            else:
                return [
                    f'cargo {obj} is not inspected at location {location}',
                    f'at location {location}, cargo {obj} is not inspected',
                    f'inspection of cargo {obj} does not occur at location {location}'
                ]

        # far
        elif fluent.startswith('conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f'location {location1} is far from location {location2}',
                f'location {location1} and location {location2} are far from each other',
                f'locations {location1} and {location2} are far from each other'
            ]
        elif fluent.startswith('-conn('):
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f'location {location1} is not far from location {location2}',
                f'location {location1} and location {location2} are not far from each other',
                f'locations {location1} and {location2} are not far from each other'
            ]

        # sells
        elif fluent.startswith('has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return [
                f'location {location} sells fuel {fuel}',
                f'fuel {fuel} is sold at location {location}'
            ]
        elif fluent.startswith('-has_fuel('):
            location, fuel = self.extract_multi_variable(fluent)
            return [
                f'location {location} does not sell fuel {fuel}',
                f'fuel {fuel} is not sold at location {location}'
            ]

        # gas station
        elif fluent.startswith('fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return [
                f'gas station increases the fuel-level from {f2} to {f1}',
                f'fuel-level at gas station is increased from {f2} to {f1}',
                f'fuel-level at gas station is raised from {f2} to {f1}'
            ]
        elif fluent.startswith('-fuel_neighbor('):
            f1, f2 = self.extract_multi_variable(fluent)
            return [
                f'gas station does not increase the fuel-level from {f2} to {f1}',
                f'fuel-level at gas station is not increased from {f2} to {f1}',
                f'fuel-level at gas station is not raised from {f2} to {f1}'
            ]

        # secured
        elif fluent.startswith('in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return [
                f'cargo {cargo} is secured in vehicle {vehicle}',
                f'vehicle {vehicle} has cargo {cargo} secured'
            ]
        elif fluent.startswith('-in('):
            cargo, vehicle = self.extract_multi_variable(fluent)
            return [
                f'cargo {cargo} is not secured in vehicle {vehicle}',
                f'vehicle {vehicle} does not have cargo {cargo} secured'
            ]

        # parks in
        elif fluent.startswith('has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return [
                f'vehicle {vehicle} parks in space {space}',
                f'space {space} has vehicle {vehicle} parked in'
            ]
        elif fluent.startswith('-has_space('):
            vehicle, space = self.extract_multi_variable(fluent)
            return [
                f'vehicle {vehicle} does not parks in space {space}',
                f'space {space} does not have vehicle {vehicle} parked in'
            ]

        # same city
        elif fluent.startswith('space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return [
                f'space {s1} is in the same city as space {s2}',
                f'spaces {s1} and {s2} are in the same city'
            ]
        elif fluent.startswith('-space_neighbor('):
            s1, s2 = self.extract_multi_variable(fluent)
            return [
                f'space {s1} is not in the same city as space {s2}',
                f'spaces {s1} and {s2} are not in the same city'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # pulled over
        if action.startswith('move('):
            vehicle, location1, location2, fuel_level1, fuel_level2 = self.extract_multi_variable(action)
            return [
                f'vehicle {vehicle} gets pulled over at {location1}',
                f'at location {location1}, vehicle {vehicle} is pulled over'
            ]
        # breaks
        elif action.startswith('load('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return [
                f'cargo {cargo} present in vehicle {vehicle} breaks at location {location}',
                f'at location {location}, cargo {cargo} in vehicle {vehicle} breaks',
                f'cargo {cargo} breaks at location {location} in vehicle {vehicle}'
            ]
        # inspected
        elif action.startswith('unload('):
            cargo, vehicle, location, space1, space2 = self.extract_multi_variable(action)
            return [
                f'cargo {cargo} and vehicle {vehicle} are inspected at location {location}',
                f'at location {location}, inspection of cargo {cargo} and vehicle {vehicle} is performed'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


class Npuzzle(BaseDomain):
    DOMAIN_NAME = 'npuzzle'

    DOMAIN_DESC_WITHOUT_RAM = (
        'Moving a tile from source position to destination position is executable if source position and destination positions are neighbors i.e next to each other, destination position is empty and initially the tile is at source position. '
        'Moving a tile from source position to destination position causes the tile to be present at destination position, destination position to be not empty, and causes source position to be empty.'
    )
    DOMAIN_DESC_WITH_RAM = (
        'Moving a tile from source position to destination position is executable if source position and destination positions are neighbors i.e next to each other, destination position is empty and initially the tile is at source position. '
        "A position is not empty if the tile is at that position. A tile cannot be on multiple positions at the same time."
    )
    
    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['empty(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['neighbor(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS
    
    SUBSTRINGS_TO_RAND = {
        # Object types
        'tile': 'gkxiurkpij', 'tiles': 'gkxiurkpij',
        
        # Fluents
        'at': 'bcqdxwynvm', 'located at': 'bcqdxwynvm', 'present in': 'bcqdxwynvm',
        # 'neighbor': 'wbsxhcqjhh', 'neighbors': 'wbsxhcqjhh',
        # 'empty': 'vigzxelnpn', 'not contain': 'vigzxelnpn', 'contains': 'not vigzxelnpn',

        # Actions
        'move': 'edclnosigi', 'moves': 'edclnosigi', 'moving': 'edclnosigi', 'moved': 'edclnosigi',
        
        # Hallucinated Fluents
        'stuck': 'xqvgtgecje', 'trapped': 'xqvgtgecje',
        'color': 'weneqhejht',
        'stolen': 'iqipcjirbi', 'robbed': 'iqipcjirbi',

        # Hallucinated Actions
        'slid diagonally': 'tqgilaraqr',
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['a tile is at a position']
            tile, position = self.extract_multi_variable(fluent)
            return [
                f'tile {tile} is at position {position}',
                f'tile {tile} is located at position {position}',
                f'tile {tile} is present in the position {position}'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['a tile is not at a position']
            tile, position = self.extract_multi_variable(fluent)
            return [
                f'tile {tile} is not at position {position}',
                f'tile {tile} is not located at position {position}',
                f'tile {tile} is not present in the position {position}'
            ]

        elif fluent.startswith('neighbor('):
            if is_without_object:
                return ['positions are neighbors']
            position1, position2 = self.extract_multi_variable(fluent)
            return [
                f'position {position1} is a neighbor of position {position2}',
                f'position {position1} and position {position2} are neighbors',
                f'positions {position1} and {position2} are neighbors'
            ]
        elif fluent.startswith('-neighbor('):
            if is_without_object:
                return ['positions are not neighbors']
            position1, position2 = self.extract_multi_variable(fluent)
            return [
                f'position {position1} is not a neighbor of position {position2}',
                f'position {position1} and position {position2} are not neighbors',
                f'positions {position1} and {position2} are not neighbors'
            ]

        elif fluent.startswith('empty('):
            if is_without_object:
                return ['a position is empty']
            position = self.extract_single_variable(fluent)
            return [
                f'position {position} is empty',
                f'position {position} does not contain any tile'
            ]
        elif fluent.startswith('-empty('):
            if is_without_object:
                return ['a position is not empty']
            position = self.extract_single_variable(fluent)
            return [
                f'position {position} is not empty',
                f'position {position} contains a tile'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return [
                f'tile {tile} is moved from position {source} to position {destination}',
                f'tile {tile} is moved to position {destination} from postion {source}',
                f'tile {tile} is moved from position {source} to {destination}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # stuck
        if fluent.startswith('at('):
            tile, position = self.extract_multi_variable(fluent)
            return [
                f'tile {tile} is stuck at position {position}',
                f'tile {tile} is trapped at position {position}',
                f'at position {position}, tile {tile} is stuck'
            ]
        elif fluent.startswith('-at('):
            tile, position = self.extract_multi_variable(fluent)
            return [
                f'tile {tile} is not stuck at position {position}',
                f'tile {tile} is not trapped at position {position}',
                f'at position {position}, tile {tile} is not stuck'
            ]
        
        # color
        elif fluent.startswith('neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return [
                f'positions {position1} and {position2} are of the same color',
                f'position {position1} and position {position2} are of the same color',
                f'color of positions {position1} and {position2} is same'
            ]
        elif fluent.startswith('-neighbor('):
            position1, position2 = self.extract_multi_variable(fluent)
            return [
                f'positions {position1} and {position2} are not of the same color',
                f'position {position1} and position {position2} are not of the same color',
                f'color of positions {position1} and {position2} is not same'
            ]

        # stolen
        elif fluent.startswith('empty('):
            position = self.extract_single_variable(fluent)
            return [
                f'position {position} is stolen',
                f'position {position} is robbed',
            ]
        elif fluent.startswith('-empty('):
            position = self.extract_single_variable(fluent)
            return [
                f'position {position} is not stolen',
                f'position {position} is not robbed',
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # slid diagonally
        if action.startswith('move('):
            tile, source, destination = self.extract_multi_variable(action)
            return [
                f'tile {tile} is slid diagonally from position {source} to position {destination}',
                f'tile {tile} slid diagonally from positions {source} to {destination}',
                f'from position {source} to position {destination}, tile {tile} is slid diagonally'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'Taking an image on the satellite with the instrument set to a mode facing to the intended direction causes it to capture an image of the intended direction with the mode with which the instrument was set to.'
    )
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
        "Taking an image on the satellite with the instrument set to a mode facing to the intended direction causes it to capture an image of the intended direction with the mode with which the instrument was set to. "
    )

    BASE_POS_FLUENTS = ['power_on(', 'calibrated(', 'have_image(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['power_avail(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['pointing(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['on_board(', 'supports(', 'calibration_target(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'satellite': 'zzofnkbesk', 'satellites': 'zzofnkbesk',
        'direction': 'apdptereua', 'directions': 'apdptereua',
        'instrument': 'rstzlaxvor', 'instruments': 'rstzlaxvor',
        'mode': 'kegmrmllim', 'modes': 'kegmrmllim',
        
        # Fluents
        'on board': 'icafejchri',
        'support': 'rnayjosbpu', 'supports': 'rnayjosbpu', 'supported': 'rnayjosbpu', 'compatible': 'rnayjosbpu',
        'pointing': 'dcxxecpmem', 'pointed': 'dcxxecpmem', 'aimed': 'dcxxecpmem',
        'power': 'ymikwvufrq', 'powers': 'ymikwvufrq', 'powering': 'ymikwvufrq',
        'powered on': 'gwuqwrsowb', 'turned on': 'gwuqwrsowb', 'switched on': 'gwuqwrsowb',
        'calibrate': 'dymysndcxa', 'calibrates': 'dymysndcxa', 'calibration': 'dymysndcxa', 'calibrated': 'dymysndcxa',
        'image': 'fetzcryvyb', 'images': 'fetzcryvyb',

        # Actions
        'turns': 'lkvmwbvnym',
        'switched': 'sqsicvmhrn', 'turned': 'sqsicvmhrn',
        'take': 'idrpvqprlo', 'takes': 'idrpvqprlo', 'taking': 'idrpvqprlo', 'taken': 'idrpvqprlo',
        
        # Hallucinated Fluents
        'out of order': 'tqsivvkqmv',
        'discovers': 'rfhweivlxw', 'discovered': 'rfhweivlxw',
        'moving': 'lcjsvpixsr',
        'orbiting': 'kijwkqyxvi',
        'functioning': 'mghenxedvq', 'not malfunctioning': 'mghenxedvq', 'malfunctioning': 'not mghenxedvq',
        'color': 'xffcackzyl',
        'blocks': 'hcegzhfbsl', 'blocking': 'hcegzhfbsl', 'blocked': 'hcegzhfbsl',
        'maintenance': 'dvhhfxkfvm',

        # Hallucinated Actions
        'spins': 'vleiknomtc',
        'fixed': 'rjjbaiaogd',
        'dead': 'yxyozmtjnl', 'ceased to function': 'yxyozmtjnl',
        'transmits the information': 'gpjopmfweu', 'information is transmitted': 'gpjopmfweu', 'transmission of information': 'gpjopmfweu',
        'crashes': 'pobuoawcld'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('on_board('):
            if is_without_object:
                return ['an instrument is on board a satellite']
            instrument, satellite = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is on board {satellite}',
                f'{satellite} carries {instrument} on board',
                f'{satellite} has {instrument} on board'
            ]
        elif fluent.startswith('-on_board('):
            if is_without_object:
                return ['an instrument is not on board a satellite']
            instrument, satellite = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is not on board {satellite}',
                f'{satellite} does not carry {instrument} on board',
                f'{satellite} does not have {instrument} on board'
            ]

        elif fluent.startswith('supports('):
            if is_without_object:
                return ['an instrument supports a mode']
            instrument, mode = self.extract_multi_variable(fluent)
            return [
                f'{instrument} supports {mode}',
                f'{mode} is supported by {instrument}',
                f'{mode} is compatible with {instrument}'
            ]
        elif fluent.startswith('-supports('):
            if is_without_object:
                return ['an instrument does not support a mode']
            instrument, mode = self.extract_multi_variable(fluent)
            return [
                f'{instrument} does not support {mode}',
                f'{mode} is not supported by {instrument}',
                f'{mode} is not compatible with {instrument}'
            ]

        elif fluent.startswith('pointing('):
            if is_without_object:
                return ['a satellite is pointing to a direction']
            satellite, direction = self.extract_multi_variable(fluent)
            return [
                f'{satellite} is pointing to {direction}',
                f'{satellite} is aimed towards {direction}',
                f'{direction} is where {satellite} is pointed'
            ]
        elif fluent.startswith('-pointing('):
            if is_without_object:
                return ['a satellite is not pointing to a direction']
            satellite, direction = self.extract_multi_variable(fluent)
            return [
                f'{satellite} is not pointing to {direction}',
                f'{satellite} is not aimed towards {direction}',
                f'{direction} is not where {satellite} is pointed'
            ]

        elif fluent.startswith('power_avail('):
            if is_without_object:
                return ['a satellite has power']
            satellite = self.extract_single_variable(fluent)
            return [
                f'{satellite} has power available',
                f'power is available for {satellite}',
                f'{satellite} has power'
            ]
        elif fluent.startswith('-power_avail('):
            if is_without_object:
                return ['a satellite does not have power']
            satellite = self.extract_single_variable(fluent)
            return [
                f'{satellite} does not have power available',
                f'power is not available for {satellite}',
                f'{satellite} does not have power'
            ]

        elif fluent.startswith('power_on('):
            if is_without_object:
                return ['an instrument is powered on']
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is powered on',
                f'{instrument} is switched on',
                f'{instrument} is turned on'
            ]
        elif fluent.startswith('-power_on('):
            if is_without_object:
                return ['an instrument is not powered on']
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is not powered on',
                f'{instrument} is not switched on',
                f'{instrument} is not turned on'
            ]

        elif fluent.startswith('calibrated('):
            if is_without_object:
                return ['an instrument is calibrated']
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is calibrated',
                f'calibration of {instrument} is complete'
            ]
        elif fluent.startswith('-calibrated('):
            if is_without_object:
                return ['an instrument is not calibrated']
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is not calibrated',
                f'calibration of {instrument} is incomplete'
            ]

        elif fluent.startswith('have_image('):
            if is_without_object:
                return ['there is an image of a direction in a mode']
            direction, mode = self.extract_multi_variable(fluent)
            return [
                f'there is an image of {direction} in {mode}',
                f'image of {direction} exists in {mode}'
            ]
        elif fluent.startswith('-have_image('):
            if is_without_object:
                return ['there is not an image of a direction in a mode']
            direction, mode = self.extract_multi_variable(fluent)
            return [
                f'there is no image of direction {direction} in {mode}',
                f'image of {direction} does not exist in {mode}'
            ]

        elif fluent.startswith('calibration_target('):
            if is_without_object:
                return ['an instrument is calibrated for a direction']
            instrument, direction = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is calibrated for {direction}',
                f'calibration of {instrument} for {direction} is complete',
                f'for {direction}, {instrument} is calibrated'
            ]
        elif fluent.startswith('-calibration_target('):
            if is_without_object:
                return ['an instrument is not calibrated for a direction']
            instrument, direction = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is not calibrated for {direction}',
                f'calibration of {instrument} for {direction} is incomplete',
                f'for {direction}, {instrument} is not calibrated'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return [
                f'{satellite} turns to {new_dir} from {old_dir}',
                f'{satellite} turns from {old_dir} to {new_dir}',
                f'from {old_dir}, {satellite} turns to {new_dir}'
            ]
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return [
                f'{instrument} on {satellite} is switched on',
                f'{instrument} that is on {satellite} is turned on',
                f'on {satellite}, {instrument} is switched on'
            ]
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return [
                f'{instrument} on {satellite} is switched off',
                f'{instrument} that is on {satellite} is turned off',
                f'on {satellite}, {instrument} is switched off'
            ]
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return [
                f'{instrument} is calibrated on {satellite} to {direction}',
                f'{instrument} that is on {satellite} is calibrated to {direction}',
                f'calibration of {instrument} which is on {satellite} to {direction} is complete'
            ]
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return [
                f'image of {direction} is taken with {instrument} on {satellite} in {mode}',
                f'{instrument} which is on {satellite} takes an image of {direction} in {mode}',
                f'{satellite}\'s {instrument} takes an image of {direction} in {mode}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # out of order
        if fluent.startswith('on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is out of order on {satellite}',
                f'{satellite}\'s {instrument} is out of order',
                f'{instrument} which is on {satellite} is out of order'
            ]
        elif fluent.startswith('-on_board('):
            instrument, satellite = self.extract_multi_variable(fluent)
            return [
                f'{instrument} is not out of order on {satellite}',
                f'{satellite}\'s {instrument} is not out of order',
                f'{instrument} which is on {satellite} is not out of order'
            ]

        # discovers
        elif fluent.startswith('supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return [
                f'{instrument} discovers {mode}',
                f'{mode} is discovered by {instrument}'
            ]
        elif fluent.startswith('-supports('):
            instrument, mode = self.extract_multi_variable(fluent)
            return [
                f'{instrument} does not discover {mode}',
                f'{mode} is not discovered by {instrument}'
            ]

        # moving
        elif fluent.startswith('pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return [
                f'{satellite} is moving to {direction}',
                f'{satellite} starts moving to {direction}'
            ]
        elif fluent.startswith('-pointing('):
            satellite, direction = self.extract_multi_variable(fluent)
            return [
                f'{satellite} is not moving to {direction}',
                f'{satellite} does not start moving to {direction}'
            ]

        # orbiting
        elif fluent.startswith('power_avail('):
            satellite = self.extract_single_variable(fluent)
            return [
                f'{satellite} is orbiting',
                f'{satellite} starts orbiting'
            ]
        elif fluent.startswith('-power_avail('):
            satellite = self.extract_single_variable(fluent)
            return [
                f'{satellite} is not orbiting',
                f'{satellite} stops orbiting'
            ]

        # functioning
        elif fluent.startswith('power_on('):
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is functioning',
                f'{instrument} is functioning properly',
                f'{instrument} is not malfunctioning'
            ]
        elif fluent.startswith('-power_on('):
            instrument = self.extract_single_variable(fluent)
            return [
                f'{instrument} is not functioning',
                f'{instrument} is not functioning properly',
                f'{instrument} is malfunctioning'
            ]

        # color
        elif fluent.startswith('calibrated('):
            instrument = self.extract_single_variable(fluent)
            return [
                f'color of {instrument} is changed',
                f'color of {instrument} is modified'
            ]
        elif fluent.startswith('-calibrated('):
            instrument = self.extract_single_variable(fluent)
            return [
                f'color of {instrument} is not changed',
                f'color of {instrument} is not modified'
            ]

        # block
        elif fluent.startswith('have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return [
                f'{direction} is blocking {mode}',
                f'{mode} is blocked by {direction}',
                f'{direction} blocks {mode}'
            ]
        elif fluent.startswith('-have_image('):
            direction, mode = self.extract_multi_variable(fluent)
            return [
                f'{direction} is not blocking {mode}',
                f'{mode} is not blocked by {direction}',
                f'{direction} does not block {mode}'
            ]

        # maintenance
        elif fluent.startswith('calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return [
                f'{instrument} needs maintenance',
                f'maintenance of {instrument} is required',
                f'{instrument} is in need of maintenance'
            ]
        elif fluent.startswith('-calibration_target('):
            instrument, direction = self.extract_multi_variable(fluent)
            return [
                f'{instrument} does not need maintenance',
                f'maintenance of {instrument} is not required',
                f'{instrument} is not in need of maintenance'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # spins
        if action.startswith('turn_to('):
            satellite, new_dir, old_dir = self.extract_multi_variable(action)
            return [
                f'{satellite} spins to {new_dir} from {old_dir}',
                f'{satellite} spins from {old_dir} to {new_dir}',
                f'from {old_dir}, {satellite} spins to {new_dir}'
            ]
        # fixed
        elif action.startswith('switch_on('):
            instrument, satellite = self.extract_multi_variable(action)
            return [
                f'{instrument} is being fixed',
                f'{instrument} is currently being fixed'
            ]
        # dead
        elif action.startswith('switch_off('):
            instrument, satellite = self.extract_multi_variable(action)
            return [
                f'{instrument} is dead',
                f'{instrument} ceased to function'
            ]
        # transmit information
        elif action.startswith('calibrate('):
            satellite, instrument, direction = self.extract_multi_variable(action)
            return [
                f'{satellite} transmits the information to {instrument}',
                f'information is transmitted to {instrument} from {satellite}',
                f'transmission of information is done from {satellite} to {instrument}'
            ]
        # crashes
        elif action.startswith('take_image('):
            satellite, direction, instrument, mode = self.extract_multi_variable(action)
            return [
                f'{satellite} crashes while taking image in {direction}',
                f'{satellite} crashes while capturing image in {direction}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


class Spanner(BaseDomain):
    DOMAIN_NAME = 'spanner'

    DOMAIN_DESC_WITHOUT_RAM = (
        'Walking from start location to destination location is executable if the man is at the start location and there is a link between start and the destination location. '
        'Walking from start location to destination location causes the man to be at the destination location and not be at the start location. '
        'Picking up a spanner from a location is executable if the man and the spanner is at the same location. '
        'Picking up a spanner from a location causes the man to carry the spanner, and the spanner to be not at any location. '
        'Tightening the nut at a location with a spanner is executable if the man and the nut are at the same location, the man is carrying the spanner, the spanner is usable, and the nut is loose. '
        'Tightening the nut at a location with a spanner causes the nut to be not loose, the spanner to be unusable and the nut to be tightened.'
    )
    DOMAIN_DESC_WITH_RAM = (
        'Walking from start location to destination location is executable if the man is at the start location initially and there is a link between start and the destination location. '
        "Walking from start location to destination location causes the man to be at the destination location after the walk action from start location to destination location is executed. "

        "Picking up a spanner from start location is executable if the man is at start location and spanner is at start location. Picking up a spanner from the start location causes the man to carry the spanner. "

        "Tightening the nut at start location with a spanner is executable if the man is at start location, nut is at the start location, the man is carrying the spanner, the spanner is usable and the nut is loose. "
        "Tightening the nut at start location with a spanner causes the nut to be tightened. "

        "A man cannot be at two different places at the same time. "
        "The spanner is not at a location if it is being hold by the man. "
        "The nut is not loose if and only if it is tightened. "
        "The spanner is not usable if and only if the nut is tightened. "
    )
    
    BASE_POS_FLUENTS = ['carrying(', 'useable(', 'tightened(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['loose(', 'useable(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['link(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        # 'location': 'pyliwxfzrf', 'locations': 'pyliwxfzrf',
        'man': 'bmojqrwpdg',
        'nut': 'uwdhnrpile', 'nuts': 'uwdhnrpile',
        'spanner': 'ujzeqlcecc', 'spanners': 'ujzeqlcecc',

        # Fluents
        'at': 'dpafcwpirl', 'located at': 'dpafcwpirl', 'currently at': 'dpafcwpirl',
        'carrying': 'ljtnkvygkl', 'carried': 'ljtnkvygkl',
        'usable': 'fgbcjqnbgp', 'used': 'rhkukedvus', 'functional': 'rhkukedvus',
        'tighten': 'xvxccombol', 'tightens': 'xvxccombol', 'tightening': 'xvxccombol', 'tightened': 'xvxccombol',
        'loose': 'gwsneakmgx', 'not secured': 'gwsneakmgx', 'secured': 'not gwsneakmgx',
        'link': 'qzylwqxpoq', 'links': 'qzylwqxpoq', 'linking': 'qzylwqxpoq', 'linked': 'qzylwqxpoq',

        # Actions
        'walk': 'fvuxqntacz', 'walks': 'fvuxqntacz', 'walking': 'fvuxqntacz', 'walked': 'fvuxqntacz',
        'pick up': 'rcholfpyyj', 'picks up': 'rcholfpyyj', 'picking up': 'rcholfpyyj', 'picked up': 'rcholfpyyj',
        
        # Hallucinated Fluents
        'currently sleeping': 'sxjhblnhmo', 'currently not sleeping': 'not sxjhblnhmo', 'sleeping': 'sxjhblnhmo', 'napping': 'sxjhblnhmo',
        'sold': 'qaspmritqg',
        'at the store': 'ihpnhnfekz',
        'working': 'jnekioysmz', 'in working condition': 'jnekioysmz', 'useable': 'jnekioysmz', 'idlying around': 'not jnekioysmz',
        'needed': 'wnmnirqfhh', 'unnecessary': 'not wnmnirqfhh', 'wanted': 'wnmnirqfhh', 'necessary': 'wnmnirqfhh',
        'lost': 'nfpgqsphgw', 'gone missing': 'nfpgqsphgw', 'not found': 'nfpgqsphgw', 'found': 'not nfpgqsphgw',
        'small': 'llzhboyvst', 'insufficiently sized': 'llzhboyvst', 'not big enough': 'llzhboyvst', 'suffiiently sized': 'not llzhboyvst', 'big enough': 'not llzhboyvst',
        'far away': 'elvzkckros',

        # Hallucinated Actions
        'eats': 'icxbyvfyoq',
        'sleeps': 'jygyrgstxf', 'sleep': 'jygyrgstxf',
        'loses': 'hqjrjcyroa', 'lost': 'hqjrjcyroa',
        'forgets': 'mahhaeambm', 'forgotten': 'mahhaeambm'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['an obj is at a location']
            obj, location = self.extract_multi_variable(fluent)
            return [
                f"{obj} is at {location}",
                f'{obj} is located at {location}',
                f'{obj} is currently at {location}'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['an obj is not at a location']
            obj, location = self.extract_multi_variable(fluent)
            return [
                f"{obj} is not at {location}",
                f'{obj} is not located at {location}',
                f'{obj} is not currently at {location}'
            ]

        elif fluent.startswith('carrying('):
            if is_without_object:
                return ['an person is carrying a spanner']
            man, spanner = self.extract_multi_variable(fluent)
            return [
                f"{man} is carrying {spanner}",
                f'{spanner} is carried by {man}',
            ]
        elif fluent.startswith('-carrying('):
            if is_without_object:
                return ['an person is not carrying a spanner']
            man, spanner = self.extract_multi_variable(fluent)
            return [
                f"{man} is not carrying {spanner}",
                f'{spanner} is not carried by {man}',
            ]

        elif fluent.startswith('useable('):
            if is_without_object:
                return ['an spanner is usable']
            spanner = self.extract_single_variable(fluent)
            return [
                f"{spanner} is usable",
                f'{spanner} can be used',
                f'{spanner} is functional'
            ]
        elif fluent.startswith('-useable('):
            if is_without_object:
                return ['an spanner is not usable']
            spanner = self.extract_single_variable(fluent)
            return [
                f"{spanner} is not usable",
                f'{spanner} can\'t be used',
                f'{spanner} is not functional'
            ]

        elif fluent.startswith('tightened('):
            if is_without_object:
                return ['a nut is tightened']
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is tightened",
                f'tightening of {nut} is complete'
            ]
        elif fluent.startswith('-tightened('):
            if is_without_object:
                return ['a nut is not tightened']
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is not tightened",
                f'tightening of {nut} is incomplete'
            ]

        elif fluent.startswith('loose('):
            if is_without_object:
                return ['a nut is loose']
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is loose",
                f'{nut} is not secured'
            ]
        elif fluent.startswith('-loose('):
            if is_without_object:
                return ['a nut is not loose']
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is not loose",
                f'{nut} is secured'
            ]

        elif fluent.startswith('link('):
            if is_without_object:
                return ['locations are linked']
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f"{location1} is linked to {location2}",
                f'{location1} and {location2} are linked',
                f'a link between {location1} and {location2} exists'
            ]
        elif fluent.startswith('-link('):
            if is_without_object:
                return ['locations are not linked']
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f"{location1} is not linked to {location2}",
                f'{location1} and {location2} are not linked',
                f'a link between {location1} and {location2} does not exist'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return [
                f"{man} walks from {start} to {end}",
                f'{man} walks to {end} from {start}',
                f'from {start} to {end}, {man} walks'
            ]
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return [
                f"{man} picks up {spanner} from {loc}",
                f'from {loc}, {man} picks up {spanner}',
                f'{spanner} is picked up by {man} from {loc}'
            ]
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return [
                f"{man} tightens {nut} with {spanner} at {loc}",
                f'{nut} is tightened by {man} using {spanner} at {loc}',
                f'at {loc}, {man} uses {spanner} to tighten {nut}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, location = self.extract_multi_variable(fluent)
            # sleeping
            if obj.startswith('man'):
                return [
                    f"{obj} is sleeping",
                    f'{obj} is currently sleeping',
                    f'{obj} is napping'
                ]
            # sells
            elif obj.startswith('nut'):
                return [
                    f'{obj} is sold at {location}',
                    f'{obj} is currently sold at {location}',
                    f'{obj} is sold at store at {location}'
                ]
            # at the store
            else:
                return [
                    f"{obj} is at the store",
                    f'{obj} is currently at the store',
                    f'{obj} is at the store currently'
                ]
        elif fluent.startswith('-at('):
            obj, location = self.extract_multi_variable(fluent)
            # sleeping
            if obj.startswith('man'):
                return [
                    f"{obj} is not sleeping",
                    f'{obj} is currently not sleeping',
                    f'{obj} is not napping'
                ]
            # sells (changed from "screwed")
            elif obj.startswith('nut'):
                return [
                    f'{obj} is not sold at {location}',
                    f'{obj} is currently not sold at {location}',
                    f'{obj} is not sold at store at {location}'
                ]
            # at the store
            else:
                return [
                    f"{obj} is not at the store",
                    f'{obj} is currently not at the store',
                    f'{obj} is not at the store currently'
                ]

        # working
        elif fluent.startswith('carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return [
                f"{spanner} is working",
                f'{spanner} is in working condition',
                f'{spanner} is useable'
            ]
        elif fluent.startswith('-carrying('):
            man, spanner = self.extract_multi_variable(fluent)
            return [
                f'{man} is not working',
                f'{man} is idlying around',
                f'{man} isn\'t working'
            ]

        # needed
        elif fluent.startswith('useable('):
            spanner = self.extract_single_variable(fluent)
            return [
                f"{spanner} is not needed",
                f'{spanner} is unnecessary',
                f'{spanner} is not wanted'
            ]
        elif fluent.startswith('-useable('):
            spanner = self.extract_single_variable(fluent)
            return [
                f"{spanner} is needed",
                f'{spanner} is necessary',
                f'{spanner} is wanted'
            ]

        # lost
        elif fluent.startswith('tightened('):
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is lost",
                f'{nut} has gone missing',
                f'{nut} is not found'
            ]
        elif fluent.startswith('-tightened('):
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is not lost",
                f'{nut} hasn\'t gone missing',
                f'{nut} is found'
            ]

        # small
        elif fluent.startswith('loose('):
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is too small",
                f'{nut} is insufficiently sized',
                f'{nut} is not big enough'
            ]
        elif fluent.startswith('-loose('):
            nut = self.extract_single_variable(fluent)
            return [
                f"{nut} is not too small",
                f'{nut} is suffiiently sized',
                f'{nut} is big enough'
            ]

        # far away
        elif fluent.startswith('link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f"{location1} is far away from {location2}",
                f'{location1} and {location2} are far away from each other'
            ]
        elif fluent.startswith('-link('):
            location1, location2 = self.extract_multi_variable(fluent)
            return [
                f"{location1} is not far away from {location2}",
                f'{location1} and {location2} are not far away from each other'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # eats, sleeps
        if action.startswith('walk'):
            start, end, man = self.extract_multi_variable(action)
            return [
                f"{man} eats at {start} and sleeps at {end}",
                f'{man} sleeps at {end} and eats at {start}',
                f'{man} eats and sleep at {start} and {end} respectively'
            ]
        # loses
        elif action.startswith('pick_up_spanner('):
            loc, spanner, man = self.extract_multi_variable(action)
            return [
                f"{man} loses {spanner} at {loc}",
                f'at {loc}, {man} loses {spanner}',
                f'{spanner} is lost by {man} at {loc}'
            ]
        # forgets
        elif action.startswith('tighten_nut('):
            loc, spanner, man, nut = self.extract_multi_variable(action)
            return [
                f"{man} forgets {spanner} at {loc}",
                f'at {loc}, {man} forgets {spanner}',
                f'{spanner} is forgotten by {man} at {loc}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


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
        'It changes the current fuel level to its next level.'
    )
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
        "Person can only be at one place."
    )
    
    BASE_POS_FLUENTS = ['fuel_level(']
    BASE_NEG_FLUENTS = ['-' + fluent for fluent in BASE_POS_FLUENTS]
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = []
    DERIVED_NEG_FLUENTS = []
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at(', 'in(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['next(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'aircraft': 'psjemaawdi', 'aircrafts': 'psjemaawdi',
        'person': 'ihpgygxfoe', 'persons': 'ihpgygxfoe', 'people': 'ihpgygxfoe',
        'city': 'uibqqmoerq', 'cities': 'uibqqmoerq',
        'fuel level': 'ndozmmwian', 'fuel-level': 'ndozmmwian', 'fuel-levels': 'ndozmmwian',
        'airport': 'vuvceigmai', 'airports': 'vuvceigmai',

        # Fluents
        'at': 'nriukdvbwt', 'located at': 'nriukdvbwt', 'present at': 'nriukdvbwt',
        'in': 'mvfjxoptbs', 'present in': 'mvfjxoptbs', 'located in': 'mvfjxoptbs',

        # Actions
        'board': 'jxfvtxvzgh', 'boards': 'jxfvtxvzgh', 'boarding': 'jxfvtxvzgh', 'boarded': 'jxfvtxvzgh',
        'debark': 'jnjwzqrpms', 'debarks': 'jnjwzqrpms', 'debarking': 'jnjwzqrpms', 'debarked': 'jnjwzqrpms',
        'fly': 'gartdizjnu', 'flies': 'gartdizjnu', 'flying': 'gartdizjnu', 'flown': 'gartdizjnu',
        'zoom': 'rqdfjbixnz', 'zooms': 'rqdfjbixnz', 'zooming': 'rqdfjbixnz', 'zoomed': 'rqdfjbixnz',
        'refuel': 'egufeqdcrz', 'refuels': 'egufeqdcrz', 'refueling': 'egufeqdcrz', 'refueled': 'egufeqdcrz',
        
        # Hallucinated Fluents
        'explores': 'cgarufkgwp', 'explored': 'cgarufkgwp', 'exploring': 'cgarufkgwp', 'explore': 'cgarufkgwp',
        'maintained': 'grtwdbivmi', 'maintenance': 'grtwdbivmi',
        'jumps out': 'btrbutofgi', 'jumps': 'btrbutofgi', 'jump out': 'btrbutofgi', 'jump': 'btrbutofgi',
        'leak': 'qlqzceeadv', 'leaking': 'qlqzceeadv',
        'interchangeable': 'xqpoqobifo', 'replaced': 'xqpoqobifo', 'exchangeable': 'xqpoqobifo',

        # Hallucinated Actions
        'changes': 'nvjnoregfl', 'changed': 'nvjnoregfl',
        'forgets': 'dwviipdzfg',
        'crashes': 'oncqmxolxj',
        'bombing': 'grztcibeqd', 'bombs': 'grztcibeqd'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at('):
            if is_without_object:
                return ['at a city']
            obj, city = self.extract_multi_variable(fluent)
            return [
                f"{obj} is at {city}",
                f'{obj} is located at {city}',
                f'{obj} is present at {city}'
            ]
        elif fluent.startswith('-at('):
            if is_without_object:
                return ['not at a city']
            obj, city = self.extract_multi_variable(fluent)
            return [
                f"{obj} is not at {city}",
                f'{obj} is not located at {city}',
                f'{obj} is not present at {city}'
            ]
        
        elif fluent.startswith('in('):
            if is_without_object:
                return ['a person is in an aircraft']
            person, aircraft = self.extract_multi_variable(fluent)
            return [
                f"{person} is in {aircraft}",
                f'{person} is present in {aircraft}',
                f'{person} is located in {aircraft}'
            ]
        elif fluent.startswith('-in('):
            if is_without_object:
                return ['a person is not in an aircraft']
            person, aircraft = self.extract_multi_variable(fluent)
            return [
                f"{person} is not in {aircraft}",
                f'{person} is not  present in {aircraft}',
                f'{person} is not located in {aircraft}'
            ]

        elif fluent.startswith('fuel_level('):
            if is_without_object:
                return ['an aircraft has a fuel level']
            aircraft, flevel = self.extract_multi_variable(fluent)
            return [
                f"{aircraft} has fuel level {flevel}",
                f'{aircraft}\'s current fuel-level is {flevel}',
                f'{aircraft} possesses a fuel level of {flevel}'
            ]
        elif fluent.startswith('-fuel_level('):
            if is_without_object:
                return ['an aircraft does not have a fuel level']
            aircraft, flevel = self.extract_multi_variable(fluent)
            return [
                f"{aircraft} does not have fuel level {flevel}",
                f'{aircraft}\'s current fuel-level is not {flevel}',
                f'{aircraft} doesn\'t possesses a fuel level of {flevel}'
            ]
        
        elif fluent.startswith('next('):
            if is_without_object:
                return ['fuel levels are next to each other']
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return [
                f"fuel level {fuel2} is next to fuel level {fuel1}",
                f'fuel-levels {fuel2} and {fuel1} are next to each other',
                f'fuel level {fuel2} is next to {fuel1}'
            ]
        elif fluent.startswith('-next('):
            if is_without_object:
                return ['fuel levels are not next to each other']
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return [
                f"fuel level {fuel2} is not next to fuel level {fuel1}",
                f'fuel-levels {fuel2} and {fuel1} are not next to each other',
                f'fuel level {fuel2} is not next to {fuel1}'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return [
                f"{person} boards {aircraft} at {city}",
                f'{aircraft} is boarded by {person} at {city}',
                f'at {city}, {person} boards {aircraft}'
            ]
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return [
                f"{person} debarks {aircraft} at {city}",
                f'{aircraft} is debarked by {person} at {city}',
                f'at {city}, {person} debarks {aircraft}'
            ]
        elif action.startswith('fly('):
            aircraft, city1, city2, flevel1, flevel2 = self.extract_multi_variable(action)
            return [
                f"{aircraft} flies from {city1} to {city2} with fuel level {flevel1} to {flevel2}",
                f'{aircraft} with fuel-levels {flevel1} to {flevel2} flies from {city1} to {city2}',
                f'from {city1}, {aircraft} flies to {city2} with fuel level {flevel1} to {flevel2}'
            ]
        elif action.startswith('zoom('):
            aircraft, city1, city2, flevel1, flevel2, flevel3 = self.extract_multi_variable(action)
            return [
                f"{aircraft} zooms from {city1} to {city2} with fuel level {flevel1} to {flevel3}",
                f'{aircraft} with fuel-levels {flevel1} to {flevel3} zooms from {city1} to {city2}',
                f'from {city1}, {aircraft} zooms to {city2} with fuel level {flevel1} to {flevel3}',
                f"{aircraft} zooms from {city1} to {city2} and the fuel level drops from {flevel1} to {flevel3}"
            ]
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return [
                f"{aircraft} gets refueled at {city} with fuel level {flevel1} to {flevel2}",
                f'at {city}, {aircraft} gets refueled with fuel levels {flevel1} to {flevel2}',
                f'{aircraft} with fuel-levels {flevel1} and {flevel2} gets refueled at {city}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        if fluent.startswith('at('):
            obj, city = self.extract_multi_variable(fluent)
            # explores
            if obj.startswith('person'):
                return [
                    f"{obj} explores {city}",
                    f'{city} is explored by {obj}',
                    f'{obj} is currently exploring {city}'
                ]
            # maintained
            else:
                return [
                    f"{obj} is maintained",
                    f'{obj} is maintained up-to-date',
                    f'maintenance of {obj} is done'
                ]
        elif fluent.startswith('-at('):
            obj, city = self.extract_multi_variable(fluent)
            # explores
            if obj.startswith('person'):
                return [
                    f"{obj} does not explore {city}",
                    f'{city} is not explored by {obj}',
                    f'{obj} is currently not exploring {city}'
                ]
            # maintained
            else:
                return [
                    f"{obj} is not maintained",
                    f'{obj} is not maintained up-to-date',
                    f'maintenance of {obj} is not done'
                ]

        # jumps
        elif fluent.startswith('in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return [
                f'{person} jumps from {aircraft}',
                f'{person} jumps out of {aircraft}',
                f'{person} jumps out from {aircraft}'
            ]
        elif fluent.startswith('-in('):
            person, aircraft = self.extract_multi_variable(fluent)
            return [
                f'{person} does not jump from {aircraft}',
                f'{person} does not jump out of {aircraft}',
                f'{person} does not jump out from {aircraft}'
            ]

        # leak
        elif fluent.startswith('fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return [
                f"{aircraft} has a fuel leak",
                f'a fuel leak in {aircraft} is present',
                f'fuel is leaking from {aircraft}'
            ]
        elif fluent.startswith('-fuel_level('):
            aircraft, flevel = self.extract_multi_variable(fluent)
            return [
                f"{aircraft} does not have a fuel leak",
                f'a fuel leak in {aircraft} is not present',
                f'fuel is not leaking from {aircraft}'
            ]

        # interchangeable
        elif fluent.startswith('next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return [
                f'{fuel1} and {fuel2} are interchangeable',
                f'{fuel1} can be replaced by {fuel2}',
                f'{fuel1} and {fuel2} are exchangeable',
            ]
        elif fluent.startswith('-next('):
            fuel1, fuel2 = self.extract_multi_variable(fluent)
            return [
                f'{fuel1} and {fuel2} are not interchangeable',
                f'{fuel1} cannot be replaced by {fuel2}',
                f'{fuel1} and {fuel2} are not exchangeable',
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # changes
        if action.startswith('board('):
            person, aircraft, city = self.extract_multi_variable(action)
            return [
                f"{person} changes {aircraft} at {city}",
                f'at {city}, {person} changes {aircraft}',
                f'{aircraft} is changed by {person} at {city}'
            ]
        # forgets
        elif action.startswith('debark('):
            person, aircraft, city = self.extract_multi_variable(action)
            return [
                f"{person} forgets to board {aircraft} at {city}",
                f'at {city}, {person} forgets to board {aircraft}',
            ]
        # maintenance
        elif action.startswith('fly('):
            aircraft, city1, city2, fleve1, flevel2 = self.extract_multi_variable(action)
            return [
                f"{aircraft} is in {city1} then flies for maintenance to {city2}",
                f'{aircraft} flies to {city2} for maintenance from {city1}',
                f'from {city1}, {aircraft} flies from {city1} to {city2} for maintenance'
            ]
        # crashes
        elif action.startswith('zoom('):
            aircraft, city1, city2, fleve1, flevel2, flevel3 = self.extract_multi_variable(action)
            return [
                f'{aircraft} flies from {city1} and crashes at {city2}',
                f'{aircraft} crashes at {city2} after flying from {city1}',
                f'{aircraft} crashes at {city2} after flying from {city1}'
            ]
        # bombing
        elif action.startswith('refuel('):
            aircraft, city, flevel1, flevel2 = self.extract_multi_variable(action)
            return [
                f'{aircraft} goes for bombing at {city} and with fuel levels {flevel1} and {flevel2}',
                f'{aircraft} bombs at {city} with fuel levels {flevel1} and {flevel2}',
                f'at {city}, {aircraft} bombs with fuel levels {flevel1} and {flevel2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


class Visitall(BaseDomain):
    DOMAIN_NAME = 'visitall'

    DOMAIN_DESC_WITHOUT_RAM = (
        'A robot can move from its current position to the next position if the robot is at its current position and the current position is connected to the next position. '
        'Moving from the current position to the next position causes the robot to be at the next position, not at the current position anymore, and marks the next position as visited.'
    )
    DOMAIN_DESC_WITH_RAM = (
        'A robot can only move from its current position to the next position if the robot is at its current position and the current position is connected to the next position. '
        "Moving from a current position to the next position causes the robot to be present at the next position. "
        "A robot cannot be at two places at the same time. A place is marked as visited if a robot has been at that place. "
    )

    BASE_POS_FLUENTS = []
    BASE_NEG_FLUENTS = []
    BASE_FLUENTS = BASE_POS_FLUENTS + BASE_NEG_FLUENTS
    DERIVED_POS_FLUENTS = ['visited(']
    DERIVED_NEG_FLUENTS = ['-' + fluent for fluent in DERIVED_POS_FLUENTS]
    DERIVED_FLUENTS = DERIVED_POS_FLUENTS + DERIVED_NEG_FLUENTS
    PERSISTENT_POS_FLUENTS = ['at_robot(']
    PERSISTENT_NEG_FLUENTS = ['-' + fluent for fluent in PERSISTENT_POS_FLUENTS]
    PERSISTENT_FLUENTS = PERSISTENT_POS_FLUENTS + PERSISTENT_NEG_FLUENTS
    STATIC_POS_FLUENTS = ['connected(']
    STATIC_NEG_FLUENTS = ['-' + fluent for fluent in STATIC_POS_FLUENTS]
    STATIC_FLUENTS = STATIC_POS_FLUENTS + STATIC_NEG_FLUENTS

    SUBSTRINGS_TO_RAND = {
        # Object types
        'robot': 'xtjpivjhco', 'robots': 'xtjpivjhco',
        'position': 'puxuduuqen', 'positions': 'puxuduuqen',
        
        # Fluents
        'at': 'xrnkqzroyd', 'located at': 'xrnkqzroyd', 'placed at': 'xrnkqzroyd',
        'connect': 'dlipeeieju', 'connects': 'dlipeeieju', 'connecting': 'dlipeeieju', 'connected': 'dlipeeieju', 'connection': 'dlipeeieju',
        'visit': 'lknwwwkrbf', 'visits': 'lknwwwkrbf', 'visiting': 'lknwwwkrbf', 'visited': 'lknwwwkrbf',

        # Actions
        'move': 'pkjjnojvly', 'moves': 'pkjjnojvly', 'moving': 'pkjjnojvly', 'moved': 'pkjjnojvly',

        # Hallucinated Fluents
        'stuck': 'husphglbmv', 'trapped': 'husphglbmv',
        'far from': 'tjxlbfhbax', 'distant': 'tjxlbfhbax',
        'observed': 'rafvaikchw', 'observation': 'rafvaikchw',

        # Hallucinated Actions
        'jumps': 'ofcqrwklfo'
    }

    def fluent_to_natural_language_helper(self, fluent, is_without_object=False):
        if fluent.startswith('at_robot('):
            if is_without_object:
                return ['a robot is at a place']
            place = self.extract_single_variable(fluent)
            return [
                f"robot is at {place}",
                f'robot is located at {place}',
                f'robot is placed at {place}'
            ]
        elif fluent.startswith('-at_robot('):
            if is_without_object:
                return ['a robot is not at a place']
            place = self.extract_single_variable(fluent)
            return [
                f"robot is not at {place}",
                f'robot is not located at {place}',
                f'robot is not placed at {place}'
            ]

        elif fluent.startswith('connected('):
            if is_without_object:
                return ['places are connected']
            place1, place2 = self.extract_multi_variable(fluent)
            return [
                f"{place1} is connected to {place2}",
                f'{place1} and {place2} are connected',
                f'there is a connection between {place1} and {place2}'
            ]
        elif fluent.startswith('-connected('):
            if is_without_object:
                return ['places are not connected']
            place1, place2 = self.extract_multi_variable(fluent)
            return [
                f"{place1} is not connected to {place2}",
                f'{place1} and {place2} are not connected',
                f'there is no connection between {place1} and {place2}'
            ]

        elif fluent.startswith('visited('):
            if is_without_object:
                return ['a place is visited']
            place = self.extract_single_variable(fluent)
            return [
                f"{place} is visited",
                f'{place} is marked as visited'
            ]
        elif fluent.startswith('-visited('):
            if is_without_object:
                return ['a place is not visited']
            place = self.extract_single_variable(fluent)
            return [
                f"{place} is not visited",
                f'{place} is not marked as visited'
            ]

        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return [
                f"moves from {place1} to {place2}",
                f'robot moves from {place1} to {place2}',
                f'from {place1}, the robot moves to {place2}',
                f'moves to {place2} from {place1}',
                f'robot moves from {place1} to {place2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')

    def fluent_to_hallucinated_natural_language_helper(self, fluent):
        # stuck
        if fluent.startswith('at_robot('):
            place = self.extract_multi_variable(fluent)
            return [
                f"robot is stuck at {place}",
                f'robot is trapped at {place}',
                f'at {place}, the robot is stuck'
            ]
        elif fluent.startswith('-at_robot('):
            place = self.extract_multi_variable(fluent)
            return [
                f"robot is not stuck at {place}",
                f'robot is not trapped at {place}',
                f'at {place}, the robot is not stuck'
            ]

        # far from
        elif fluent.startswith('connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return [
                f"{place1} is far from to {place2}",
                f'{place1} and {place2} are far from each other',
                f'{place1} is distant from {place2}'
            ]
        elif fluent.startswith('-connected('):
            place1, place2 = self.extract_multi_variable(fluent)
            return [
                f"{place1} is not far from to {place2}",
                f'{place1} and {place2} are not far from each other',
                f'{place1} is not distant from {place2}'
            ]

        # observed
        elif fluent.startswith('visited('):
            place = self.extract_single_variable(fluent)
            return [
                f"{place} is observed",
                f'{place} is being observed',
                f'observation of {place} is taken'
            ]
        elif fluent.startswith('-visited('):
            place = self.extract_single_variable(fluent)
            return [
                f"{place} is not observed",
                f'{place} is not being observed',
                f'observation of {place} is not taken'
            ]
        else:
            raise Exception(f'fluent: {fluent} is not defined')

    def action_to_hallucinated_natural_language_helper(self, action):
        action = strip_action_prefix(action)
        # jump
        if action.startswith('move('):
            place1, place2 = self.extract_multi_variable(action)
            return [
                f"jumps from {place1} to {place2}",
                f'robot jumps from {place1} to {place2}',
                f'from {place1}, the robot jumps to {place2}',
                f'jumps to {place2} from {place1}',
                f'robot jumps from {place1} to {place2}'
            ]
        else:
            raise Exception(f'action: "{action}" is not defined')


ALL_DOMAIN_CLASSES = [Blocksworld, Depots, Driverlog, Goldminer, Grippers, Logistics, Miconic, Mystery, Npuzzle,
                      Satellite, Spanner, Visitall, Zenotravel]
ALL_DOMAIN_CLASSES_BY_NAME = {d.DOMAIN_NAME: d for d in ALL_DOMAIN_CLASSES}
DOMAIN_NAMES = [d.DOMAIN_NAME for d in ALL_DOMAIN_CLASSES]

if __name__ == '__main__':
    dom = Blocksworld(is_random_sub=False, is_ramifications=True)
    print(dom.domain_description)
    dom = Blocksworld(is_random_sub=True, is_ramifications=True)
    print(dom.domain_description)
    
    # domain = Visitall(is_random_sub=True, is_ramifications=False)
    # print(domain.fluent_to_natural_language('at_robot(p)'))
    # print(domain.fluent_to_natural_language('at_robot(p)'))
    # print(domain.fluent_to_natural_language('at_robot(p)'))
    # print(domain.fluent_to_natural_language('at_robot(p)'))

    # domain = Depots(is_random_sub=False, is_ramifications=False)
    # print(domain.fluent_to_natural_language('-clear(box2)', is_hallucinated=True))
