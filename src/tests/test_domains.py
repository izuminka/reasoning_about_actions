
import sys
sys.path.insert(0,'../../')
from src.questions_construction.domains import *
import unittest

random.seed(42)


class TestDomains(unittest.TestCase):
    bd = BaseDomain(False, True)

    def test_replace_substring_no_replacement(self):
        res = self.bd.replace_substring('unstacking more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('unstacking more blocks', res)

        res = self.bd.replace_substring('stuff unstacking more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('stuff unstacking more blocks', res)

        res = self.bd.replace_substring('stuff more blocks unstacking', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('stuff more blocks unstacking', res)

        res = self.bd.replace_substring('stackingzz more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('stackingzz more blocks', res)

        res = self.bd.replace_substring('stuff stackingzz more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('stuff stackingzz more blocks', res)

        res = self.bd.replace_substring('stuff more blocks stackingzz', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('stuff more blocks stackingzz', res)

    def test_replace_substring_replacement(self):
        res = self.bd.replace_substring('Stacking more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('Sdnfjkdsnfkj more blocks', res)

        res = self.bd.replace_substring('STACKING. more blocks', 'stacking', 'ghsks')
        self.assertEqual('GHSKS. more blocks', res)

        res = self.bd.replace_substring('stacking, more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('sdnfjkdsnfkj, more blocks', res)

        res = self.bd.replace_substring('stacking" more blocks', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('sdnfjkdsnfkj" more blocks', res)

        res = self.bd.replace_substring('stacking!', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('sdnfjkdsnfkj!', res)

        res = self.bd.replace_substring('stacking', 'stacking', 'sdnfjkdsnfkj')
        self.assertEqual('sdnfjkdsnfkj', res)

    def test_replace_substrings(self):
        text = ('picking up a block is \n\n only possible if that block is clear, on the table, and the hand is empty. '
                'Unstacking the first block from the second causes first block to be held A block is said to be clear if it is not being held and there are no blocks that are on top of it. '
                'The hand is said to be empty if and only if it is not holding any block. The block can only be at one place at a time.')

        obj_dict = Blocksworld.SUBSTRINGS_TO_RAND
        res = self.bd.replace_substrings(text, obj_dict)
        expected = ('ovyuecllio a qbyyxzqvdh is \n\n only possible if that qbyyxzqvdh is clear, '
                    'wtuwjwbuja the gcbwvwyvkv, and the egpbpdtalq is empty. Wxqdwukszo the first '
                    'qbyyxzqvdh from the second causes first qbyyxzqvdh to be casqqrrojp A '
                    'qbyyxzqvdh is said to be clear if it is not being casqqrrojp and there are '
                    'no qbyyxzqvdhs that are wtuwjwbuja top of it. The egpbpdtalq is said to be '
                    'empty if and only if it is not casqqrrojp any qbyyxzqvdh. The qbyyxzqvdh can '
                    'only be at one place at a time.')
        self.assertEqual(expected, res)

    def test_replace_many_times_substrings(self):
        text = ('picking up a block is \n\n only possible if that block is clear, on the table, and the hand is empty. '
                'Unstacking the first block from the second causes first block to be held A block is said to be clear if it is not being held and there are no blocks that are on top of it. '
                'The hand is said to be empty if and only if it is not holding any block. The block can only be at one place at a time.')

        obj_dict = Blocksworld.SUBSTRINGS_TO_RAND
        res = self.bd.replace_substrings(text, obj_dict)
        res = self.bd.replace_substrings(res, obj_dict)
        res = self.bd.replace_substrings(res, obj_dict)
        res = self.bd.replace_substrings(res, obj_dict)
        expected = ('ovyuecllio a qbyyxzqvdh is \n\n only possible if that qbyyxzqvdh is clear, '
                    'wtuwjwbuja the gcbwvwyvkv, and the egpbpdtalq is empty. Wxqdwukszo the first '
                    'qbyyxzqvdh from the second causes first qbyyxzqvdh to be casqqrrojp A '
                    'qbyyxzqvdh is said to be clear if it is not being casqqrrojp and there are '
                    'no qbyyxzqvdhs that are wtuwjwbuja top of it. The egpbpdtalq is said to be '
                    'empty if and only if it is not casqqrrojp any qbyyxzqvdh. The qbyyxzqvdh can '
                    'only be at one place at a time.')
        self.assertEqual(expected, res)

    def test_upper_lower_substrings(self):
        text = 'picking up a block is OnlY possible if that block is CLEAr, on the table, and the hand is empty. '

        obj_dict = Blocksworld.SUBSTRINGS_TO_RAND
        res = self.bd.replace_substrings(text, obj_dict)
        print(res)
        expected = 'ovyuecllio a qbyyxzqvdh is OnlY possible if that qbyyxzqvdh is CLEAr, wtuwjwbuja the gcbwvwyvkv, and the egpbpdtalq is empty. '
        self.assertEqual(expected, res)

    def test_domains_init(self):
        for dom in ALL_DOMAIN_CLASSES:
            for is_random_sub in [True, False]:
                for is_ramifications in [True, False]:
                    domain_class = dom(is_random_sub, is_ramifications)
                    self.assertIsNotNone(domain_class.domain_description)
                    self.assertTrue(domain_class)

    def test_blocksworld_fluents_actions(self):
        dom = ALL_DOMAIN_CLASSES[0]
        for is_random_sub in [True, False]:
            for is_ramifications in [True, False]:
                domain_class = dom(is_random_sub, is_ramifications)
                for is_hallucinated in [True, False]:
                    res = domain_class.fluent_to_natural_language('clear(b1)', is_hallucinated)
                    print(res)
                    self.assertTrue(res)
                    res = domain_class.action_to_natural_language('stack(b1,b2)', is_hallucinated)
                    self.assertTrue(res)

    def test_blocksworld_domain_description(self):
        dom = ALL_DOMAIN_CLASSES[0]
        domain_class = dom(False, True)
        expected_text = ('Picking up a block is only possible if that block is clear, on the table, '
                         'and the hand is empty. Picking up the block leads to the block being held. '
                         'Putting down the block can only be executed if the block is being held. '
                         'Putting down the block causes the block to be on the table. A block can be '
                         'stacked on the second block if it is being held and the second block is '
                         'clear. By stacking the first block on the second, it causes the first block '
                         'to be on top of the second block. The block can also be unstacked from the '
                         'top of the second block only if the hand is empty and the first block is '
                         'clear and on top of the second block. Unstacking the first block from the '
                         'second causes first block to be held A block is said to be clear if it is '
                         'not being held and there are no blocks that are on top of it. The hand is '
                         'said to be empty if and only if it is not holding any block. The block can '
                         'only be at one place at a time.\n'
                         '\n'
                         'A state is a set of valid properties. Properties may or may not involve '
                         'negations. Properties of the state can be of 4 types: base, derived, '
                         'persistent, and static. Base properties of the state are properties that '
                         "don't depend on other properties. In this domain, they are: a block is on "
                         'the table and a block is not on the table. Derived properties of the state '
                         'are properties that depend on other properties. In this domain, they are: a '
                         'block is clear, hand is empty, a block is not clear and hand is not empty. '
                         'Self constraint properties of the state are properties that depend on '
                         'themselves. In this domain, they are: a block is being held, a block is on '
                         'another block, a block is not being held and a block is not on another '
                         "block. Static properties of the state are properties that don't change under "
                         'any action. There are no static properties of the state in this domain. ')

        self.assertEqual(expected_text, domain_class.domain_description)


if __name__ == '__main__':
    unittest.main()
