# Python search and replace.

The `sr.py` script is practically a pure python equivalent to:

```
ag <regex> -l <search_args> | xargs sed -i 's/<regex>/<replace>/g'
```

## Requirements

You need python 2.7+ and a search program like [`ag`](https://github.com/ggreer/the_silver_searcher).

## Rationale

There are two main reasons that made me write this:

* `sed` regex engine is quite limited. E.g. there is no support for look-aheads and other more
advanced features.

* The API for combining `ag`, `sed` and `xargs` is clunky at best.

## Performance

This is not written with performance in mind, but since the searching it leverages

## Usage

### Search for files matching pattern and replace all matches.

```
python3 sr.py multi 'search_pattern' 'replace' -s -l --hidden
```

### Search for pattern on a single file and replace it with pattern.

```
python3 sr.py single 'search_pattern' 'replace' /path/to/file
```
