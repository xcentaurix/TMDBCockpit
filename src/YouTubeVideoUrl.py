# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


try:
    from yt_dlp import YoutubeDL
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False


class YouTubeVideoUrl():

    @staticmethod
    def _extract_with_ytdlp(video_id):
        """Extract video URL using yt-dlp Python library"""
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 10,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_id, download=False)
                url = info.get('url')
                if not url:
                    formats = info.get('requested_formats')
                    if formats:
                        url = formats[0].get('url')
                if url:
                    print('[YouTubeVideoUrl] yt-dlp extracted URL successfully')
                    return url
        except Exception as ex:
            print('[YouTubeVideoUrl] yt-dlp extraction failed:', ex)
        return None

    def extract(self, video_id, yt_auth=None):
        if not HAS_YTDLP:
            raise RuntimeError('python3-yt-dlp is not installed. Install it with: opkg install python3-yt-dlp')
        url = self._extract_with_ytdlp(video_id)
        if url:
            return url
        raise RuntimeError('Failed to extract YouTube video URL')
