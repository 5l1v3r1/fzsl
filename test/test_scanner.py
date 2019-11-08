import configparser
import io
import os

import pytest

import fzsl


@pytest.fixture
def testdir():
    return os.path.realpath(os.path.dirname(__file__))


@pytest.fixture
def basename():
    return os.path.basename(__file__)


def test_sort():
    s1 = fzsl.SimpleScanner("test", "echo", priority=1)
    s2 = fzsl.SimpleScanner("test", "echo", priority=2)

    assert [s1, s2] == sorted([s2, s1])


def test_root_path_match(testdir):
    s = fzsl.SimpleScanner("test", "echo", root_path=testdir)
    assert s.is_suitable(testdir)
    assert s.is_suitable("%s/test/stuff" % (testdir,))
    assert not s.is_suitable(os.path.dirname(testdir))
    assert not s.is_suitable("%s/../" % (testdir,))


def test_root_path_cmd(testdir):
    s = fzsl.SimpleScanner(
        "test", "echo", root_path="!echo %s" % (testdir,), detect_cmd="true"
    )
    assert s.is_suitable(testdir)


def test_detect_cmd_match(testdir, basename):
    cmd = "[ -f %s ]" % (basename,)
    s = fzsl.SimpleScanner("test", "echo", detect_cmd=cmd)

    assert s.is_suitable(testdir)
    assert not s.is_suitable("%s/../" % (testdir,))

    cmd = "[ -f thisfileisnothere ]"
    s2 = fzsl.SimpleScanner("test", "echo", detect_cmd=cmd)
    assert not s2.is_suitable(testdir)


def test_cmd(testdir, basename):
    cmd = "find . -name %s" % (basename,)
    s = fzsl.SimpleScanner("test", cmd)
    assert "./" + basename in s.scan(testdir)
    assert ".git" + basename not in s.scan(testdir)

    assert not s.scan("%s/../bin" % (testdir,))


def test_fallthrough(testdir):
    s = fzsl.SimpleScanner("test", "echo")
    assert s.is_suitable(testdir)


def test_scanner(testdir, tmpdir):
    cache = os.path.join(tmpdir, "cache")

    with open(cache, "w") as tp:
        with open(os.path.join(testdir, "files"), "r") as src:
            tp.write("\n".join(src.read().split()))

    s = fzsl.SimpleScanner("test", "echo hi", cache=cache)
    results = s.scan()
    assert len(results) == 49168

    results = s.scan(rescan=True)
    assert len(results) == 1
    assert results[0] == "hi"


def test_load_rule():
    buf = "[some-rule]\n"

    parser = configparser.RawConfigParser()
    parser.read_file(io.StringIO(buf))

    with pytest.raises(fzsl.NoTypeError):
        fzsl.scanner_from_configparser("some-rule", parser)

    buf += "type: junk\n"
    parser.read_file(io.StringIO(buf))
    with pytest.raises(fzsl.UnknownTypeError):
        fzsl.scanner_from_configparser("some-rule", parser)

    buf = "[some-rule]\ntype = simple\n"
    parser.read_file(io.StringIO(buf))
    with pytest.raises(configparser.NoOptionError):
        fzsl.scanner_from_configparser("some-rule", parser)

    buf += "cmd = echo\n"
    parser.read_file(io.StringIO(buf))
    r = fzsl.scanner_from_configparser("some-rule", parser)
    assert isinstance(r, fzsl.Scanner)


def test_load_plugin(testdir):
    buf = "[rule]\ntype=python\npath=%s/plugins/test_plugin.py\n" % (testdir,)

    parser = configparser.RawConfigParser()

    parser.read_file(io.StringIO(buf + "object=UnsuitableScanner\n"))
    scanner = fzsl.scanner_from_configparser("rule", parser)
    assert not scanner.is_suitable("")

    parser = configparser.RawConfigParser()
    parser.read_file(io.StringIO(buf + "object=ABCScanner\n"))
    scanner = fzsl.scanner_from_configparser("rule", parser)
    assert scanner.is_suitable("")
    assert scanner.scan("") == ["a", "b", "c"]

    b = buf + "object=KwdsScanner\n"
    b += "arg1=1\narg2=abc\narg3=some string\n"
    parser = configparser.RawConfigParser()
    parser.read_file(io.StringIO(b))
    scanner = fzsl.scanner_from_configparser("rule", parser)
    assert scanner.scan("") == ["1", "abc", "some string"]

    with pytest.raises(fzsl.ConfigError):
        parser = configparser.RawConfigParser()
        parser.read_file(io.StringIO(buf + "object=BrokenScanner1\n"))
        scanner = fzsl.scanner_from_configparser("rule", parser)

    with pytest.raises(fzsl.ConfigError):
        parser = configparser.RawConfigParser()
        parser.read_file(io.StringIO(buf + "object=BrokenScanner2\n"))
        scanner = fzsl.scanner_from_configparser("rule", parser)

    with pytest.raises(fzsl.ConfigError):
        parser = configparser.RawConfigParser()
        parser.read_file(io.StringIO(buf + "object=BrokenScanner3\n"))
        scanner = fzsl.scanner_from_configparser("rule", parser)
