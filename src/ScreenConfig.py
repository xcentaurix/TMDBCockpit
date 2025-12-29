# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.ActionMap import ActionMap
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Screens.Screen import Screen
from .__init__ import _
from .Version import PLUGIN, VERSION
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class ScreenConfig(Screen, ConfigListScreen):
    skin = readFile(getSkinPath("ConfigScreen.xml"))

    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(
            self, self.list, session=session, on_change=self.changedEntry)

        self["actions"] = ActionMap(
            ["TMDBActions"],
            {
                "cancel": self.exit,
                "save": self.ok,
                "red": self.exit,
                "green": self.ok,
            },
            -2
        )

        self["key_green"] = Label(_("OK"))
        self["key_red"] = Label(_("Cancel"))

        self.list = []
        self.createConfigList()
        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        self.setTitle(PLUGIN + " - " + VERSION)

    def createConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry(
            _("Language:"), config.plugins.tmdbcockpit.lang))
        self.list.append(getConfigListEntry(
            _("Skip to movie details for single result:"), config.plugins.tmdbcockpit.skip_to_movie))
        self.list.append(getConfigListEntry(
            _("Yellow key for TMDB infos in EPGs:"), config.plugins.tmdbcockpit.key_yellow))
        self.list.append(getConfigListEntry(
            _("Cover resolution:"), config.plugins.tmdbcockpit.cover_size))
        self.list.append(getConfigListEntry(
            _("Backdrop resolution:"), config.plugins.tmdbcockpit.backdrop_size))
        self.list.append(getConfigListEntry(
            _("Player for trailers:"), config.plugins.tmdbcockpit.trailer_player))
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def ok(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def exit(self):
        self.close()
