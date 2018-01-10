#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# module: fxr
# author: Panagiotis Mavrogiorgos - pmav99 google mail

"""

Examples
--------

``` python
fxr add 'search_pattern' 'text to be added' --single /path/to/file
fxr delete 'search_pattern' --lines_before 2 --include_line --single /path/to/file
fxr replace 'search_pattern' 'replace' --single /path/to/file
```

"""


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

__version__ = "0.2.3"

import io
import re
import sys
import shutil
import argparse
import subprocess

from contextlib import contextmanager


def handle_no_match(args):
    msg = "Couldn't find a match."
    if args.raise_if_no_change:
        sys.exit(msg)
    else:
        print("Warning: %s" % msg)


def literal_replace(pattern, replacement, original):
    return original.replace(pattern, replacement)


def regex_replace(pattern, replacement, original):
    return re.sub(pattern, replacement, original)


def literal_match(line, pattern):
    return pattern in line


def regex_match(line, pattern):
    return re.search(pattern, line)


def compress(data, indices_to_drop):
    selectors = (0 if index in indices_to_drop else 1 for index in range(len(data)))
    return (d for d, s in zip(data, selectors) if s)


def search_for_files(args):
    search_prog = args.search_prog
    search_args = args.search_args
    # Check if the search engine is available
    if shutil.which(search_prog) is None:
        sys.exit("Coulnd't find <%s>. Please install it and try again." % search_prog)
    # We DO need "-l" when we use ag!
    if search_prog == "ag":
        if search_args and "-l" not in search_args:
            search_args.append("-l")
        else:
            search_args = ['-l']
    # most search programs support -F as an alias for --literal for grep compatibility.
    if args.literal:
        search_args.append("-F")
    cmd = [search_prog]
    cmd.extend(search_args)
    cmd.append(args.pattern)
    try:
        output = subprocess.check_output(cmd)
        filepaths = output.decode("utf-8").splitlines()
    except subprocess.CalledProcessError:
        sys.exit("Couldn't find any matches. Check your the pattern: %s" % args.pattern)
    return filepaths


def add_text(args, filepath):
    # input validation
    if args.pattern == '' or args.added_text == '':
        sys.exit("In <add> mode, you must specify both <pattern> and <added_text>.")
    added_text = args.added_text
    prepend = args.prepend
    pattern = re.compile(args.pattern)
    with io.open(str(filepath), "rb") as fd:
        original_text = fd.read().decode('utf-8')
    original_lines = [line.strip() for line in original_text.splitlines()]
    changed_lines = original_lines[:]
    for n, line in enumerate(original_lines):
        if pattern.search(line):
            index = n if prepend else n + 1
            changed_lines.insert(index, added_text)
    output_text = "\n".join(changed_lines)
    # write file inplace
    with io.open(str(filepath), "wb") as fd:
        fd.write(output_text.encode("utf-8"))
    if original_text == output_text:
        handle_no_match(args)


def replace_text(args, filepath):
    # input validation
    if args.pattern == '' or args.replacement == '':
        sys.exit("In <replace> mode, you must specify both <pattern> and <replacement>.")
    # open file
    with io.open(str(filepath), "rb") as fd:
        original = fd.read().decode('utf-8')
    # replace text
    replace_method = literal_replace if args.literal else regex_replace
    substituted = replace_method(args.pattern, args.replacement, original)
    if original == substituted:
        handle_no_match(args)
    else:
        # write file inplace
        with io.open(str(filepath), "wb") as fd:
            fd.write(substituted.encode('utf-8'))


def delete_text(args, filepath):
    # local names
    pattern = args.pattern.encode("utf-8")
    lines_before = args.lines_before
    lines_after = args.lines_after
    include_line = args.include_line
    # open file
    with io.open(str(filepath), "rb") as fd:
        original_lines = [line.rstrip(b"\r\n") for line in fd.readlines()]
    no_lines = len(original_lines)
    # delete lines
    match_method = literal_match if args.literal else regex_match
    indices_to_be_deleted = []
    for n, line in enumerate(original_lines):
        if match_method(line, pattern):
            # we have a match!
            if include_line:
                indices_to_be_deleted.append(n)
            if lines_after:
                indices_to_be_deleted.extend((n + i) for i in range(1, lines_after + 1))
            if lines_before:
                indices_to_be_deleted.extend((n - i) for i in range(1, lines_before + 1))
    # Remove duplicates from indices_to_be_deleted
    indices_to_be_deleted = {item for item in indices_to_be_deleted if (item >= 0 and item <= no_lines)}
    # Discard lines to be removed.
    lines_to_be_kept = list(compress(original_lines, indices_to_be_deleted))
    print(lines_to_be_kept)
    if len(lines_to_be_kept) == no_lines:
        handle_no_match(args)
    else:
        # write file inplace
        changed = b"\n".join(lines_to_be_kept)
        with io.open(str(filepath), "wb") as fd:
            fd.write(changed)


