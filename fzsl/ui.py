import curses
import functools
import os
import sys

import fzsl

for i, color in enumerate(('white', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan')):
    vars()['COL_%s' % (color.upper())] = i
    vars()['COL_B%s' % (color.upper())] = i + 8

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
        _ = [curses.init_pair(i + 1, i, -1) for i in range(curses.COLORS)]

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
        self._show_score = False

    @curses_method
    def run(self, scr):
        scanner = fzsl.Scanner(self._config)

        scr.addstr("Scanning ...")
        scr.refresh()
        files = scanner.scan()

        fm = fzsl.FuzzyMatch(files=files)
        max_y, _ = scr.getmaxyx()
        max_y -= 1

        class Closure(object):
            selection = 0
        closure = Closure

        def draw():
            scr.erase()
            m = fm.top_matches(max_y)
            if closure.selection > len(m):
                closure.selection = 0

            for index, match in enumerate(m):
                prefix = ''
                if self._show_score:
                    prefix = "%f     " % (fm.score(match),)
                offset = len(prefix)


                start = fm.start(match)
                end = fm.end(match)

                if closure.selection == index:
                    scr.addstr(max_y - index - 1, 0, prefix + match[:start], curses.A_UNDERLINE)
                    scr.addstr(max_y - index - 1, start+offset, match[start:end+1], curses.A_UNDERLINE|curses.color_pair(COL_BCYAN))
                    scr.addstr(max_y - index - 1, end+offset, match[end+1:], curses.A_UNDERLINE)
                else:
                    scr.addstr(max_y - index - 1, 0, prefix + match[:start])
                    scr.addstr(max_y - index - 1, start+offset, match[start:end+1], curses.color_pair(COL_BCYAN))
                    scr.addstr(max_y - index - 1, end+offset, match[end+1:])

            scr.addstr(max_y, 2, "%d/%d >  %s" % (fm.n_matches, fm.n_files, search))
            scr.refresh()



        search = ''
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
                self._show_score = not self._show_score
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
    ui = SimplePager()
    #pylint: disable=E1120
    result = ui.run()
    sys.stdout.write(result.strip())

if __name__ == '__main__':
    main()
