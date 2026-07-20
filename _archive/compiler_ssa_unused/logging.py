"""Logging - 统一日志格式"""

import os
from enum import Enum


class LogLevel(Enum):
    NORMAL = 0
    VERBOSE = 1
    DEBUG = 2


# 全局日志级别
_current_level = LogLevel.NORMAL


def set_level(level: LogLevel):
    global _current_level
    _current_level = level


def get_level() -> LogLevel:
    return _current_level


def should_log(level: LogLevel) -> bool:
    return level.value <= _current_level.value


def normal(msg: str):
    if should_log(LogLevel.NORMAL):
        print(msg)


def verbose(msg: str):
    if should_log(LogLevel.VERBOSE):
        print(msg)


def debug(msg: str):
    if should_log(LogLevel.DEBUG):
        print(msg)


# 环境变量控制
def init_from_env():
    env = os.environ.get("SMS_LOG", "normal").lower()
    if env == "verbose":
        set_level(LogLevel.VERBOSE)
    elif env == "debug":
        set_level(LogLevel.DEBUG)
    else:
        set_level(LogLevel.NORMAL)
