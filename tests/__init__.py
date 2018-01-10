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
    diff = list(difflib.unified_diff([l.strip() for l in temp_file.readlines()], expected.splitlines()))
    assert temp_file.read() == expected, pprint.pformat(diff)


def check_backup(temp_file, args):
    if args["backup"]:
        backup_filename = fxr.get_backup_filename(temp_file, args["backup"])
        assert backup_filename.exists(), backup_filename
        assert_OK(backup_filename, args["original"])


class BaseFXRTest(object):

    """ Base class for testing fxr. """

    version = "0.2.5"

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
        check_backup(temp_file, args)


    def _test_run_valid_code(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        self.run_code(args=args, filepath=temp_file)
        assert_OK(temp_file, args["expected"])
        # check_backup(temp_file, args)

    def _test_run_exceptions(self, temp_file, args):
        args = Munch(**args)
        temp_file.write(args["original"])
        with pytest.raises(SystemExit) as exc:
            self.run_code(args=args, filepath=temp_file)
        assert exc.typename == args["exception_type"]
        assert str(exc.value) == args["exception_text"]

    def test_version(self):
        # We need to capture stderr because argparse in Python < 3.4 prints
        # version there
        # https://bugs.python.org/issue18920
        cmd = shlex.split("fxr %s --version" % self.action)
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        out = out.decode('utf-8').strip()
        expected = " ".join(item for item in ("fxr", self.action, self.version) if item)
        assert out == expected, (out, expected)

