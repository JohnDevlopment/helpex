"""
Show the help message of a command.

Information about the command is taken from
~/.local/etc/helpex/x.json, where x is the name of a JSON file.
"""

from __future__ import annotations
from glob import glob
from json.decoder import JSONDecodeError
from pathlib import Path
from textwrap import TextWrapper
from typing import Any, NoReturn
import json, shutil, sys

class CommandDocumentation:
    INDENT = "    "
    RIGHT_MARGIN = 10

    def __init__(self, data: dict[str, Any]):
        self.sigature: str = data['signature']
        self.name: str = data['name']
        self.description: str = self._parse_description(data['description'])
        self.exit_status: str | None = data.get('exit status', None)
        self.wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN,
            self.INDENT, self.INDENT)

    @property
    def terminal_width(self) -> int:
        term_size = shutil.get_terminal_size((87, 90))
        return term_size.columns

    def _parse_description(self, paras: list[str | list[str]] | str) -> str:
        if isinstance(paras, list):
            INDENT = self.INDENT
            description = []
            paragraph = ""

            # Wrap paragraphs
            list_wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN, INDENT)
            wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN, INDENT, INDENT)
            for para in paras:
                if isinstance(para, list):
                    # Is a list of strings (denotes a list in the final string)
                    items = para

                    # Formate each list item as its own paragraph
                    new_items: list[str] = []
                    for item in items:
                        # Prepend a bullet to each item
                        item = "%s %s" % ("\u2022", item)

                        # Calculate
                        length = item.find("-") + 2
                        list_wrapper.subsequent_indent = " " * length + self.INDENT
                        new_items.append("".join(list_wrapper.fill(item)))

                    paragraph = "\n".join(new_items)
                else:
                    paragraph = "".join(wrapper.fill(para))

                description.append(paragraph)

            return "\n\n".join(description)
        else:
            # Is str
            return paras

    def __str__(self) -> str:
        exit_status = self.exit_status or ""
        if exit_status:
            exit_status = "".join(self.wrapper.fill(exit_status))
            exit_status = f"\n\n{self.INDENT}Exit Status:\n{exit_status}"

        return f"{self.name}: {self.sigature}\n{self.description}{exit_status}"

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
    main()
