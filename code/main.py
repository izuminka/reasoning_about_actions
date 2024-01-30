import os, traceback


class DataGenerator:
    """ Generate data about actions for a given domain, instance and plan sequence"""

    PART_OF_PLAN_KEY = "part_of_plan?"
    FEASIBLE_KEY = "feasible?"
    FLUENTS_KEY = "fluents"

    @staticmethod
    def open_asp(asp_path):
        with open(asp_path) as f:
            asp = f.read()
        return asp

    def __init__(self, asp_domain_path, asp_instance_path):
        self.domain_path = asp_domain_path
        self.asp_domain = self.open_asp(self.domain_path)

        self.asp_instance_path = asp_instance_path
        self.asp_instance = self.open_asp(self.asp_instance_path)
        # TODO define objects
        # TODO define initial_state
        # TODO define final_state

        self.data = []
        # data format
        # data = [
        # { action(var1, var2): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False},
        #   action(var2, var5): {"fluents": [fluent1, fluent2, ...], "feasable": True/False, "part_of_plan": True/False}
        # }, ...]

    def all_actions(self, current_state):
        # TODO ASP code to list all possible and impossible actions for a given state
        return []

    def is_action_feasable(self, current_state, action):
        # TODO ASP code to determine if action is feasable
        # return True/False
        return True

    def fluents_of_state(self, state):
        # TODO ASP code to list all fluents of a given state
        return []

    def generate_data(self, plan_sequence, initial_state):
        for i in range(len(plan_sequence)):
            current_state = initial_state
            data_for_step_i = {}
            for action in self.all_actions(current_state):
                action_data = {self.PART_OF_PLAN_KEY: action == plan_sequence[i],
                               self.FEASIBLE_KEY: self.is_action_feasable(current_state, action)}
                if action_data[self.FEASIBLE_KEY]:
                    action_data[self.FLUENTS_KEY] = self.fluents_of_state(current_state)
                else:
                    action_data[self.FLUENTS_KEY] = None
                data_for_step_i[action] = action_data
            self.data.append(data_for_step_i)
        return self.data
