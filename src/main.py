import sys
import jsonlines
import os
from clyngor.inline import ASP_last_model

CODE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CODE_PATH)

ASP_EXECUTION_TIME_LIMIT = 10
ASP_CODE_PATH = f'{CODE_PATH}/ASP'
TMP_ASP_EXEC_PATH = f'{ASP_CODE_PATH}/tmp'


def assemble_asp_code(paths, additional_asp_code='', separator='\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n'):
    asp_code = []
    for path in paths:
        with open(path, 'r') as f:
            asp_code.append(f.read())
    asp_code = separator.join(asp_code)
    if additional_asp_code:
        asp_code += f"{separator}{additional_asp_code}"
    return asp_code


def open_jsonl(path):
    with jsonlines.open(path, 'r') as r:
        data = [obj for obj in r]
    return data


class DataGenerator:
    """ Generate data about actions for a given domain, instance and plan sequence"""

    PART_OF_PLAN_KEY = "part_of_plan?"
    FEASIBLE_KEY = "feasible?"
    FLUENTS_KEY = "fluents"

    CURRENT_STATE_PREFIX = "current_state("
    INIT_ACTION_KEY = 'action_init'

    @staticmethod
    def open_asp(asp_path):
        with open(asp_path) as f:
            asp = f.read()
        return asp

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

    def all_actions(self, current_state_set):
        if not current_state_set:
            return set()

        current_state_asp_str = self.set_to_asp_string_state(current_state_set)
        show_actions_path = os.path.join(ASP_CODE_PATH, 'show_actions.lp')
        paths = [show_actions_path, self.domain_path, self.asp_inst_objects_path]
        asp_code = assemble_asp_code(paths, additional_asp_code=current_state_asp_str)

        return set([action[0] for _, action in ASP_last_model(asp_code)])

    def next_state(self, current_state_set, action):
        action_occurs = f"occurs({action}, 1)."
        current_state_asp_str = self.set_to_asp_string_state(current_state_set)
        additional_asp_code = '\n' + '\n'.join([action_occurs, current_state_asp_str])

        next_state_path = os.path.join(ASP_CODE_PATH, 'next_state.lp')
        paths = [self.domain_path, self.asp_inst_objects_path, next_state_path]
        asp_code = assemble_asp_code(paths, additional_asp_code=additional_asp_code)
        next_state = set()
        for prefix, contents in ASP_last_model(asp_code):
            if prefix == 'not_exec':
                return []
            next_state.add(contents[0])
        return list(next_state)

    def asp_string_state_to_set(self, state_str, prefix=CURRENT_STATE_PREFIX):
        # string_state is a sting with "prefix(fluent1, fluent2, ...)
        state_str = state_str.replace("\n", "")
        state_str = state_str.replace(prefix, "")
        state_str = state_str.replace(").", "")
        return set(state_str.split(';'))

    def set_to_asp_string_state(self, state_set, prefix=CURRENT_STATE_PREFIX):
        return prefix + ';'.join(list(state_set)) + ').'

    def generate_data(self, plan_sequence):
        current_state = self.initial_state
        self.data.append({self.INIT_ACTION_KEY: {self.PART_OF_PLAN_KEY: True,
                                            self.FLUENTS_KEY: list(current_state), self.FEASIBLE_KEY: True}})
        for i in range(len(plan_sequence)):
            data_for_step_i = {}
            for action in self.all_actions(current_state):
                data_for_step_i[action] = {
                    self.PART_OF_PLAN_KEY: action == plan_sequence[i],
                    self.FLUENTS_KEY: self.next_state(current_state, action)}
                data_for_step_i[action][self.FEASIBLE_KEY] = bool(data_for_step_i[action][self.FLUENTS_KEY])
            self.data.append(data_for_step_i)
            current_state = self.next_state(current_state, plan_sequence[i])
        return self.data

    def save_data(self, save_path):
        with jsonlines.open(save_path, 'w') as w:
            w.write_all(self.data)
