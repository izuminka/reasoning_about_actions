import os, traceback

ASP_EXECUTION_TIME_LIMIT = 60


def assemble_asp(domain_path, instance_path, asp_general_path):
    asp_script = ''

    with open(asp_general_path) as f:
        general_asp = f.read()
    asp_script += '% GENERAL -------------------- \n\n'
    asp_script += general_asp + '\n\n'

    with open(domain_path) as f:
        domain = f.read()
    asp_script += '% DOMAIN  --------------------\n\n'
    asp_script += domain + '\n\n'

    with open(instance_path) as f:
        instance = f.read()
    asp_script += '% OBJECTS & INIT/GOAL --------------------\n\n'
    asp_script += instance

    return asp_script


def execute_asp(asp_path, solution_save_path, time_limit=ASP_EXECUTION_TIME_LIMIT):
    try:
        # --outf=0 -V0 --out-atomf=%s. --quiet=1,2,2 | head -n1 | tr ' ' '\n'
        os.system(f"clingo --outf=2 --opt-mode=OptN --time-limit={time_limit} {asp_path} > {solution_save_path}")
    except Exception as e:
        print(e)
        print(traceback.format_exc(), '\n')





class DataGenerator:
    def __init__(self, asp_domain_path, asp_init_goal):
        self.domain_path = asp_domain_path
        # TODO define ASP domain
        # TODO define ASP instance

        self.instance_path = asp_init_goal
        # TODO define initial_state
        # TODO define final_state

        self.data = []
        # data format
        # data = [
        # { action(var1, var2): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False},
        #   action(var2, var5): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False}
        # }, ...]

    def all_actions(self, current_state):
        # TODO ASP code to list all possible and imporssible actions
        return []

    def is_action_feasable(self, current_state, action):
        # TODO ASP code to determine if action is feasable
        # return True/False
        return True

    def generate_data(self, plan_sequence, initial_state):
        for i in range(len(plan_sequence)):
            current_state = initial_state
            data_for_step_i = {}
            for action in self.all_actions(current_state):
                action_data = {"part_of_plan?": action == plan_sequence[i],
                               "feasable?": self.is_action_feasable(current_state, action)}
                if action_data["feasable?"]:
                    # TODO
                    # generate state, save fluents
                    action_data["fluents"] = []
                else:
                    action_data["fluents"] = None
                data_for_step_i[action] = action_data
            self.data.append(data_for_step_i)
        return self.data
