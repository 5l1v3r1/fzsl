import contextlib
import curses
import os
import sys

import fzsl

for i, color in enumerate(('white', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan')):
    vars()['COL_%s' % (color.upper())] = i
    vars()['COL_B%s' % (color.upper())] = i + 8


@contextlib.contextmanager
def ncurses():
    # Push stdout to stderr so that we still get the curses
    # output while inside of a pipe or subshell
    old_stdout = sys.__stdout__
    old_stdout_fd = os.dup(sys.stdout.fileno())
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

    scr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    _ = [curses.init_pair(i + 1, i, -1) for i in range(curses.COLORS)]

    curses.noecho()
    curses.cbreak()
    curses.raw()
    curses.curs_set(0)

    scr.keypad(1)

    exc = None
    try:
        yield scr
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


class SimplePager(object):
    def __init__(self, scr):
        self._scr = scr

        self._config = {
            'default': 'find ./'
        }
        self._show_score = False
        self._fm = fzsl.FuzzyMatch()
        self._selection = 0
        self._search = ''

        max_y, _ = self._scr.getmaxyx()
        self._max_y = max_y - 1

    def _draw(self):
        self._scr.erase()
        m = self._fm.top_matches(self._max_y)
        if self._selection >= len(m):
            self._selection = max(len(m) - 1, 0)

        for index, match in enumerate(m):
            if len(self._search) > 0 and self._fm.score(match) == 0:
                continue

            prefix = ''
            if self._show_score:
                prefix = "%f     " % (self._fm.score(match),)
            offset = len(prefix)

            start = self._fm.start(match)
            end = self._fm.end(match)
            line = self._max_y - index - 1
            decor = 0
            if self._selection == index:
                decor = curses.A_UNDERLINE

            self._scr.addstr(line, 0, prefix + match[:start], decor)
            self._scr.addstr(line, start+offset, match[start:end], decor|curses.color_pair(COL_BCYAN))
            self._scr.addstr(line, end+offset, match[end:], decor)

        self._scr.addstr(self._max_y, 2, "%d/%d >  %s" % (
            self._fm.n_matches, self._fm.n_files, self._search))
        self._scr.refresh()

    def run(self):
        scanner = fzsl.Scanner(self._config)

        self._scr.addstr("Scanning ...")
        self._scr.refresh()
        files = scanner.scan()
        self._fm.add_files(files)

        self._draw()

        # Read from stdin instead of using curses.getch  so we can
        # differentiate between ctrl+j and enter, and similar.
        while True:
            c = ord(sys.stdin.read(1))

            if c == 13:
                # enter
                break
            elif c in (66, 10):
                # down arrow, ctrl+j
                self._selection = self._selection - 1 if self._selection > 0 else 0
            elif c in (65, 11):
                # up arrow, ctrl+k
                self._selection = self._selection + 1 if self._selection < self._max_y - 2 else self._selection
            elif c == 22:
                # ctrl+v
                self._show_score = not self._show_score
            elif c == 27:
                # escape
                return ''
            else:
                if c in (126, 127):
                    # delete, backspace
                    if len(self._search):
                        self._search = self._search[:-1]
                else:
                    self._search += chr(c)

                self._fm.update_scores(self._search)

            self._draw()

        return self._fm.top_matches(self._max_y)[self._selection]


def main():
    with ncurses() as scr:
        ui = SimplePager(scr)
        result = ui.run()
    sys.stdout.write(result.strip())

if __name__ == '__main__':
    main()
