from __future__ import annotations
from pathlib import Path
from logging import getLogger
import logging.config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any

from platformdirs import user_log_path
import yaml

APPNAME = "helpex"

def setup_logging():
    LOGPATH = user_log_path("helpex")
    LOGPATH.mkdir(parents=True, exist_ok=True)

    fp = Path(__file__).parent / "logging.yaml"

    with open(fp, 'rt') as fd:
        LOGGING_CONFIG: dict[str, Any] = yaml.safe_load(fd)

        match LOGGING_CONFIG:
            case {'handlers': {'file': keys}}:
                assert isinstance(keys, dict)
                filename: str = keys['filename']
                keys['filename'] = filename.replace("$LOGDIR", str(LOGPATH))

        logging.config.dictConfig(LOGGING_CONFIG)

    logger = getLogger(APPNAME)
    logger.info("Logging initialized.")
    logger.debug("Log path set to '%s'", LOGPATH)

setup_logging()
