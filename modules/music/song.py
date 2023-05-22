import discord
import spotipy
import sclib

from typing import Any, Optional

from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials

from .utils import *
from ..logger import Logger

class TimedableAudioSource(discord.PCMVolumeTransformer):
    position: float
    def __init__(self, original: Any, volume: float = 1):
        super().__init__(original, volume)
        self.position = 0.0
        
    def cleanup(self) -> None:
        self.position = 0.0
        return super().cleanup()
    
    def read(self) -> bytes:
        byte = super().read()
        if byte == b'':
            self.position = .0
            return byte
        else:
            self.position += .002
            return byte

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
    
    @property
    def duration(self) -> int: ...
    @property
    def uploader(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def thumbnail(self) -> str: ...
    @property
    def like_count(self) -> str: ...
    @property
    def target_url(self) -> str: ...
    @property
    def watch_count(self) -> str: ...
        
class Youtube(Song):
    __data: dict[str]
    __yt_downloader: YoutubeDL = YoutubeDL({
        'format': 'bestaudio/best',
        'no_warnings': True,
        'logger': Logger('youtube'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192'
        }],
        'cookfile': "cookies.txt"
    })
    
    def __init__(self, url: str):
        super().__init__(url)
        if self.enable:
            with self.__yt_downloader as ydl:
                self.__data = ydl.extract_info(self.url, download=False)
                if 'entries' in self.__data:
                    self.__data = self.__data['entries'].pop(0)
    
    @classmethod
    def search(cls, query: str) -> Song:
        return cls(f"ytsearch:{query}")
        
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            return discord.FFmpegPCMAudio(self.__data['url'], **self.ffmpeg_options)
        
    @property
    def duration(self) -> int:
        return self.__data.get('duration', -1)
    
    @property
    def uploader(self) -> str:
        return self.__data.get('uploader', 'unknown uploader')
    
    @property
    def name(self) -> str:
        return self.__data.get('title', 'unknown title')
    
    @property
    def thumbnail(self) -> str:
        return self.__data.get('thumbnail', 'https://i.imgur.com/6uXXT2P.png')
    
    @property
    def like_count(self) -> str:
        return self.__data.get('like_count', '0')
    
    @property
    def target_url(self) -> str:
        return self.__data.get('webpage_url', 'https://www.youtube.com/')
    
    @property
    def watch_count(self) -> str:
        return self.__data.get('view_count', '0')

class Spotify(Song):
    __data: dict[str]
    
    __client: spotipy.Spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=get_spotify_id(),
        client_secret=get_spotify_secret()
    ))
    __sp_downloader: YoutubeDL = YoutubeDL({
        'format': 'bestaudio/best',
        'no_warnings': True,
        'logger': Logger('spotify'),
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
            self.__data = self.__client.track(self.url)
    
    def __get_artist_names(self, artists: list[dict[str, Any]]) -> list[str]:
        return [artist.get('name', 'unknown') for artist in artists]
    
    @classmethod
    def search(cls, query: str) -> Song:
        return cls(cls.__client.search(f"{query.replace(' ', '%20')}&include_external=audio")['tracks']['items'][0]['external_urls']['spotify'])
    
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            search = 'ytsearch:{} - {}'.format(
                (self.__get_artist_names(self.__data["artists"])
                    if "artists" in self.__data
                    else [self.__data["show"].get("publisher", "unknown")])[0],
                self.__data.get("name", "unknown")
            )
            
            with self.__sp_downloader as sdl:
                info = sdl.extract_info(search, download=False)
                if 'entries' in info:
                    info = info['entries'].pop(0)
                
            return discord.FFmpegPCMAudio(info['url'], **self.ffmpeg_options)
        
    @property
    def duration(self) -> int:
        return self.__data.get('duration_ms', -1000) // 1000
    
    @property
    def uploader(self) -> str:
        return safe_list_get(self.__data['artists'], 0, {}).get('name', "unknown uploader")
    
    @property
    def name(self) -> str:
        return self.__data.get('name', 'unknown title')
    
    @property
    def thumbnail(self) -> str:
        return safe_list_get(self.__data['album']['images'], 0, {}).get('url', 'https://i.imgur.com/Et5AJpz.png')
    
    @property
    def like_count(self) -> str:
        return self.__data.get('popularity', '0')
    
    @property
    def target_url(self) -> str:
        return self.__data['external_urls'].get('spotify', 'https://open.spotify.com/')
    
    @property
    def watch_count(self) -> str:
        return 'unknown'

class SoundCloud(Song):
    __api: sclib.SoundcloudAPI
    __data: sclib.Track
    
    def __init__(self, url: str):
        super().__init__(url)
        if get_soundcloud_id() is None:
            SoundCloud.enabled = False
        else:
            self.__api = sclib.SoundcloudAPI(get_soundcloud_id())
            self.__data = self.__api.resolve(self.url)
    
    @classmethod
    def search(cls, query: str) -> Song:
        return Youtube.search(query)
    
    def to_source(self) -> Optional[discord.AudioSource]:
        if self.enabled:
            url = self.__data.get_stream_url()
                
            return discord.FFmpegPCMAudio(url, **self.ffmpeg_options)
        
    @property
    def duration(self) -> int:
        return self.__data.duration
    
    @property
    def uploader(self) -> str:
        return self.__data.artist
    
    @property
    def name(self) -> str:
        return self.__data.title
    
    @property
    def thumbnail(self) -> str:
        return self.__data.artwork_url
    
    @property
    def like_count(self) -> str:
        return self.__data.likes_count
    
    @property
    def target_url(self) -> str:
        return self.__data.permalink_url
    
    @property
    def watch_count(self) -> str:
        return self.__data.user