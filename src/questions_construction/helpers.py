import json
import random
from collections import defaultdict
import re
import uuid

class DomainMainMethods:
    def __init__(self, data):
        with open(data, 'r') as f:
            self.data = f.readlines()
        self.data = [json.loads(x) for x in self.data]
        optimal_sequence = []
        for timestep in self.data:
            for action, value in timestep.items():
                if value['part_of_plan?'] == True:
                    optimal_sequence.append(action)
        self.instance_id = '' #TODO add instance id
        self.optimal_sequence = optimal_sequence
        self.executable_actions = self.extract_executable_actions()
        self.inexecutable_actions = self.extract_inexecutable_actions()
        self.fluents_from_executable_actions = self.extract_fluents_from_executable_actions()
        self.fluents_from_optimal_sequence = self.extract_fluents_from_optimal_sequence()

    def get_random_inexecutable_sequence(self, plan_length):
        # Checking whether any inexecutable actions are present till the sequence length
        all_empty = True
        for i in range(plan_length):
            if self.inexecutable_actions[i+1]:
                all_empty = False
                break
        if all_empty:
            return None

        optimal_sequence = self.optimal_sequence[1:plan_length+1]
        index = random.randint(0,plan_length-1)    # This contains index of the inexecutable action
        while not self.inexecutable_actions[index+1]:    # If no inexecutable action exists for that location
            index = random.randint(0,plan_length-1)
        inexecutable_action = random.choice(self.inexecutable_actions[index+1])
        sequence = optimal_sequence[:index] + [inexecutable_action]
        while len(sequence) < plan_length:
            sequence += [random.choice(self.optimal_sequence[random.randint(1,20)])]    # Adding sequence from randomly generated optimal plan
        return sequence, index
    
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

class DomainQuestionGen(DomainMainMethods):
    QUESTION_MULTIPLICITY = 5
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    ACTION_JOIN_STR = ', '

    def __init__(self, data):
        super().__init__(data)

    def qa_object(self, question_type, question, answer):
        return {
            'id': uuid.uuid4(),
            'domain_name': self.domain_name,
            'instance_id': self.instance_id,
            'action_sequence': self.optimal_sequence,
            'question_type': question_type,
            'question': question,
            'answer': answer}

    def fluent_to_natual_language(self, fluent):
        raise('Implement it in the child class')
    
    def action_to_natural_language(self, action):
        raise('Implement it in the child class')

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]
    
    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')
    
    def unique_questions(self,question_generator, plan_length, multiplicity):
        # TODO implement dedup!!
        results = []
        for i in range(multiplicity):
            results.append(question_generator(plan_length))
        return results
    
    def question_constructors(self):
        return [self.composite_question_1, 
                self.composite_question_2,
                self.composite_question_3,
                self.composite_question_4,
                self.sub_question_1,
                self.sub_question_2,
                self.sub_question_3,
                self.sub_question_4,
                self.sub_question_5,
                self.sub_question_6,
                self.sub_question_7,
                self.sub_question_8,
                self.sub_question_9,
                self.sub_question_10,
                self.sub_question_11,
                self.sub_question_12,
                self.sub_question_13,
                self.sub_question_14,
                self.sub_question_15]
    
    def create_questions(self, plan_length, multiplicity=QUESTION_MULTIPLICITY):
        results = []
        for question_constructor in self.question_constructors():
            results.append(self.unique_questions(question_constructor, plan_length, multiplicity))
        return results
    
    
    def composite_question_1(self, plan_length):
        inexecutable_sequence, inexecutable_action_index = self.get_random_inexecutable_sequence(plan_length)

        inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join([self.action_to_natural_language(action) for action in inexecutable_sequence])
        questions = [
            f'Given the initial state, I plan to execute the following sequence of actions: {inexecutable_sequence_nlp}, what will be the state before the first inexecutable action occurs? If there are None, answer "None"',
            f'Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, what is the state before the first inexecutable action? If there are None, answer "None"',
        ]
        question = question[0] #TODO add random choice
        answer = self.fluents_from_optimal_sequence[inexecutable_action_index-1]

        return self.qa_object(self.composite_question_1.__name__, question, answer) 
    
    def composite_question_2(self, plan_length):
        # TODO implement
        pass

    def composite_question_3(self, plan_length):
        # TODO implement
        pass

    def composite_question_4(self, plan_length):
        # TODO implement
        pass

    def sub_question_1(self, plan_length):
        # TODO implement
        pass

    def sub_question_2(self, plan_length):
        # TODO implement
        pass

    def sub_question_3(self, plan_length):    
        # TODO implement
        pass    

    def sub_question_4(self, plan_length):
        # TODO implement
        pass

    def sub_question_5(self, plan_length):
        # TODO implement
        pass    

    def sub_question_6(self, plan_length):    
        # TODO implement
        pass    

    def sub_question_7(self, plan_length):
        # TODO implement
        pass    

    def sub_question_8(self, plan_length):
        # TODO implement
        pass

    def sub_question_9(self, plan_length):
        # TODO implement
        pass

    def sub_question_10(self, plan_length):
        # TODO implement
        pass

    def sub_question_11(self, plan_length):
        # TODO implement
        pass

    def sub_question_12(self, plan_length):
        # TODO implement
        pass    

    def sub_question_13(self, plan_length):
        # TODO implement
        pass    

    def sub_question_14(self, plan_length):
        # TODO implement
        pass    

    def sub_question_15(self, plan_length):
        # TODO implement
        pass    

    
        






