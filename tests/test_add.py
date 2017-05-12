#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: tests/test_add.py
# author: Panagiotis Mavrogiorgos <pmav99,gmail>

"""

"""

import re
import json
import shlex
import subprocess

import importlib
import frx

from munch import Munch
import pytest



with open("./tests/fixtures.json") as fd:
    FIXTURES = json.load(fd)


@pytest.fixture
def temp_file(tmpdir):
    sample_file = tmpdir.join("file.txt")
    return sample_file


class TestFRX(object):

    def run_add_cli(self, filepath, pattern, added_text, prepend=False, literal=False, **kwargs):
        literal = '--literal' if literal else ''
        prepend = "--prepend" if prepend else ''
        cmd = "python frx add {literal} {prepend} --single {filepath} '{pattern}' '{added_text}'"
        cmd = shlex.split(cmd.format(**locals()))
        subprocess.check_call(cmd)

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["add"]["valid"])
    def test_add_valid(self, temp_file, testdata):
        temp_file.write(testdata["original"])
        self.run_add_cli(temp_file, **testdata)
        assert temp_file.read() == testdata["expected"]

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["add"]["exceptions"])
    def test_add_exceptions(self, temp_file, testdata):
        testdata = Munch(**testdata)
        temp_file.write(testdata["original"])
        with pytest.raises(SystemExit) as exc:
            frx.add_text(args=testdata, filepath=temp_file, raise_on_error=True)
        assert exc.typename == testdata["exception_type"]
        assert str(exc.value) == testdata["exception_text"]


# class TestAdd(object):

    # def run_single(self, filepath, pattern, addition, prepend=False, literal=False):
        # literal = '--literal' if literal else ''
        # prepend = "--prepend" if prepend else ''
        # cmd = "python frx add {literal} {prepend} --single {filepath} '{pattern}' '{addition}'"
        # cmd = shlex.split(cmd.format(**locals()))
        # subprocess.check_call(cmd)

    # @pytest.mark.parametrize("prepend", [True, False])                          # Prepend vs Append
    # @pytest.mark.parametrize("pattern", [r"\d A", r"\d B", "Cream", r"\d D"])   # Matches first, second, third last line
    # @pytest.mark.parametrize("added_text", ["ADD", "ADD\nADD\nADD"])            # Single and multiple lines
    # def test(self, temp_file, prepend, pattern, added_text):
        # original = temp_file.read().strip()
        # original_lines = original.splitlines()
        # self.run_single(temp_file, pattern, added_text, prepend)
        # changed = temp_file.read()
        # changed_lines = changed.splitlines()
        # no_lines = added_text.splitlines()
        # #
        # assert added_text not in original
        # assert added_text in changed
        # assert len(changed_lines) > len(original_lines)
        # assert len(changed_lines) == len(original_lines) + len(no_lines)

        # before, after = re.split(pattern, changed, 1)
        # if prepend:
            # assert added_text in before
            # assert added_text not in after
        # else:
            # assert added_text not in before
            # assert added_text in after

        # print('=' * 80)
        # print(original)
        # print('-' * 80)
        # print(changed)
        # print('=' * 80)

    # @pytest.mark.parametrize("prepend", [True, False])
    # @pytest.mark.parametrize("added_text", ["ADD", "ADD\nADD\nADD"])
    # def test_multiple_matches_per_line_are_matched_only_once(self, temp_file, prepend, added_text):
        # pattern = "Cream"
        # original = temp_file.read().strip()
        # original_lines = original.splitlines()
        # self.run_single(temp_file, pattern=pattern, addition=added_text, prepend=prepend)
        # changed = temp_file.read()
        # changed_lines = changed.splitlines()
        # no_lines = added_text.splitlines()
        # #
        # assert added_text not in original
        # assert added_text in changed
        # assert len(changed_lines) > len(original_lines)
        # assert len(changed_lines) == len(original_lines) + len(no_lines)
        # #
        # before, after = re.split(pattern, changed, 1)
        # if prepend:
            # assert added_text in before
            # assert added_text not in after
        # else:
            # assert added_text not in before
            # assert added_text in after

        # print('=' * 80)
        # print(original)
        # print('-' * 80)
        # print(changed)
        # print('=' * 80)


    # @pytest.mark.parametrize("prepend", [True, False])
    # @pytest.mark.parametrize("literal", [True, False])
    # def test_empty_addition_raise_error(self, temp_file, prepend, literal):
        # args = Munch(
            # pattern="pattern",
            # addition="",
            # filepath=temp_file,
            # prepend=prepend,
            # literal=literal,
        # )

        # with pytest.raises(subprocess.CalledProcessError):
            # self.run_single(**args)

        # with pytest.raises(SystemExit):
            # frx.add_text(args, temp_file)

    # def test_empty_addition_raise_error(self):
        # with pytest.raises(ValueError):
            # self.run_single('/tmp/foo.txt', '', 'pattern')

    # def test_ignore_multiple_matches_per_line(self, temp_file):
        # added_text = "ADDITION"
        # original = temp_file.read().strip()
        # original_lines = original.splitlines()
        # self.run_single(temp_file, pattern, added_text, prepend)
        # changed = temp_file.read()
        # changed_lines = changed.splitlines()

    # def test_ignore_multiple_lines_per_line(self, temp_file):
        # raise NotImplementedError


