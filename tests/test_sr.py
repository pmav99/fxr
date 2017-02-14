#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module:
# author: Panagiotis Mavrogiorgos <pmav99,gmail>

"""

"""

import shlex
import subprocess

import pytest


@pytest.fixture
def temp_file(tmpdir):
    sample_file = tmpdir.join("file.txt")
    return sample_file


def run_single(pattern, replacement, filepath, literal=False):
    literal = '--literal' if literal else ''
    cmd = "python3 sr.py single {literal} '{pattern}' '{replacement}' {filepath} "
    cmd = shlex.split(cmd.format(
        literal=literal, pattern=pattern, replacement=replacement, filepath=filepath
    ))
    subprocess.check_call(cmd)


@pytest.mark.parametrize("literal, pattern, replacement, content, no_substitutions", [
    (False, r"\d{3}", "ASD", "substitute number: 123 is this ok? asdf123qwer", 2),
    (False, " 123 ", "ASD", "substitute number: 123 is this ok? asdf123qwer", 1),
    (False, "123", "ASD", "substitute number: 123 is this ok? asdf123qwer", 2),
    #
    (True, r"\d{3}", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 1),
    (True, " 123 ", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 1),
    (True, "123", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 2),
])
def test_sr_single(temp_file, literal, pattern, replacement, content, no_substitutions):
    temp_file.write(content)
    original = temp_file.read()
    assert replacement not in original
    # run script
    run_single(pattern=pattern, replacement=replacement, filepath=temp_file, literal=literal)
    substituted = temp_file.read()
    # check that substitutions are OK
    assert pattern not in substituted
    assert replacement in substituted
    assert len(substituted.split(replacement)) == no_substitutions + 1


@pytest.mark.parametrize("literal", [True, False])
def test_sr_single_no_matches(temp_file, literal):
    with pytest.raises(subprocess.CalledProcessError):
        run_single(literal, "pattern", "replacement", temp_file)


#@pytest.mark.parametrize("pattern, replacement, content", [
    # (" \d{3} ", "ASD", "substitute number: 123 asdf \d{3} is this ok? asdf123qwer"),
    # (" 123 ", "ASD", "substitute number: 123 asdf \d{3} is this ok? asdf123qwer"),
# ])
# def test_sr_single(temp_file, pattern, replacement, content):
    # temp_file.write(content)
    # original = temp_file.read()
    # assert replacement not in original
    # # run script
    # cmd = "python3 sr.py single '{pattern}' '{replacement}' {filepath} "
    # cmd = shlex.split(cmd.format(pattern=pattern, replacement=replacement, filepath=temp_file))
    # subprocess.check_call(cmd)
    # substituted = temp_file.read()
    # # check that substitutions are OK
    # assert "123" in substituted
    # assert " 123 " not in substituted
    # assert replacement in substituted
