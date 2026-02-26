# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from twisted.internet import threads, reactor
from enigma import eServiceReference
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import MoviePlayer
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .ScreenConfig import ScreenConfig
from .ScreenPeople import ScreenPeople
from .ScreenSeason import ScreenSeason
from .Picture import Picture
from .Debug import logger
from .SearchMovie import SearchMovie
from .MoreOptions import MoreOptions
from .PluginUtils import getPlugin, WHERE_SEARCH
from .SkinUtils import getSkinPath
from .FileUtils import readFile
from .YouTubeVideoUrl import YouTubeVideoUrl


class TrailerPlayer(MoviePlayer):
    """Custom trailer player based on TMDB plugin"""
    def __init__(self, session, service):
        MoviePlayer.__init__(self, session, service)
        self.skinName = 'MoviePlayer'
        self["actions"] = HelpableActionMap(
            self,
            "MoviePlayerActions",
            {
                "leavePlayer": (self.leavePlayer, _("Leave trailer player"))
            }
        )
        self.setTitle(_("Trailer Player"))

    def leavePlayer(self):
        self.close()

    def doEofInternal(self, _playing):
        self.close()

    def showMovies(self):
        pass

    def openServiceList(self):
        if hasattr(self, 'toggleShow'):
            self.toggleShow()


