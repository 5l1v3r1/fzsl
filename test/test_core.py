import pytest

import fzsl


def test_library():
    fm = fzsl.FuzzyMatch()

    assert 0 == fm.n_matches
    assert 0 == fm.n_files
    assert [] == fm.top_matches()

    with pytest.raises(KeyError):
        fm.score("a")

    fm.add_files(["a", "b", "c"])
    assert 3 == fm.n_matches
    assert 3 == fm.n_files
    assert ["a", "b", "c"] == sorted(fm.top_matches())

    assert 0 == fm.score("a")
    assert 0 == fm.start("a")
    assert 0 == fm.end("a")

    fm.reset_files([])
    assert 0 == fm.n_matches
    assert 0 == fm.n_files
    assert [] == fm.top_matches()


def test_update_scores():
    fm = fzsl.FuzzyMatch()

    files = ["abc/def/ghi", "abc/d", "abc/ggg", "z/1", "z/2", "zz/3"]

    fm.add_files(files)

    fm.update_scores("abc")
    assert 3 == fm.n_matches
    matches = fm.top_matches()

    fm.update_scores("abcd")
    assert 2 == fm.n_matches

    fm.update_scores("abc")
    assert 3 == fm.n_matches
    assert matches == fm.top_matches()

    fm.update_scores("ab")
    fm.update_scores("a")
    fm.update_scores("")
    assert fm.n_matches == fm.n_files


def test_prefer_latter():
    fm = fzsl.FuzzyMatch()

    files = ["prefix/abc/stuff", "abc/d", "some/prefix/abc"]

    fm.add_files(files)
    fm.update_scores("abc")
    assert "some/prefix/abc" == fm.top_matches(1)[0]


def test_prefer_shorter():
    fm = fzsl.FuzzyMatch()

    files = ["a/z/b/z/c", "a/b/c", "a/bbbbb/c"]

    fm.add_files(files)
    fm.update_scores("abc")
    assert "a/b/c" == fm.top_matches(1)[0]


def test_start_end():
    fm = fzsl.FuzzyMatch()

    files = ["abc/def/ghi", "ggg/a/b/ggg/c/d", "ggg/abc"]

    fm.add_files(files)
    fm.update_scores("abc")

    assert 0 == fm.start("abc/def/ghi")
    assert 2 == fm.end("abc/def/ghi")

    assert 4 == fm.start("ggg/a/b/ggg/c/d")
    assert 12 == fm.end("ggg/a/b/ggg/c/d")

    assert 4 == fm.start("ggg/abc")
    assert 6 == fm.end("ggg/abc")


def test_ignorecase():
    fm = fzsl.FuzzyMatch()

    files = ["abc/def/ghi", "abc/d", "abc/ggg", "z/1", "z/2", "zz/3"]

    fm.add_files(files)

    fm.update_scores("ABC")
    assert 3 == fm.n_matches
