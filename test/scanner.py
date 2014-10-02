import os
import sys
import unittest

TESTDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTDIR, '..')))

import fzsl

class ScannerTest(unittest.TestCase):
    def setUp(self):
        self.bn = os.path.basename(__file__)

    def test_sort(self):
        s1 = fzsl.Scanner('echo', priority=1)
        s2 = fzsl.Scanner('echo', priority=2)

        l = [s2, s1]
        l.sort()

        self.assertEqual(l[0], s1)
        self.assertEqual(l[1], s2)

    def test_root_path_match(self):
        s = fzsl.Scanner('echo', root_path=TESTDIR)
        self.assertTrue(s.is_suitable(TESTDIR))
        self.assertTrue(s.is_suitable('%s/test/stuff' % (TESTDIR,)))
        self.assertFalse(s.is_suitable(os.path.dirname(TESTDIR)))
        self.assertFalse(s.is_suitable('%s/../' % (TESTDIR,)))

    def test_detect_cmd_match(self):
        cmd = '[ -f %s ]' % (self.bn,)
        s = fzsl.Scanner('echo', detect_cmd=cmd)
        self.assertTrue(s.is_suitable(TESTDIR))
        self.assertFalse(s.is_suitable('%s/../' % (TESTDIR,)))

        cmd = '[ -f thisfileisnothere ]'
        s2 = fzsl.Scanner('echo', detect_cmd=cmd)
        self.assertFalse(s2.is_suitable(TESTDIR))

    def test_cmd(self):
        cmd = 'find . -name %s' % (self.bn,)
        s = fzsl.Scanner(cmd)
        self.assertIn('./' + self.bn, s.scan(TESTDIR))
        self.assertNotIn('.git' + self.bn, s.scan(TESTDIR))

        self.assertEqual(0, len(s.scan('%s/../bin' % (TESTDIR,))))

    def test_fallthrough(self):
        s = fzsl.Scanner('echo')
        self.assertTrue(s.is_suitable(TESTDIR))

def main():
    unittest.main()

if __name__ == '__main__':
    main()

