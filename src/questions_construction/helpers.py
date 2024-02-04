import json

class Domain_question_generation:

    def __init__(self, data):
        with open(data, 'r') as f:
            self.data = f.readlines()
        self.data = [json.loads(x) for x in self.data]
        optimal_sequence = []
        for timestep in self.data:
            for action, value in timestep.items():
                if value['part_of_plan?'] == True:
                    optimal_sequence.append(action)
        self.optimal_sequence = optimal_sequence
        self.executable_actions = self.extract_executable_actions()
        self.inexecutable_actions = self.extract_inexecutable_actions()
        self.fluents_from_executable_actions = self.extract_fluents_from_executable_actions()
        self.fluents_from_optimal_sequence = self.extract_fluents_from_optimal_sequence()

    def extract_executable_actions(self):
        """This function extracts the executable actions
            from the entire plan which are not included
            in the optimal sequence"""

        exeutable_actions = []
        for timestep in self.data:  # timestep is a dictionary with action as key and value as another dictionary
            timestep_executable_actions = []
            for action, value in timestep.items():
                if value['part_of_plan?'] == False and value['feasible?'] == True and len(value['fluents']) > 0:
                    timestep_executable_actions.append(action)
            exeutable_actions.append(timestep_executable_actions)
        return exeutable_actions

    def extract_inexecutable_actions(self):
        """This function extracts the inexecutable actions from the entire plan"""

        inexecutable_actions = []
        for timestep in self.data:
            timestep_inexecutable_actions = []
            for action, value in timestep.items():
                if value['part_of_plan?'] == False and value['feasible?'] == False and len(value['fluents']) == 0:
                    timestep_inexecutable_actions.append(action)
            inexecutable_actions.append(timestep_inexecutable_actions)
        return inexecutable_actions

    def extract_fluents_from_executable_actions(self):
        """This function extracts the fluents
            from the executable actions which
            are not in the optimal plan from the entire plan"""

        fluents_from_executable_actions = []
        for timestep in self.data:
            timestep_fluents_from_executable_actions = []
            for action, value in timestep.items():
                if value['part_of_plan?'] == False and value['feasible?'] == True and len(value['fluents']) > 0:
                    # timestep_fluents_from_executable_actions.append(value['fluents'])
                    for fluent in value['fluents']:
                        timestep_fluents_from_executable_actions.append(fluent)
            fluents_from_executable_actions.append(timestep_fluents_from_executable_actions)
        return fluents_from_executable_actions


    def extract_fluents_from_optimal_sequence(self):
        """This function extracts the fluents from the optimal sequence"""

        fluents_from_optimal_sequence = []
        for timestep in self.data:
            timestep_fluents_from_optimal_sequence = []
            for action, value in timestep.items():
                if value['part_of_plan?'] == True and value['feasible?'] == True and len(value['fluents']) > 0:
                    # timestep_fluents_from_optimal_sequence.append(value['fluents'])
                    for fluent in value['fluents']:
                        timestep_fluents_from_optimal_sequence.append(fluent)
            fluents_from_optimal_sequence.append(timestep_fluents_from_optimal_sequence)
        return fluents_from_optimal_sequence

    def print_all(self):
        print(self.optimal_sequence)
        print(self.executable_actions)
        print(self.inexecutable_actions)
        print(self.fluents_from_executable_actions)
        print(self.fluents_from_optimal_sequence)


