from datetime import datetime
from logging import Formatter as BaseFormatter
from logging import LogRecord, StreamHandler
from re import compile
from sys import stderr
from time import strftime

PACKAGE_REGEXP = compile(r"^hannah_family\.infrastructure\.")
LOG_FMT = "{asctime} [{name}:{funcName}:{lineno}/{levelname}] {message}"


class Formatter(BaseFormatter):
    def formatTime(self, record: LogRecord, datefmt=None):
        if datefmt:
            ct = self.converter(record.created)
            return strftime(datefmt, ct)

        dt = datetime.fromtimestamp(record.created)
        return dt.isoformat(timespec="microseconds")

    def format(self, record):
        record.name = PACKAGE_REGEXP.sub("", record.name, count=1)
        return super().format(record)


formatter = Formatter(fmt=LOG_FMT, style="{")

handler = StreamHandler(stream=stderr)
handler.setFormatter(formatter)
