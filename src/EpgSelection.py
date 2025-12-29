# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Screens.EpgSelection import EPGSelection
from Components.ActionMap import ActionMap
from .ScreenMain import ScreenMain
from .__init__ import _


original_init = None


def initEPGSelection():
    global original_init  # pylint: disable=global-statement
    if original_init is None:
        original_init = EPGSelection.__init__
    EPGSelection.__init__ = our_init


def our_init(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None):
    def yellow():
        event_name = ""
        current = self["list"].getCurrent()
        if current and current[0]:
            event_name = current[0].getEventName()
        session.open(ScreenMain, event_name, 2)

    original_init(self, session, service, zapFunc, eventid,
                  bouquetChangeCB, serviceChangeCB)
    self["tmdb_actions"] = ActionMap(
        ["EPGSelectActions"],
        {
            "yellow": yellow,
        }
    )
    self["key_yellow"].setText(_("TMDB Infos"))
