# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config, ConfigYesNo, ConfigSelection, ConfigSubsection
from Components.Language import language
from .LanguageSelection import LanguageSelection
from .Debug import logger, setLogLevel, log_levels, initLogging


class ConfigInit(LanguageSelection):

    def __init__(self):
        logger.info("...")
        LanguageSelection.__init__(self)
        lang = language.getActiveLanguage()
        logger.debug("lang: %s", lang)
        lang_choices = self.getLangChoices(lang)
        config.plugins.tmdbcockpit = ConfigSubsection()
        config.plugins.tmdbcockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.tmdbcockpit.cover_size = ConfigSelection(
            default="original", choices=["w92", "w185", "w500", "original"])
        config.plugins.tmdbcockpit.backdrop_size = ConfigSelection(
            default="original", choices=["w300", "w780", "w1280", "original"])
        config.plugins.tmdbcockpit.lang = ConfigSelection(
            default=lang[:2], choices=lang_choices)
        config.plugins.tmdbcockpit.skip_to_movie = ConfigYesNo(default=True)
        config.plugins.tmdbcockpit.key_yellow = ConfigYesNo(default=True)

        config.plugins.tmdbcockpit.trailer_player = ConfigSelection(
            default="MediaPortal", choices=["MediaPortal", "MyTube"])
        setLogLevel(log_levels[config.plugins.tmdbcockpit.debug_log_level.value])
        initLogging()
