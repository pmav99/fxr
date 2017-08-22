#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: tests/test_add.py
# author: Panagiotis Mavrogiorgos <pmav99,gmail>

"""

"""

import shlex
import subprocess

import fxr

import pytest


from . import load_fixtures, TestFXR


class TestFXRDelete(TestFXR):

    """ Test `fxr delete`. """

    def run_code(self, args, filepath):
        return fxr.delete_text(args=args, filepath=filepath)

    def run_cli(self, filepath, pattern, lines_before, lines_after, include_line, literal, **kwargs):
        literal = '--literal' if literal else ''
        lines_before = '--lines_before %d' % lines_before if lines_before else ''
        lines_after = '--lines_after %d' % lines_after if lines_after else ''
        include_line = "--include_line" if include_line else ''
        cmd = "fxr delete {literal} {lines_before} {lines_after} {include_line} --single {filepath} '{pattern}'"
        cmd = shlex.split(cmd.format(**locals()))
        subprocess.check_call(cmd)

    @pytest.mark.parametrize("args", load_fixtures("tests/delete_fixtures.json", "valid"))
    def test_add_valid_cli(self, temp_file, args):
        self._test_run_valid_cli(temp_file, args)

    @pytest.mark.parametrize("args", load_fixtures("tests/delete_fixtures.json", "valid"))
    def test_add_valid_code(self, temp_file, args):
        self._test_run_valid_code(temp_file, args)

    @pytest.mark.parametrize("args", load_fixtures("tests/delete_fixtures.json", "exceptions"))
    def test_add_exceptions(self, temp_file, args):
        self._test_run_exceptions(temp_file, args)
