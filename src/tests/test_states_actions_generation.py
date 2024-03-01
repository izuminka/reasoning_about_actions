from src.states_actions_generation.states_actions_generation import *
import unittest
import shutil

TESTS_DIR = CODE_PATH + '/tests'
TMP_DIR = TESTS_DIR + '/tmp'


class TestStateActionsGeneration(unittest.TestCase):
    DG = StatesActionsGenerator(CODE_PATH + '/tests/asp/domains/blocksworld/domain.lp',
                                CODE_PATH + '/tests/asp/domains/blocksworld/instances/inst1/init.lp',
                                CODE_PATH + '/tests/asp/domains/blocksworld/instances/inst1/objects.lp')

    # from the initial condition
    init_state = {'handempty', 'ontable(b1)', 'on(b2,b1)', 'clear(b2)'}
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
        actions = self.DG.all_actions()
        self.assertEqual(actions, self.infeasible_actions.union(self.feasible_actions))

    def test_next_state_infeasible_actions(self):
        for a in self.infeasible_actions:
            self.assertEqual([], self.DG.next_state(self.DG.initial_state, a))

    def test_next_state_feasible_actions(self):
        action = 'action_unstack(b2,b1)'
        expected_state = ['holding(b2)', 'clear(b1)', 'ontable(b1)'].sort()
        self.assertEqual(expected_state, self.DG.next_state(self.DG.initial_state, action).sort())

    def test_pipeline(self):
        plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_pick_up(b1)', 'action_stack(b1,b2)']
        data = self.DG.create_data(plan_sequence)
        self.assertEqual(len(data), len(plan_sequence) + 1)

        part_of_plan_actions = []
        for i, states in enumerate(data[1:]):  # data[0] is the init condition
            for action, d in states.items():
                self.assertTrue('action_' in action)
                if d[EXECUTABLE_ACTION_BOOL_KEY]:
                    self.assertTrue(len(d[FLUENTS_KEY]) > 0)
                else:
                    self.assertEqual([], d[FLUENTS_KEY])

                if action == plan_sequence[i]:
                    print(plan_sequence[i])
                    print(d[FLUENTS_KEY])
                    self.assertTrue(d[PART_OF_PLAN_KEY])
                    self.assertTrue(len(d[FLUENTS_KEY]) > 0)
                    part_of_plan_actions.append(action)
        self.assertEqual(part_of_plan_actions, plan_sequence)

    def test_save_data_validate(self):
        plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)', 'action_pick_up(b1)', 'action_stack(b1,b2)']
        data = self.DG.create_data(plan_sequence)
        save_path = TMP_DIR + '/data.jsonl'
        self.DG.save_data(save_path)

        data_from_file = open_jsonl(save_path)
        self.assertEqual(data, data_from_file)

    def test_edge_case1(self):
        pred_state = self.DG.next_state(['ontable(b1)', 'clear(b1)', 'holding(b2)'], 'action_put_down(b2)')
        true_state = ['ontable(b1)', 'clear(b1)', 'ontable(b2)', 'clear(b2)', 'handempty']
        self.assertEqual(set(true_state), set(pred_state))

    def test_edge_case2(self):
        pred_state = self.DG.next_state(['ontable(b1)', 'clear(b1)', 'holding(b2)'], 'action_put_down(b2)',
                                        asp_code_fname='next_state_neg_fluents.lp')
        expected_neg_fluents = ['-holding(b2)', '-holding(b1)', '-on(b1,b2)', '-on(b2,b1)']
        self.assertEqual(set(expected_neg_fluents), set(pred_state))

    def test_garbage_action_next_state(self):
        current_state = ['ontable(b1)', 'clear(b1)', 'holding(b2)']
        garbadge = 'asfsdkjfnds'
        pred_state = self.DG.next_state(current_state, garbadge)
        self.assertEqual(set(current_state), set(pred_state))

    def test_garbage_action_next_state_negative(self):
        current_state = ['ontable(b1)', 'clear(b1)', 'holding(b2)']
        neg_current_state = ['-ontable(b2)', '-clear(b2)', '-handempty', '-on(b1,b2)', '-on(b2,b1)', '-holding(b1)']
        garbadge = 'asfsdkjfnds'
        pred_state = self.DG.next_state(current_state, garbadge, asp_code_fname='next_state_neg_fluents.lp')
        self.assertEqual(set(neg_current_state), set(pred_state))

    def test_parse_objects(self):
        expected = {'block': ['a', 'b', 'c']}
        for objects_str in ['block(a;b;c).\n',
                            'block(a;\nb;c\n).\n']:
            objects_dict = self.DG.parse_objects(objects_str)
            self.assertEqual(expected, objects_dict)

        expected = {'block': ['a', 'b', 'c'], 'truck': ['t1', 't2', 't3']}
        for objects_str in ['block(a;b;c).\ntruck(t1;t2;t3)',
                            'block(a;\nb;c\n).\n\ntruck(t1;\nt2;\nt3\n)\n']:
            objects_dict = self.DG.parse_objects(objects_str)
            self.assertEqual(expected, objects_dict)


if __name__ == '__main__':
    unittest.main()
