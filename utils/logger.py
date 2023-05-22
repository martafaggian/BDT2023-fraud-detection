"""
This module provides a set of classes for logging messages with different levels
to different files and streams.

The module defines five levels of logging: DEBUG, INFO, WARNING, ERROR and
CRITICAL. Each level has a corresponding logger class that inherits from the
BaseLogger class and the logging.Logger class. The BaseLogger class handles the
common attributes and methods for creating a logger object, adding file and
stream handlers, and formatting the messages. The logger classes for each level
have their own name, level, file name and stream parameters.

The module also defines a Logger class that creates and uses the logger classes
for each level only when needed. The Logger class has methods for logging
messages with each level using the corresponding logger object. The Logger class
also has a static method for getting a logger object from a configuration
dictionary that specifies the directory and file names for each level.

The module can be used as follows:

from logger import Logger

conf = {
    "dir": "./logs",
    "info_file": "info.log",
    "warning_file": "warning.log",
    "error_file": "error.log",
    "critical_file": "critical.log",
    "debug_file": "debug.log"
}

logger = Logger.get_logger_from_conf("run_name", conf)

logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
logger.debug("This is a debug message")
"""

from __future__ import annotations
import os
import sys
import logging
from enum import Enum
from typing import Dict
import _io

class Colors:
    WHITE = '\033[1m\033[37m'
    BOLD_CYAN = '\033[1m\033[36m'
    BOLD_ORANGE = '\033[1m\033[33m'
    BOLD_RED = '\033[1m\033[31m'
    BOLD_GREEN = '\033[1m\033[32m'
    BOLD_HIGHLIGHT_RED = '\033[1m\033[41m'
    RESET = '\033[0m'

