import re

import envoy

def run_stdout(cmd, env=None):
    child = envoy.run(cmd, env=env)
    if child.status_code != 0:
        raise SubprocessError(cmd)
    return child.std_out

class SubprocessError(Exception):
    def __init__(self, cmd):
        super(SubprocessError, self).__init__('Failed to run: "%s"' % (cmd,))

class MatchInfo(object):
    def __init__(self, start=0, end=0, score=0, round_ejected=0):
        """
        Information about how a patch matches against the given search

        @attr start         - index in path where match starts
        @attr end           - index in path where match ends
        @attr score         - match score
        @attr round_ejected - the round (length of search string) that this path
                              was removed as a possible match
        """
        self.start = start
        self.end = end
        self.score = score
        self.round_ejected = round_ejected

    def update(self, start=None, end=None, score=None, round_ejected=None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if score is not None:
            self.score = score
        if round_ejected is not None:
            self.round_ejected = round_ejected

def default_scorer(path, c_round, regex):
    m = regex.search(path, re.IGNORECASE)
    if m is not None:
        r = 1.0 / (m.end() - m.start())
        return m.start(), m.end(), r, 0
    else:
        return 0, 0, 0.0, c_round

class FuzzyMatch(object):
    def __init__(self, files=None, scorer=default_scorer):
        if files is not None:
            self._library = {path:MatchInfo() for path in files}
        else:
            self._library = {}

        self._scorer = scorer
        self._search = ''

    @property
    def n_matches(self):
        return len([info for info in self._library.values() if info.round_ejected == 0])

    @property
    def n_files(self):
        return len(self._library)

    def update_scores(self, search):
        s_len = len(search)

        if s_len < len(self._search):
            _ = [self._library[path].update(round_ejected=0)
                    for path, info in self._library.items()
                    if info.round_ejected == s_len + 1]

        self._search = search

        if s_len == 0:
            return
        elif s_len == 1:
            # In the single character search case, it's far faster to use the
            # string index function over regex.  This is important as we want
            # to slim down the potential matches as quickly as possible.
            #
            # > def f(): 'aoacoeaemaoceaimfoaijhaohfeiahfoefhoeia'.index(j)
            # > def f2(): re.search('j', 'aoacoeaemaoceaimfoaijhaohfeiahfoefhoeia')
            # > timeit.timeit('f()', 'from __main__ import f')
            # 0.5705671310424805
            # > timeit.timeit('f()', 'from __main__ import f2 as f')
            # 2.7029879093170166
            def quick_score(path, info):
                index = path.find(search)
                if index != -1:
                    info.update(start=index, end=index, score=1.0)
                else:
                    info.update(round_ejected=1)

            _ = [quick_score(path, info) for path, info in self._library.items()]
            return

        ore = search[0]
        for i in range(1, s_len):
            ore += '[^%s]*?%s' % (re.escape(search[i-1]), re.escape(search[i]))
        regex = re.compile(ore)

        scorer = self._scorer
        _ = [info.update(*scorer(path, s_len, regex))
                    for path, info in self._library.items()
                    if info.round_ejected == 0]

    def score(self, path):
        return self._library[path].score

    def top_matches(self, depth=10):
        ret = sorted(self._library, key=lambda x: self._library[x].score, reverse=True)[:depth]
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

        return [f.strip() for f in files.split()]

