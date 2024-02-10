from ..questions_construction.domains import *
from ..questions_construction.main import *
import unittest
from ..common import *
import random

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'

jsonl_object = open_jsonl(TESTS_DIR + '/toy_data.blocksworld.jsonl')
domain_class = Blocksworld()
instance_id = 'sdf'
plan_length_range = [1, 2, 3, 4]


class TestHelpers(unittest.TestCase):
    def assertListofListsIndepObjOrder(self, expected, predicted):
        """ assumes that the order of the lists in the list of lists is not important"""
        for e_ls, p_ls in zip(expected, predicted):
            self.assertEqual(set(e_ls), set(p_ls))

    def assert_qa_object(self, qa_object):
        for _k, v in qa_object.items():
            self.assertIsNotNone(v)

        self.assertTrue(qa_object['question'])
        if qa_object[OUT_OBJ_ANSWER_TYPE] == TRUE_FALSE_ANSWER:
            self.assertTrue(qa_object['answer'] in [True, False], msg=qa_object['answer'])

        for forbidden_char in "[]()'_-":
            self.assertTrue(forbidden_char not in qa_object['question'],
                            f"\n\n forbidden char: {forbidden_char}, \n question: {qa_object['question']}")
            if qa_object[OUT_OBJ_ANSWER_TYPE] == FREE_ANSWER:
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


class TestObjectTrackingQuestionsBlocksworld(TestHelpers):
    qa_class = ObjectTrackingQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_all_questions(self):
        multiplicity = 1
        plan_lengths = [1, 2, 3, 4]
        questions = self.qa_class.create_questions(multiplicity, plan_lengths)
        self.assertEqual(len(questions), 4*len(plan_lengths))

        for q in questions:
            self.assert_qa_object(q)

class TestFluentTrackingQuestionsBlocksworld(TestHelpers):
    qa_class = FluentTrackingQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)
    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_q5(self):
        self.assert_qa_objects(self.qa_class.question_5)

    def test_q6(self):
        self.assert_qa_objects(self.qa_class.question_6)


class TestStateTrackingQuestionsBlocksworld(TestHelpers):
    qa_class = StateTrackingQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)


class TestActionExecutabilityQuestionsBlocksworld(TestHelpers):
    qa_class = ActionExecutabilityQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_q5(self):
        self.assert_qa_objects(self.qa_class.question_5)

    def test_q6(self):
        self.assert_qa_objects(self.qa_class.question_6)


class TestEffectsQuestionsQuestionsBlocksworld(TestHelpers):
    qa_class = EffectsQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

class TestLoopingQuestionsBlocksworld(TestHelpers):
    qa_class = LoopingQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_q5(self):
        self.assert_qa_objects(self.qa_class.question_5)

    def test_q6(self):
        self.assert_qa_objects(self.qa_class.question_6)


class TestNumericalReasoningQuestionsBlocksworld(TestHelpers):
    qa_class = NumericalReasoningQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_q5(self):
        self.assert_qa_objects(self.qa_class.question_5)

    def test_q6(self):
        self.assert_qa_objects(self.qa_class.question_6)


class TestHallucinationQuestionsBlocksworld(TestHelpers):
    qa_class = HallucinationQuestions(jsonl_object, domain_class, instance_id)

    def test_q1(self):
        self.assert_qa_objects(self.qa_class.question_1)

    def test_q2(self):
        self.assert_qa_objects(self.qa_class.question_2)

    def test_q3(self):
        self.assert_qa_objects(self.qa_class.question_3)

    def test_q4(self):
        self.assert_qa_objects(self.qa_class.question_4)

    def test_q5(self):
        self.assert_qa_objects(self.qa_class.question_5)

    def test_q6(self):
        self.assert_qa_objects(self.qa_class.question_6)

class TestQuestionGenerationAll(unittest.TestCase):

    def test_all_questions_one_domain_one_instance(self):
        jsonl_object = open_jsonl(TESTS_DIR + '/data20.jsonl')
        instance_id = 'sdf'
        domain_class = Blocksworld()
        all_questions = AllQuestions(jsonl_object, domain_class, instance_id)

    def test_all_questions_one_domain_all_instances(self):
        pass

    def test_all_questions_all_domain_all_instances(self):
        domain_clases = [d() for d in ALL_DOMAIN_CLASSES]
        jsonl_objects = [open_jsonl(os.path.join(TESTS_DIR + f'{d}.Instance_1.data20.jsonl')) for d in domain_clases]
        all_questions = []
        for domain_class in domain_clases:
            for instance_id, jsonl in jsonl_objects.items():
                all_questions += AllQuestions(jsonl, domain_class, instance_id)


if __name__ == '__main__':
    unittest.main()
