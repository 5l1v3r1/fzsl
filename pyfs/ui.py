import curses
import os
import sys

import pyfs

class SimplePager(object):
    def __init__(self):
        self._old_stdout = sys.__stdout__
        self._old_stdout_fd = os.dup(sys.stdout.fileno())
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

        tty = open('/dev/tty')
        os.dup2(tty.fileno(), 0)

        self._scr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.raw()

        self._scr.keypad(1)

        self._config = {
            'default': 'find ./'
        }

    def cleanup(self):
        self._scr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

        os.dup2(self._old_stdout_fd, sys.stdout.fileno())
        sys.stdout = self._old_stdout

    def run(self):
        scanner = pyfs.Scanner(self._config)
        scorer = pyfs.WeightedDistanceScore()

        self._scr.addstr("Scanning ...")
        self._scr.refresh()
        files = scanner.scan()

        max_y, _ = self._scr.getmaxyx()
        max_y -= 1

        self._scr.clear()
        for line, match in enumerate(files[:max_y]):
            self._scr.addstr(line, 0, match)
        self._scr.refresh()


        fm = pyfs.FuzzyMatch(files=files, scorer=scorer)

        search = ''
        while True:
            c = self._scr.getch()

            if c in (curses.KEY_ENTER, ord('\n')):
                break
            elif c in (curses.KEY_DC, curses.KEY_BACKSPACE):
                if len(search):
                    search = search[:-1]
            else:
                search += chr(c)

            fm.update_scores(search)

            self._scr.clear()
            for line, match in enumerate(fm.top_matches(max_y)):
                self._scr.addstr(line, 0, match)
            self._scr.refresh()

        self._scr.refresh()
        self.cleanup()
        return fm.top_matches(1)[0]


def main():
    ui = SimplePager()
    result = ui.run()
    sys.stdout.write(result.strip())

if __name__ == '__main__':
    main()
