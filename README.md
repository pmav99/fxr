# Python search and replace.

[![Build Status](https://travis-ci.org/pmav99/search-and-replace.svg?branch=master)](https://travis-ci.org/pmav99/search-and-replace)

The `sr.py` script is practically a pure python equivalent to:

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
./sr.py multi 'pattern' 'replacement' -s -l --hidden
```

### Search for pattern on a single file and replace it with pattern.

```
./sr.py single 'pattern' 'replacement' /path/to/file
```

### Literal matches

Some care is needed when you use `--literal` since newlines etc might be messed up by your shell:

```
python sr.py single --literal $'Multiple lines will\nbe converted to single lines\n' $'Only single lines here\n' sample.txt
```


## Performance

This is not written with performance in mind, but since the search for matching files is being done
with `ag`, performance shouldn't be bad.

