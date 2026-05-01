#!/usr/bin/env python

import asyncio
import datetime
import json
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
    ] = "./tmp",
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
    print(
        f"{now.strftime('%Y-%m-%d %H:%M')} Starting download (concurrency={concurrency} stack={stack})..."
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
                # Include all the "big" stuff...
                "soakdb_files": True,
                "unaligned_pdbs": True,
                "ligand_cifs": True,
                "event_maps": True,
                "inspection_maps": True,
                "residual_maps": True,
                "real_space_maps": True,
                "transformation_files": True,
                "reflections_files": True,
                # Don't extract the download
                "extract": False,
                # Download destination
                "destination": destination,
                # Verbose? And the iteration number (for logging)
                "debug": verbose,
                "iteration": iteration,
                # Request debugging?
                "debug_requests": debug,
            },
        )
        process.start()
        processes.append(process)

    # Wait until all downloads are done...
    for p in processes:
        p.join()

    now = datetime.datetime.now()
    elapsed_s: int = int(time.time() - start_time_s)
    print(f"{now.strftime('%Y-%m-%d %H:%M')} Elapsed(S): {elapsed_s}")


async def _run_one_runner(
    runner: int, http_bin: str, host: str, calls: list[dict]
) -> None:
    for call in calls:
        method: str = call["method"]
        path: str = call["path"]
        har_index: int = call["harIndex"]
        query_params: dict = call.get("queryParams") or {}

        url: str = f"https://{host}{path}"
        args: list[str] = [
            http_bin,
            "--ignore-stdin",
            "--check-status",
            "--timeout=300",
            method,
            url,
            *(f"{k}=={v}" for k, v in query_params.items()),
        ]

        start: float = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr_bytes = await proc.communicate()
        rc: int = proc.returncode or 0
        elapsed_ms: float = (time.perf_counter() - start) * 1000

        if rc == 0:
            suffix: str = ""
        else:
            reason: str = (
                stderr_bytes.decode(errors="replace").strip().replace("\n", " | ")
            )
            if len(reason) > 200:
                reason = reason[:197] + "..."
            suffix = f" FAIL rc={rc} {reason}" if reason else f" FAIL rc={rc}"
        print(
            f"[{runner}] harIndex={har_index} {method} {path}"
            f" ({elapsed_ms:.0f}ms){suffix}"
        )


async def _run_sequences(concurrency: int, host: str, file: str) -> None:
    http_bin: str | None = shutil.which("http")
    if http_bin is None:
        typer.echo(
            "The 'http' (httpie) binary was not found on PATH. "
            "Run 'uv sync' to install it.",
            err=True,
        )
        raise typer.Exit(code=1)

    with open(file) as f:
        data = json.load(f)
    calls: list[dict] = data["calls"]

    await asyncio.gather(
        *(_run_one_runner(i + 1, http_bin, host, calls) for i in range(concurrency))
    )


@app.command()
def sequence(
    concurrency: Annotated[
        int, typer.Argument(help="Number of concurrent sequences")
    ] = 1,
    host: Annotated[
        str, typer.Argument(help="The Fragalysis host to call")
    ] = "fragalysis.xchem.diamond.ac.uk",
    file: Annotated[
        str, typer.Argument(help="Path to a JSON file describing the call sequence")
    ] = "test-data/api-sequence.json",
) -> None:
    """Replay an API call sequence stress testing

    Reads a JSON file containing a list of 'calls' (each with harIndex,
    method, path, queryParams) and replays them against the given host
    using httpie. With concurrency > 1, that number of full sequences
    runs in parallel; calls within a single sequence run serially."""

    now: datetime.datetime = datetime.datetime.now()
    print(
        f"{now.strftime('%Y-%m-%d %H:%M')} Starting sequence"
        f" (concurrency={concurrency} host={host} file={file})..."
    )

    start_time_s: float = time.time()
    asyncio.run(_run_sequences(concurrency, host, file))

    now = datetime.datetime.now()
    elapsed_s: int = int(time.time() - start_time_s)
    print(f"{now.strftime('%Y-%m-%d %H:%M')} Elapsed(S): {elapsed_s}")


if __name__ == "__main__":
    app()