class BaseLogger:
    """
    A base class for logging messages with a given level to a file and a stream.

    :param name:      name of logger object
    :type name:       str
    :param level:     level of logger object
    :type level:      int
    :param file_name: name of file to write messages to
    :type file_name:  str
    :param stream:    stream to write messages to
    :type stream:     file-like object
    """
    def __init__(
        self,
        name: str,
        level: int,
        file_name: str,
        stream: _io.TextIOWrapper,
        color: Colors = Colors.WHITE
    ):
        # Create logger object with name and level
        self.level = level
        self.color = color
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # File handler that writes to given file name
        dir_name = os.path.dirname(file_name)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(level)

        # Stream handler that writes to given stream
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(level)

        # Add timestamps and other information to messages
        formatter = logging.Formatter(f"%(asctime)s - {self.color}%(name)s{Colors.RESET} >>> %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def log(self, message: str):
        """
        Logs a message with the given level using the logger object.

        :param message: message to log
        :type message:  str
        """
        self.logger.log(self.logger.level, message)

class InfoLogger(BaseLogger, logging.Logger):
    """
    A class for logging messages with the INFO level to a file and stdout.

    :param name:    the name of the logger object
    :type name:     str
    :param outfile: the name of the file to write the messages to
                    (default is "info.log")
    :type outfile:  str
    """
    def __init__(self, name: str, outfile: str = "info.log"):
        super().__init__(f'{name}.INFO', logging.INFO, outfile,
                         sys.stdout, Colors.BOLD_CYAN)

class WarningLogger(BaseLogger, logging.Logger):
    """
    A class for logging messages with the WARNING level to a file and stdout.

    :param name:    the name of the logger object
    :type name:     str
    :param outfile: the name of the file to write the messages to
                    (default is "warning.log")
    :type outfile:  str
    """
    def __init__(self, name, outfile="warning.log"):
        super().__init__(f'{name}.WARNING', logging.WARNING, outfile,
                         sys.stdout, Colors.BOLD_ORANGE)

class ErrorLogger(BaseLogger, logging.Logger):
    """
    A class for logging messages with the ERROR level to a file and stdout.

    :param name:    the name of the logger object
    :type name:     str
    :param outfile: the name of the file to write the messages to
                    (default is "error.log")
    :type outfile:  str
    """
    def __init__(self, name, outfile="error.log"):
        super().__init__(f'{name}.ERROR', logging.ERROR, outfile,
                         sys.stderr, Colors.BOLD_RED)

class CriticalLogger(BaseLogger, logging.Logger):
    """
    A class for logging messages with the CRITICAL level to a file and stdout.

    :param name:    the name of the logger object
    :type name:     str
    :param outfile: the name of the file to write the messages to
                    (default is "critical.log")
    :type outfile:  str
    """
    def __init__(self, name, outfile="critical.log"):
        super().__init__(f'{name}.CRITICAL', logging.CRITICAL, outfile,
                         sys.stderr, Colors.BOLD_HIGHLIGHT_RED)

class DebugLogger(BaseLogger, logging.Logger):
    """
    A class for logging messages with the DEBUG level to a file and stdout.

    :param name:    the name of the logger object
    :type name:     str
    :param outfile: the name of the file to write the messages to
                    (default is "debug.log")
    :type outfile:  str
    """
    def __init__(self, name, outfile="debug.log"):
        super().__init__(f'{name}.DEBUG', logging.DEBUG, outfile,
                         sys.stdout, Colors.BOLD_GREEN)

class Logger:
    """
    A class for logging messages with different levels to different files and
    streams.

    The class creates and uses logger objects for each level only when needed.
    The class has methods for logging messages with each level using the
    corresponding logger object. The class also has a static method for getting
    a logger object from a configuration dictionary that specifies the directory
    and file names for each level.

    :param name:          name of logger object
    :type name:           str
    :param info_file:     name of file to write info messages to
                          (default is "info.log")
    :type info_file:      str
    :param warning_file:  name of file to write warning messages to
                          (default is "warning.log")
    :type warning_file:   str
    :param error_file:    name of file to write error messages to
                          (default is "error.log")
    :type error_file:     str
    :param critical_file: name of file to write critical messages to
                          (default is "critical.log")
    :type critical_file:  str
    :param debug_file:    name of file to write debug messages to
                          (default is "debug.log")
    :type debug_file:     str
    """
    def __init__(
        self,
        name: str,
        info_file: str = "info.log",
        warning_file: str = "warning.log",
        error_file: str = "error.log",
        critical_file: str = "critical.log",
        debug_file: str = "debug.log"
    ):
        self.name = name
        self.info_file = info_file
        self.warning_file = warning_file
        self.error_file = error_file
        self.critical_file = critical_file
        self.debug_file = debug_file

        self.info_logger = None
        self.warning_logger = None
        self.error_logger = None
        self.critical_logger = None
        self.debug_logger = None

    def info(self, message: str):
        """
        Logs a message with the INFO level using the info logger object.

        If the info logger object does not exist, it creates one using the
        InfoLogger class with the given name and info file.

        :param message: the message to log
        :type message:  str
        """
        if self.info_logger is None:
            self.info_logger = InfoLogger(self.name, self.info_file)
        self.info_logger.log(message)

    def warning(self, message: str):
        """
        Logs a message with the WARNING level using the warning logger object.

        If the warning logger object does not exist, it creates one using the
        WarningLogger class with the given name and warning file.

        :param message: the message to log
        :type message:  str
        """
        if self.warning_logger is None:
            self.warning_logger = WarningLogger(self.name, self.warning_file)
        self.warning_logger.log(message)

    def error(self, message: str):
        """
        Logs a message with the ERROR level using the error logger object.

        If the error logger object does not exist, it creates one using the
        ErrorLogger class with the given name and error file.

        :param message: the message to log
        :type message:  str
        """
        if self.error_logger is None:
            self.error_logger = ErrorLogger(self.name, self.error_file)
        self.error_logger.log(message)

    def critical(self, message: str):
        """
        Logs a message with the CRITICAL level using the critical logger object.

        If the critical logger object does not exist, it creates one using the
        CriticalLogger class with the given name and critical file.

        :param message: the message to log
        :type message:  str
        """
        if self.critical_logger is None:
            self.critical_logger = CriticalLogger(self.name, self.critical_file)
        self.critical_logger.log(message)

    def debug(self, message: str):
        """
        Logs a message with the DEBUG level using the debug logger object.

        If the debug logger object does not exist, it creates one using the
        DebugLogger class with the given name and debug file.

        :param message: the message to log
        :type message: str
        """
        if self.debug_logger is None:
            self.debug_logger = DebugLogger(self.name, self.debug_file)
        self.debug_logger.log(message)

    @staticmethod
    def get_logger_from_conf(name:str, conf: Dict[str, str]) -> Logger:
        """
        Gets a logger object from a configuration dictionary that specifies the
        directory and file names for each level.

        The method creates a Logger object with the given name and the file
        names for each level based on the directory given in the configuration
        dictionary.

        :param name: the name of the logger object
        :type name:  str
        :param conf: the configuration dictionary
                     It should have the following keys and values:
                        dir: directory where the logs are saved
                        info_file: file name for info logs
                        warning_file: file name for warning logs
                        error_file: file name for error logs
                        critical_file: file name for critical logs
                        debug_file: file name for debug logs
        :type conf:  dict[str, str]
        :return:     a Logger object
        :rtype:      Logger
        """
        conf_paths = {k: os.path.join(conf['dir'], v) for k, v in
                     conf.items() if k not in 'dir'}
        return Logger(
            name=name,
            info_file=conf_paths['info_file'],
            warning_file=conf_paths['warning_file'],
            error_file=conf_paths['error_file'],
            critical_file=conf_paths['critical_file'],
            debug_file=conf_paths['debug_file']
        )
