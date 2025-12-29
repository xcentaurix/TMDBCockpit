# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from pathlib import Path
from Components.config import config
from .Debug import logger


def getSkinPath(file_name):
    logger.info("file_name: %s", file_name)
    primary_skin = config.skin.primary_skin.value.split("/")[0]
    logger.debug("primary_skin: %s", primary_skin)
    skin_path = Path(__file__).parent / "skin" / primary_skin / file_name
    logger.info("skin_path: %s", skin_path)
    return skin_path
