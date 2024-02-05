import json
import random
import re
import uuid
import sys


class DomainMainMethods:
    def __init__(self, states_actions_jsonl, instance_id):
        with open(states_actions_jsonl, 'r') as f:
            self.states_actions = f.readlines()
        self.states_actions = [json.loads(x) for x in self.states_actions] # self.data[i] defines all action->states at time i, i==0 is NULL->initial state
        self.instance_id = instance_id
        self.given_plan_sequence = self.extract_given_plan_sequence()
        self.plan_length_max = len(self.given_plan_sequence) - 1 # since i=0 is a NULL action
        self.executable_actions = self.extract_executable_actions()
        self.inexecutable_actions = self.extract_inexecutable_actions()
        self.fluents_from_executable_actions = self.extract_fluents_from_executable_actions()
        self.fluents_from_optimal_sequence = self.extract_fluents_from_optimal_sequence()

    def extract_given_plan_sequence(self):
        given_plan_sequence = []
        for timestep in self.states_actions: # first is the null action
            for action, value in timestep.items():
                if value['part_of_plan?']:
                    given_plan_sequence.append(action)
        return given_plan_sequence
    
    def get_sequence_with_unknown_actions(self, plan_length):
        list_of_unknown_actions = ['action_shuffle','action_move','action_rotate','action_twist']
        unique_blocks = [block for action in self.given_plan_sequence for block in re.findall(r'\((.*?)\)', action)]
        unique_blocks = [block.split(',') for block in unique_blocks]
        unique_blocks = list({block for sublist in unique_blocks for block in sublist})
        random_paranthesis = f"""({random.choice(unique_blocks)}, {random.choice(unique_blocks)})"""
        random_action = f"""{random.choice(list_of_unknown_actions)}{random_paranthesis}"""
        unknown_action_index = random.randint(0,plan_length-1)
        sequences_with_unknown_actions = self.given_plan_sequence[1:plan_length+1].copy()
        sequences_with_unknown_actions.insert(unknown_action_index,random_action)
        while len(sequences_with_unknown_actions)<plan_length:
            sequences_with_unknown_actions += [random.choice(self.given_plan_sequence)]
        return sequences_with_unknown_actions, unknown_action_index
        
        pass

    def get_random_inexecutable_sequence(self, plan_length):
        # Checking whether any inexecutable actions are present till the sequence length
        all_empty = True
        for i in range(plan_length):
            if self.inexecutable_actions[i + 1]:
                all_empty = False
                break
        if all_empty:
            return None

        optimal_sequence = self.given_plan_sequence[1:plan_length+1]  # 1:plan_length + 1 because the first elemnt is the null action that points to the initial state
        index = random.randint(0, plan_length - 1)  # This contains index of the inexecutable action
        while not self.inexecutable_actions[index + 1]:  # If no inexecutable action exists for that location
            index = random.randint(0, plan_length - 1)
        inexecutable_action = random.choice(self.inexecutable_actions[index + 1])
        sequence = optimal_sequence[:index] + [inexecutable_action]
        while len(sequence) < plan_length:
            # sequence += [random.choice(
            #     self.given_plan_sequence[random.randint(0, self.plan_length_max - 1)])]  # Adding sequence from randomly generated optimal plan
            sequence += [random.choice(self.given_plan_sequence)]
        return sequence, index

    def extract_executable_actions(self):
        """This function extracts the executable actions
            from the entire plan which are not included
            in the optimal sequence"""

        exeutable_actions = []
        for timestep in self.states_actions:  # timestep is a dictionary with action as key and value as another dictionary
            timestep_executable_actions = []
            for action, value in timestep.items():
                if not value['part_of_plan?'] and value['feasible?'] and len(value['fluents']) > 0:
                    timestep_executable_actions.append(action)
            exeutable_actions.append(timestep_executable_actions)
        return exeutable_actions

    def extract_inexecutable_actions(self):
        """This function extracts the inexecutable actions from the entire plan"""

        inexecutable_actions = []
        for timestep in self.states_actions:
            timestep_inexecutable_actions = []
            for action, value in timestep.items():
                if not value['part_of_plan?'] and not value['feasible?'] and len(value['fluents']) == 0:
                    timestep_inexecutable_actions.append(action)
            inexecutable_actions.append(timestep_inexecutable_actions)
        return inexecutable_actions

    def extract_fluents_from_executable_actions(self):
        """This function extracts the fluents
            from the executable actions which
            are not in the optimal plan from the entire plan"""

        fluents_from_executable_actions = []
        for timestep in self.states_actions:
            timestep_fluents_from_executable_actions = []
            for action, value in timestep.items():
                if not value['part_of_plan?'] and value['feasible?'] and len(value['fluents']) > 0:
                    # timestep_fluents_from_executable_actions.append(value['fluents'])
                    for fluent in value['fluents']:
                        timestep_fluents_from_executable_actions.append(fluent)
            fluents_from_executable_actions.append(timestep_fluents_from_executable_actions)
        return fluents_from_executable_actions

    def extract_fluents_from_optimal_sequence(self):
        """This function extracts the fluents from the optimal sequence"""

        fluents_from_optimal_sequence = []
        for timestep in self.states_actions:
            timestep_fluents_from_optimal_sequence = []
            for action, value in timestep.items():
                if value['part_of_plan?'] and value['feasible?'] and len(value['fluents']) > 0:
                    # timestep_fluents_from_optimal_sequence.append(value['fluents'])
                    for fluent in value['fluents']:
                        timestep_fluents_from_optimal_sequence.append(fluent)
            fluents_from_optimal_sequence.append(timestep_fluents_from_optimal_sequence)
        return fluents_from_optimal_sequence

    def print_all(self):
        print(self.given_plan_sequence)
        print(self.executable_actions)
        print(self.inexecutable_actions)
        print(self.fluents_from_executable_actions)
        print(self.fluents_from_optimal_sequence)


