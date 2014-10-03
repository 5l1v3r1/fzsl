import functools
import os

import envoy

class SubprocessError(Exception):
    def __init__(self, cmd, cwd):
        super(SubprocessError, self).__init__(
                'Failed to run: "%s" in %s' % (cmd, cwd))


@functools.total_ordering
class Scanner(object):
    def __init__(self, cmd, detect_cmd=None, root_path=None, priority=0, cache=None):
        """
        Create a scanner.

        @param cmd  - shell command used to scan for files
        @param detect_cmd   - If specified, this command will be used to
                              check if this scanner can be used for a
                              given path.  If the command returns 0, the
                              scanner will be used
        @param root_path    - If specified, this path serves two purposes:
                              If no detect_cmd is specified, any path that
                              is a child of the root_path will allow the use
                              of this scanner.  Secondly, when scanning, the
                              current working directory will be set to this
                              path
        @param priority     - Priority for this scanner.  Scanners with a
                              higher priority will be favored for any given
                              path.  If the priority is less than 0, the
                              scanner will be ignored by any automatic
                              scanner picking
        @param cache        - If specified, path where this scanner will store
                              a cache of files it scans.  By default, calls
                              to scan will just return the files in the cache.
                              This can be changed by passing rescan=True to
                              scan().
        """
        self._cmd = cmd
        self._detect_cmd = detect_cmd
        self._root_path = None
        self._priority = priority
        self._cache = None

        if root_path is not None:
            root_path = os.path.expandvars(root_path)
            root_path = os.path.expanduser(root_path)
            root_path = os.path.normpath(root_path)
            self._root_path = os.path.realpath(root_path)

        if cache is not None:
            cache = os.path.expandvars(cache)
            cache = os.path.expanduser(cache)
            cache = os.path.normpath(cache)
            self._cache = os.path.realpath(cache)

            cachedir = os.path.dirname(os.path.realpath(cache))
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)

    def __eq__(self, other):
        return (self._cmd == other._cmd
                and self._detect_cmd == other._detect_cmd
                and self._priority == other._priority
                and self._root_path == other._root_path)

    def __lt__(self, other):
        return self._priority < other._priority

    @classmethod
    def from_configparser(cls, section, parser):
        """
        Create a scanner from a config parser section.

        @param config_section   - config parser object defining a scanner.
        """
        kwds = {}
        if parser.has_option(section, 'detect_cmd'):
            kwds['detect_cmd'] = parser.get(section, 'detect_cmd')

        if parser.has_option(section, 'root_path'):
            kwds['root_path'] = parser.get(section, 'root_path')

        if parser.has_option(section, 'priority'):
            kwds['priority'] = parser.get(section, 'priority')

        if parser.has_option(section, 'cache'):
            kwds['cache'] = parser.get(section, 'cache')

        return cls(parser.get(section, 'cmd'), **kwds)

    def is_suitable(self, path):
        """
        Check if this scanner is suitable to run on the given path.
        This involves running the detect_cmd to see if we are
        in an appropriate directory type and checking to see if
        the specified path is a descendent of the root_path.

        @param path - path to check
        @return     - True if this scanner is suitable to scan in
                      the specified path
        """
        if self._root_path is not None:
            path = os.path.realpath(os.path.normpath(path))
            if path.startswith(self._root_path):
                return True

        if self._detect_cmd is not None:
            try:
                c = envoy.run(self._detect_cmd, cwd=path)
            except:
                raise SubprocessError(self._detect_cmd, path)
            if c.status_code == 0:
                return True

        if self._root_path is None and self._detect_cmd is None:
            return True

        return False

    def scan(self, path=None, rescan=False):
        """
        Scan for files at the given path.  This assumes that the
        scanner is suitable for scanning (self.is_suitable()).
        If a root_path was specified for the command, it is used
        as the current working directory for the command, otherwise
        the path itself is.  If a cache was passed to the
        constructor, the file list will be generated by simply
        reading the cache.  This can be bypassed by setting rescan.


        @param path     - path at which to start scanning, if undefined
                          then the current working directory is used
        @param rescan   - force a full rescan of files instead of using
                          a cached list
        @return         - list of detected files
        """
        have_cache = self._cache is not None and os.path.exists(self._cache)
        ret = None

        if have_cache and not rescan:
            with open(self._cache, 'r') as fp:
                ret = [f.strip() for f in fp.read().split()]
        else:
            if path is None:
                path = os.getcwd()

            cwd = path if self._root_path is None else self._root_path
            c = envoy.run(self._cmd, cwd=cwd)
            if c.status_code != 0:
                raise SubprocessError(self._cmd, cwd)
            ret = [f.strip() for f in c.std_out.split()]

            if self._cache is not None:
                with open(self._cache, 'w') as fp:
                    fp.write('\n'.join(ret))

        return ret

