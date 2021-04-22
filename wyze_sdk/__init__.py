import logging

from .api import Client  # noqa

default_format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def set_stream_logger(name, level=logging.INFO, format_string=None):
    """
    A convenience method to set the global logger to stream.
    """

    global log

    if not format_string:
        format_string = default_format_string

    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.StreamHandler()
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger


def set_file_logger(name, filepath, level=logging.INFO, format_string=None):
    """
    A convenience method to set the global logger to a file.
    """

    global log

    if not format_string:
        format_string = default_format_string

    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(filepath)
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger
