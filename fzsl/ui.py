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
        super(SimplePager, self).__init__()
        self._scr = scr

        self._config = {
            'default': 'find ./'
        }
        self._show_score = False

    def run(self):
        scanner = fzsl.Scanner(self._config)

        self._scr.addstr("Scanning ...")
        self._scr.refresh()
        files = scanner.scan()

        fm = fzsl.FuzzyMatch(files=files)
        max_y, _ = self._scr.getmaxyx()
        max_y -= 1

        class Closure(object):
            selection = 0
        closure = Closure

        search = ''

        def draw():
            self._scr.erase()
            m = fm.top_matches(max_y)
            if closure.selection >= len(m):
                closure.selection = max(len(m) - 1, 0)

            for index, match in enumerate(m):
                if len(search) > 0 and fm.score(match) == 0:
                    continue

                prefix = ''
                if self._show_score:
                    prefix = "%f     " % (fm.score(match),)
                offset = len(prefix)


                start = fm.start(match)
                end = fm.end(match)

                if closure.selection == index:
                    self._scr.addstr(max_y - index - 1, 0, prefix + match[:start], curses.A_UNDERLINE)
                    self._scr.addstr(max_y - index - 1, start+offset, match[start:end], curses.A_UNDERLINE|curses.color_pair(COL_BCYAN))
                    self._scr.addstr(max_y - index - 1, end+offset, match[end:], curses.A_UNDERLINE)
                else:
                    self._scr.addstr(max_y - index - 1, 0, prefix + match[:start])
                    self._scr.addstr(max_y - index - 1, start+offset, match[start:end], curses.color_pair(COL_BCYAN))
                    self._scr.addstr(max_y - index - 1, end+offset, match[end:])

            self._scr.addstr(max_y, 2, "%d/%d >  %s" % (fm.n_matches, fm.n_files, search))
            self._scr.refresh()


        draw()

        # Read from stdin instead of using curses.getch  so we can
        # differentiate between ctrl+j and enter, and similar.
        while True:
            c = ord(sys.stdin.read(1))

            if c == 13:
                # enter
                break
            elif c in (66, 10):
                # down arrow, ctrl+j
                closure.selection = closure.selection - 1 if closure.selection > 0 else 0
            elif c in (65, 11):
                # up arrow, ctrl+k
                closure.selection = closure.selection + 1 if closure.selection < max_y - 2 else closure.selection
            elif c == 22:
                # ctrl+v
                self._show_score = not self._show_score
            elif c == 27:
                # escape
                return ''
            else:
                if c in (126, 127):
                    # delete, backspace
                    if len(search):
                        search = search[:-1]
                else:
                    search += chr(c)

                fm.update_scores(search)

            draw()

        return fm.top_matches(max_y)[closure.selection]


def main():
    with ncurses() as scr:
        ui = SimplePager(scr)
        result = ui.run()
    sys.stdout.write(result.strip())

if __name__ == '__main__':
    main()
