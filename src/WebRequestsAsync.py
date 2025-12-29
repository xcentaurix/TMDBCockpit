# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
import threading
import requests
from .WebRequests import WebRequests
from .Debug import logger


class WebRequestsAsync(WebRequests):
    def __init__(self):
        """
        Initialize the WebRequestsAsync class
        """
        WebRequests.__init__(self)

    def downloadFileAsync(self, url, path):
        """
        Asynchronous version of downloadFile that supports callbacks
        Returns a Downloader object with addCallback, addErrback, and addProgback methods
        """
        logger.info("url: %s, path: %s", url, path)
        return Downloader(self, url, path)

    def getContentAsync(self, url, params=None):
        """
        Asynchronous version of getContent that supports callbacks
        Returns a ContentGetter object with addCallback and addErrback methods
        """
        logger.info("url: %s", url)
        return ContentGetter(self, url, params)

    def postContentAsync(self, url, data=None):
        """
        Asynchronous version of postContent that supports callbacks
        Returns a ContentPoster object with addCallback and addErrback methods
        """
        logger.info("url: %s", url)
        return ContentPoster(self, url, data)


class BaseRequestHandler:
    """Base class for async request handlers"""

    def __init__(self):
        self.callback = None
        self.errback = None
        self._cancelled = False
        self._session = None
        self._thread = None

    def addCallback(self, callback):
        self.callback = callback
        return self

    def addErrback(self, errback):
        """Add callback for request errors"""
        self.errback = errback
        return self

    def cancel(self):
        """Cancel the request process"""
        self._cancelled = True
        if self._session:
            self._session.close()  # Force-close the session
        if self._thread and self._thread.is_alive():
            # Note: We can't force-kill a thread in Python, but we set the cancelled flag
            # and the thread will check it and exit gracefully
            pass
        return True

    def _callCallback(self, result):
        """Call callback in a thread-safe way"""
        if self.callback:
            try:
                self.callback(result)
            except Exception as e:
                logger.error("Error in callback: %s", e)

    def _callErrback(self, error):
        """Call errback in a thread-safe way"""
        if self.errback:
            try:
                self.errback(error)
            except Exception as e:
                logger.error("Error in errback: %s", e)


class Downloader(BaseRequestHandler):
    """Helper class for asynchronous downloads with callback support"""

    def __init__(self, client, url, path):
        BaseRequestHandler.__init__(self)
        self.client = client
        self.url = url
        self.path = path
        self.progback = None
        self.total_size = 0
        self.downloaded = 0

    def addProgback(self, progback):
        """Add callback for download progress updates"""
        self.progback = progback
        return self

    def start(self):
        """Start the download process"""
        self._thread = threading.Thread(target=self.execute)
        self._thread.daemon = True
        self._thread.start()
        return self

    def execute(self):
        """Execute the download process"""
        try:
            self._cancelled = False
            self._session = requests.Session()  # Create and store session

            headers = {"user-agent": self.client.getUserAgent()}
            response = self._session.get(self.url, headers=headers, stream=True, allow_redirects=True, verify=False)
            logger.debug("response.url: %s", response.url)
            logger.debug("response.status_code: %s", response.status_code)
            response.raise_for_status()

            self.total_size = int(response.headers.get('content-length', 0))
            self.downloaded = 0

            with open(self.path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # Check if cancelled before processing each chunk
                    if self._cancelled:
                        logger.debug("Download cancelled during chunk processing")
                        response.close()
                        break

                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        self.downloaded += len(chunk)
                        if self.progback and self.total_size:
                            progress = int(100 * self.downloaded / self.total_size)
                            self.progback(self.downloaded, self.total_size, progress)

            response.close()

            if self._cancelled:
                self._callErrback("cancelled")
                return False

            self._callCallback(self.path)
            return True
        except Exception as e:
            logger.error("exception: %s", e)
            self._callErrback(e)
            return False


class ContentGetter(BaseRequestHandler):
    """Helper class for asynchronous GET requests with callback support"""

    def __init__(self, web_requests, url, params=None):
        BaseRequestHandler.__init__(self)
        self.web_requests = web_requests
        self.url = url
        self.params = params if params is not None else {}

    def start(self):
        """Start the GET request process"""
        self._thread = threading.Thread(target=self.execute)
        self._thread.daemon = True
        self._thread.start()
        return self

    def execute(self):
        """Execute the GET request process"""
        try:
            self._cancelled = False
            self._session = requests.Session()  # Create and store session

            headers = {"user-agent": self.web_requests.getUserAgent()}
            response = self._session.get(
                self.url, headers=headers, params=self.params,
                allow_redirects=True, verify=False, stream=True
            )
            logger.debug("response.url: %s", response.url)
            logger.debug("response.status_code: %s", response.status_code)

            # Check if cancelled before reading content
            if self._cancelled:
                logger.debug("Request cancelled before reading content")
                response.close()
                return None

            # Read the content
            content = response.content
            response.raise_for_status()

            # Check if cancelled before calling callback
            if self._cancelled:
                self._callErrback("cancelled")
                return None

            self._callCallback(content)
            return content
        except Exception as e:
            logger.error("exception: %s", e)
            if not self._cancelled:
                self._callErrback(e)
            return None


class ContentPoster(BaseRequestHandler):
    """Helper class for asynchronous POST requests with callback support"""

    def __init__(self, web_requests, url, data=None):
        BaseRequestHandler.__init__(self)
        self.web_requests = web_requests
        self.url = url
        self.data = data if data is not None else {}

    def start(self):
        """Start the POST request process"""
        self._thread = threading.Thread(target=self.execute)
        self._thread.daemon = True
        self._thread.start()
        return self

    def execute(self):
        """Execute the POST request process"""
        try:
            self._cancelled = False
            self._session = requests.Session()  # Create and store session

            headers = {"user-agent": self.web_requests.getUserAgent(), "Content-Type": "text/plain"}

            # Check if cancelled before making request
            if self._cancelled:
                logger.debug("POST request cancelled before execution")
                return None

            response = self._session.post(
                self.url, headers=headers, data=json.dumps(self.data),
                allow_redirects=True, verify=False
            )
            logger.debug("response.url: %s", response.url)
            logger.debug("response.status_code: %s", response.status_code)

            # Check if cancelled before processing response
            if self._cancelled:
                logger.debug("POST request cancelled after execution")
                response.close()
                return None

            response.raise_for_status()
            logger.debug("response.text: %s", response.text)
            content = response.text

            # Check if cancelled before calling callback
            if self._cancelled:
                self._callErrback("cancelled")
                return None

            self._callCallback(content)
            return content
        except Exception as e:
            logger.error("exception: %s", e)
            if not self._cancelled:
                self._callErrback(e)
            return None
