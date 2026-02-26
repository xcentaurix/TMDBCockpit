# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from pathlib import Path
from Components.config import config
from skin import loadSkin
from .Debug import logger


def getSkinPath(file_name):
    logger.info("file_name: %s", file_name)
    primary_skin = config.skin.primary_skin.value.split("/")[0]
    logger.debug("primary_skin: %s", primary_skin)
    skin_path = Path(__file__).parent / "skin" / "default" / file_name
    if primary_skin == "E2-DarkOS":
        skin_path = Path(__file__).parent / "skin" / primary_skin / file_name
    if not os.path.isfile(skin_path):
        skin_path = Path(__file__).parent / "skin" / file_name
    logger.info("skin_path: %s", skin_path)
    return str(skin_path)


def loadPluginSkin(file_name):
    primary_skin = config.skin.primary_skin.value.split("/")[0]
    if primary_skin == "E2-DarkOS":
        loadSkin(getSkinPath(file_name))
