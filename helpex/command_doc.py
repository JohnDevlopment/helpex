from __future__ import annotations
from io import StringIO
from . import APPNAME
from textwrap import TextWrapper
from typing import TYPE_CHECKING, cast
import logging, shutil

_Logger = logging.getLogger(APPNAME)

if TYPE_CHECKING:
    from typing import Any, Iterable

class CommandDocumentation:
    INDENT = "    "
    RIGHT_MARGIN = 10

    def __init__(self, data: dict[str, Any]):
        self.wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN,
            self.INDENT, self.INDENT)
        self.list_wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN,
            self.INDENT, f"{self.INDENT}  ")
        self.sigature: str = data['signature']
        self.name: str = data['name']
        self.exit_status: str | None = data.get('exit status', None)
        self.description: str = self._parse_description(data['description'])

    # Utility functions

    def _fill_text(self, text: str) -> str:
        wrapper = self.wrapper
        return "".join(wrapper.fill(text))

    def _indent_text(self, text: str) -> str:
        from io import StringIO
        indent = self.wrapper.subsequent_indent
        ofs = StringIO()

        with StringIO(text) as ifs:
            print(ifs.readline(), file=ofs)
            for line in ifs:
                print(f"{indent}{line}", file=ofs)
        ofs.seek(0)
        return ofs.read()

    ###

    @property
    def terminal_width(self) -> int:
        term_size = shutil.get_terminal_size((87, 90))
        return term_size.columns

    def _parse_list_obj(self, heading: str, items: list[str]) -> str:
        result: list[str] = [f"{self.INDENT}{heading}"]
        list_wrapper = self.list_wrapper

        for item in items:
            item = "%s %s" % ("\u2022", item)
            paragraph = "".join(list_wrapper.fill(item))
            result.append(paragraph)

        return "\n".join(result)

    def _parse_options_obj(self, items: Iterable[list[str]]) -> str:
        PADDING = 2
        ofs = StringIO("Options:")

        def _first_column_length(item: Iterable[str]):
            result = 0
            match item:
                case [fc, sc]:
                    result = max(len(fc), result)

                case v:
                    _Logger.error("Invalid option item '%s'", v)
            return result

        first_column_length = max(map(_first_column_length, items))

        print(f"{self.INDENT}Options:", file=ofs)
        for item in items:
            kw = {
                'indent': f"{self.INDENT}  ",
                'fc': item[0],
                'description': item[1],
            }
            fmt = "{indent}{fc:%d}{description}" % (first_column_length + PADDING)
            print(fmt.format(**kw), file=ofs)

        ofs.seek(0)

        return ofs.read().rstrip()

    def _parse_special_obj(self, data: dict[str, str]) -> str | None:
        match data:
            case {'type': "list", 'heading': heading, 'items': items}:
                assert isinstance(items, list)
                items = cast(list[str], items)
                return self._parse_list_obj(heading, items)

            case {'type': "options", 'items': items}:
                assert isinstance(items, list)
                items = cast(list[list[str]], items)
                return self._parse_options_obj(items)

            case _:
                _Logger.warn("Unknown object: %r", data)

    def _parse_description(self, paras: list[str | dict[str, Any]]) -> str:
        if isinstance(paras, list):
            description: list[str] = []
            paragraph: str = ""

            # Wrap paragraphs
            for para in paras:
                if isinstance(para, dict):
                    # Para is a dict, so parse it as a "special object"
                    temp = self._parse_special_obj(para)
                    if temp is None:
                        continue
                    paragraph = temp
                elif isinstance(para, str):
                    # Is a string, treat as another paragraph
                    paragraph = self._fill_text(para)

                # Add "paragraph" to the list
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
