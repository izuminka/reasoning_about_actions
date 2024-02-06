from ..questions_construction.main import *
from ..questions_construction.domains import *
import unittest
from ..common import *
import shutil
import random

random.seed(10)

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'


class TestQuestionGenerationMainMethods(unittest.TestCase):
    instance_id = 'sdf'
    DMM = DomainMainMethods(TESTS_DIR + '/data20.jsonl', instance_id)
    random.seed(10)

    def test_extract_given_plan_sequence(self):
        true_plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_pick_up(b1)',
                              'action_stack(b1,b2)']
        self.assertEqual(true_plan_sequence, self.DMM.extract_given_plan_sequence())

    def test_extract_executable_actions(self):
        executable_actions_true = [['action_unstack(b2,b1)'],
                                   ['action_put_down(b2)', 'action_stack(b2,b1)'],
                                   ['action_pick_up(b2)', 'action_pick_up(b1)'],
                                   ['action_stack(b1,b2)', 'action_put_down(b1)']]
        self.assertEqual(executable_actions_true, self.DMM.extract_executable_actions())

    def test_extract_inexecutable_actions(self):
        inexecutable_actions_true = [
            ['action_pick_up(b2)', 'action_stack(b1,b2)', 'action_put_down(b2)', 'action_pick_up(b1)',
             'action_put_down(b1)', 'action_unstack(b1,b2)', 'action_stack(b2,b1)'],
            ['action_pick_up(b2)', 'action_stack(b1,b2)', 'action_pick_up(b1)', 'action_put_down(b1)',
             'action_unstack(b2,b1)', 'action_unstack(b1,b2)'],
            ['action_stack(b1,b2)', 'action_put_down(b2)', 'action_put_down(b1)', 'action_unstack(b2,b1)',
             'action_unstack(b1,b2)', 'action_stack(b2,b1)'],
            ['action_pick_up(b2)', 'action_put_down(b2)', 'action_pick_up(b1)', 'action_unstack(b2,b1)',
             'action_unstack(b1,b2)', 'action_stack(b2,b1)']]
        self.assertEqual(inexecutable_actions_true, self.DMM.extract_inexecutable_actions())

    def test_get_random_inexecutable_sequence(self):
        random.seed(10)

        inexecutable_sequence = self.DMM.get_random_inexecutable_sequence(3)
        expected = (['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_stack(b1,b2)'], 2)
        self.assertEqual(expected, inexecutable_sequence)

    # def test_extract_fluents_from_executable_actions(self):
    #     true_fluents = [['ontable(b1)', 'holding(b2)', 'clear(b1)'],
    #                     ['ontable(b1)', 'clear(b2)', 'handempty', 'clear(b1)', 'ontable(b2)', 'ontable(b1)', 'clear(b2)', 'on(b2,b1)', 'handempty'],
    #                     ['ontable(b1)', 'holding(b2)', 'clear(b1)', 'ontable(b2)', 'holding(b1)', 'clear(b2)'],
    #                     ['on(b1,b2)', 'ontable(b2)', 'handempty', 'clear(b1)', 'ontable(b1)', 'clear(b2)', 'handempty', 'clear(b1)', 'ontable(b2)']]
    #
    #     print(self.DMM.extract_fluents_from_executable_actions())


class TestQuestionGenerationSingleDomain(unittest.TestCase):

    def test_object_tracking_questions(self):
        jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
        instance_id = 'sdf'
        domain_class = Blocksworld()
        object_tracking_questions = ObjectTrackingQuestions(jsonl_object, domain_class, instance_id)

    def test_all_questions(self):
        jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
        instance_id = 'sdf'
        domain_class = Blocksworld()
        all_questions = AllQuestions(jsonl_object, domain_class, instance_id)

    def test_all_instances_object_tracking_questions(self):
        domain_class = Blocksworld()
        jsonl_objects = [open_jsonl(TESTS_DIR + '/data20.jsonl')]
        all_questions = []
        for instance_id, jsonl in jsonl_objects.items():
            all_questions += ObjectTrackingQuestions(jsonl, domain_class, instance_id)

class TestQuestionGenerationMultiDomain(unittest.TestCase):

    def test_everything(self):
        domain_clases = [Blocksworld()]
        jsonl_objects = [open_jsonl(TESTS_DIR + '/data20.jsonl')] # TODO
        all_questions = []
        for domain_class in domain_clases:
            for instance_id, jsonl in jsonl_objects.items():
                all_questions += AllQuestions(jsonl, domain_class, instance_id)




if __name__ == '__main__':
    unittest.main()