DISPATCHER = {
    "add": add_text,
    "replace": replace_text,
    "delete": delete_text,
}


def get_backup_filename(filepath, backup):
    return filepath + "." + backup


@contextmanager
def handle_backup(filepath, backup):
    if not backup:
        # do nothing!
        yield
    else:
        # create backup file
        backup_file = get_backup_filename(filepath, backup)
        shutil.copy2(filepath, backup_file)
        try:
            yield
        except Exception:
            # Something went wrong, restore file
            shutil.copy2(backup_file, filepath)
            raise


def main(args):
    run = DISPATCHER[args.mode]
    if args.single:
        filepaths = [str(args.single)]
    else:
        filepaths = search_for_files(args)
    backup = args.backup
    for filepath in filepaths:
        with handle_backup(filepath, backup):
            run(args, filepath)


def add_common_args_to_cli_subcommand(parser):
    parser.add_argument("--backup", type=str, default=None, metavar='', help="If provided, it is going to be used as a prefix for backup files.")                                 # noqa
    parser.add_argument("--literal", action="store_true", default=False, help="Search literally for <pattern>, i.e. don't treat <pattern> as a regex.")                 # noqa
    parser.add_argument("--raise_if_no_change", action="store_true", help="Raise an exception if the file has remained unchanged.")                                     # noqa
    parser.add_argument("--single", action="store", default=False, help="Add text only to the specified file.", metavar='')                                             # noqa
    parser.add_argument("--search_prog", help="The executable that we want to use in order to search for matches. Defaults to 'ag'.", default="ag", metavar='')         # noqa
    parser.add_argument("--search_args", help="Arguments passed to the search executable (e.g. 'ag').", nargs=argparse.REMAINDER, default=('-s', '-l', '--hidden'))     # noqa
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))


def get_parser():
    # Create the top-level parser and the subparsers
    main_parser = argparse.ArgumentParser(description="A pure python 'search & replace' script.")
    main_parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    subparsers = main_parser.add_subparsers(help='Choose mode of operation', dest='mode', title="subcommands")      # noqa
    add_parser = subparsers.add_parser("add", help="Append/prepend text to lines matching <pattern>.")              # noqa
    delete_parser = subparsers.add_parser("delete", help="Delete text before/after lines matching <pattern>.")      # noqa
    replace_parser = subparsers.add_parser("replace", help="Replace text in lines matching <pattern>.")             # noqa

    # Add
    add_parser.add_argument("pattern", help="The pattern we want to match.")
    add_parser.add_argument("added_text", help="The text that we want to add.")
    add_parser.add_argument("--prepend", action="store_true", help="Prepend text to the <pattern>'s matches. Defaults to False.")
    add_common_args_to_cli_subcommand(add_parser)

    # Delete
    delete_parser.add_argument("pattern", help="The pattern we want to match.")
    delete_parser.add_argument("--lines_after", metavar='', type=int, default=0, help="Nunmber lines to delete after the matched pattern. Defaults to 0")       # noqa
    delete_parser.add_argument("--lines_before", metavar='', type=int, default=0, help="Number lines to delete before the matched pattern. Defaults to 0")      # noqa
    delete_parser.add_argument("--include_line", action="store_true", help="Also delete the matching line. Defaults to False.")                    # noqa
    add_common_args_to_cli_subcommand(delete_parser)

    # Replace
    replace_parser.add_argument("pattern", help="The pattern we want to match.")
    replace_parser.add_argument("replacement", help="The text we want to use as a replacement.")
    add_common_args_to_cli_subcommand(replace_parser)

    return main_parser


def cli():
    parser = get_parser()
    args = parser.parse_args()
    if args.mode:
        main(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    cli()
