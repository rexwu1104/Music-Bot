import unittest
import logging

import spotipy
import sclib
import discord

from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials

class DownloadTest(unittest.TestCase):
    def __get_artist_names(self, artists) -> list[str]:
        return [artist.get('name', 'unknown') for artist in artists['artists']]
    
    def spotify_download(self):
        client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="7e4d26d0223e4917832b54216ff8169e",
            client_secret="574aeb7662c143b3a018c860d293b8fe"
        ))
        __sp_downloader: YoutubeDL = YoutubeDL({
            'format': 'bestaudio/best',
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredquality': '192'
            }],
            'logger': logging.getLogger('none')
        })
        
        track = client.track("https://open.spotify.com/track/4BvuZVf9KyBN3QiPfeI9hw")
        search = f'ytsearch:{(self.__get_artist_names(track) if "artists" in track else [track["show"].get("publisher", "unknown")])[0]} - {track.get("name", "unknown")} audio'
        
        with __sp_downloader as sdl:
            info = sdl.extract_info(search, download=False)
            
    def soundcloud_download(self):
        __api: sclib.SoundcloudAPI = sclib.SoundcloudAPI("DgFeY88vapbGCcK7RrT2E33nmNQVWX82")
        
        data = __api.resolve("https://soundcloud.com/leftalivemecha71/oshi-no-ko-op-opening-full-6")
        url = data.get_stream_url()
        print(url)