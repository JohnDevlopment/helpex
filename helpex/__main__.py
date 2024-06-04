"""
Show the help message of a command.

Information about the command is taken from
~/.local/etc/helpex/x.json, where x is the name of a JSON file.
"""

from __future__ import annotations
from .run import main

if __name__ == '__main__':
    exit(main())