# @pytest.mark.parametrize("literal, pattern, replacement, content, no_substitutions", [
    # (False, r"\d{3}", "ASD", "substitute number: 123 is this ok? asdf123qwer", 2),
    # (False, " 123 ", "ASD", "substitute number: 123 is this ok? asdf123qwer", 1),
    # (False, "123", "ASD", "substitute number: 123 is this ok? asdf123qwer", 2),
    # # Regex with literal
    # (True, r"\d{3}", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 1),
    # (True, " 123 ", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 1),
    # (True, "123", "ASD", r"Just text 123 more text: \d{3} asdf123qwer final text", 2),
# ])
# def test_sr_single(temp_file, literal, pattern, replacement, content, no_substitutions):
    # temp_file.write(content)
    # original = temp_file.read()
    # assert replacement not in original
    # # run script
    # run_single(pattern=pattern, replacement=replacement, filepath=temp_file, literal=literal)
    # # check that substitutions are OK
    # substituted = temp_file.read()
    # assert pattern not in substituted
    # assert replacement in substituted
    # assert len(substituted.split(replacement)) == no_substitutions + 1


# @pytest.mark.parametrize("literal", [True, False])
# def test_sr_single_no_matches(temp_file, literal):
    # with pytest.raises(subprocess.CalledProcessError):
        # run_single("pattern", "replacement", temp_file, literal)


# def test_sr_regex_pattern_not_valid(temp_file):
    # temp_file.write("asd( asdf")
    # with pytest.raises(subprocess.CalledProcessError):
        # run_single("asd(", "replacement", temp_file)

# def test_sr_literal_pattern_not_valid(temp_file):
    # temp_file.write("asd( asdf")
    # run_single("asd(", "replacement", temp_file, literal=True)
    # # check that substitutions are OK
    # substituted = temp_file.read()
    # assert pattern not in substituted
    # assert replacement in substituted
    # assert len(substituted.split(replacement)) == no_substitutions + 1



#@pytest.mark.parametrize("pattern, replacement, content", [
    # (" \d{3} ", "ASD", "substitute number: 123 asdf \d{3} is this ok? asdf123qwer"),
    # (" 123 ", "ASD", "substitute number: 123 asdf \d{3} is this ok? asdf123qwer"),
# ])
# def test_sr_single(temp_file, pattern, replacement, content):
    # temp_file.write(content)
    # original = temp_file.read()
    # assert replacement not in original
    # # run script
    # cmd = "python3 frx single '{pattern}' '{replacement}' {filepath} "
    # cmd = shlex.split(cmd.format(pattern=pattern, replacement=replacement, filepath=temp_file))
    # subprocess.check_call(cmd)
    # substituted = temp_file.read()
    # # check that substitutions are OK
    # assert "123" in substituted
    # assert " 123 " not in substituted
    # assert replacement in substituted
