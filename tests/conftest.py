#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: tests/conftest.py
# author: Panagiotis Mavrogiorgos <pmav99,gmail>

"""

"""


import pytest


@pytest.fixture
def temp_file(tmpdir):
    sample_file = tmpdir.join("file.txt")
    return sample_file
