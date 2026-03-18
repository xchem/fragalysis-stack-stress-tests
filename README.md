# Fragalysis stack stress testing

[![Test](https://github.com/xchem/fragalysis-stack-stress-tests/actions/workflows/test.yaml/badge.svg)](https://github.com/xchem/fragalysis-stack-stress-tests/actions/workflows/test.yaml)

Python utilities to stress-test a Fragalysis Stack.

The repository code is managed by [uv].

Before you start, if you are intending to contribute to the code,
you will need to install the pre-commit hooks and verify they run successfully
against the current code: -

    uv run pre-commit install -t commit-msg -t pre-commit
    uv run pre-commit run --all-files

The current tests relate to parallel download testing, but run `--help` to
see what can be done: -

    uv run main.py --help

Then, maybe, run something like the following, which (at the time of writing)
initiates a download of `A71EV2A` from the staging stack, writing it to
`/tmp/xchem-stress/01/A71EV2A.tar.gz`: -

    uv run main.py

---

[uv]: https://docs.astral.sh/uv/
