#!/usr/bin/env python

import datetime
from multiprocessing import Process
import os
import shutil
import time
from typing import Annotated

from fragalysis.requests.download import download_target
import typer

app = typer.Typer()

@app.command()
def download(
    tas: Annotated[str, typer.Argument(help="A Target Access String")],
    concurrency: Annotated[int, typer.Argument(help="Number of concurrent processes")] = 1,
    target: Annotated[str, typer.Argument(help="The name of the user to greet")] = "A71EV2A",
    stack: Annotated[str, typer.Argument(help="An optional stack identity")] = "staging",
    download_root: Annotated[str, typer.Argument(help="The root download directory")] = "/tmp/xchem-stress",
) -> None:
    """Download target stress testing

    A stress-test for the download_target function.
    You define the concurrency, and each download
    is written to a separate sub-directory of the
    designated download root with the value of the
    concurrency number (i.e. 01, 02, 03)"""

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
            kwargs={"destination": destination, "debug": True},
        )
        process.start()
        processes.append(process)

    # Wait for each process
    for p in processes:
        p.join()

    now: datetime.datetime = datetime.datetime.now()
    elapsed_s: int = int(time.time() - start_time_s)
    print(f"{now.strftime('%Y-%m-%d %H:%M')} Elapsed(S): {elapsed_s}")

if __name__ == "__main__":
    app()
