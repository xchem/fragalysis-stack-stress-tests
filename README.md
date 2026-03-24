# Fragalysis stack stress testing

[![Test](https://github.com/xchem/fragalysis-stack-stress-tests/actions/workflows/test.yaml/badge.svg)](https://github.com/xchem/fragalysis-stack-stress-tests/actions/workflows/test.yaml)

Python utilities to stress-test a Fragalysis Stack.

The repository code is managed by [uv]. Once you've cloned the repository,
if you don't have [uv], install it into your system Python: -

    pip install uv

If you are intending to contribute to the code, you will need to install
the pre-commit hooks and verify they run successfully against the current code.
Even if you're not intending to contribute to the code installing the hooks is a good
idea anyway: -

    uv run pre-commit install -t commit-msg -t pre-commit
    uv run pre-commit run --all-files

The current tests relate to parallel download testing, but run `--help` to
see what can be done: -

    uv run main.py --help

Then, maybe, run something like the following, which (at the time of writing)
initiates a four downloads of `A71EV2A` from the staging stack, writing it to
`/tmp/xchem-stress/01/A71EV2A.tar.gz`: -

    uv run main.py 4

You can display progressive download status information by adding `--verbose` and
even debug the underlying requests (which use the urllib3 module) with `--debug`: -

    uv run main.py 4 --verbose --debug

## Controlling the 'fancy stuff'
Some of the underlying logic (in fragalysis) uses the [rich] library for rich text
and formatting in the terminal. The output of some of the stress-tests can look
confusing when it's logging is interleaved with rich.

To disable _pretty_ things like progress reporting you can set `TTY_INTERACTIVE=0`
when running a test, e.g.: -

    TTY_INTERACTIVE=0 uv run main.py 4 --verbose

---

[rich]: https://pypi.org/project/rich/
[uv]: https://docs.astral.sh/uv/
