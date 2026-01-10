# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.Language import language
from .Debug import logger


class LanguageSelection():

    def __init__(self):
        return

    def getLangChoices(self, sys_lang):
        logger.info("sys_lang: %s", sys_lang)
        if sys_lang == "en_EN":
            sys_lang = "en_GB"
        langs = language.lang.get(sys_lang, {})
        choices = []
        for lang in langs:
            if "_" in lang:
                choice = (lang[:2], langs[lang])
                choices.append(choice)
        logger.debug("choices: %s", choices)
        return choices
