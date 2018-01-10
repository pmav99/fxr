# fxr

[![Travis](https://travis-ci.org/pmav99/fxr.svg?branch=master)](https://travis-ci.org/pmav99/fxr)
[![coveralls](https://coveralls.io/repos/pmav99/fxr/badge.svg?branch=master&service=github)](https://coveralls.io/r/pmav99/fxr)

`fxr` (pronounced "fixer") is a CLI utility that can be used to find matching patterns in text files
and:

* append/prepend lines
* delete lines before/after the matching line.
* replace text

In other words, you can consider it as a replacement for `ag`, `xargs` and `sed` (with a nicer API!)

**Warning**: *`fxr` currently has no dry-run mode and by default changes files inplace. If you want
backups, you need to explicitly enable them!

## Installation

All you need is Python `2.7+/3.3+` and a search program like
[`ag`](https://github.com/ggreer/the_silver_searcher):

```
pip install -U fxr
pip install --user -U fxr           # this will install fxr on ~/.local/
```

The latest version is `0.2.5`:

## Modes of operation

`fxr` has three modes of operations:

* `fxr add`
* `fxr delete`
* `fxr replace`

### `fxr add`

In this mode you search for lines matching `<pattern>` and you append/prepend text to them.

```
fxr add <pattern> <added_text>              # Appends text to lines matching pattern
fxr add --prepend <pattern> <added_text>    # Prepends text to lines matching pattern
```

### `fxr delete`

In this mode you search for lines matching `<pattern>` and you can:

1. delete N lines preceding the matching line
2. delete M lines following the matching line
3. delete the matching line itself
4. or any combination of the above!

E.g. to delete 3 lines before the line matching pattern, 2 lines after it and the matching line
itself:

```
fxr delete --before 3 --after 2 --include_line <pattern>
```

### `fxr replace`

In this mode you can replace text on a single line. This is more or less equivalent to:

```
ag <pattern> -l | xargs sed -i 's/<pattern>/<replacement>/g'
```

You can use it like this:

```
fxr replace <pattern> <replacement>
```

## Common interface

All the above subcommands share the following flags/arguments:

* `--backup`: The provided value is used as a prefix for the backup files. If it is not provided,
  the changes are being done in-place.
* `--literal`: When you set this flag, the pattern will not be parsed as a regex.
* `--raise-if-no-change`: When you set this flag, an exception will be raised if there were no
  changes in the file.
* `--single <filename>`: When you specify this argument, fxr will only try to do its magic on the
  specified file. I.e. `ag` will not be used.
* `--search_prog`: If you don't like `ag` you can specify  an alternate program (e.g. `rg`).
* `--search_args`: You can specify additional arguments for the search program.

## Notes

### Rationale

There were two compelling arguments that made me write this:

1. `sed` regex engine is quite limited. E.g. there is no support for look-aheads and other more
   advanced features, which you don't really need, until you need them!
   ([link](https://www.gnu.org/software/sed/manual/html_node/Regular-Expressions.html)).

2. The API for combining `ag`, `sed` and `xargs` is clunky at best (e.g. repeating `<pattern>` both
   in `ag` and `sed` etc). E.g.:
   `ag <pattern> -l | xargs sed -i 's/<pattern>/<replacement>/g'`


### Performance

The script has not been written with performance in mind.  Since the search for matching files is
being done using `ag`, performance shouldn't be too bad, but keep in mind that the main use case
is to make changes to source code and configuration files; not a multi-GB CSV file/database dump.

### Search programs

If you wish to use a different program than `ag` you can do so by using the appropriate `CLI` argument.

