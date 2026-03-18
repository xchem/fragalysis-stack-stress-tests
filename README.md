# Fragalysis stack stress testing
Python utilities to stress-test a Fragalysis Stack.

The repository code is managed by [uv].

The current tests relate to parallel download testing: -

    uv run main.py --help

Then, maybe, run something like the following, which (at the time of writing)
initiates a download of A71EV2A from the staging stack, writing it to
/tmp/xchem-stress/01/A71EV2A.tar.gz: -

    uv run main.py lb32627-66

---

[uv]: https://docs.astral.sh/uv/
