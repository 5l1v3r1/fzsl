import curses
import functools
import os
import sys

import pyfs


def curses_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        # Push stdout to stderr so that we still get the curses
        # output while inside of a pipe or subshell
        old_stdout = sys.__stdout__
        old_stdout_fd = os.dup(sys.stdout.fileno())
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

        scr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()

        curses.noecho()
        curses.cbreak()
        curses.raw()
        curses.curs_set(0)


        scr.keypad(1)

        args = list(args)
        args.insert(1, scr)

        exc = None
        try:
            ret = func(*args, **kwds)
        #pylint: disable=W0703
        except Exception:
            exc = sys.exc_info()

        scr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

        os.dup2(old_stdout_fd, sys.stdout.fileno())
        sys.stdout = old_stdout

        if exc is not None:
            raise exc[0], exc[1], exc[2]

        return ret
    return wrapper

class SimplePager(object):
    def __init__(self):
        super(SimplePager, self).__init__()

        self._config = {
            'default': 'find ./'
        }

    @curses_method
    def run(self, scr):
        scanner = pyfs.Scanner(self._config)
        scorer = pyfs.WeightedDistanceScore()

        scr.addstr("Scanning ...")
        scr.refresh()
        files = scanner.scan()

        max_y, _ = scr.getmaxyx()

        scr.clear()
        for line, match in enumerate(files[:max_y]):
            scr.addstr(line, 0, match)
        scr.refresh()


        fm = pyfs.FuzzyMatch(files=files, scorer=scorer)

        search = ''
        while True:
            c = scr.getch()

            if c in (curses.KEY_ENTER, ord('\n')):
                break
            elif c in (curses.KEY_DC, curses.KEY_BACKSPACE):
                if len(search):
                    search = search[:-1]
            else:
                search += chr(c)

            fm.update_scores(search)

            scr.clear()
            for line, match in enumerate(fm.top_matches(max_y)):
                scr.addstr(line, 0, match)
            scr.refresh()

        scr.refresh()
        return fm.top_matches(1)[0]


def main():
    ui = SimplePager()
    #pylint: disable=E1120
    result = ui.run()
    sys.stdout.write(result.strip())

if __name__ == '__main__':
    main()
