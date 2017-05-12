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



with open("./tests/fixtures.json") as fd:
    FIXTURES = json.load(fd)


@pytest.fixture
def temp_file(tmpdir):
    sample_file = tmpdir.join("file.txt")
    return sample_file


class TestFXR(object):

    @abc.abstractmethod
    def run_cli(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def run_code(self, *args, **kwargs):
        pass

    def _test_exception(self, temp_file, testdata):
        testdata = Munch(**testdata)
        temp_file.write(testdata["original"])
        with pytest.raises(SystemExit) as exc:
            self.run_code(temp_file, testdata)
        assert exc.typename == testdata["exception_type"]
        assert str(exc.value) == testdata["exception_text"]


class TestFXRAdd(TestFXR):

    def run_cli(self, filepath, pattern, added_text, prepend=False, literal=False, **kwargs):
        literal = '--literal' if literal else ''
        prepend = "--prepend" if prepend else ''
        cmd = "fxr add {literal} {prepend} --single {filepath} '{pattern}' '{added_text}'"
        cmd = shlex.split(cmd.format(**locals()))
        subprocess.check_call(cmd)

    def run_code(self, filepath, testdata):
        return fxr.add_text(args=testdata, filepath=filepath, raise_on_error=True)

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["add"]["valid"])
    def test_add_valid_cli(self, temp_file, testdata):
        temp_file.write(testdata["original"])
        self.run_cli(temp_file, **testdata)
        assert temp_file.read() == testdata["expected"]

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["add"]["valid"])
    def test_add_valid_code(self, temp_file, testdata):
        testdata = Munch(**testdata)
        temp_file.write(testdata["original"])
        self.run_code(temp_file, testdata)
        assert temp_file.read() == testdata["expected"]

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["add"]["exceptions"])
    def test_add_exceptions(self, temp_file, testdata):
        self._test_exception(temp_file, testdata)


class TestFXRReplace(TestFXR):

    def run_code(self, filepath, testdata):
        return fxr.replace_text(args=testdata, filepath=filepath, raise_on_error=True)

    @pytest.mark.parametrize("testdata", FIXTURES["tests"]["replace"]["exceptions"])
    def test_add_exceptions(self, temp_file, testdata):
        self._test_exception(temp_file, testdata)
