# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.PluginComponent import plugins


WHERE_SEARCH = -99
WHERE_TMDB_SEARCH = -98
WHERE_TMDB_MOVIELIST = -97
WHERE_MEDIATHEK_SEARCH = -96
WHERE_TVMAGAZINE_SEARCH = -95
WHERE_COVER_DOWNLOAD = -94
WHERE_JOBCOCKPIT = -93


def getPlugin(where):
    plugin = None
    plugins_list = plugins.getPlugins(where=where)
    if plugins_list:
        plugin = plugins_list[0]
    return plugin
