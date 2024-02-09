
from ..questions_construction.domains import *
from ..questions_construction.main import *
import unittest
from ..common import *
import random

random.seed(10)

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'


class TestHelpers(unittest.TestCase):
    def assertListofListsIndepObjOrder(self, expected, predicted):
        """ assumes that the order of the lists in the list of lists is not important"""
        for e_ls, p_ls in zip(expected, predicted):
            self.assertEqual(set(e_ls), set(p_ls))


class TestQuestionGenerationMainMethods(TestHelpers):
    jsonl_object = open_jsonl(TESTS_DIR + '/toy_data.blocksworld.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    DMM = QuestionGenerationHelpers(jsonl_object, domain_class, instance_id)

    def test_extract_given_plan_sequence(self):
        true_plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_pick_up(b1)', 'action_stack(b1,b2)']
        self.assertEqual(true_plan_sequence, self.DMM.extract_given_plan_sequence())

    def test_extract_executable_actions(self):
        executable_actions_expected = [['action_unstack(b2,b1)'],
                                   ['action_put_down(b2)', 'action_stack(b2,b1)'],
                                   ['action_pick_up(b2)', 'action_pick_up(b1)'],
                                   ['action_stack(b1,b2)', 'action_put_down(b1)']]
        self.assertListofListsIndepObjOrder(executable_actions_expected, self.DMM.extract_executable_actions())

    def test_extract_inexecutable_actions(self):
        inexecutable_actions_expected = [
            ['action_pick_up(b2)', 'action_stack(b1,b2)', 'action_put_down(b2)', 'action_pick_up(b1)',
             'action_put_down(b1)', 'action_unstack(b1,b2)', 'action_stack(b2,b1)'],
            ['action_pick_up(b2)', 'action_stack(b1,b2)', 'action_pick_up(b1)', 'action_put_down(b1)',
             'action_unstack(b2,b1)', 'action_unstack(b1,b2)'],
            ['action_stack(b1,b2)', 'action_put_down(b2)', 'action_put_down(b1)', 'action_unstack(b2,b1)',
             'action_unstack(b1,b2)', 'action_stack(b2,b1)'],
            ['action_pick_up(b2)', 'action_put_down(b2)', 'action_pick_up(b1)', 'action_unstack(b2,b1)',
             'action_unstack(b1,b2)', 'action_stack(b2,b1)']]

        self.assertListofListsIndepObjOrder(inexecutable_actions_expected, self.DMM.extract_inexecutable_actions())

    def test_get_random_inexecutable_sequence(self):
        inexecutable_sequence = self.DMM.get_random_inexecutable_sequence(3)
        expected = (['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_put_down(b1)'], 2)
        self.assertEqual(expected, inexecutable_sequence)

    def test_extract_fluents_from_executable_actions(self):
        expected_fluents = [['on(b2, b1)', 'ontable(b1)', 'handempty', 'clear(b2)'],#INIT state, note: ", "
                        ['ontable(b1)', 'holding(b2)', 'clear(b1)'],
                        ['ontable(b1)', 'ontable(b2)', 'clear(b1)',  'clear(b2)', 'handempty'],
                        ['ontable(b2)', 'clear(b2)', 'holding(b1)'],
                        ['on(b1, b2)', 'ontable(b2)', 'handempty', 'clear(b1)']]
        self.assertListofListsIndepObjOrder(expected_fluents, self.DMM.extract_fluents_for_given_plan())

    def test_extract_neg_fluents_from_executable_actions(self):
        # expected_fluents = [['on(b2, b1)', 'ontable(b1)', 'handempty', 'clear(b2)'],#INIT state, note: ", "
        #                 ['ontable(b1)', 'holding(b2)', 'clear(b1)'],
        #                 ['ontable(b1)', 'ontable(b2)', 'clear(b1)',  'clear(b2)', 'handempty'],
        #                 ['ontable(b2)', 'clear(b2)', 'holding(b1)'],
        #                 ['on(b1, b2)', 'ontable(b2)', 'handempty', 'clear(b1)']]
        self.assertListofListsIndepObjOrder(expected_fluents, self.DMM.extract_fluents_for_given_plan())

    def test_qa_object(self):
        # TODO
        pass


class TestObjectTrackingQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = ObjectTrackingQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1,5,10,15,20]

    def test_q1(self):
        qa_object = self.object_tracking_questions.question_1()

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

class TestFluentTrackingQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = FluentTrackingQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestStateTrackingQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = StateTrackingQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestActionExecutabilityQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = ActionExecutabilityQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestEffectsQuestionsQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = EffectsQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestLoopingQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = LoopingQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestNumericalReasoningQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = NumericalReasoningQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass

class TestHallucinationQuestionsBlocksworld(unittest.TestCase):
    jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
    instance_id = 'sdf'
    domain_class = Blocksworld()
    object_tracking_questions = HallucinationQuestions(jsonl_object, domain_class, instance_id)
    plan_lengths = [1, 5, 10, 15, 20]

    def test_q1(self):
        # todo
        pass

    def test_q2(self):
        # todo
        pass

    def test_q3(self):
        # todo
        pass

    def test_q4(self):
        # todo
        pass

    def test_q5(self):
        # todo
        pass

    def test_q6(self):
        # todo
        pass


# class TestQuestionGenerationBlocksworld(unittest.TestCase):
#
#     def test_object_tracking_questions(self):
#         jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
#         instance_id = 'sdf'
#         domain_class = Blocksworld()
#         object_tracking_questions = ObjectTrackingQuestions(jsonl_object, domain_class, instance_id)
#
#     def test_all_questions(self):
#         jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
#         instance_id = 'sdf'
#         domain_class = Blocksworld()
#         all_questions = AllQuestions(jsonl_object, domain_class, instance_id)
#
#     def test_all_instances_object_tracking_questions(self):
#         domain_class = Blocksworld()
#         jsonl_objects = [open_jsonl(TESTS_DIR + '/data20.jsonl')]
#         all_questions = []
#         for instance_id, jsonl in jsonl_objects.items():
#             all_questions += ObjectTrackingQuestions(jsonl, domain_class, instance_id)
#
# class TestQuestionGenerationMultiDomain(unittest.TestCase):
#
#     def test_everything(self):
#         domain_clases = [Blocksworld()]
#         jsonl_objects = [open_jsonl(TESTS_DIR + '/data20.jsonl')] # TODO
#         all_questions = []
#         for domain_class in domain_clases:
#             for instance_id, jsonl in jsonl_objects.items():
#                 all_questions += AllQuestions(jsonl, domain_class, instance_id)



if __name__ == '__main__':
    unittest.main()
