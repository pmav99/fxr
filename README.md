# Python search and replace.

The `sr.py` script is practically a pure python equivalent to:

```
ag <regex> -l <search_args> | xargs sed -i 's/<regex>/<replace>/g'
```

## Rationale

There are two main reasons that made me write this:

* `sed` regex engine is quite limited. E.g. there is no support for look-aheads and other more
advanced features.

* The API for combining `ag`, `sed` and `xargs` is clunky at best.

## Requirements

You need python 2.7+ and a search program like [`ag`](https://github.com/ggreer/the_silver_searcher).
If you wish to use a different program that `ag` you can do so by using the appropriate `CLI`
argument.

## Usage

### Search for files matching pattern and replace all matches.

```
python3 sr.py multi 'search_pattern' 'replace' -s -l --hidden
```

### Search for pattern on a single file and replace it with pattern.

```
python3 sr.py single 'search_pattern' 'replace' /path/to/file
```

## Performance

This is not written with performance in mind, but since the search for matching files is being done
with `ag`, performance shouldn't be bad.

