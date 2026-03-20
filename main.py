#!/usr/bin/env python

import datetime
from multiprocessing import Process
import os
import shutil
import time
from typing import Annotated

from fragalysis.requests.download import download_target
import typer

CONCURRENT_TASK_START_DELAY_S: int = 4

app: typer.Typer = typer.Typer()


@app.command()
def download(
    concurrency: Annotated[
        int, typer.Argument(help="Number of concurrent processes")
    ] = 1,
    tas: Annotated[str, typer.Argument(help="A Target Access String")] = "lb32627-66",
    target: Annotated[str, typer.Argument(help="The name of the Target")] = "A71EV2A",
    stack: Annotated[
        str,
        typer.Argument(
            help="An optional built-in stack identity ('staging' or 'production') or a URL"
        ),
    ] = "staging",
    download_root: Annotated[
        str, typer.Argument(help="The root download directory")
    ] = "/tmp/xchem-stress",
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Debug underlying HTTP requests. This can generate a lot of output",
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Add additional download log")
    ] = False,
) -> None:
    """Download target stress testing

    A stress-test for the download_target function.
    You define the concurrency, and each download
    is written to a separate sub-directory of the
    designated download root with the value of the
    concurrency number (i.e. 01, 02, 03)"""

    now: datetime.datetime = datetime.datetime.now()
    if verbose:
        print(
            f"{now.strftime('%Y-%m-%d %H:%M')} Starting download (concurrency={concurrency})..."
        )

    # Run each download (to a separate local destination)
    # as a concurrent set of (parallel) processes.

    start_time_s: float = time.time()
    processes: list[Process] = []

    for c in range(concurrency):
        iteration: int = c + 1

        # We need to wipe (and recreate) each target download directory
        destination: str = f"{download_root}/{iteration:02d}"
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        os.makedirs(destination)

        # Create a Process, start it,
        # and add it to a list of running processes
        process = Process(
            target=download_target,
            args=(target, tas, stack),
            kwargs={
                "destination": destination,
                "debug": verbose,
                "iteration": iteration,
                "debug_requests": debug,
            },
        )
        process.start()
        processes.append(process)

    # Wait until all downloads are done...
    for p in processes:
        p.join()

    if verbose:
        now = datetime.datetime.now()
        elapsed_s: int = int(time.time() - start_time_s)
        print(f"{now.strftime('%Y-%m-%d %H:%M')} Elapsed(S): {elapsed_s}")


if __name__ == "__main__":
    app()
