import os, traceback
import re
import time
import json

ASP_EXECUTION_TIME_LIMIT = 10
ASP_CODE_PATH = './ASP'
TMP_ASP_EXEC_PATH = f'{ASP_CODE_PATH}/tmp'


def tmp_name():
    return str(time.time()).replace('.', '_')

def rm_tmp_file(file_name):
    os.system(f"rm {file_name}")


def execute_asp(paths, time_limit=ASP_EXECUTION_TIME_LIMIT):
    if not os.path.isdir(TMP_ASP_EXEC_PATH):
        os.makedirs(TMP_ASP_EXEC_PATH)
    solution_save_path = os.path.join(TMP_ASP_EXEC_PATH, f'{tmp_name()}.lp.sol')
    try:
        # --outf=0 -V0 --out-atomf=%s. --quiet=1,2,2 | head -n1 | tr ' ' '\n'
        os.system(f"clingo --outf=2 --opt-mode=OptN --time-limit={time_limit} {paths.join(' ')} > {solution_save_path}")
        with open(solution_save_path) as f:
            asp_json = json.load(f)
        rm_tmp_file(solution_save_path)
        return asp_json
    except Exception as e:
        print(e)
        print(traceback.format_exc(), '\n')





class DataGenerator:
    """ Generate data about actions for a given domain, instance and plan sequence"""

    PART_OF_PLAN_KEY = "part_of_plan?"
    FEASIBLE_KEY = "feasible?"
    FLUENTS_KEY = "fluents"

    INIT_REGEX = re.compile(r'(init\((.|\n)+\)\.)')
    GOAL_REGEX = re.compile(r'(goal\((.|\n)+\)\.)')

    @staticmethod
    def open_asp(asp_path):
        with open(asp_path) as f:
            asp = f.read()
        return asp

    @staticmethod
    def extract_instance_state(instance_str, state_type):
        if state_type == "init":
            match = DataGenerator.INIT_REGEX.search(instance_str)
            if not match:
                raise Exception("No init state found in instance file.")
        elif state_type == "goal":
            match = DataGenerator.GOAL_REGEX.search(instance_str)
            if not match:
                raise Exception("No goal state found in instance file.")
        else:
            raise Exception("Unknown state type.")
        return match.group(0)

    def __init__(self, asp_domain_path, asp_instane_init_path, asp_instane_objects_path):
        self.domain_path = asp_domain_path
        self.asp_domain = self.open_asp(self.domain_path)

        self.asp_inst_init_path = asp_instane_init_path
        self.asp_inst_objects_path = asp_instane_objects_path

        self.initial_state = self.string_state_to_set(self.asp_inst_init_path, prefix='init(')

        self.data = []
        # data format
        # data = [
        # { action(var1, var2): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False},
        #   action(var2, var5): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False}
        # }, ...]

    def all_actions(self, current_state_asp_str):
        # TODO test
        tmp_current_state_path = os.path.join(ASP_CODE_PATH, f'{tmp_name()}.lp')
        with open(tmp_current_state_path, 'w') as f:
            f.write(current_state_asp_str)

        show_actions_path = os.path.join(ASP_CODE_PATH, 'show_actions.lp')
        paths = [current_state_asp_str, show_actions_path, self.domain_path, self.asp_inst_objects_path]
        asp_json = execute_asp(paths, time_limit=ASP_EXECUTION_TIME_LIMIT)

        actions = asp_json['Call'][0]['Witnesses']['Value'][0]
        rm_tmp_file(tmp_current_state_path)

        return actions

    def next_state(self, current_state, action):
        # TODO ASP code to determine next state, or return empty if not feasable
        next_state = set()
        return next_state

    def string_state_to_set(self, string_state, prefix='init('):
        # string_state is a sting with "prefix(fluent1, fluent2, ...)
        string_state = string_state.replace("\n", "")
        string_state = string_state.replace(prefix, "")
        string_state = string_state.replace(").", "")
        return set(string_state.split(';'))

    def generate_data(self, plan_sequence):
        current_state = self.string_state_to_set(self.initial_state)
        for i in range(len(plan_sequence)):
            data_for_step_i = {}
            for action in self.all_actions(current_state):
                data_for_step_i[action] = {
                    self.PART_OF_PLAN_KEY: action == plan_sequence[i],
                    self.FEASIBLE_KEY: self.is_action_feasable(current_state, action),
                    self.FLUENTS_KEY: self.next_state(current_state, action)}
            self.data.append(data_for_step_i)
            current_state = self.next_state(current_state, plan_sequence[i])
        return self.data
