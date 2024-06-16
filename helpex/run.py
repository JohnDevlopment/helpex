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
import json, logging, shlex, shutil, subprocess

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

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--edit", action="store_true",
                       help="edit COMMAND's source file with either $VISUAL or $EDITOR")
    group.add_argument('-p', '--path', action="store_true",
                        help="print the path to COMMAND's source file")

    parser.add_argument("COMMAND", nargs="?")
    return parser.parse_args()

def _edit(fp: Path) -> int:
    logger = logging.getLogger(APPNAME)

    # Get either $VISUAL or $EDITOR
    editor = get_env("VISUAL")
    if editor is None:
        logger.error("VISUAL is not set in the environment")
        return 0

    # Looks for the absolute path to editor in $PATH
    editor_path = shutil.which(editor)
    if editor_path is None:
        logger.error("'%s' does not exist in PATH.", editor)
        return 0

    logger.debug("Using %s (path: '%s') to edit '%s'.",
                 editor, editor_path, fp)

    # $VISUAL_ARGS arg the arguments to $VISUAL, as the name would imply
    editor_args = get_env("VISUAL_ARGS") or ""
    editor_args = shlex.split(editor_args)

    # Run $VISUAL on the file
    cmd = [editor_path, *editor_args, str(fp)]
    logger.debug("Command: $ %s", shlex.join(cmd))
    cp = subprocess.run(cmd, text=True)
    if cp.returncode:
        # There is an error, so die
        die(f"{editor} returned error", code=cp.returncode)

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
    elif args.path:
        print(fp)
        return 0

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
