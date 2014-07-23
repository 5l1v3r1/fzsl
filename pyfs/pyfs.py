import collections
import re
import sys

import nltk

class _Scorer(object):
    def update(self, needle):
        raise NotImplemented()

    def score(self, needle, haystack):
        raise NotImplemented()

class SimpleRegexScore(_Scorer):
    def __init__(self):
        self._needle = ''
        self._regex = re.compile('.*')

    def update(self, needle):
        self._needle = needle
        self._regex = re.compile('.*%s.*' % '.*'.join(iter(needle)))

    def score(self, path):
        if self._regex.search(path) is not None:
            return nltk.edit_distance(path, self._needle)
        else:
            return -1

class WeightedDistanceScore(_Scorer):
    def __init__(self):
        self._needle = ''

    def update(self, needle):
        self._needle = needle

    def score(self, path):
        if len(self._needle) == 0:
            return 0

        inc = 0
        score = 0
        needle_index = 0
        needle_len = len(self._needle)

        for c in iter(path):
            if c == self._needle[needle_index]:
                needle_index += 1
                inc = 0
                if needle_index == needle_len:
                    break
            else:
                score += needle_index
                inc += 1
        else:
            return -1

        return score

class FuzzyMatch(object):
    def __init__(self, library=None, scorer=None):
        self._library = None
        if library is not None:
            self._library = dict(zip((s for s in library), [0] * len(library)))
        self._matches = self._library.copy()

        self._scorer = scorer

    def update_scores(self, search):
        self._scorer.update(search)

        for haystack in self._matches.keys():
            score = self._scorer.score(haystack)
            if score < 0:
                del self._matches[haystack]
            else:
                self._matches[haystack] = score

    def top_matches(self, depth=10):
        ret = sorted(self._matches, key=self._matches.get)[:depth]
        ret.reverse()
        return ret

def main():
    import cProfile

    runs = {}
    files = open(sys.argv[2]).read().split()

    scorers = (
    #        'SimpleRegexScore',
            'WeightedDistanceScore',
    )

    for cls in scorers:
        scorer = globals()[cls]()
        fm = FuzzyMatch(library=files, scorer=scorer)

        pr = cProfile.Profile()
        pr.enable()
        for i in range(len(sys.argv[1])):
            fm.update_scores(sys.argv[1][:i])
        pr.disable()
        pr.print_stats()
        stats = pr.create_stats()
        print('\n'.join(fm.top_matches()))


if __name__ == '__main__':
    main()
