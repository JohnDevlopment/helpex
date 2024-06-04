"""
Show the help message of a command.

Information about the command is taken from
~/.local/etc/helpex/x.json, where x is the name of a JSON file.
"""

from __future__ import annotations

from . import APPNAME
from .command_doc import CommandDocumentation
from glob import glob
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING
import json, logging

from platformdirs import user_data_path
from icecream import ic

if TYPE_CHECKING:
    from typing import Any, NoReturn

def die(msg: str, *args: Any, code: int=1) -> NoReturn:
    logger = logging.getLogger(APPNAME)
    logger.error(msg, *args)
    exit(code)

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser("helpex", description=__doc__)
    parser.add_argument("COMMAND", nargs="?")
    return parser.parse_args()

def main():
    args = parse_arguments()
    cmd: str | None = args.COMMAND

    logger = logging.getLogger(APPNAME)

    # Data directory
    DATADIR = user_data_path("helpex")
    if not DATADIR.exists():
        DATADIR.mkdir()
        logger.info("Created '%s'.", DATADIR)
    logger.debug("Data directory set to '%s'.", DATADIR)

    # List commands
    if cmd is None:
        print("Commands:")
        for file in sorted(map(Path, glob(f"{DATADIR}/*.json"))):
            print(f"    {file.stem}")
        return

    fp = DATADIR / f"{cmd}.json"
    try:
        with open(fp, 'rt') as fd:
            # Get documentation
            data = json.load(fd)
            doc = CommandDocumentation(data)
    except FileNotFoundError:
        die(f"helpex: Unknown command: '{cmd}'")
    except KeyError as exc:
        die(f"helpex internal: Invalid help specification for command '{cmd}'. Missing key: {exc}.")
    except JSONDecodeError as exc:
        die(f"helpex: Unable to decode '{fp}': {exc}")

    print(doc)

if __name__ == '__main__':
    raise NotImplementedError
