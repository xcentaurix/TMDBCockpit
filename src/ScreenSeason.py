# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from twisted.internet import threads, reactor
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .ScreenConfig import ScreenConfig
from .Picture import Picture
from .Debug import logger
from .DelayTimer import DelayTimer
from .SearchSeason import SearchSeason
from .MoreOptions import MoreOptions
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class ScreenSeason(MoreOptions, Picture, Screen, HelpableScreen):
    skin = readFile(getSkinPath("ScreenSeason.xml"))

    def __init__(self, session, movie, ident, media, service_path):
        logger.info("movie: %s, ident: %s, media: %s", movie, ident, media)
        Screen.__init__(self, session)
        MoreOptions.__init__(self, session, service_path)
        self.title = "TMDB - The Movie Database - " + _("Seasons")
        Picture.__init__(self)
        self.session = session
        self.movie = movie
        self.ident = ident
        self.media = media
        self.service_path = service_path
        self.files_saved = False
        self.result = []
        self['searchinfo'] = Label()
        self["overview"] = self.overview_label = ScrollLabel()
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label()
        self['key_yellow'] = Label()
        self["key_blue"] = Label(
            _("more ...")) if self.service_path else Label("")
        self['list'] = self.list = List()
        self['cover'] = Pixmap()
        self['backdrop'] = Pixmap()

        HelpableScreen.__init__(self)
        self["actions"] = HelpableActionMap(
            self,
            "TMDBActions",
            {
                "cancel": (boundFunction(self.exit, True), _("Exit")),
                "up": (self.list.up, _("Selection up")),
                "down": (self.list.down, _("Selection down")),
                "nextBouquet": (self.overview_label.pageUp, _("Details down")),
                "prevBouquet": (self.overview_label.pageDown, _("Details up")),
                "right": (self.list.pageDown, _("Page down")),
                "left": (self.list.pageUp, _("Page down")),
                "red": (boundFunction(self.exit, False), _("Cancel")),
                "blue": (self.showMenu, _("more ...")),
                "menu": (self.setup, _("Setup"))
            },
            -1,
        )

        self.onLayoutFinish.append(self.onFinish)
        self["list"].onSelectionChanged.append(self.onSelectionChanged)

    def onSelectionChanged(self):
        DelayTimer.stopAll()
        if self["list"].getCurrent():
            DelayTimer(200, self.showInfo)

    def onFinish(self):
        logger.debug("Selected: %s", self.movie)
        self.showPicture(self["backdrop"], "backdrop", self.ident, None)
        threads.deferToThread(self.getData, self.gotData)

    def getData(self, callback):
        self["searchinfo"].setText(_("Looking up: %s ...") % (
            self.movie + " - " + _("Seasons")))
        result = SearchSeason().getResult(self.result, self.ident)
        reactor.callFromThread(callback, result)  # pylint: disable=no-member

    def gotData(self, result):
        if not result:
            self["searchinfo"].setText(_("No results for: %s") % _("Seasons"))
        else:
            self["searchinfo"].setText(self.movie + " - " + _("Seasons"))
            self["list"].setList(result)

    def showMenu(self):
        self.menu(self.ident, self.overview)

    def showInfo(self):
        self["overview"].setText("...")
        current = self['list'].getCurrent()
        if current:
            cover_url = current[1]
            self.overview = current[2]
            self.ident = current[3]
            logger.debug("ident: %s", self.ident)
            self.showPicture(self["cover"], "cover", self.ident, cover_url)
            self["overview"].setText(self.overview)

    def setup(self):
        self.session.open(ScreenConfig)

    def exit(self, do_exit):
        DelayTimer.stopAll()
        self["list"].onSelectionChanged.remove(self.onSelectionChanged)
        self.close(do_exit, self.files_saved)
