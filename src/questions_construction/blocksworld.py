from collections import defaultdict
import random
from helpers import Domain_question_generation


class Blocksworld(Domain_question_generation):
    def __init__(self, data):
        super().__init__(data)

    def composite_question_1(self):
        composite_question_answers = defaultdict(dict)
        sequence_length = 1

        for i in range(3):
            custom_valid_action_sequences = self.optimal_sequence.copy()
            custom_valid_action_sequences = custom_valid_action_sequences[:sequence_length]
            select_random_inexecutable_action = random.choice(self.inexecutable_actions[i + 1])
            random_index = random.choice(range(len(custom_valid_action_sequences) + 1))
            custom_valid_action_sequences.insert(random_index, select_random_inexecutable_action)
            if random_index == 0:
                sequence_before_first_infeasible_action = self.fluents_from_optimal_sequence[
                    self.optimal_sequence.index(custom_valid_action_sequences[random_index + 1])]
            else:
                sequence_before_first_infeasible_action = self.fluents_from_optimal_sequence[
                    self.optimal_sequence.index(custom_valid_action_sequences[random_index - 1])]
            question = f"""Given the sequence of actions: {custom_valid_action_sequences},what is the state before the first infeasible action in the sequence??"""
            composite_question_answers[question] = sequence_before_first_infeasible_action
            sequence_length += 1
        return composite_question_answers
