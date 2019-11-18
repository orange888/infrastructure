from logging import getLogger

from .logging import handler

logger = getLogger(__name__)
logger.addHandler(handler)
