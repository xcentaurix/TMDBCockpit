# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

import os
from twisted.internet import threads, reactor
from PIL import Image
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger
from .Utils import temp_dir
from .WebRequests import WebRequests
from .FileUtils import deleteFile


class Picture(WebRequests):
    def __init__(self):
        WebRequests.__init__(self)
        self.ident = None

    def showPicture(self, widget, atype, ident, url):
        logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
        self.ident = ident
        path = os.path.join(temp_dir, f"{atype}{ident}.jpg")
        if url and not url.endswith("None") and not os.path.isfile(path):
            threads.deferToThread(self.downloadPicture,
                                  widget, ident, atype, url, path)
        else:
            self.displayPicture(ident, widget, path)

    def downloadPicture(self, widget, ident, atype, url, path):
        logger.info("atype: %s, ident: %s, url: %s, path: %s", atype, ident, url, path)
        try:
            if atype == 'backdrop':
                logger.debug("Downloading backdrop to path: %s", path)
                path_name, path_ext = os.path.splitext(path)
                path_name = os.path.basename(path_name)
                path_dir = os.path.dirname(path)
                tmp_path = os.path.join(path_dir, f"tmp_{path_name}{path_ext}")
                self.downloadFile(url, tmp_path)

                # if type is 'backdrop' construct overlay
                logger.debug("tmp_path: %s", tmp_path)
                # get widget size
                width = 1920
                height = 1080
                if widget and widget.instance:
                    size = widget.instance.size()
                    width = size.width()
                    height = size.height()
                    logger.debug("Widget size: %dx%d", width, height)

                # Use compatible resampling filter
                try:
                    resample = Image.Resampling.LANCZOS
                except AttributeError:
                    resample = Image.LANCZOS

                img = None
                dim = None
                out = None
                try:
                    # load original jpg
                    with Image.open(tmp_path) as base_img:
                        img = base_img.convert("RGBA")
                    # scale to widget size (or fallback to 1920x1080)
                    img = img.resize((width, height), resample)
                    logger.debug("Scaled backdrop to widget size: %dx%d", width, height)
                    # construct dim layer
                    dim = Image.new("RGBA", img.size, (0, 0, 0, 160))  # 160 ~57% opacity
                    # merge dim layer with the image
                    out = Image.alpha_composite(img, dim)
                    # save merged image to original path
                    out.convert("RGB").save(path, quality=95)
                finally:
                    # Clean up image objects
                    if out:
                        out.close()
                    if dim:
                        dim.close()
                    if img:
                        img.close()
                    deleteFile(tmp_path)
            else:
                logger.debug("Downloaded cover to path: %s", path)
                self.downloadFile(url, path)
        except Exception as e:
            logger.error("Error processing picture: %s", str(e))
        finally:
            reactor.callFromThread(self.displayPicture, ident, widget, path)

    def displayPicture(self, ident, widget, path):
        logger.info("...")
        if widget and widget.instance and ident == self.ident:
            if path and os.path.isfile(path):
                widget.instance.setPixmap(LoadPixmap(path))
                widget.show()
            else:
                logger.debug("picture does not exist: %s", path)
                widget.hide()
