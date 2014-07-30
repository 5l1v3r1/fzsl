import cProfile
import os
import pstats
import sys
import unittest

TESTDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTDIR, '..')))

import pyfs

class Benchmark(unittest.TestCase):
    def setUp(self):
        config = {
            'default': 'cat %s/files' % (TESTDIR,)
        }
        self._scanner = pyfs.Scanner(config)

    def testeth100e(self):
        files = self._scanner.scan()

        scorer = pyfs.WeightedDistanceScore()
        fm = pyfs.FuzzyMatch(files=files, scorer=scorer)
        search = 'drineethe100eph'

        pr = cProfile.Profile()
        for i in range(1, len(search)):
            pr.enable()
            fm.update_scores(search[:i])
            pr.disable()
            stats = pstats.Stats(pr)
            pr.clear()
            self.assertLess(stats.total_tt, 0.5)
            print 'search for %-20s: %f' % (search[:i], stats.total_tt)
        print('\n'.join(fm.top_matches()))
        self.assertIn(
                '/usr/src/linux/drivers/net/ethernet/intel/e1000e/phy.c',
                fm.top_matches())

def main():
    unittest.main()

if __name__ == '__main__':
    main()

