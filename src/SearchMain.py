# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from Components.config import config
from . import tmdbsimple as tmdb
from .__init__ import _
from .Debug import logger
from .Json import Json


class SearchMain(Json):

    def __init__(self):
        Json.__init__(self)

    def getResult(self, res, menu_selection, text, ident, page):
        logger.info("menu_selection: %s, text: %s, ident: %s, page: %s",
                    menu_selection, text, ident, page)
        lang = config.plugins.tmdbcockpit.lang.value
        totalpages = 0
        json_data = {}
        if menu_selection == 1:
            json_data = tmdb.Movies().now_playing(page=page, language=lang)
        elif menu_selection == 2:
            json_data = tmdb.Movies().upcoming(page=page, language=lang)
        elif menu_selection == 3:
            json_data = tmdb.Movies().popular(page=page, language=lang)
        elif menu_selection == 4:
            json_data = tmdb.Movies(ident).similar_movies(
                page=page, language=lang)
        elif menu_selection == 5:
            json_data = tmdb.Movies(ident).recommendations(
                page=page, language=lang)
        elif menu_selection == 6:
            json_data = tmdb.Movies().top_rated(page=page, language=lang)
        else:
            json_data = tmdb.Search().multi(query=text, language=lang)

        results = {}
        self.parseJson(results, json_data, ["total_pages", "results"])
        totalpages = results["total_pages"]
        for entry in results["results"]:
            logger.debug("entry: %s", entry)
            result = {}
            keys = ["media_type", "id", "title", "name", "release_date",
                    "first_air_date", "poster_path", "backdrop_path", "profile_path"]
            self.parseJson(result, entry, keys)

            media = result["media_type"]
            ident = result["id"]
            title_movie = result["title"]
            title_series = result["name"]
            title_person = result["name"]
            date_movie = result["release_date"]
            date_tv = result["first_air_date"]
            cover_path = result["poster_path"]
            profile_path = result["profile_path"]
            backdrop_path = result["backdrop_path"]

            title = search_title = ""
            if media == "movie" and title_movie:
                title = f"{title_movie} ({_('Movie')}, {date_movie[:4]})"
                search_title = title_movie
            elif media == "tv" and title_series:
                title = f"{title_series} ({_('Series')}, {date_tv[:4]})"
                search_title = title_series
            elif media == "person" and title_person:
                title = f"{title_person} ({_('Person')})"
                search_title = title_person
            elif menu_selection and title_movie:
                media = "movie"
                title = f"{title_movie} ({_('Movie')}, {date_movie[:4]})"
                search_title = title_movie
            else:
                media = ""

            if media == "person":
                cover_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.cover_size.value}{profile_path}"
            else:
                cover_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.cover_size.value}{cover_path}"
            backdrop_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.backdrop_size.value}{backdrop_path}"

            logger.debug("ident: %s, title: %s, media: %s",
                         ident, title, media)
            if ident and title and media:
                res.append(
                    (title, ident, media, cover_url, backdrop_url, search_title))
        del json_data
        return totalpages, res
