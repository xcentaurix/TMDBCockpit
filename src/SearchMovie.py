# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from Components.config import config
from . import tmdbsimple as tmdb
from .__init__ import _
from .Debug import logger
from .Json import Json
from .Parsers import Parsers


class SearchMovie(Parsers, Json):
    def __init__(self):
        Parsers.__init__(self)
        Json.__init__(self)

    def getResult(self, result, ident, media):
        logger.debug("ident: %s, media: %s", ident, media)
        json_data = {}
        keys_movie = ["title", "original_title", "overview", "year", "vote_average", "vote_count", "runtime", "production_countries",
                      "production_companies", "genres", "tagline", "release_date", "seasons", "videos", "credits", "releases"]
        keys_tv = keys_movie + ["name", "first_air_date", "origin_country", "created_by",
                                "networks", "number_of_seasons", "number_of_episodes", "credits", "content_ratings"]
        for lang in (config.plugins.tmdbcockpit.lang.value, "en"):
            if media == "movie":
                json_data = tmdb.Movies(ident).info(
                    language=lang, append_to_response="videos,credits,releases")
                # logger.debug("json_data: %s", json_data)
                self.parseJson(result, json_data, keys_movie)
                if result["overview"]:
                    break
            if media == "tv":
                json_data = tmdb.TV(ident).info(
                    language=lang, append_to_response="videos,credits,content_ratings")
                # logger.debug("json_data: %s", json_data)
                self.parseJson(result, json_data, keys_tv)
                if result["overview"]:
                    break
            del json_data

        # base for movie and tv series
        result["year"] = result["release_date"][:4]
        result["rating"] = f"{float(result['vote_average']):.1f}"
        result["votes"] = str(result["vote_count"])
        result["votes_brackets"] = f"({str(result['vote_count'])})"
        result["runtime"] = f"{result['runtime']} {_('min')}"

        self.parseCountry(result)
        self.parseGenre(result)
        self.parseCast(result)
        self.parseCrew(result)
        self.parseStudio(result)
        self.parseFsk(result, media)

        if media == "movie":
            result["seasons"] = ""
            self.parseMovieVideos(result)

        elif media == "tv":
            # modify data for TV/Series
            result["year"] = result["first_air_date"][:4]

            self.parseTVCountry(result)
            self.parseTVCrew(result)
            self.parseTVStudio(result)
            self.parseTVSeasons(result)

        result["fulldescription"] = \
            f"{result['tagline']}\n" \
            + f"{result['genre']}, {result['country']}, {result['year']}\n\n" \
            + f"{result['overview']} \n\n" \
            + f"{result['cast']}\n{result['crew']}\n{result['seasons']}\n"
        logger.debug("result: %s", result)
        return result
