from __future__ import annotations

import logging

LOGGER_NAME = "nudb_config"

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.NullHandler())
