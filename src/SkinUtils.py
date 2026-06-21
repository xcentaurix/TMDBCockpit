# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from pathlib import Path
from Tools.Directories import SCOPE_SKIN
from Components.config import config
from skin import loadSkin
# from .Debug import logger


def getSkinPath(file_name):
    # logger.info("file_name: %s", file_name)
    primary_skin = config.skin.primary_skin.value.split("/")[0]
    # logger.debug("primary_skin: %s", primary_skin)
    skin_path = Path(__file__).parent / "skin" / primary_skin / file_name
    if not os.path.isfile(skin_path):
        skin_path = Path(__file__).parent / "skin" / "default" / file_name
    if not os.path.isfile(skin_path):
        skin_path = Path(__file__).parent / "skin" / file_name
    # logger.info("skin_path: %s", skin_path)
    return str(skin_path)


def loadPluginSkin(file_name="skin.xml"):
    skin_file = getSkinPath(file_name)
    loadSkin(skin_file, scope=SCOPE_SKIN)
