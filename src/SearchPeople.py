# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from . import tmdbsimple as tmdb
from .Debug import logger
from .Json import Json


class SearchPeople(Json):
    def __init__(self):
        Json.__init__(self)

    def getResult(self, res, ident, media):
        logger.info("ident: %s", ident)
        json_data = {}
        lang = config.plugins.tmdbcockpit.lang.value
        if media == "movie":
            json_data = tmdb.Movies(ident).credits(language=lang)
            logger.debug("json_data: %s", json_data)
        if media == "tv":
            json_data = tmdb.TV(ident).info(
                language=lang, append_to_result="credits")
            logger.debug("json_data: %s", json_data)

        result = {}
        self.parseJson(result, json_data, ["cast", "seasons", "credits"])

        for casts in result["cast"]:
            result2 = {}
            keys = ["id", "name", "profile_path", "character"]
            self.parseJson(result2, casts, keys)
            cover_ident = result2["id"]
            name = result2["name"]
            title = f"{result2['name']} ({result2['character']})"
            cover_path = result2["profile_path"]
            cover_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.cover_size.value}/{cover_path}"
            if cover_ident and name != "None":
                res.append((title, name, cover_url, cover_ident))

        if media == "tv":
            season_number = 1
            for season in result["seasons"]:
                # logger.debug("######: %s", season)
                result2 = {}
                keys2 = ["season_number", "id", "name", "air_date"]
                self.parseJson(result2, season, keys2)
                season_number = result2["season_number"]
                # logger.debug("#########: %s", result2["season_number"])
                cover_ident = result2["id"]
                name = result2["name"]
                date = result2["air_date"][:4]
                title = f"{name} ({date})"
                logger.debug("title: %s", title)
                logger.debug("name: %s", name)
                if name != "None":
                    res.append((title, name, None, ""))

                    json_data = tmdb.TV_Seasons(
                        ident, season_number).credits(language=lang)
                    result3 = {}
                    self.parseJson(result3, json_data, ["cast"])
                    for casts in result3["cast"]:
                        result4 = {}
                        keys4 = ["id", "name", "character", "profile_path"]
                        self.parseJson(result4, casts, keys4)
                        cover_ident = result4["id"]
                        name = result4["name"]
                        character = result4["character"]
                        title = f"    {name} ({character})"
                        cover_path = result4["profile_path"]
                        cover_url = f"http://image.tmdb.org/t/p/{config.plugins.tmdbcockpit.cover_size.value}{cover_path}"

                        if cover_ident and name != "None":
                            res.append(
                                (title, name, cover_url, cover_ident))
        del json_data
        logger.debug("res: %s", res)
        return res
