# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import gettext
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.Language import language
from .Version import PLUGIN
from .Debug import initLogging


def initLocale():
    os.environ["LANGUAGE"] = language.getLanguage()[:2]
    locale = resolveFilename(SCOPE_PLUGINS, "Extensions/" + PLUGIN + "/locale")
    if not os.path.exists(locale):
        locale = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/" + PLUGIN + "/locale")
    if os.path.exists(locale):
        gettext.bindtextdomain(PLUGIN, locale)


def _(txt):
    return gettext.dgettext(PLUGIN, txt)


initLogging()
initLocale()
language.addCallback(initLocale)
