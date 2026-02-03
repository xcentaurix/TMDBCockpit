# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import shutil
import glob
from pathlib import Path
from .Debug import logger


def stripCutNumber(path):
    filename, ext = os.path.splitext(path)
    if len(filename) > 3:
        if filename[-4] == "_" and filename[-3:].isdigit():
            filename = filename[:-4]
        path = filename + ext
    return path


def readFile(path, mode="r"):
    data = ""
    try:
        if mode == "rb":
            with open(path, mode) as f:  # pylint: disable=unspecified-encoding
                data = f.read()
        else:
            with open(path, mode, encoding="utf-8") as f:
                data = f.read()
    except Exception as e:
        logger.info("path: %s, exception: %s", path, e)
    return data


def writeFile(path, data, mode="w"):
    try:
        if mode == "wb":
            with open(path, "wb") as f:
                f.write(data)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def deleteFile(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def deleteFiles(path, clear=False):
    for afile in glob.glob(path):
        if clear:
            writeFile(afile, "")
        deleteFile(afile)


def touchFile(path):
    try:
        Path(path).touch()
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def copyFile(src_path, dest_path):
    try:
        shutil.copy2(src_path, dest_path)
    except Exception as e:
        logger.error("src: %s, dest: %s, exception: %s", src_path, dest_path, e)


def renameFile(src_path, dest_path):
    try:
        shutil.move(src_path, dest_path)
    except Exception as e:
        logger.error("src: %s, dest: %s, exception: %s", src_path, dest_path, e)


def createDirectory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def createSymlink(src, dst):
    try:
        os.symlink(src, dst)
    except Exception as e:
        logger.error("src: %s, dst: %s, exception: %s", src, dst, e)


def deleteDirectory(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)
