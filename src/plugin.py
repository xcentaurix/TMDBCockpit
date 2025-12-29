# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from .__init__ import _
from .Debug import logger
from .Version import VERSION
from .ConfigInit import ConfigInit
from .EpgSelection import initEPGSelection
from .ScreenMain import ScreenMain
from .ScreenTMDB import ScreenTMDB
from .PluginUtils import WHERE_TMDB_SEARCH, WHERE_TMDB_MOVIELIST


def showEventInfos(session, event="", service="", **__):
    if not service:
        service = session.nav.getCurrentService()
    info = service.info()
    if not event:
        event = info.getEvent(0)  # 0 = now, 1 = next
    event_name = event and event.getEventName() or info.getName() or ""
    session.open(ScreenMain, event_name, 2)


def queryEventInfos(search, callback, **__):
    logger.info("search: %s", search)
    ScreenTMDB(search, callback)


def movieList(session, service, **kwargs):
    logger.info("...")
    callback = kwargs["callback"] if "callback" in kwargs else None
    if callback:
        session.openWithCallback(callback, ScreenMain, service, 1)
    else:
        session.open(ScreenMain, service, 1)


def main(session, **__):
    session.open(ScreenMain, "", 3)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            # session = kwargs["session"]
            if config.plugins.tmdbcockpit.key_yellow.value:
                initEPGSelection()
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__):
    ConfigInit()

    descriptors = [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART,
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="TMDBCockpit",
            description=_("TMDB Infos"),
            where=[
                WHERE_TMDB_MOVIELIST,
                PluginDescriptor.WHERE_MOVIELIST,
            ],
            fnc=movieList
        ),
        PluginDescriptor(
            name="TMDBCockpit",
            description=_("TMDB Infos"),
            where=[
                WHERE_TMDB_SEARCH,
            ],
            fnc=queryEventInfos
        ),
        PluginDescriptor(
            name=_("TMDB Infos"),
            description=_("TMDB Infos"),
            where=[
                PluginDescriptor.WHERE_EVENTINFO,
            ],
            fnc=showEventInfos
        ),
        PluginDescriptor(
            name=_("TMDBCockpit"),
            description=_("TMDB Infos"),
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
            ],
            icon="TMDBCockpit.png",
            fnc=main
        )
    ]
    return descriptors
