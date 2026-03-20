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
initiates a download of `A71EV2A` from the staging stack, writing it to
`/tmp/xchem-stress/01/A71EV2A.tar.gz`: -

    uv run main.py

You can display progressive download status information by adding `--verbose` and
even debug the underlying requests (which use the urllib3 module) with `--debug`: -

    uv run main.py --verbose --debug

---

[uv]: https://docs.astral.sh/uv/
