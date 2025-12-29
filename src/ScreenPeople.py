# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from twisted.internet import threads, reactor
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .ScreenConfig import ScreenConfig
from .ScreenPerson import ScreenPerson
from .Picture import Picture
from .SearchPeople import SearchPeople
from .Debug import logger
from .DelayTimer import DelayTimer
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class ScreenPeople(Picture, Screen, HelpableScreen):
    skin = readFile(getSkinPath("ScreenPeople.xml"))

    def __init__(self, session, movie, ident, media, cover_url, backdrop_url):
        logger.info("movie %s, ident: %s, media: %s, cover_url: %s, backdrop_url: %s",
                    movie, ident, media, cover_url, backdrop_url)
        Screen.__init__(self, session)
        Picture.__init__(self)
        self.title = _("Crew")
        self.session = session
        self.movie = movie
        self.ident = ident
        self.media = media
        self.cover_url = cover_url
        self.backdrop_url = backdrop_url
        self.result = []

        self['searchinfo'] = Label()
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Details"))
        self["key_yellow"] = Label()
        self['key_blue'] = Label()
        self['list'] = self.list = List()
        self['cover'] = Pixmap()
        self['backdrop'] = Pixmap()

        HelpableScreen.__init__(self)
        self["actions"] = HelpableActionMap(
            self,
            "TMDBActions",
            {
                "ok": (self.ok, _("Show details")),
                "cancel": (boundFunction(self.exit, True), _("Exit")),
                "up": (self.list.up, _("Selection up")),
                "down": (self.list.down, _("Selection down")),
                "right": (self.list.pageDown, _("Page down")),
                "left": (self.list.pageUp, _("Page down")),
                "red": (boundFunction(self.exit, False), _("Cancel")),
                "green": (self.ok, _("Show details")),
                "menu": (self.setup, _("Setup"))
            },
            -1,
        )

        self.onLayoutFinish.append(self.__onLayoutFinish)
        self["list"].onSelectionChanged.append(self.onSelectionChanged)

    def onSelectionChanged(self):
        DelayTimer.stopAll()
        self.showPicture(self["cover"], "cover", "", None)
        if self["list"].getCurrent():
            DelayTimer(200, self.showInfo)

    def __onLayoutFinish(self):
        logger.debug("movie: %s", self.movie)
        self.showPicture(self["backdrop"], "backdrop", self.ident, self.backdrop_url)
        threads.deferToThread(self.getData, self.gotData)

    def getData(self, callback):
        self["searchinfo"].setText(
            _("Looking up: %s ...") % (self.movie + " - " + _("Crew")))
        result = SearchPeople().getResult(self.result, self.ident, self.media)
        reactor.callFromThread(callback, result)  # pylint: disable=no-member

    def gotData(self, result):
        if not result:
            self["searchinfo"].setText(_("No results for: %s") % _("Crew"))
        else:
            self["searchinfo"].setText(self.movie + " - " + _("Crew"))
            self["list"].setList(result)

    def showInfo(self):
        current = self["list"].getCurrent()
        if current:
            cover_url = current[2]
            cover_ident = current[3]
            self.showPicture(self["cover"], "cover", cover_ident, cover_url)

    def ok(self):
        current = self['list'].getCurrent()
        if current:
            name = current[1]
            cover_ident = current[3]
            if cover_ident:
                self.session.openWithCallback(
                    self.screenPersonCallback, ScreenPerson, name, cover_ident, self.ident)

    def screenPersonCallback(self, do_exit):
        if do_exit:
            self.exit(True)

    def setup(self):
        self.session.open(ScreenConfig)

    def exit(self, do_exit):
        DelayTimer.stopAll()
        self["list"].onSelectionChanged.remove(self.onSelectionChanged)
        self.close(do_exit)
