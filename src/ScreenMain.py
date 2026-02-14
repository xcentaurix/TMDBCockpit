# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

import os
from twisted.internet import threads, reactor
from Components.ActionMap import HelpableActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from enigma import eServiceCenter
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.HelpMenu import HelpableScreen
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from . import tmdbsimple as tmdb
from .__init__ import _
from .ScreenConfig import ScreenConfig
from .ScreenMovie import ScreenMovie
from .ScreenPerson import ScreenPerson
from .Utils import temp_dir, cleanText
from .Picture import Picture
from .FileUtils import createDirectory, deleteDirectory
from .Debug import logger
from .DelayTimer import DelayTimer
from .Json import Json
from .SearchMain import SearchMain
from .Utils import getApiKey
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class ScreenMain(Picture, Json, Screen, HelpableScreen):
    skin = readFile(getSkinPath("ScreenMain.xml"))

    def __init__(self, session, service, mode):
        Screen.__init__(self, session)
        Picture.__init__(self)
        Json.__init__(self)
        self.session = session

        tmdb.API_KEY = getApiKey()

        self.title = "TMDB - The Movie Database - " + _("Overview")
        self.menu_selection = 0
        self.search_title = ""
        self.direction_up = False
        self.page = 1
        self.total_pages = 0
        self.ident = 0
        self.count = 0
        self.service_path = ""
        self.files_saved = False
        self.result = []

        self['searchinfo'] = Label()
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Details"))
        self['key_yellow'] = Label(_("Edit search"))
        self['key_blue'] = Label(_("more ..."))
        self['key_menu'] = StaticText(_("Setup"))

        self['list'] = List()
        self['cover'] = Pixmap()
        self['backdrop'] = Pixmap()

        HelpableScreen.__init__(self)
        self["actions"] = HelpableActionMap(
            self,
            "TMDBActions",
            {
                "ok": (self.ok, _("Show details")),
                "red": (self.exit, _("Exit")),
                "down": (self.down, _("Up")),
                "up": (self.up, _("Down")),
                "nextBouquet": (self.nextBouquet, _("Details down")),
                "prevBouquet": (self.prevBouquet, _("Details up")),
                "cancel": (self.exit, _("Cancel")),
                "green": (self.ok, _("Show details")),
                "yellow": (self.searchString, _("Edit search")),
                "blue": (self.menu, _("more ...")),
                "menu": (self.setup, _("Setup")),
                "eventview": (self.searchString, _("Edit search"))
            },
            -1,
        )

        if mode == 1:
            self.service_path = service.getPath()
            self.service_name = service.getName()
            if self.service_name:
                self.text = cleanText(self.service_name)
            elif os.path.isdir(self.service_path):
                self.service_path = os.path.normpath(self.service_path)
                self.text = cleanText(os.path.basename(self.service_path))
            else:
                info = eServiceCenter.getInstance().info(service)
                name = info.getName(service)
                self.text = cleanText(os.path.splitext(name)[0])
        elif mode == 2:
            name = service
            self.text = cleanText(name)
        else:
            self.text = ""
            self.menu_selection = 1
            self.search_title = _("Current movies in cinemas")

        logger.debug("text: %s", self.text)

        createDirectory(temp_dir)
        self.onLayoutFinish.append(self.onDialogShow)
        self["list"].onSelectionChanged.append(self.onSelectionChanged)

    def onSelectionChanged(self):
        logger.info("...")
        DelayTimer.stopAll()
        self["cover"].hide()
        self["backdrop"].hide()
        if config.plugins.tmdbcockpit.skip_to_movie.value and self.count == 1:
            DelayTimer(10, self.ok)
        else:
            DelayTimer(500, self.showPictures)

    def onDialogShow(self):
        logger.info("...")
        if self.menu_selection or self.text:
            self.searchData()
        else:
            logger.debug("no search string specified")
            self["searchinfo"].setText(_("No search string specified."))

    def searchData(self):
        logger.debug("menu_selection: %s, text: %s",
                     self.menu_selection, self.text)
        self.result = []
        if self.menu_selection:
            self["searchinfo"].setText(self.search_title)
            threads.deferToThread(
                self.getData, self.menu_selection, self.text, self.ident, self.page, self.gotData)
        else:
            self.search_iteration = 0
            self.search_words = self.text.split(" ")
            self.last_text = self.text
            self["searchinfo"].setText(_("Looking up: %s ...") % self.text)
            self.search(0, [])

    def search(self, totalpages, result):
        if self.search_iteration and self.search_words:
            del self.search_words[-1]
            text = " ".join(self.search_words)
        else:
            text = self.text
        if not result and text:
            self["searchinfo"].setText(_("Looking up: %s ...") % text)
            self.search_iteration += 1
            self.last_text = text
            logger.debug("iteration: %s, text: %s",
                         self.search_iteration, text)
            threads.deferToThread(
                self.getData, self.menu_selection, text, self.ident, self.page, self.search)
        else:
            self.gotData(totalpages, result, self.last_text)

    def getData(self, menu_selection, text, ident, page, callback):
        totalpages, result = SearchMain().getResult(
            self.result, menu_selection, text, ident, page)
        reactor.callFromThread(callback, totalpages, result)

    def gotData(self, totalpages, result, text=""):
        logger.info("text: %s", text)
        logger.info("len(result): %s", len(result))
        self.count = len(result)
        self.totalpages = totalpages
        if self.menu_selection:
            if result:
                self["searchinfo"].setText(
                    f"{self.search_title} ({_('page')} {self.page}/{totalpages})")
            else:
                self['searchinfo'].setText(
                    f"{_('No results for:')} {self.search_title}")
        elif result:
            if text != self.text:
                self['searchinfo'].setText(f"{text} ({self.text})")
            else:
                self['searchinfo'].setText(self.text)
        else:
            self['searchinfo'].setText(f"{_('No results for:')} {self.text}")
        self["list"].setList(result)
        if result:
            if self.direction_up:
                self["list"].setIndex(len(result) - 1)
            else:
                self["list"].setIndex(0)

    def showPictures(self):
        logger.info("...")
        current = self["list"].getCurrent()
        if current:
            ident = current[1]
            cover_url = current[3]
            backdrop_url = current[4]
            self.showPicture(self["cover"], "cover", ident, cover_url)
            self.showPicture(self["backdrop"], "backdrop", ident, backdrop_url)
        else:
            self["cover"].hide()
            self["backdrop"].hide()

    def ok(self):
        current = self['list'].getCurrent()
        logger.info("current: %s", current)
        if current:
            title = current[0]
            ident = current[1]
            media = current[2]
            cover_url = current[3]
            backdrop_url = current[4]
            if media in {"movie", "tv"}:
                self.session.openWithCallback(
                    self.screenMovieCallback, ScreenMovie, title, media, cover_url, ident, self.service_path, backdrop_url)
            elif media == "person":
                self.session.openWithCallback(
                    self.screenPersonCallback, ScreenPerson, title, ident, "")
            else:
                logger.debug("unsupported media: %s", media)

    def screenMovieCallback(self, do_exit, files_saved):
        logger.info("files_saved: %s", files_saved)
        self.files_saved = files_saved
        if do_exit:
            self.exit()
        elif self.count == 1:
            self.showPictures()

    def screenPersonCallback(self, do_exit):
        if do_exit:
            self.exit()

    def menu(self):
        logger.info("...")
        self.direction_up = False
        options = [
            (_("TMDB Infos"), 0),
            (_("Current movies in cinemas"), 1),
            (_("Upcoming movies"), 2),
            (_("Popular movies"), 3),
            (_("Similar movies"), 4),
            (_("Recommendations"), 5),
            (_("Best rated movies"), 6)
        ]
        self.session.openWithCallback(
            self.menuCallback,
            ChoiceBox,
            windowTitle=_("TMDB categories"),
            title=_("Please select a category"),
            list=options
        )

    def menuCallback(self, ret):
        logger.info("ret: %s", ret)
        if ret is not None:
            self.page = 1
            self.search_title = ret[0]
            self.menu_selection = ret[1]
            current = self['list'].getCurrent()
            if current:
                self.ident = current[1]
                self.searchData()

    def up(self):
        list_length = len(self["list"].list) if self["list"].list else 0
        logger.info("SelectionIndex: %s, len(list): %s",
                    self["list"].getSelectedIndex(), list_length)
        if self["list"].getSelectedIndex() == 0:
            self.nextBouquet()
        else:
            self["list"].up()

    def down(self):
        list_length = len(self["list"].list) if self["list"].list else 0
        logger.info("SelectionIndex: %s, len(list): %s",
                    self["list"].getSelectedIndex(), list_length)
        if self["list"].getSelectedIndex() == list_length - 1:
            self.prevBouquet()
        else:
            self["list"].down()

    def prevBouquet(self):
        logger.info("...")
        if self.menu_selection:
            self.direction_up = False
            self.page += 1
            if self.page > self.totalpages:
                self.page = 1
            self.searchData()

    def nextBouquet(self):
        logger.info("...")
        if self.menu_selection:
            self.direction_up = True
            self.page -= 1
            if self.page <= 0:
                self.page = self.totalpages
            self.searchData()

    def setup(self):
        self.session.open(ScreenConfig)

    def searchString(self):
        self.menu_selection = 0
        current = self['list'].getCurrent()
        logger.info("current: %s", current)
        if current:
            search_title = current[5]
            self.text = search_title
        self.session.openWithCallback(self.goSearch, VirtualKeyBoard, title=(
            _("Search for Movie:")), text=self.text)

    def goSearch(self, text):
        if text:
            self.text = text
            self.searchData()

    def exit(self):
        logger.info("files_saved: %s", self.files_saved)
        DelayTimer.stopAll()
        self["list"].onSelectionChanged.remove(self.onSelectionChanged)
        deleteDirectory(temp_dir)
        self.close(self.files_saved)
