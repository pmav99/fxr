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


def apply_search_and_replace(pattern, replacement, filepath, raise_on_error=False):
    # open file
    with open(filepath) as fd:
        original = fd.read()
    # replace text
    try:
        substituted = re.sub(pattern, replacement, original)
    except Exception:
        sys.exit("The regex pattern is invalid: %r" % pattern)
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


def search_for_files(search_prog, search_args, pattern):
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
    cmd.append(pattern)
    try:
        output = subprocess.check_output(cmd)
        filepaths = output.decode("utf-8").splitlines()
    except subprocess.CalledProcessError:
        sys.exit("Couldn't find any matches. Check your the pattern: %s" % pattern)
    return filepaths


def main(args):
    pattern = re.escape(args.pattern) if args.literal else args.pattern
    filepaths = [args.filepath] if args.mode == "single" else search_for_files(args.search_prog, args.search_args, pattern)
    raise_on_error = (len(filepaths) == 1)
    for filepath in filepaths:
        apply_search_and_replace(pattern, args.replacement, filepath, raise_on_error)


if __name__ == "__main__":
    # create the top-level parser
    main_parser = argparse.ArgumentParser(description="A pure python 'search & replace' script.")
    # Create the parent-parser which contains the common options among the subparsers.
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("pattern", help="The regex pattern we want to match.")
    parent_parser.add_argument("replacement", help="The text we want to replace <pattern> with.")
    parent_parser.add_argument("--debug", action="store_true", default=False, help="Debug mode on")
    parent_parser.add_argument("--literal", action="store_true", default=False, help="Make a literal substitution (i.e. don't treat <pattern> as a regex).")
    # Create the sub-parsers.
    subparsers = main_parser.add_subparsers(help='Choose mode of operation', dest='mode', title="subcommands", description="Valid subcommands")
    single_parser = subparsers.add_parser('single', help='"Search & replace" on a single file', parents=[parent_parser])
    multi_parser = subparsers.add_parser('multi', help='Search for files matching pattern and replace all occurrences.', parents=[parent_parser], add_help=True)
    # single parser arguments
    single_parser.add_argument("filepath", help="The path to the file on which we want to replace text.")
    # multi parser arguments
    multi_parser.add_argument("search_args", help="Any additional arguments are passed to the search executable (i.e. 'ag').", nargs=argparse.REMAINDER, default=('-s', '-l', '--hidden'))
    multi_parser.add_argument("--search", help="The executable that we want to use in order to search for matches. Defaults to 'ag'.", default="ag", metavar='')
    args = main_parser.parse_args()
    if args.debug:
        print(args)
    main(args)
