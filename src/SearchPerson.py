# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from . import tmdbsimple as tmdb
from .Debug import logger
from .Json import Json
from .Parsers import Parsers


class SearchPerson(Parsers, Json):
    def __init__(self):
        Parsers.__init__(self)
        Json.__init__(self)

    def getResult(self, result, ident):
        logger.debug("ident: %s", ident)
        keys = ["biography", "name", "birthday", "place_of_birth", "gender",
                "also_known_as", "popularity", "movie_credits", "tv_credits"]
        for lang in (config.plugins.tmdbcockpit.lang.value, "en"):
            json_data = tmdb.People(ident).info(
                language=lang, append_to_response="movie_credits, tv_credits")
            # logger.debug("json_data: %s", json_data)
            self.parseJson(result, json_data, keys)
            if result["biography"]:
                break

        logger.debug("result: %s", result)

        self.parsePersonGender(result)
        self.parseJsonList(result, "also_known_as", ",")
        result["popularity"] = f"{float(result['popularity']):.1f}"

        data_movies = []
        for source in (
                (result["movie_credits"], ["release_date", "title", "character"], "movie"),
                (result["tv_credits"], ["first_air_date", "name", "character"], "tv")):
            result2 = {}
            self.parseJson(result2, source[0], ["cast"])
            logger.debug("result2: %s", result2)
            for cast in result2["cast"]:
                logger.debug("cast: %s", cast)
                movie = {}
                self.parseJson(movie, cast, source[1])
                logger.debug("movie: %s", movie)
                if source[2] == "movie":
                    if movie["release_date"] != "None":
                        data_movies.append(
                            f"{movie['release_date']} {movie['title']} ({movie['character']})")
                elif movie["first_air_date"] != "None":
                    data_movies.append(
                        f"{movie['first_air_date']} {movie['name']} ({movie['character']})")
        data_movies.sort(reverse=True)
        movies = "\n".join(data_movies)
        result["movies"] = movies
        del json_data
        return result
