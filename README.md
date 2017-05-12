# Python Find and Replace.

[![Build Status](https://travis-ci.org/pmav99/fxr.svg?branch=master)](https://travis-ci.org/pmav99/fxr)

The `fxr` script is practically a pure python equivalent to:

```
ag <pattern> -l <search_args> | xargs sed -i 's/<pattern>/<replacement>/g'
```

## Rationale

There are two main reasons that made me write this:

* `sed` regex engine is quite limited. E.g. there is no support for look-aheads and other more
   advanced features
   ([link](https://www.gnu.org/software/sed/manual/html_node/Regular-Expressions.html)).

* The API for combining `ag`, `sed` and `xargs` is clunky at best (e.g. repeating `<pattern>` etc).

## Requirements

You need Python `2.7+/3.3+` and a search program like
[`ag`](https://github.com/ggreer/the_silver_searcher).  If you wish to use a different program that
`ag` you can do so by using the appropriate `CLI` argument.

## Usage

### Search for files matching pattern and replace all matches.

```
./fxr multi 'pattern' 'replacement' -s -l --hidden
```

### Search for pattern on a single file and replace it with pattern.

```
./fxr single 'pattern' 'replacement' /path/to/file
```

### Strings containing both single and double quotes:

Some care is being required. You will probably want to enclose the string into `'` and then escape
`'` in the string. E.g.

```
'Multiple '\''single quoted\'\\ and "double quoted" phrase.'
```

### Literal matches

Some care is needed when you use `--literal` since e.g. newlines etc might be messed up by your shell:

```
python fxr single --literal $'Multiple lines will\nbe converted to single lines\n' $'Only single lines here\n' sample.txt
```


## Performance

This is not written with performance in mind, but since the search for matching files is being done
with `ag`, performance shouldn't be bad.

