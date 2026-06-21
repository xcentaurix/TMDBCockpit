# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import re
import base64
from .FileUtils import readFile
from .Debug import logger


temp_dir = "/var/volatile/tmp/TMDBCockpit/"
api_key_file = "/etc/enigma2/tmdb_key.txt"


def getApiKey():
    api_key = ""
    if os.path.isfile(api_key_file):
        api_key = readFile(api_key_file)[:32]
    if not api_key:
        api_key = base64.b64decode(
            "M2I2NzAzYjg3MzRmZWUxYjU5OGRlOWVkN2JiZDNiNDc=")
    # logger.debug(api_key: %s", api_key)
    return api_key


def cleanText(text):
    logger.debug("text 1: %s", text)

    text = re.sub(r'\(.*\)', '', text).rstrip()  # remove (xyz)"
    logger.debug("text 2: %s", text)

    unwanted = [":", "-", "_", ",", ".", "+", "[", "]", "(", ")"]
    for char in unwanted:
        text = text.replace(char, " ")
    logger.debug("text 3: %s", text)

    text = " ".join(text.split())  # remove multiple spaces
    logger.debug("text 4: >%s<", text)
    return text


def checkText(text):
    # tuples indicate the bottom and top of the range, inclusive
    cjk_ranges = [
        (0x0600, 0x06FF),  # arabic
        (0x0750, 0x97FF),
        (0xAC00, 0xD7AF),  # hangul
        (0x4E00, 0x62FF),  # chinese
        (0x6300, 0x77FF),
        (0x7800, 0x8CFF),
        (0x8D00, 0x9FCC),
        (0x3400, 0x4DB5),
        (0x20000, 0x215FF),
        (0x21600, 0x230FF),
        (0x23100, 0x245FF),
        (0x24600, 0x260FF),
        (0x26100, 0x275FF),
        (0x27600, 0x290FF),
        (0x29100, 0x2A6DF),
        (0x2A700, 0x2B734),
        (0x2B740, 0x2B81D),
        (0x2B820, 0x2CEAF),
        (0x2CEB0, 0x2EBEF),
        (0x2F800, 0x2FA1F),
    ]

    def is_cjk(char):
        char_code = ord(char)
        return any(bottom <= char_code <= top for bottom, top in cjk_ranges)

    res = text
    if any(is_cjk(char) for char in text):
        res = ""
    return res
