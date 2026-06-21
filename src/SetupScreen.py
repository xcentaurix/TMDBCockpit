# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Screens.Setup import Setup
from .__init__ import _
from .Version import PLUGIN
from .Debug import setLogLevel, log_levels


class SetupScreen(Setup):

    def __init__(self, session):
        Setup.__init__(self, session, setup="tmdbcockpit", plugin="Extensions/TMDBCockpit", PluginLanguageDomain=PLUGIN)
        self.setTitle(PLUGIN + " - " + _("Setup"))

    def keySave(self):
        setLogLevel(log_levels[config.plugins.tmdbcockpit.debug_log_level.value])
        Setup.keySave(self)
