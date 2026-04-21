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
initiates four downloads of `A71EV2A` from the staging stack, writing it to
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

>   The number of concurrent downloads might be limited because of your client's
    processing capability - if you're on a 4 core machine do not expect the best
    performance when trying to download 12 concurrent copies of a given target.

## Continuous stress tests
A script that calls the main application repeatedly can be found in
`keep-downloading.sh`. This downloads 8 copies the default target
(from the production stack), starting each new download on the next 20-minute
boundary (i.e. at 00, 20 or 40 past the hour).

To continually run the stress tests (from an Amazon Linux machine) you might have to
install `python` and `pip`. The following commands should be sufficient to get stuff
ready to run a stress-test...

    sudo yum update -y
    sudo yum install git python python-pip -y
    git clone https://github.com/xchem/fragalysis-stack-stress-tests
    cd fragalysis-stack-stress-tests
    pip install uv
    uv sync

Then, you can continually run the default test and test production
(downloading 16 copies concurrently)...

    export TTY_INTERACTIVE=0
    nohup ./keep-downloading.sh 16 &

Or you can test the staging installation: -

    export TTY_INTERACTIVE=0
    nohup ./keep-downloading.sh 16 staging &

And watch the output with: -

    tail -f keep-downloading.log

>   You will need to make sure your local volume has sufficient space to accommodate
    all the downloads you plan to generate. A single copy of the default (`A71EV2A`)
    will consume about **3.8G** of disk space on the client.

---

[rich]: https://pypi.org/project/rich/
[uv]: https://docs.astral.sh/uv/
