"""Custom logger definition."""

import logging
import sys
import typing as t

LOG_FORMAT: str = (
    "%(asctime)s - %(name)s [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
)

logger: logging.Logger = logging.getLogger("instana-wrapper")
logger.setLevel(logging.DEBUG)

console_handler: logging.StreamHandler[t.Any] = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

logger.addHandler(console_handler)