class ScreenMovie(MoreOptions, Picture, Screen, HelpableScreen):
    skin = readFile(getSkinPath("ScreenMovie.xml"))

    def __init__(self, session, movie, media, cover_url, ident, service_path, backdrop_url):
        logger.debug(
            "movie: %s, media: %s, cover_url: %s, ident: %s, service_path: %s, backdrop_url: %s",
            movie, media, cover_url, ident, service_path, backdrop_url
        )
        Screen.__init__(self, session)
        Picture.__init__(self)
        MoreOptions.__init__(self, session, service_path)
        self.title = _("Movie Details")
        self.session = session
        self.movie = movie
        self.media = media
        self.cover_url = cover_url
        self.backdrop_url = backdrop_url
        self.ident = ident
        self.service_path = service_path
        self.files_saved = False
        self.overview = ""
        self.result = {}
        self.movie_title = ""
        self.original_title = ""
        self.videos = []

        self["genre"] = Label()
        self["genre_txt"] = Label()
        self["fulldescription"] = self.fulldescription = ScrollLabel("")
        self["rating"] = Label()
        self["votes"] = Label()
        self["votes_brackets"] = Label()
        self["votes_txt"] = Label()
        self["runtime"] = Label()
        self["runtime_txt"] = Label()
        self["year"] = Label()
        self["year_txt"] = Label()
        self["country"] = Label()
        self["country_txt"] = Label()
        self["director"] = Label()
        self["director_txt"] = Label()
        self["author"] = Label()
        self["author_txt"] = Label()
        self["studio"] = Label()
        self["studio_txt"] = Label()

        self.fields = {
            "genre": (_("Genre:"), "-"),
            "fulldescription": (None, ""),
            "rating": (None, "0.0"),
            "votes": (_("Votes:"), "-"),
            "votes_brackets": (None, ""),
            "runtime": (_("Runtime:"), "-"),
            "year": (_("Year:"), "-"),
            "country": (_("Countries:"), "-"),
            "director": (_("Director:"), "-"),
            "author": (_("Author:"), "-"),
            "studio": (_("Studio:"), "-"),
        }

        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Crew"))
        self["key_yellow"] = Label(
            _("Seasons")) if self.media == "tv" else Label("")
        self["key_blue"] = Label(
            _("more ...")) if self.service_path else Label("")

        self["searchinfo"] = Label()
        self["cover"] = Pixmap()
        self["backdrop"] = Pixmap()
        self["fsklogo"] = Pixmap()
        self["star"] = Pixmap()

        HelpableScreen.__init__(self)
        self["actions"] = HelpableActionMap(
            self,
            "TMDBActions",
            {
                "ok": (self.green, _("Crew")),
                "red": (boundFunction(self.exit, True), _("Exit")),
                "up": (self.fulldescription.pageUp, _("Selection up")),
                "down": (self.fulldescription.pageDown, _("Selection down")),
                "left": (self.fulldescription.pageUp, _("Page up")),
                "right": (self.fulldescription.pageDown, _("Page down")),
                "cancel": (boundFunction(self.exit, False), _("Cancel")),
                "green": (self.green, _("Crew")),
                "yellow": (self.yellow, _("Seasons")),
                "blue": (self.showMenu, _("more ...")),
                "menu": (self.setup, _("Setup")),
                "eventview": (self.search, _("Search"))
            },
            -1,
        )

        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        logger.debug("movie: %s", self.movie)
        self.showPicture(self["cover"], "cover", self.ident, self.cover_url)
        self.showPicture(self["backdrop"], "backdrop",
                         self.ident, self.backdrop_url)
        self["searchinfo"].setText(_("Looking up: %s ...") % self.movie)
        threads.deferToThread(self.getData, self.gotData)

    def getData(self, callback):
        result = SearchMovie().getResult(self.result, self.ident, self.media)
        logger.debug("result: %s", result)
        reactor.callFromThread(callback, result)

    def gotData(self, result):
        if not result:
            self["searchinfo"].setText(_("No results for: %s") % self.movie)
            self.overview = ""
        else:
            self["searchinfo"].setText(self.movie)
            path = "/usr/lib/enigma2/python/Plugins/Extensions/TMDBCockpit/skin/images/star.png"
            self["star"].instance.setPixmap(LoadPixmap(path))
            path = "/usr/lib/enigma2/python/Plugins/Extensions/TMDBCockpit/skin/images/fsk_" + \
                result["fsk"] + ".png"
            self["fsklogo"].instance.setPixmap(LoadPixmap(path))

            for field, (label, default) in self.fields.items():
                # logger.debug("field: %s", field)
                # logger.debug("result: %s", result[field])
                if label:
                    self[field + "_txt"].setText(label)
                if result[field]:
                    self[field].setText(result[field])
                else:
                    self[field].setText(default)

            self.overview = result["overview"]

            self.movie_title = self.original_title = ""
            if self.media == "movie":
                self.movie_title = result["title"]
                self.original_title = result["original_title"]
                self.videos = result["videos"]
                self["key_yellow"].setText(
                    f"{_('Videos')} ({len(self.videos)})")
            elif self.media == "tv":
                self.movie_title = result["name"]

    def showMenu(self):
        self.menu(self.ident, self.overview)

    def search(self):
        search_plugin = getPlugin(WHERE_SEARCH)
        if search_plugin:
            search_plugin(self.session, self.movie_title, self.original_title)
        else:
            self.session.open(MessageBox, _(
                "No search provider registered."), type=MessageBox.TYPE_INFO)

    def setup(self):
        self.session.open(ScreenConfig)

    def yellow(self):
        if self.media == "tv":
            self.session.openWithCallback(
                self.screenSeasonCallback, ScreenSeason, self.movie, self.ident, self.media, self.service_path)
        elif self.media == "movie" and self.videos:
            videolist = []
            for video in self.videos:
                vKey = video["key"]
                vName = video["name"]
                videolist.append((str(vName), str(vKey)))

            if len(videolist) > 1:
                videolist = sorted(videolist, key=lambda x: x[0])
                self.session.openWithCallback(
                    self.videolistCallback,
                    ChoiceBox,
                    windowTitle=_("TMDB videos"),
                    title=_("Please select a video"),
                    list=videolist,
                )
            elif len(videolist) == 1:
                self.videolistCallback(videolist[0])

    def screenSeasonCallback(self, do_exit, files_saved):
        self.files_saved = files_saved
        if do_exit:
            self.exit(True)

    def videolistCallback(self, ret):
        if ret:
            video_id = ret[1]
            # Try to extract actual playable URL using YouTubeVideoUrl
            try:
                ytdl = YouTubeVideoUrl()
                url = ytdl.extract(video_id)
                if url:
                    # Create service reference with extracted URL
                    ref = eServiceReference(4097, 0, url)
                    ref.setName(ret[0])  # Set video name as title
                    self.session.open(TrailerPlayer, ref)
                    return
            except Exception as e:
                logger.error("Failed to extract YouTube URL: %s", str(e))
                self.session.open(MessageBox, _('Trailer playback failed.'), MessageBox.TYPE_INFO, timeout=3)

    def green(self):
        self.session.openWithCallback(self.screenPeopleCallback, ScreenPeople,
                                      self.movie, self.ident, self.media, self.cover_url, self.backdrop_url)

    def screenPeopleCallback(self, do_exit):
        if do_exit:
            self.exit(True)

    def exit(self, do_exit):
        self.close(do_exit, self.files_saved)
