import cProfile
import os
import pstats
import sys
import unittest

TESTDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTDIR, '..')))

import fzsl

class Benchmark(unittest.TestCase):
    def setUp(self):
        self._scanner = fzsl.SimpleScanner(
                'test',
                cmd='cat %s/files' % (TESTDIR,),
                priority=1)

    def testeth100e(self):
        files = self._scanner.scan(TESTDIR)

        for search in ['drineethe100ephy', 'drinete100phy.c', 'e100phy.c']:
            fm = fzsl.FuzzyMatch(files=files)
            pr = cProfile.Profile()
            for i in range(1, len(search)):
                pr.enable()
                fm.update_scores(search[:i])
                pr.disable()
                stats = pstats.Stats(pr)
                pr.clear()
                self.assertLess(stats.total_tt, 10)
                print "%d/%d" % (len(fm._library), len([f for f in fm._library.values() if f.round_ejected == 0]))
                print 'search for %-20s: %f' % (search[:i], stats.total_tt)
            print('\n'.join(fm.top_matches()))
            self.assertIn(
                    '/usr/src/linux/drivers/net/ethernet/intel/e1000e/phy.c',
                    fm.top_matches())

    def test_delete(self):
        files = self._scanner.scan(TESTDIR)

        fm = fzsl.FuzzyMatch(files=files)

        fm.update_scores("abc")
        matches = fm.n_matches

        fm.update_scores("abcd")
        self.assertNotEqual(matches, fm.n_matches)

        fm.update_scores("abc")
        self.assertEqual(matches, fm.n_matches)

        fm.update_scores("ab")
        fm.update_scores("a")
        fm.update_scores("")
        self.assertEqual(fm.n_matches, fm.n_files)


def main():
    unittest.main()

if __name__ == '__main__':
    main()

