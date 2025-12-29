#!/bin/sh
rm -f /etc/opkg/cockpit-feed.conf
opkg update
src/gz cockpit https://xcentaurix.github.io/Cockpit-Feed/packages/all > /etc/opkg/cockpit-feed-all.conf
opkg update
opkg install enigma2-plugin-extensions-tmdbcockpit
init 2
init 3
