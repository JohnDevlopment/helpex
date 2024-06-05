from __future__ import annotations
from . import APPNAME
from textwrap import TextWrapper
from typing import TYPE_CHECKING, cast
import logging, shutil

_Logger = logging.getLogger(APPNAME)

if TYPE_CHECKING:
    from typing import Any

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

    def _parse_special_obj(self, data: dict[str, str]) -> str | None:
        match data:
            case {'type': "list", 'heading': heading, 'items': items}:
                assert isinstance(items, list)
                items = cast(list[str], items)
                return self._parse_list_obj(heading, items)

            case _:
                _Logger.warn("Unknown object: %r", data)

    def _parse_description(self, paras: list[str | list[str] | dict[str, Any]]) -> str:
        if isinstance(paras, list):
            INDENT = self.INDENT
            description: list[str] = []
            paragraph: str = ""

            # Wrap paragraphs
            list_wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN, INDENT)
            # wrapper = TextWrapper(self.terminal_width - self.RIGHT_MARGIN, INDENT, INDENT)
            wrapper = self.wrapper
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
                elif isinstance(para, dict):
                    temp = self._parse_special_obj(para)
                    if temp is None:
                        continue
                    paragraph = temp
                else:
                    paragraph = "".join(wrapper.fill(para))

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
