# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from twisted.internet import threads, reactor
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .Picture import Picture
from .Debug import logger
from .ScreenConfig import ScreenConfig
from .SearchPerson import SearchPerson
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class ScreenPerson(Picture, Screen, HelpableScreen):
    skin = readFile(getSkinPath("ScreenPerson.xml"))

    def __init__(self, session, person, cover_ident, backdrop_ident):
        logger.info("cover_ident: %s, backdrop_ident: %s",
                    cover_ident, backdrop_ident)
        Screen.__init__(self, session)
        Picture.__init__(self)
        self.title = "TMDB - The Movie Database - " + _("Person Details")
        self.session = session
        self.person = person
        self.cover_ident = cover_ident
        self.backdrop_ident = backdrop_ident
        self.result = {}

        self['searchinfo'] = Label()
        self['fulldescription'] = self.fulldescription = ScrollLabel("")
        self['cover'] = Pixmap()
        self['backdrop'] = Pixmap()

        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label()
        self['key_yellow'] = Label()
        self['key_blue'] = Label()

        HelpableScreen.__init__(self)
        self["actions"] = HelpableActionMap(
            self,
            "TMDBActions",
            {
                "cancel": (boundFunction(self.exit, True), _("Exit")),
                "up": (self.fulldescription.pageUp, _("Selection up")),
                "down": (self.fulldescription.pageDown, _("Selection down")),
                "left": (self.fulldescription.pageUp, _("Page up")),
                "right": (self.fulldescription.pageDown, _("Page down")),
                "red": (boundFunction(self.exit, False), _("Cancel")),
                "menu": (self.setup, _("Setup")),
            },
            -1,
        )

        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        self.showPicture(self["backdrop"], "backdrop",
                         self.backdrop_ident, None)
        self.showPicture(self["cover"], "cover", self.cover_ident, None)
        self["searchinfo"].setText(_("Looking up: %s ...") % self.person)
        threads.deferToThread(self.getData, self.gotData)

    def getData(self, callback):
        result = SearchPerson().getResult(self.result, self.cover_ident)
        logger.debug("result: %s", result)
        reactor.callFromThread(callback, result)  # pylint: disable=no-member

    def gotData(self, result):
        if not result:
            self["searchinfo"].setText(_("No results for: %s") % self.person)
        else:
            self["searchinfo"].setText(result["name"])
            if result["birthday"] == "None":
                result["birthday"] = _("not specified")
            if result["place_of_birth"] == "None":
                result["place_of_birth"] = _("not specified")
            fulldescription = result["birthday"] + ", " \
                + result["place_of_birth"] + ", " \
                + result["gender"] + "\n" \
                + result["also_known_as"] + "\n" \
                + _("Popularity") + ": " + result["popularity"] + "\n\n" \
                + result["biography"] + "\n\n"
            if result["movies"]:
                fulldescription += _("Known for:") + "\n" \
                    + result["movies"]
            self["fulldescription"].setText(fulldescription)

    def setup(self):
        self.session.open(ScreenConfig)

    def exit(self, do_exit):
        self.close(do_exit)
