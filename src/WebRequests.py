# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
import random
import requests
from .Debug import logger


class Content():
    def __init__(self):
        self.text = ""
        self.status_code = "999"


class WebRequests():

    def __init__(self):
        return

    def getUserAgent(self):
        user_agents = [
            'Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20120101 Firefox/35.0',
            'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
        ]
        user_agent = random.choice(user_agents)
        return user_agent

    def getSession(self):
        session = requests.Session()
        session.headers.update({"user-agent": self.getUserAgent()})
        return session

    def postContent(self, url, data=None):
        logger.info("url: %s", url)
        headers = {"user-agent": self.getUserAgent(), "Content-Type": "text/plain"}
        if data is None:
            data = {}
        try:
            content = requests.post(url, headers=headers, data=json.dumps(data), allow_redirects=True, verify=False, timeout=30)
            logger.debug("content.url: %s", content.url)
            logger.debug("content.status_code: %s", content.status_code)
            content.raise_for_status()
        except Exception:
            # logger.error("exception: %s", e)
            content = Content()
        logger.debug("content.text: %s", content.text)
        return content

    def getContent(self, url, params=None):
        logger.info("url: %s", url)
        headers = {"user-agent": self.getUserAgent()}
        if params is None:
            params = {}
        try:
            response = requests.get(url, headers=headers, params=params, allow_redirects=True, verify=False, timeout=30)
            logger.debug("response.url: %s", response.url)
            logger.debug("response.status_code: %s", response.status_code)
            response.raise_for_status()
            # Return decoded text for Python 3 compatibility
            content = response.text
        except Exception as e:
            logger.error("exception: %s", e)
            content = ""
        return content

    def downloadFile(self, url, path):
        """Stream download large files to avoid memory issues"""
        logger.info("url: %s, path: %s", url, path)
        headers = {"user-agent": self.getUserAgent()}
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True, verify=False, timeout=30)
        logger.debug("response.url: %s", response.url)
        logger.debug("response.status_code: %s", response.status_code)
        response.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)

        response.close()
        return True
