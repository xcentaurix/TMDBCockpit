# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


def getCurrent(alist):
    current = alist.getCurrent()
    title = ident = media = cover_url = backdrop_url = search_title = None
    if current:
        title = current[0]
        ident = current[1]
        media = current[2]
        cover_url = current[3]
        backdrop_url = current[4]
        search_title = current[5]
    return title, ident, media, cover_url, backdrop_url, search_title
