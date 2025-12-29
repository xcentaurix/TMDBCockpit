# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import sys
import logging
from Components.config import config, ConfigSubsection, ConfigDirectory, ConfigSelection  # noqa: F401, pylint: disable=unused-import
from .Version import ID, PLUGIN


logger = None
streamer = None
format_string = ID + ": " + "%(levelname)s: %(filename)s: %(funcName)s: %(message)s"
log_levels = {"ERROR": logging.ERROR, "INFO": logging.INFO, "DEBUG": logging.DEBUG}
log_level_choices = list(log_levels.keys())
plugin = PLUGIN.lower()
exec("config.plugins." + plugin + " = ConfigSubsection()")  # noqa: F401, pylint: disable=exec-used
exec("config.plugins." + plugin + ".debug_log_level = ConfigSelection(default='INFO', choices=log_level_choices)")  # noqa: F401, pylint: disable=exec-used


def initLogging():
    global logger  # pylint: disable=global-statement
    global streamer  # pylint: disable=global-statement
    if not logger:
        logger = logging.getLogger(ID)
        formatter = logging.Formatter(format_string)
        streamer = logging.StreamHandler(sys.stdout)
        streamer.setFormatter(formatter)
        logger.addHandler(streamer)
        logger.propagate = False
        setLogLevel(log_levels[eval("config.plugins." + plugin + ".debug_log_level").value])  # pylint: disable=eval-used


def setLogLevel(level):
    logger.setLevel(level)
    streamer.setLevel(level)
    logger.info("level: %s", level)
