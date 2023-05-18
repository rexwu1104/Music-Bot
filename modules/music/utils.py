import toml

config = toml.load("config.toml")

def get_youtube_cookie() -> str | None:
    if 'youtube' in config:
        return config['youtube'].get('cookie', None)
    else: return None

def get_spotify_id() -> str | None:
    if 'spotify' in config:
        return config['spotify'].get('id', None)
    else: return None
    
def get_spotify_secret() -> str | None:
    if 'spotify' in config:
        return config['spotify'].get('secret', None)
    else: return None
    
def get_soundcloud_id() -> str | None:
    if 'soundcloud' in config:
        return config['soundcloud'].get('id', None)
    else: return None
    
import re
    
youtube_single_re = re.compile('(?:www\.)?youtu\.?be(?:\.com)?/(?:watch\?v=)?[A-Za-z0-9-_]{11,11}')
spotify_single_re = re.compile('open\.spotify\.com/track/[A-Za-z0-9-_]{22,22}')
soundcloud_single_re = re.compile('soundcloud\.com/[a-z0-9-]+/[a-z0-9-]+')

youtube_playlist_re = re.compile('www\.youtube\.com/playlist\?list=[A-Za-z0-9-_]{34,34}')
spotify_playlist_re = re.compile('open\.spotify\.com/(?:album|playlist)/[A-Za-z0-9-_]{22,22}')
soundcloud_playlist_re = re.compile('soundcloud\.com/[a-z0-9-]+/sets/[a-z0-9-]+')