#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2026 by xcentaurix
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
from PIL import Image
from Tools.LoadPixmap import LoadPixmap
from twisted.internet import reactor, threads
from .Debug import logger
from .Utils import temp_dir
from .WebRequestsAsync import WebRequestsAsync


class Picture(WebRequestsAsync):
    def __init__(self):
        WebRequestsAsync.__init__(self)
        # Dictionary to track pending downloads and their associated pixmaps
        self.pending_downloads = {}
        self.download_counter = 0

    def showPicture(self, pixmap, atype, ident, url):
        logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
        path = temp_dir + atype + str(ident) + ".jpg"

        file_exists = os.path.isfile(path)
        logger.info("path: %s, file_exists: %s", path, file_exists)

        if url and not url.endswith("None") and not file_exists:
            logger.info("Starting download for %s (atype: %s, ident: %s)", path, atype, ident)
            # Create unique download ID and store pixmap reference
            self.download_counter += 1
            download_id = self.download_counter

            # Store pixmap reference with strong reference to prevent GC
            self.pending_downloads[download_id] = {
                'pixmap': pixmap,
                'path': path,
                'url': url,
                'atype': atype,
                'ident': ident
            }

            # Use WebRequestsAsync for downloading
            downloader = self.downloadFileAsync(url, path)
            downloader.addCallback(lambda result: self.downloadComplete(download_id, result))
            downloader.addErrback(lambda error: self.downloadError(download_id, error))
            downloader.start()
        else:
            if file_exists:
                logger.debug("File already exists, displaying directly: %s", path)
            elif not url or url.endswith("None"):
                logger.debug("No valid URL, skipping: url=%s", url)
            self.displayPictureDirectly(pixmap, path)

    def downloadComplete(self, download_id, path):
        """Callback when download completes successfully"""
        logger.info("Download completed successfully for %s (ID: %s)", path, download_id)

        # Schedule UI updates on the main thread to avoid blocking
        reactor.callFromThread(self._handleDownloadComplete, download_id, path)  # pylint: disable=no-member

    def _handleDownloadComplete(self, download_id, path):
        """Handle download completion on the main thread"""
        if download_id in self.pending_downloads:
            download_info = self.pending_downloads[download_id]
            pixmap = download_info['pixmap']
            atype = download_info['atype']

            # Clean up the pending download
            del self.pending_downloads[download_id]

			# if type is 'backdrop' construct overlay in code
            if atype == 'backdrop':
                # load original jpg
                img = Image.open(path).convert("RGBA")
				# construct dim layer
                dim = Image.new("RGBA", img.size, (0, 0, 0, 160))  # 160 ~57% oppacity
				# merge dim layer with the image
                out = Image.alpha_composite(img, dim)
				# save merged image to original path
                out.convert("RGB").save(path, quality=95)

            # Display the picture with the correct pixmap (now on main thread)
            self.displayPictureDirectly(pixmap, path)
        else:
            logger.warning("Download ID %s not found in pending downloads", download_id)

    def downloadError(self, download_id, error):
        """Callback when download fails"""
        logger.error("Download failed (ID: %s): %s", download_id, error)

        # Schedule UI updates on the main thread to avoid blocking
        reactor.callFromThread(self._handleDownloadError, download_id)  # pylint: disable=no-member

    def _handleDownloadError(self, download_id):
        """Handle download error on the main thread"""
        if download_id in self.pending_downloads:
            download_info = self.pending_downloads[download_id]
            pixmap = download_info['pixmap']

            # Clean up the pending download
            del self.pending_downloads[download_id]

            # Hide the pixmap widget (now on main thread)
            if pixmap and hasattr(pixmap, 'hide'):
                pixmap.hide()
        else:
            logger.warning("Download ID %s not found in pending downloads", download_id)

    def displayPictureDirectly(self, pixmap, path):
        """Display picture directly to the specified pixmap widget"""
        logger.info("Displaying picture from %s", path)

        if not pixmap:
            logger.warning("Pixmap widget is None!")
            return

        if not pixmap.instance:
            logger.warning("Pixmap widget has no instance!")
            return

        if not path:
            logger.warning("Path is None or empty!")
            pixmap.hide()
            return

        if not os.path.isfile(path):
            logger.warning("File does not exist: %s - hiding widget", path)
            pixmap.hide()
            return

        # Get widget size for proper scaling
        size = pixmap.instance.size()
        width = size.width()
        height = size.height()

        # Skip loading if widget has no size (not laid out yet)
        if width <= 0 or height <= 0:
            logger.warning("Widget has invalid size: %dx%d, skipping load", width, height)
            pixmap.hide()
            return

        logger.debug("Widget size: %dx%d for %s", width, height, path)

        # Load pixmap in background thread to avoid blocking UI
        d = threads.deferToThread(self.loadPixmapInThread, path, width, height)
        d.addCallback(lambda result: self.displayPixmap(pixmap, result))
        d.addErrback(lambda error: self.loadPixmapError(pixmap, error))

    def loadPixmapInThread(self, path, width, height):
        """Load and scale pixmap in background thread (runs in thread pool)"""
        logger.debug("Loading pixmap in thread: %s (%dx%d)", path, width, height)
        try:
            # LoadPixmap automatically scales to width/height
            # Signature: LoadPixmap(path, desktop=None, cached=None, width=0, height=0)
            # cached=True enables Enigma2's pixmap cache for decoded images
            pixmap = LoadPixmap(path, desktop=None, cached=False, width=width, height=height)

            if pixmap:
                logger.debug("Pixmap loaded successfully: %s", path)
                return pixmap
            logger.error("LoadPixmap returned None for: %s", path)
            return None
        except Exception as e:
            logger.error("Error loading pixmap %s: %s", path, e)
            return None

    def displayPixmap(self, widget, pixmap):
        """Display the loaded pixmap on the widget (runs in main thread via reactor callback)"""
        logger.debug("Displaying pixmap on widget")
        # This callback is already on the main thread thanks to deferToThread
        if widget and widget.instance:
            try:
                if pixmap:
                    widget.instance.setPixmap(pixmap)
                    widget.show()
                    logger.debug("Pixmap displayed successfully")
                else:
                    logger.warning("Pixmap is None, hiding widget")
                    widget.hide()
            except Exception as e:
                logger.error("Error setting pixmap on widget: %s", e)
                if hasattr(widget, 'hide'):
                    widget.hide()
        else:
            logger.warning("Widget or widget.instance is None")

    def loadPixmapError(self, widget, error):
        """Handle pixmap loading error (runs in main thread)"""
        logger.error("Pixmap loading error: %s", error)
        if widget and hasattr(widget, 'hide'):
            widget.hide()

    def cancelPendingDownloads(self):
        """Cancel all pending downloads and clean up references"""
        logger.info("Cancelling %d pending downloads", len(self.pending_downloads))

        # Clear all pending downloads to release pixmap references
        for download_id in list(self.pending_downloads.keys()):
            logger.debug("Cancelling download ID: %s", download_id)
            del self.pending_downloads[download_id]

        # Reset counter
        self.download_counter = 0
