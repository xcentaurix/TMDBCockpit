# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

import os
from twisted.internet import threads, reactor
from PIL import Image
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger
from .Utils import temp_dir
from .WebRequests import WebRequests


class Picture(WebRequests):
    def __init__(self):
        WebRequests.__init__(self)
        self.ident = None

    def showPicture(self, widget, atype, ident, url):
        logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
        self.ident = ident
        path = temp_dir + atype + str(ident) + ".jpg"
        if url and not url.endswith("None") and not os.path.isfile(path):
            threads.deferToThread(self.downloadPicture,
                                  widget, ident, atype, url, path)
        else:
            self.displayPicture(ident, widget, path)

    def downloadPicture(self, widget, ident, atype, url, path):
        logger.info("...")
        self.downloadFile(url, path)
        # if type is 'backdrop' construct overlay in code
        if atype == 'backdrop':
            # load original jpg
            with Image.open(path) as base_img:
                img = base_img.convert("RGBA")
            # construct dim layer
            dim = Image.new("RGBA", img.size, (0, 0, 0, 160))  # 160 ~57% opacity
            # merge dim layer with the image
            out = Image.alpha_composite(img, dim)
            # save merged image to original path
            out.convert("RGB").save(path, quality=95)
            # Clean up image objects
            out.close()
            dim.close()
            img.close()
        reactor.callFromThread(self.displayPicture, ident, widget, path)  # pylint: disable=no-member

    def displayPicture(self, ident, widget, path):
        logger.info("...")
        if widget and widget.instance and ident == self.ident:
            if path and os.path.isfile(path):
                widget.instance.setPixmap(LoadPixmap(path))
                widget.show()
            else:
                logger.debug("picture does not exist: %s", path)
                widget.hide()
