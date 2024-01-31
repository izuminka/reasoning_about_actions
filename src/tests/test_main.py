from ..main import *
import unittest
import shutil

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'


class TestStringMethods(unittest.TestCase):
    DG = DataGenerator(CODE_PATH + '/tests/asp/domains/blocksworld/domain.lp',
                       CODE_PATH + '/tests/asp/domains/blocksworld/instances/inst1/init.lp',
                       CODE_PATH + '/tests/asp/domains/blocksworld/instances/inst1/objects.lp')

    # from the initial condition
    init_state = {'handempty', 'ontable(b1)', 'on(b2, b1)', 'clear(b2)'}
    infeasible_actions = {'action_put_down(b2)', 'action_unstack(b1,b2)', 'action_stack(b1,b2)',
                          'action_pick_up(b1)', 'action_put_down(b1)', 'action_stack(b2,b1)', 'action_pick_up(b2)'}
    feasible_actions = {'action_unstack(b2,b1)'}

    def setUp(self):
        if not os.path.isdir(TMP_DIR):
            os.makedirs(TMP_DIR)

    def tearDown(self):
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_attributes(self):
        self.assertEqual(self.DG.initial_state, self.init_state)
        self.assertEqual(self.DG.objects, 'block(b1; b2).')

    def test_all_actions(self):
        self.assertEqual(set(), self.DG.all_actions(set()))

        actions = self.DG.all_actions(self.DG.initial_state)
        self.assertEqual(actions, self.infeasible_actions.union(self.feasible_actions))

    def test_next_state_infeasible_actions(self):
        for a in self.infeasible_actions:
            self.assertEqual([], self.DG.next_state(self.DG.initial_state, a))

    def test_next_state_feasible_actions(self):
        action = 'action_unstack(b2,b1)'
        expected_state = ['holding(b2)', 'clear(b1)', 'ontable(b1)'].sort()
        self.assertEqual(expected_state, self.DG.next_state(self.DG.initial_state, action).sort())

    def test_pipeline(self):
        plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)']
        data = self.DG.generate_data(plan_sequence)
        self.assertEqual(len(data), len(plan_sequence) + 1)

        part_of_plan_actions = []
        for i, states in enumerate(data[1:]):  # data[0] is the init condition
            for action, d in states.items():
                self.assertTrue('action_' in action)
                if d[DataGenerator.FEASIBLE_KEY]:
                    self.assertTrue(len(d[DataGenerator.FLUENTS_KEY]) > 0)
                else:
                    self.assertEqual([], d[DataGenerator.FLUENTS_KEY])

                if action == plan_sequence[i]:
                    self.assertTrue(d[DataGenerator.PART_OF_PLAN_KEY])
                    part_of_plan_actions.append(action)
        self.assertEqual(part_of_plan_actions, plan_sequence)

    def test_save_data_validate(self):
        plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)']
        data = self.DG.generate_data(plan_sequence)
        save_path = TMP_DIR + '/data.jsonl'
        self.DG.save_data(save_path)

        data_from_file = open_jsonl(save_path)
        self.assertEqual(data, data_from_file)


if __name__ == '__main__':
    unittest.main()
