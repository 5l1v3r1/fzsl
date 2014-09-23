import functools
import heapq
import multiprocessing
import re
import signal

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
    matches = [m for m in regex.finditer(path, re.IGNORECASE)]
    if matches:
        def score(match):
            return 1.0 / (len(path) - match.start(1))

        ranked = [(score(m), m) for m in matches]
        score, best = max(ranked)

        return path, (best.start(1), best.end(1), score, 0)
    else:
        return path, (0, 0, 0.0, c_round)

class FuzzyMatch(object):
    def __init__(self, files=None, scorer=default_scorer):
        if files is not None:
            self._library = {path:MatchInfo() for path in files}
        else:
            self._library = {}

        self._scorer = scorer
        self._search = ''

        def pool_init():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        self._pool = multiprocessing.Pool(initializer=pool_init)

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

        regex = re.compile('(?=(' + '.*?'.join(re.escape(c) for c in search) + '))')


        scorer = functools.partial(self._scorer, c_round=s_len, regex=regex)
        candidates = [path for path, info in self._library.items() if info.round_ejected == 0]
        _ = [self._library[path].update(*update) for path, update in self._pool.map(scorer, candidates)]

    def score(self, path):
        return self._library[path].score

    def start(self, path):
        return self._library[path].start

    def end(self, path):
        return self._library[path].end

    def top_matches(self, depth=10):
        ret = heapq.nlargest(depth, self._library, key=lambda x: self._library[x].score)
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

