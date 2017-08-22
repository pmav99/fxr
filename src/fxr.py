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
import os
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


def get_last_line(filepath):
    filepath = str(filepath)
    if not os.stat(filepath).st_size:
        # No reason to open empty files
        last = b''
    else:
        with io.open(str(filepath), "rb") as fd:
            fd.readline()      # Read the first line.
            fd.seek(-2, 2)              # Jump to the second last byte.
            while fd.read(1) != b"\n":  # Until EOL is found...
                try:
                    fd.seek(-2, 1)      # ...jump back the read byte plus one more.
                except IOError:
                    # the file has just a single line!
                    fd.seek(0)
                    break
            last = fd.readline()        # Read last line.
    return last.decode('utf-8')


@contextmanager
def inplace(filename, mode='r', buffering=-1, encoding=None, errors=None,
            newline=None, backup_extension=None):
    """Allow for a file to be replaced with new content.

    yields a tuple of (readable, writable) file objects, where writable
    replaces readable.

    If an exception occurs, the old file is restored, removing the
    written data.

    mode should *not* use 'w', 'a' or '+'; only read-only-modes are supported.

    http://www.zopatista.com/python/2013/11/26/inplace-file-rewriting/

    """

    # move existing file to backup, create new file with same permissions
    # borrowed extensively from the fileinput module
    if set(mode).intersection('wa+'):
        raise ValueError('Only read-only file modes can be used')

    filename = str(filename)
    backupfilename = str(filename + (backup_extension or os.extsep + 'bak'))
    try:
        os.unlink(backupfilename)
    except os.error:
        pass
    os.rename(filename, backupfilename)
    readable = io.open(backupfilename, mode, buffering=buffering,
                       encoding=encoding, errors=errors, newline=newline)
    try:
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        writable = io.open(filename, 'w' + mode.replace('r', ''), buffering=buffering,
                           encoding=encoding, errors=errors, newline=newline)
    else:
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if hasattr(os, 'O_BINARY'):
            os_mode |= os.O_BINARY
        fd = os.open(filename, os_mode, perm)
        writable = io.open(fd, "w" + mode.replace('r', ''), buffering=buffering,
                           encoding=encoding, errors=errors, newline=newline)
        try:
            if hasattr(os, 'chmod'):
                os.chmod(filename, perm)
        except OSError:
            pass
    try:
        yield readable, writable
    except Exception:
        try:
            os.unlink(filename)
        except os.error:
            pass
        finally:
            os.rename(backupfilename, filename)
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backupfilename)
        except os.error:
            pass


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
    added_text = args.added_text + "\n"
    prepend = args.prepend
    pattern = re.compile(args.pattern)
    found = False
    last_line = get_last_line(filepath)
    with inplace(filepath, "r") as (infile, outfile):
        for line in infile:
            if pattern.search(line):
                # line = line.encode("utf-8")
                found = True
                if not prepend and line == last_line:
                    added_text = "\n" + args.added_text
                lines = [added_text, line] if prepend else [line, added_text]
                outfile.writelines(lines)
            else:
                outfile.write(line)
    if not found:
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
        original_lines = [line.strip() for line in fd.readlines()]
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


def main(args):
    run = DISPATCHER[args.mode]
    if args.single:
        filepaths = [str(args.single)]
    else:
        filepaths = search_for_files(args)
    for filepath in filepaths:
        run(args, filepath)


def add_common_args_to_cli_subcommand(parser):
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
