#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: tests/test_add.py
# author: Panagiotis Mavrogiorgos <pmav99,gmail>

"""

"""

import re
import abc
import json
import shlex
import subprocess

import importlib
import fxr

from munch import Munch
import pytest



def load_fixtures(path, key):
    if key not in {"valid", "exceptions"}:
        raise ValueError('<key> must be one of `{"valid", "exceptions"}`, not `%s`' % key)
    with open(path) as fd:
        fixtures = json.load(fd)[key]
    return fixtures


@pytest.fixture
def temp_file(tmpdir):
    sample_file = tmpdir.join("file.txt")
    return sample_file


class TestFXR(object):

    @abc.abstractmethod
    def run_cli(self, args, filepath):
        raise NotImplementedError

    @abc.abstractmethod
    def run_code(self, args, filepath):
        raise NotImplementedError

    def _test_run_valid_cli(self, temp_file, args):
        temp_file.write(args["original"])
        self.run_cli(temp_file, **args)
        assert temp_file.read() == args["expected"]

    def _test_run_valid_code(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        self.run_code(args=args, filepath=temp_file)
        assert temp_file.read() == args["expected"]

    def _test_run_exceptions(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        with pytest.raises(SystemExit) as exc:
            self.run_code(args=args, filepath=temp_file)
        assert exc.typename == args["exception_type"]
        assert str(exc.value) == args["exception_text"]

class TestFXRAdd(TestFXR):

    def run_code(self, args, filepath):
        return fxr.add_text(args=args, filepath=filepath, raise_on_error=True)

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





class TestFXRReplace(TestFXR):

    def run_code(self, filepath, testdata):
        return fxr.replace_text(args=testdata, filepath=filepath, raise_on_error=True)

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["replace"]["exceptions"])
    def test_add_exceptions(self, temp_file, testdata):
        self._test_exception(temp_file, testdata)
