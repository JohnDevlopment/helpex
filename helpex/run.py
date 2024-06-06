"""
Show the help message of a command.

Information about the command is taken from
~/.local/etc/helpex/x.json, where x is the name of a JSON file.
"""

from __future__ import annotations

from . import APPNAME
from .command_doc import CommandDocumentation
from .utils import get_env
from glob import glob
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING
import json, logging, shutil, subprocess

from platformdirs import user_data_path

if TYPE_CHECKING:
    from typing import Any, NoReturn

def die(msg: str, *args: Any, code: int=1) -> NoReturn:
    logger = logging.getLogger(APPNAME)
    logger.error(msg, *args)
    exit(code)

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser("helpex", description=__doc__)
    parser.add_argument("-e", "--edit", action="store_true")
    parser.add_argument("COMMAND", nargs="?")
    return parser.parse_args()

def _edit(fp: Path) -> int:
    logger = logging.getLogger(APPNAME)
    editor = get_env("EDITOR")
    if editor is None:
        logger.warn("EDITOR is not set in the environment.")
        print(fp)
        return 0

    editor_path = shutil.which(editor)
    if editor_path is None:
        logger.warn("'%s' does not exist in PATH.", editor)
        print(fp)
        return 0

    logger.debug("Using %s (path: '%s') to edit '%s'.",
                 editor, editor_path, fp)

    # Run $EDITOR on the file
    cp = subprocess.run([editor_path, str(fp)], capture_output=True, text=True)
    if cp.returncode:
        # There is an error, so die
        die(cp.stderr, code=cp.returncode)

    return 0

def main() -> int:
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
        return 0

    fp = DATADIR / f"{cmd}.json"

    if args.edit:
        return _edit(fp)

    try:
        # Open command help file
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

    return 0

if __name__ == '__main__':
    raise NotImplementedError
