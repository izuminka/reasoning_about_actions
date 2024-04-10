import re
import sys
import os
from clyngor import ASP

sys.path.append('..')
sys.path.append('../../')
from src.common import *

ASP_CODE_PATH = f'{CODE_PATH}/states_actions_generation/ASP'
ASP_CHECK_SEQUENCE_PATH = os.path.join(ASP_CODE_PATH, 'check_sequence.lp')

def execute_asp_code(asp_code, time_limit=0):
    answers = list(ASP(asp_code, time_limit=time_limit))
    first = answers[0]
    for a in answers:
        if a != first:
            raise 'Returned ASP sets are not the same!'
    return first

def open_asp_action_sequence(plan_path):
    with open(plan_path) as f:
        plan_sequence_asp = f.read()
    plan_sequence = sorted([(action[1], action[0]) for _, action in execute_asp_code(plan_sequence_asp)],
                           key=lambda x: x[0])
    return [p for _, p in plan_sequence]


class StatesActionsGenerator:
    """ Generate data about actions for a given domain, instance and plan sequence"""

    CURRENT_STATE_PREFIX = "init("
    OBJECT_TYPES_REGEX = r'(\w+)\('
    OBJECT_INSTANCES_REGEX = r'(?<=\().+?(?=\))'

    @staticmethod
    def open_asp(asp_path):
        with open(asp_path) as f:
            asp = f.read()
        return asp

    @staticmethod
    def parse_objects(objects):
        # objects = 'block(a;b;c).\ntruck(t1;t2;t3)'
        # return {'block': ['a', 'b', 'c'], 'truck': ['t1', 't2', 't3']}        
        objects = objects.replace('\n', ' ')
        object_types = re.findall(StatesActionsGenerator.OBJECT_TYPES_REGEX, objects)
        object_dict = {}
        for t in object_types:
            instances = re.findall(StatesActionsGenerator.OBJECT_INSTANCES_REGEX, objects)[object_types.index(t)]
            instances = [obj.strip() for obj in instances.split(';')]
            object_dict[t] = instances
        return object_dict

    def __init__(self, asp_domain_path, asp_instance_init_path, asp_instance_objects_path):
        self.domain_path = asp_domain_path
        self.asp_domain = self.open_asp(self.domain_path)

        self.asp_inst_init_path = asp_instance_init_path
        self.asp_inst_objects_path = asp_instance_objects_path

        self.initial_state = self.asp_string_state_to_set(self.open_asp(self.asp_inst_init_path), prefix='init(')
        self.objects = self.open_asp(self.asp_inst_objects_path)

        self.data = []
        # data format
        # data = [
        # { action(var1, var2): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False},
        #   action(var2, var5): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False}
        # }, ...]

    def all_actions(self):
        show_actions_path = os.path.join(ASP_CODE_PATH, 'show_actions.lp')
        paths = [show_actions_path, self.domain_path, self.asp_inst_objects_path]
        asp_code = assemble_asp_code(paths)

        return set([action[0] for _, action in execute_asp_code(asp_code)])

    def next_state(self, current_state_set, action, asp_code_fname='next_state.lp'):
        action_occurs = f"occurs({action}, 1)."
        current_state_asp_str = self.set_to_asp_string_state(current_state_set)
        additional_asp_code = '\n' + '\n'.join([action_occurs, current_state_asp_str])

        next_state_path = os.path.join(ASP_CODE_PATH, asp_code_fname)
        paths = [ASP_CHECK_SEQUENCE_PATH, self.domain_path, next_state_path, self.asp_inst_objects_path]
        asp_code = assemble_asp_code(paths, additional_asp_code=additional_asp_code)
        next_state = set()
        for prefix, contents in execute_asp_code(asp_code):
            if prefix == 'not_exec':
                return []
            if contents[0]:
                next_state.add(contents[0])
        return list(next_state)

    def asp_string_state_to_set(self, state_str, prefix=CURRENT_STATE_PREFIX):
        # string_state is a sting with "prefix(fluent1, fluent2, ...)
        state_str = state_str.replace("\n", "")
        state_str = state_str.replace(prefix, "")
        state_str = state_str.replace(").", "")
        state_str = state_str.replace(", ", ",")
        state = set(state_str.split(';'))
        if "" in state:
            state.remove("")
        return state

    def set_to_asp_string_state(self, state_set, prefix=CURRENT_STATE_PREFIX):
        return prefix + ';'.join(list(state_set)) + ').'

    def create_data(self, plan_sequence):
        current_state = self.initial_state
        all_actions = self.all_actions()
        self.data.append({INIT_ACTION_KEY: {PART_OF_PLAN_KEY: True,
                                            FLUENTS_KEY: list(current_state),
                                            # HACK: i pass garbage like then just returns the neg fluents of the current state
                                            NEG_FLUENTS_KEY: self.next_state(current_state, 'sdfsdfd',
                                                                             'next_state_neg_fluents.lp'),
                                            OBJECTS_KEY: self.parse_objects(self.objects),
                                            EXECUTABLE_ACTION_BOOL_KEY: True}})
        for i in range(len(plan_sequence)):
            data_for_step_i = {}
            for action in all_actions:
                data_for_step_i[action] = {
                    PART_OF_PLAN_KEY: action == plan_sequence[i],
                    FLUENTS_KEY: self.next_state(current_state, action),
                    NEG_FLUENTS_KEY: self.next_state(current_state, action, 'next_state_neg_fluents.lp')}
                data_for_step_i[action][EXECUTABLE_ACTION_BOOL_KEY] = bool(data_for_step_i[action][FLUENTS_KEY])
            self.data.append(data_for_step_i)
            current_state = self.next_state(current_state, plan_sequence[i])
        return self.data

    def save_data(self, save_path):
        with jsonlines.open(save_path, 'w') as w:
            w.write_all(self.data)


def main(domain_name, instance_name):
    save_dir = f'{STATES_ACTIONS_PATH}/{domain_name}'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = f'{save_dir}/{instance_name}.jsonl'
    if os.path.exists(save_path):
        raise f'File {save_path} already exists'

    domain_path = f'{DATA_PATH}/initial/asp/{domain_name}/domain.lp'
    instance_path = f'{DATA_PATH}/initial/asp/{domain_name}/instances/{instance_name}'

    action_sequence = open_asp_action_sequence(f'{instance_path}/plan.lp')
    states_actions_generator = StatesActionsGenerator(domain_path, f'{instance_path}/init.lp', f'{instance_path}/objects.lp')
    print('generating data')
    data = states_actions_generator.create_data(action_sequence)

    optimal_sequence = []
    for timestep in data:
        for action, value in timestep.items():
            if value['part_of_plan?']:
                optimal_sequence.append(action)
    assert (optimal_sequence[1:] == action_sequence)
    print('quick validation passed')

    print('saving')
    save_jsonl(data, save_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate data for a given domain, instance (init, objects, plan)')
    parser.add_argument('--domain_name', '-d', type=str, help='Specify the domain name', required=True)
    parser.add_argument('--instance_name', '-i', type=str, help='Specify the instance name', required=True)
    args = parser.parse_args()

    main(args.domain_name, args.instance_name)
