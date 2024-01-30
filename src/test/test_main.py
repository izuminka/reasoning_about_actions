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

if __name__ == '__main__':
    unittest.main()