class DomainQuestionGen(DomainMainMethods):
    """ Generates QAs * multiplicity for a given domain, init cond + plan sequence"""
    QUESTION_MULTIPLICITY = 5
    OBJ_IN_PAREN_REGEX = r'\((.*?)\)'
    ACTION_JOIN_STR = ', '

    def __init__(self,states_actions_jsonl,instance_id):
        super().__init__(states_actions_jsonl, instance_id)

    def domain_name(self):
        raise ('Implement it in the child class')

    def qa_data_object(self, question_type, question, answer):
        return {
            'id': uuid.uuid4(),
            'domain_name': self.domain_name(),
            'instance_id': self.instance_id,
            'action_sequence': self.given_plan_sequence,
            'question_type': question_type,
            'question': question,
            'answer': answer}

    def fluent_to_natual_language(self, fluent):
        raise ('Implement it in the child class')

    def action_to_natural_language(self, action):
        raise ('Implement it in the child class')

    def out_of_domain_action_name(self):
        #TODO create an out of domain action name. Has to be random, has to take random number of arguments,
        # ex: crane_lift(car1, structure2)
        # can be tricky since we are trying to tune the model later, need to make sure it's not gonna guess it easily
        # also need to return a NLP version of the action and params for self.action_to_natural_language child class
        pass

    def extract_single_variable(self, obj):
        return re.findall(self.OBJ_IN_PAREN_REGEX, obj)[0]

    def extract_multi_variable(self, obj):
        match = re.search(self.OBJ_IN_PAREN_REGEX, obj)
        return match.group(1).split(',')

    @staticmethod
    def unique_questions(question_generator, plan_length, multiplicity):
        # TODO implement dedup
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

    def create_questions(self, multiplicity=QUESTION_MULTIPLICITY):
        results = []
        for plan_length in range(1, self.plan_length_max + 1):
            for question_constructor in self.question_constructors():
                results += self.unique_questions(question_constructor, plan_length, multiplicity)
        return results

    @staticmethod
    def question_phrasing_choice(questions):
        # return random.choice(questions)
        return questions[0]  # TODO add random choice

    def composite_question_1(self, plan_length):
        inexecutable_sequence, inexecutable_action_index = self.get_random_inexecutable_sequence(plan_length)

        inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join(
            [self.action_to_natural_language(action) for action in inexecutable_sequence])
        questions = [
            f'Given the initial state, I plan to execute the following sequence of actions: {inexecutable_sequence_nlp}, what will be the state before the first inexecutable action occurs? If there are None, answer "None"',
            f'Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, what is the state before the first inexecutable action? If there are None, answer "None"',
        ]# TODO add more question variations (if needed)
        question = self.question_phrasing_choice(questions)
        answer = self.fluents_from_optimal_sequence[inexecutable_action_index]

        return self.qa_data_object(self.composite_question_1.__name__, question, answer)

    def composite_question_2(self, plan_length):
        # TODO implement
        pass

    def composite_question_3(self, plan_length):
        # TODO implement
        # pass
        inexecutable_sequence, inexecutable_action_index = self.get_random_inexecutable_sequence(plan_length)
        inexecutable_sequence_nlp = self.ACTION_JOIN_STR.join(
            [self.action_to_natural_language(inexecutable_sequence[action]) for action in range(1,len(inexecutable_sequence))])       
        # print(inexecutable_sequence)
        # break
        # sys.exit()         
        question = f"""Given the initial state and the sequence of actions: {inexecutable_sequence_nlp}, how many actions are performed before we encounter an inexecutable action?"""
        answer = inexecutable_action_index
        # pass
        return self.qa_data_object(self.composite_question_3.__name__,question,answer) 
        return f"""question: {question} answer: {answer}"""

    def composite_question_4(self, plan_length):
        # TODO implement
        # pass
        unknown_sequence, unknown_action_index = self.get_sequence_with_unknown_actions(plan_length)
        question = f"""Given the initial state, I plan to execute the following sequence of actions: {unknown_sequence}, what will be the state before the first unknown action occurs?"""
        if unknown_action_index == 0:
            answer = self.fluents_from_optimal_sequence[unknown_action_index]
        else:
            answer = self.fluents_from_optimal_sequence[unknown_action_index]
        # answer = self.fluents_from_optimal_sequence[unknown_action_index - 1]
        return self.qa_data_object(self.composite_question_4.__name__,question,answer)

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

# if __name__ == '__main__':
    # all_questions = []
    # for domain_class in domain_list:
    #     for instance_jsonl in instance_list:
    #         domain_instance = domain_class(instance_jsonl)
    #         all_questions += domain_instance.create_questions()
    # # TODO add batching
    # with open('questions.jsonl', 'w') as f:
    #     for question in all_questions:
    #         f.write(json.dumps(question) + '\n')
