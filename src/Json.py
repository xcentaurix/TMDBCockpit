# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import six
from .Debug import logger
from .Utils import checkText


class Json():
    def __init__(self):
        return

    def parseJson(self, result, source, keys):
        for key in keys:
            self.parseJsonSingle(result, source, key)

    def parseJsonSingle(self, result, source, key):
        value = "None"
        if key in source:
            value = source[key]
        if isinstance(value, six.text_type):
            value = six.ensure_str(value)
        if value is None:
            value = "None"
        result[key] = value

    def parseJsonList(self, result, key, separator):
        logger.info("result: %s, key: %s, separator: %s",
                    result, key, separator)
        alist = ""
        if key in result:
            logger.debug("key: %s", result[key])
            for source in result[key]:
                # logger.debug("source: %s", source)
                text = checkText(source)
                # logger.debug("checked text: %s", text)
                text = six.ensure_str(text)
                if alist and text:
                    alist += separator + " "
                if text:
                    alist += text
            logger.debug("alist: %s", alist)
            result[key] = alist
        else:
            result[key] = ""
        logger.debug("result[key]: %s", result[key])
