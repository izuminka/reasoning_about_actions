from src.questions_construction.domains import *
import unittest


class TestDomains(unittest.TestCase):
    bd = BaseDomain(False, True)

    def test_replace_substring_no_replacement(self):
        res = self.bd.replace_substring('unstacking more blocks', 'stacking', 'REPL')
        self.assertEqual('unstacking more blocks', res)

        res = self.bd.replace_substring('stuff unstacking more blocks', 'stacking', 'REPL')
        self.assertEqual('stuff unstacking more blocks', res)

        res = self.bd.replace_substring('stuff more blocks unstacking', 'stacking', 'REPL')
        self.assertEqual('stuff more blocks unstacking', res)

        res = self.bd.replace_substring('stackingzz more blocks', 'stacking', 'REPL')
        self.assertEqual('stackingzz more blocks', res)

        res = self.bd.replace_substring('stuff stackingzz more blocks', 'stacking', 'REPL')
        self.assertEqual('stuff stackingzz more blocks', res)

        res = self.bd.replace_substring('stuff more blocks stackingzz', 'stacking', 'REPL')
        self.assertEqual('stuff more blocks stackingzz', res)

    def test_replace_substring_replacement(self):
        res = self.bd.replace_substring('stacking more blocks', 'stacking', 'REPL')
        self.assertEqual('REPL more blocks', res)

        res = self.bd.replace_substring('stacking. more blocks', 'stacking', 'REPL')
        self.assertEqual('REPL. more blocks', res)

        res = self.bd.replace_substring('stacking, more blocks', 'stacking', 'REPL')
        self.assertEqual('REPL, more blocks', res)

        res = self.bd.replace_substring('stacking" more blocks', 'stacking', 'REPL')
        self.assertEqual('REPL" more blocks', res)

        res = self.bd.replace_substring('stacking!', 'stacking', 'REPL')
        self.assertEqual('REPL!', res)

        res = self.bd.replace_substring('stacking', 'stacking', 'REPL')
        self.assertEqual('REPL', res)

    def test_replace_substrings(self):
        text = ('Picking up a block is only possible if that block is clear, on the table, and the hand is empty. '
                'Unstacking the first block from the second causes first block to be held A block is said to be clear if it is not being held and there are no blocks that are on top of it. '
                'The hand is said to be empty if and only if it is not holding any block. The block can only be at one place at a time.')

        obj_dict = Blocksworld.SUBSTRINGS_TO_RAND
        res = self.bd.replace_substrings(text, obj_dict)
        print(res)
        expected = ('Ovyuecllio a qbyyxzqvdh is only possible if that qbyyxzqvdh is clear, on the '
                    'zewwtdxhfs, and the egpbpdtalq is empty. Wxqdwukszo the first qbyyxzqvdh '
                    'from the second causes first qbyyxzqvdh to be casqqrrojp a qbyyxzqvdh is '
                    'said to be clear if it is not being casqqrrojp and there are no qbyyxzqvdhs '
                    'that are on top of it. The egpbpdtalq is said to be empty if and only if it '
                    'is not casqqrrojp any qbyyxzqvdh. The qbyyxzqvdh can only be at one place at '
                    'a time.')
        self.assertEqual(expected, res)

    def test_domains_init(self):
        for dom in ALL_DOMAIN_CLASSES:
            for is_random_sub in [True, False]:
                for is_ramifications in [True, False]:
                    domain_class = dom(is_random_sub, is_ramifications)
                    print(domain_class.domain_description)
                    self.assertTrue(domain_class)


if __name__ == '__main__':
    unittest.main()
