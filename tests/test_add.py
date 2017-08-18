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

from . import TestFXR, load_fixtures


class TestFXRAdd(TestFXR):

    """ Test `fxr add`. """

    def run_code(self, args, filepath):
        return fxr.add_text(args=args, filepath=filepath)

    def run_cli(self, filepath, pattern, added_text, prepend=False, literal=False, **kwargs):
        literal = '--literal' if literal else ''
        prepend = "--prepend" if prepend else ''
        cmd = "fxr add {literal} {prepend} --single {filepath} '{pattern}' '{added_text}'"
        cmd = shlex.split(cmd.format(**locals()))
        subprocess.check_call(cmd)

    @pytest.mark.parametrize("args", load_fixtures("tests/add_fixtures.json", "valid"))
    def test_add_valid_cli(self, temp_file, args):
        self._test_run_valid_cli(temp_file, args)

    @pytest.mark.parametrize("args", load_fixtures("tests/add_fixtures.json", "valid"))
    def test_add_valid_code(self, temp_file, args):
        self._test_run_valid_code(temp_file, args)

    @pytest.mark.parametrize("args", load_fixtures("tests/add_fixtures.json", "exceptions"))
    def test_add_exceptions(self, temp_file, args):
        self._test_run_exceptions(temp_file, args)
