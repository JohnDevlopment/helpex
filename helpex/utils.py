from __future__ import annotations
from os import getenv

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Optional

get_env = getenv

__all__ = [
    "get_env"
]
