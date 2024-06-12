from ..questions_construction.domains import *
from ..questions_construction.questions import *
import unittest
from ..common import *
import random

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'

jsonl_object = open_jsonl(TESTS_DIR + '/data/toy_data.blocksworld.jsonl')
domain_class = Blocksworld(False, False)
instance_id = 'sdf'
plan_length_range = [1, 2, 3]


class TestHelpers(unittest.TestCase):
    def assertListofListsIndepObjOrder(self, expected, predicted):
        """ assumes that the order of the lists in the list of lists is not important"""
        for e_ls, p_ls in zip(expected, predicted):
            self.assertEqual(set(e_ls), set(p_ls))

    def assert_qa_object(self, qa_object):
        for _k, v in qa_object.items():
            self.assertIsNotNone(v)

        self.assertTrue(qa_object['question'])
        if qa_object[OUT_OBJ_ANSWER_TYPE] == TRUE_FALSE_ANSWER_TYPE:
            self.assertTrue(qa_object['answer'] in ['True', 'False'], msg=qa_object['answer'])

        for forbidden_char in "[]()'_-":
            self.assertTrue(forbidden_char not in qa_object['question'],
                            f"\n\n forbidden char: {forbidden_char}, \n question: {qa_object['question']}")
            if qa_object[OUT_OBJ_ANSWER_TYPE] == FREE_ANSWER_TYPE:
                self.assertTrue(forbidden_char not in qa_object['answer'],
                                f"\n\n forbidden char: {forbidden_char}, \n question: {qa_object['question']}")

        # Print manually
        print('\n\n')
        print(qa_object['question'])
        print(qa_object['answer'])

    def assert_qa_objects(self, question_constructor, plan_length_range=plan_length_range):
        for plan_length in plan_length_range:
            qa_object = question_constructor(plan_length)
            self.assert_qa_object(qa_object)

class TestQuestionGenerationMainMethods(TestHelpers):
    DMM = QuestionGenerationHelpers(jsonl_object, domain_class, instance_id)

    def setUp(self):
        random.seed(42)

    def test_extract_given_plan_sequence(self):
        true_plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_pick_up(b1)',
                              'action_stack(b1,b2)']
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
        expected_fluents = [['on(b2, b1)', 'ontable(b1)', 'handempty', 'clear(b2)'],  # INIT state, note: ", "
                            ['ontable(b1)', 'holding(b2)', 'clear(b1)'],
                            ['ontable(b1)', 'ontable(b2)', 'clear(b1)', 'clear(b2)', 'handempty'],
                            ['ontable(b2)', 'clear(b2)', 'holding(b1)'],
                            ['on(b1,b2)', 'ontable(b2)', 'handempty', 'clear(b1)']]
        self.assertListofListsIndepObjOrder(expected_fluents, self.DMM.extract_fluents_for_given_plan())

    def test_extract_neg_fluents_from_executable_actions(self):
        expected_neg_fluents = [['-clear(b1)', '-on(b1,b2)', '-holding(b2)', '-holding(b1)', '-ontable(b2)'],
                                ['-handempty', '-on(b1,b2)', '-on(b2,b1)', '-ontable(b2)', '-holding(b1)',
                                 '-clear(b2)'],
                                ['-holding(b2)', '-on(b2,b1)', '-on(b1,b2)', '-holding(b1)'],
                                ['-ontable(b1)', '-clear(b1)', '-handempty', '-on(b1,b2)', '-holding(b2)',
                                 '-on(b2,b1)'],
                                ['-ontable(b1)', '-holding(b2)', '-on(b2,b1)', '-holding(b1)', '-clear(b2)']]
        self.assertListofListsIndepObjOrder(expected_neg_fluents,
                                            self.DMM.extract_fluents_for_given_plan(NEG_FLUENTS_KEY))


if __name__ == '__main__':
    unittest.main()
