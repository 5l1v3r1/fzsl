import sys

import envoy

def run_stdout(cmd, env=None, cwd=None):
    child = envoy.run(cmd, env=env)
    if child.status_code != 0:
        raise SubprocessError(cmd)
    return child.std_out

class SubprocessError(Exception):
    def __init__(self, cmd):
        super(SubprocessError, self).__init__('Failed to run: "%s"' % (cmd,))

class WeightedDistanceScore(object):
    def __init__(self):
        self._needle = ''

    def update(self, needle):
        self._needle = needle

    def score(self, path):
        needle_len = len(self._needle)
        if needle_len <= 0:
            return (0, path)

        mult = path.find(self._needle[-1])
        if mult < 0:
            return (-1, '')

        return (mult * needle_len, path[mult + 1:])

class FuzzyMatch(object):
    def __init__(self, files=None, scorer=None):
        self._library = {}
        if files is not None:
            for f in files:
                self._library[f] = {
                        'score': 0,
                        'remainder': f}
        self._matches = self._library.copy()
        self._scorer = scorer
        self._search = ''

    def update_scores(self, search):
        if len(search) < len(self._search):
            self._matches = self._library.copy()

        self._scorer.update(search)
        scorer = self._scorer.score

        for path, vals in self._matches.items():
            score, remainder = scorer(vals['remainder'])
            if score < 0:
                del self._matches[path]
            else:
                self._matches[path]['score'] = score
                self._matches[path]['remainder'] = remainder

    def top_matches(self, depth=10):
        ret = sorted(self._matches, key=lambda x: self._matches[x]['score'])[:depth]
        ret.reverse()
        return ret

class Scanner(object):
    def __init__(self, scanner_conf):
        self._dir_type = None
        self._conf = scanner_conf

        c = envoy.run('git rev-parse')
        if c.status_code == 0:
            self._dir_type = 'git'

    def scan(self):
        try:
            if self._dir_type == 'git':
                files = run_stdout(self._conf['git'])
            else:
                files = run_stdout(self._conf['default'])
        except KeyError:
            files = run_stdout(self._conf['default'])

        return [file.strip() for file in files.split()]

