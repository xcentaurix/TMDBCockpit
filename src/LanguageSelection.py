# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.Language import language
from .Debug import logger


class LanguageSelection():

    def __init__(self):
        return

    def getLangChoices(self, sys_lang):
        logger.info("sys_lang: %s", sys_lang)
        choices = []
        for lang_key, lang_data in language.lang.items():
            choice = (lang_key[:2], lang_data[0])
            if choice not in choices:
                choices.append(choice)
        if not choices:
            choices.append(("en", "English"))
        logger.debug("choices: %s", choices)
        return choices
