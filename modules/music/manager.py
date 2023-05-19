import asyncio

import discord

from typing import Optional
from dataclasses import dataclass
from functools import partial

from discord.ext import commands

from .song import *
from .utils import (
    youtube_single_re,
    spotify_single_re,
    soundcloud_single_re,
    youtube_playlist_re,
    spotify_playlist_re,
    soundcloud_playlist_re
)

from ..logger import Logger

__all__ = (
    'GuildController',
    'Manager'
)

class GuildController:
    guild: discord.Guild
    connection: Optional[discord.VoiceClient]
    bot: "Bot"
    
    volume: int
    prevs: list[Song]
    current: Optional[Song]
    afters: list[Song]
    full: list[Song]
    
    class Guild:
        id: int
        
        def __init__(self, id: int) -> None:
            self.id = id
    
    def __init__(self, bot: "Bot", guild: discord.Guild | int) -> None:
        if isinstance(guild, discord.Guild):
            self.guild = guild
        else:        
            self.guild = GuildController.Guild(guild)
            
        self.connection = None
        self.bot = bot
        self.prevs = []
        self.afters = []
        self.full = []
        self.current = None
        self.volume = 1
            
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, GuildController):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return self.id
    
    @property
    def id(self) -> int:
        return self.guild.id
    
    @property
    def is_playing(self):
        return self.connection is not None and self.connection.is_playing()
    
    @property
    def is_paused(self):
        return self.connection is not None and self.connection.is_paused()
    
    async def __error_process(self, err, ctx: commands.Context):
        if err is not None:
            print(err)
            return
        
        await self.next(ctx)
        
    def append(self, query: str):
        self.bot.manager.logger.info(f"query: {query}")
        if query.startswith('https:'):
            if youtube_single_re.search(query) is not None:
                self.afters.append(Youtube(query))
            if spotify_single_re.search(query) is not None:
                self.afters.append(Spotify(query))
            if soundcloud_single_re.search(query) is not None:
                self.afters.append(SoundCloud(query))
        else:
            if Youtube.enabled:
                self.search_by(query, 'youtube')
            elif Spotify.enabled:
                self.search_by(query, 'spotify')
            else:
                self.search_by(query, 'soundcloud')
                
        self.afters[-1]
        
    def search_by(self, query: str, type: str):
        match type:
            case 'spotify':
                self.afters.append(Spotify.search(query))
            case 'youtube':
                self.afters.append(Youtube.search(query))
            case 'soundcloud':
                self.afters.append(SoundCloud.search(query))
                
    async def with_channel(self, id: int):
        channel = self.bot.get_channel(id)
        assert isinstance(channel, discord.VoiceChannel) or \
               isinstance(channel, discord.StageChannel)
        
        self.connection = await channel.connect()
                
    async def start(self, ctx: commands.Context):
        if self.current is None:
            self.current = self.afters.pop(0)
            
        self.connection.play(
            TimedableAudioSource(self.current.to_source(), self.volume),
            after=lambda err: asyncio.ensure_future(self.__error_process(err, ctx), loop=self.bot.loop))
        await ctx.send(embed=to_embed(ctx, self.current))
        
    async def next(self, ctx: commands.Context):
        self.prevs.append(self.current)
        self.current = None
        
        if len(self.afters):
            await self.start(ctx)

class Manager:
    gourps: set[GuildController]
    logger: Logger
    
    def __init__(self):
        self.gourps = set()
        self.logger = Logger('bot')
        
    def __contains__(self, __value: int) -> bool:
        return GuildController(__value) in self.gourps
    
    def __getitem__(self, id: int) -> Optional[GuildController]:
        for controller in self.gourps:
            if controller.id == id:
                return controller
            
        return None
        
    def add_controller(self, controller: GuildController) -> bool:
        length = len(self.gourps)
        self.gourps.add(controller)
        self.logger.info(f"add controller: {controller.id}")
        return len(self.gourps) == length + 1
    
    def remove_controller(self, id: int) -> bool:
        length = len(self.gourps)
        self.gourps.remove(GuildController(id))
        self.logger.info(f"remove controller: {id}")
        return len(self.gourps) == length - 1
    
@dataclass
class Bot(commands.Bot):
    manager: Manager
        