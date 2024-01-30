from ..main import *
import unittest


class TestStringMethods(unittest.TestCase):
    DG = DataGenerator(CODE_PATH + '/test/asp/domains/blocksworld/domain.lp',
                       CODE_PATH + '/test/asp/domains/blocksworld/instances/inst1/init.lp',
                       CODE_PATH + '/test/asp/domains/blocksworld/instances/inst1/objects.lp')

    # from the initial condition
    init_state = {'handempty', 'ontable(b1)', 'on(b2, b1)', 'clear(b2)'}
    infeasible_actions = {'action_put_down(b2)', 'action_unstack(b1,b2)', 'action_stack(b1,b2)',
                          'action_pick_up(b1)', 'action_put_down(b1)', 'action_stack(b2,b1)', 'action_pick_up(b2)'}
    feasible_actions = {'action_unstack(b2,b1)'}

    def test_attributes(self):
        self.assertEqual(self.DG.initial_state, self.init_state)
        self.assertEqual(self.DG.objects, 'block(b1; b2).')

    def test_all_actions(self):
        self.assertEqual(set(), self.DG.all_actions(set()))

        actions = self.DG.all_actions(self.DG.initial_state)
        self.assertEqual(actions, self.infeasible_actions.union(self.feasible_actions))

    def test_next_state_infeasible_actions(self):
        for a in self.infeasible_actions:
            self.assertEqual(set(), self.DG.next_state(self.DG.initial_state, a))

    def test_next_state_feasible_actions(self):
        action = 'action_unstack(b2,b1)'
        expected_state = {'handempty', 'ontable(b1)', 'holding(b2)'}
        self.assertNotEqual(expected_state, self.DG.next_state(self.DG.initial_state, action))

    def test_pipeline(self):
        plan_sequence = ['action_unstack(b2,b1)', 'action_put_down(b2)']
        data = self.DG.generate_data(plan_sequence)
        self.assertEqual(len(data), len(plan_sequence))

        part_of_plan_actions = []
        for i, states in enumerate(data):
            for action, d in states.items():
                self.assertTrue('action_' in action)
                if d[DataGenerator.FEASIBLE_KEY]:
                    self.assertNotEqual(set(), d[DataGenerator.FLUENTS_KEY])
                else:
                    self.assertEqual(set(), d[DataGenerator.FLUENTS_KEY])

                if action == plan_sequence[i]:
                    self.assertTrue(d[DataGenerator.PART_OF_PLAN_KEY])
                    part_of_plan_actions.append(action)
        self.assertEqual(part_of_plan_actions, plan_sequence)

if __name__ == '__main__':
    unittest.main()
