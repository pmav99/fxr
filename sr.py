#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: sr.py
# author: Panagiotis Mavrogiorgos - pmav99 google mail

"""

    python3 sr.py single 'search_pattern' 'replace' /path/to/file

    python3 sr.py multi 'search_pattern' 'replace' -s -l --hidden

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import sys
import shutil
import argparse
import subprocess


def apply_search_and_replace(regex, replace, filepaths, raise_on_error=False):
    for filepath in filepaths:
        # open file
        with open(filepath) as fd:
            original = fd.read()
        # replace text
        try:
            substituted = re.sub(regex, replace, original)
        except Exception:
            sys.exit("The regex is invalid: %r" % regex)
        if original == substituted:
            msg = "no substitutions made: %s" % filepath
            if raise_on_error:
                sys.exit(msg)
            else:
                print("Warning: %s" % msg)
        else:
            # write file inplace
            with open(filepath, "w") as fd:
                fd.write(substituted)


def search_for_files(search_prog, search_args, regex):
    # Check if the search engine is available
    if shutil.which(search_prog) is None:
        sys.exit("Coulnd't find <%s>. Please install it and try again." % search_prog)

    # We DO need "-l" when we use ag!
    if search_prog == "ag":
        if search_args and "-l" not in search_args:
            search_args.append("-l")
        else:
            search_args = ['-l']

    cmd = [search_prog]
    cmd.extend(search_args)
    cmd.append(regex)
    try:
        output = subprocess.check_output(cmd)
        filepaths = output.decode("utf-8").splitlines()
    except subprocess.CalledProcessError:
        sys.exit("Couldn't find any matches. Check your regex")
    return filepaths


def main(args):
    debug = args.debug
    regex = args.regex
    replace = args.replace
    if debug:
        print(args)
    if args.mode == "single":
        filepaths = [args.filepath]     # create a list!
        raise_on_error = True
    elif args.mode == 'multi':
        # use ag to search for the pattern.
        search_prog = args.search
        search_args = args.search_args
        filepaths = search_for_files(search_prog, search_args, regex)
        raise_on_error = False
    else:
        raise ValueError("WTF?!?!?")
    apply_search_and_replace(regex, replace, filepaths, raise_on_error)


if __name__ == "__main__":
    # create the top-level parser and the sub-parser
    parser = argparse.ArgumentParser(description="A pure python search and replace script.")

    subparsers = parser.add_subparsers(help='Choose mode of operation', dest='mode')
    single_parser = subparsers.add_parser('single', help='Search and replace on a single file')
    multi_parser = subparsers.add_parser('multi', help='Search for pattern and replace it on all matching files.')
    # single parser arguments
    single_parser.add_argument("regex", help="The regex pattern we want to match.")
    single_parser.add_argument("replace", help="The replace text that we want to use.")
    single_parser.add_argument("filepath", help="The path to the file on which we want to apply the regex.")
    single_parser.add_argument("-d", "--debug", action="store_true", default=False, help="Debug mode on")
    # multi parser arguments
    multi_parser.add_argument("regex", help="The regex pattern we want to match.")
    multi_parser.add_argument("replace", help="The replace text that we want to use.")
    multi_parser.add_argument("search_args", help="Any additional arguments are passed to the search executable.", nargs=argparse.REMAINDER, default=('-s', '-l', '--hidden'))
    multi_parser.add_argument("-s", "--search", help="The executable that we want to use in order to search for matches. Defaults to 'ag'.", default="ag", metavar='')
    multi_parser.add_argument("-d", "--debug", action="store_true", default=False, help="Debug mode on")
    args = parser.parse_args()
    main(args)
