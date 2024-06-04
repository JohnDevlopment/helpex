"""
Show the help message of a command.

Information about the command is taken from
~/.local/etc/helpex/x.json, where x is the name of a JSON file.
"""

from __future__ import annotations

from .command_doc import CommandDocumentation
from glob import glob
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING
import json, sys

if TYPE_CHECKING:
    from typing import Any, NoReturn

def die(msg: str, code: int=1) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(code)

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser("helpex", description=__doc__)
    parser.add_argument("COMMAND", nargs="?")
    return parser.parse_args()

def main():
    args = parse_arguments()
    cmd: str | None = args.COMMAND

    # List commands
    if cmd is None:
        pth = Path("~/.local/etc/helpex").expanduser()
        print("Commands:")
        for file in sorted(map(Path, glob(f"{pth}/*.json"))):
            print(f"    {file.stem}")
        return

    fp = Path("~/.local/etc/helpex").expanduser() / f"{cmd}.json"
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
