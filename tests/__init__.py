#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: tests/__init__.py
# author: Panagiotis Mavrogiorgos - pmav99 google mail

import re
import abc
import json
import shlex
import pprint
import difflib
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


def assert_OK(temp_file, expected):
    diff = difflib.unified_diff([l.strip() for l in temp_file.readlines()], expected.splitlines())
    assert temp_file.read() == expected, pprint.pformat(diff)


class BaseFXRTest(object):

    """ Base class for testing fxr. """

    @abc.abstractmethod
    def run_cli(self, args, filepath):
        raise NotImplementedError

    @abc.abstractmethod
    def run_code(self, args, filepath):
        raise NotImplementedError

    def _test_run_valid_cli(self, temp_file, args):
        temp_file.write(args["original"])
        self.run_cli(temp_file, **args)
        assert_OK(temp_file, args["expected"])

    def _test_run_valid_code(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        self.run_code(args=args, filepath=temp_file)
        assert_OK(temp_file, args["expected"])

    def _test_run_exceptions(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        with pytest.raises(SystemExit) as exc:
            self.run_code(args=args, filepath=temp_file)
        assert exc.typename == args["exception_type"]
        assert str(exc.value) == args["exception_text"]
