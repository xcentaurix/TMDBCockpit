# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from Components.config import config
from . import tmdbsimple as tmdb
from .Debug import logger
from .Json import Json


class SearchTMDB(Json):

    def __init__(self):
        Json.__init__(self)

    def getResult(self, res, text):
        logger.info("text: >%s<", text)
        lang = config.plugins.tmdbcockpit.lang.value
        json_data = {}
        results = {}
        json_data = tmdb.Search().multi(query=text, language=lang)
        self.parseJson(results, json_data, ["results"])
        logger.debug("json_data: %s", json_data)

        for entry in results["results"]:
            logger.debug("entry: %s", entry)
            result = {}
            keys = ["media_type", "id", "title", "original_title", "name", "release_date",
                    "first_air_date", "poster_path", "backdrop_path", "profile_path"]
            self.parseJson(result, entry, keys)

            media = result["media_type"]
            ident = result["id"]
            title = result["title"] if media == "movie" else result["name"]
            cover_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.cover_size.value}{result['poster_path']}"
            backdrop_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.backdrop_size.value}{result['backdrop_path']}"

            logger.debug("ident: %s, title: %s, media: %s",
                         ident, title, media)
            if ident and title and media:
                res.append(((title, ident, media, cover_url, backdrop_url), ))
                break
        del json_data
        return res
