import logging

import discord
import spotipy
import sclib

from typing import Any, Optional
from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials

from .utils import *

class TimedableAudioSource(discord.PCMVolumeTransformer):
    position: float
    def __init__(self, original: Any, volume: float = 1):
        super().__init__(original, volume)
        self.position = 0.0
        
    def cleanup(self) -> None:
        self.position = 0.0
        return super().cleanup()
    
    def read(self) -> bytes:
        self.position += 0.002
        return super().read()

class Song:
    url: str
    enabled: bool = True
    
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }
    
    @classmethod
    def enable(cls, state: bool) -> bool:
        cls.enabled = state
        return cls.enabled
    
    def __init__(self, url: str):
        self.url = url
    
    @classmethod
    def search(self, query: str) -> "Song": ...
    def to_source(self) -> Optional[discord.AudioSource]: ...
        
class Youtube(Song):
    __yt_downloader: YoutubeDL = YoutubeDL({
        'format': 'bestaudio/best',
        'no_warnings': True,
        'logger': logging.getLogger('none'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192'
        }],
        'cookfile': "cookies.txt"
    })
    
    @classmethod
    def search(cls, query: str) -> Song:
        return cls(f"ytsearch:{query} official audio")
        
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            with self.__yt_downloader as ydl:
                info = ydl.extract_info(self.url, download=False)
                if 'entries' in info:
                    info = info['entries'].pop(0)
                
            return discord.FFmpegPCMAudio(info['url'], **self.ffmpeg_options)

class Spotify(Song):
    __client: spotipy.Spotify
    
    __sp_downloader: YoutubeDL = YoutubeDL({
        'format': 'bestaudio/best',
        'no_warnings': True,
        'logger': logging.getLogger('none'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192'
        }]
    })
    
    def __init__(self, url: str):
        super().__init__(url)
        if get_spotify_id() is None or get_spotify_secret() is None:
            Spotify.enabled = False
        else:
            self.__client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=get_spotify_id(),
                client_secret=get_spotify_secret()
            ))
    
    def __get_artist_names(self, artists: list[dict[str, Any]]) -> list[str]:
        return [artist.get('name', 'unknown') for artist in artists]
    
    @classmethod
    def search(cls, query: str) -> Song:
        return cls(cls.__client.search(f"track:{query}")['tracks']['items'][0]['external_urls']['spotify'])
    
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            track = self.__client.track(self.url)
            search = 'ytsearch:{} - {} official'.format(
                (self.__get_artist_names(track["artists"]) if "artists" in track else [track["show"].get("publisher", "unknown")])[0],
                track.get("name", "unknown")
            )
            
            with self.__sp_downloader as sdl:
                info = sdl.extract_info(search, download=False)
                if 'entries' in info:
                    info = info['entries'].pop(0)
                
            return discord.FFmpegPCMAudio(info['url'], **self.ffmpeg_options)

class SoundCloud(Song):
    __api: sclib.SoundcloudAPI
    
    def __init__(self, url: str):
        super().__init__(url)
        if get_soundcloud_id() is None:
            SoundCloud.enabled = False
        else:
            self.__api = sclib.SoundcloudAPI(get_soundcloud_id())
    
    @classmethod
    def search(cls, query: str) -> Song:
        return Youtube.search(query)
    
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            data = self.__api.resolve(self.url)
            url = data.get_stream_url()
                
            return discord.FFmpegPCMAudio(url, **self.ffmpeg_options)