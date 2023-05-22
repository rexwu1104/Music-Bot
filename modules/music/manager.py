import asyncio

import discord

from typing import Optional
from dataclasses import dataclass
from enum import IntEnum

from discord.ext import commands

from .view import *
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
    bot: "Bot"
    __guild: discord.Guild
    __connection: Optional[discord.VoiceClient]
    __interaction: Optional[discord.Interaction]
    
    __volume: int
    __prevs: list[Song]
    __current: Optional[Song]
    __current_source: Optional[TimedableAudioSource]
    __afters: list[Song]
    __lock_list: set[int]
    __repeat_mode: "RepeatEnum"
    
    class RepeatEnum(IntEnum):
        Nothing = 0
        Single = 1
        Full = 2
        Reverse = 3
        Range = 4
    
    def __init__(self, bot: "Bot", guild: discord.Guild | int) -> None:
        if isinstance(guild, discord.Guild):
            self.__guild = guild
        else:        
            self.__guild = discord.Object(id=guild)
            
        self.bot = bot
        self.__connection = None
        self.__interaction = None
        self.__prevs = []
        self.__afters = []
        self.__lock_list = set()
        self.__current = None
        self.__current_source = None
        self.__volume = 1
        self.__repeat_mode = GuildController.RepeatEnum.Nothing
            
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, GuildController):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return self.id
    
    @property
    def id(self) -> int:
        return self.__guild.id
    
    @property
    def repeat_mode(self) -> str:
        return self.__repeat_mode.name
    
    @property
    def duration(self) -> float:
        return self.__current_source.position
    
    @property
    def volume(self) -> int:
        return self.__volume * 100
    
    @property
    def position(self) -> int:
        return len(self.__prevs) + 1
    
    @property
    def length(self) -> int:
        return len(self.__prevs) + 1 + len(self.__afters)
       
    @property
    def is_playing(self):
        return self.__connection is not None and self.__connection.is_playing()
    
    @property
    def is_paused(self):
        return self.__connection is not None and self.__connection.is_paused()
    
    def is_locked(self, id: int) -> bool:
        return id in self.__lock_list
    
    def lock(self, id: int) -> bool:
        self.__lock_list.add(id)
        
    def unlock(self, id: int) -> bool:
        self.__lock_list.remove(id)
        
    async def reset(self):
        await self.__connection.disconnect(force=True)
        await self.__interaction.delete_original_response()
        
        self.__connection = None
        self.__interaction = None
        self.__prevs = []
        self.__afters = []
        self.__lock_list = set()
        self.__current = None
        self.__current_source = None
        self.__volume = 1
        self.__repeat_mode = GuildController.RepeatEnum.Nothing
        
    async def set_interaction(self, interaction: discord.Interaction):
        if self.__interaction is not None:
            await self.__interaction.delete_original_response()
            
        self.__interaction = interaction
    
    async def __error_process(self, err):
        if err is not None:
            print(err)
            return
        
        await self.next()
        
    async def append(self, query: str):
        assert self.__interaction is not None
        self.bot.manager.logger.info(f"query: {query}")
        if query.startswith('https:'):
            if youtube_single_re.search(query) is not None:
                self.__afters.append(Youtube(query))
            if spotify_single_re.search(query) is not None:
                self.__afters.append(Spotify(query))
            if soundcloud_single_re.search(query) is not None:
                self.__afters.append(SoundCloud(query))
        else:
            if Youtube.enabled:
                self.search_by(query, 'youtube')
            elif Spotify.enabled:
                self.search_by(query, 'spotify')
            else:
                self.search_by(query, 'soundcloud')
                
        await self.__interaction.edit_original_response(embed=to_append_embed(self.__interaction, self.__afters[-1]))
        
    def search_by(self, query: str, type: str):
        match type:
            case 'spotify':
                self.__afters.append(Spotify.search(query))
            case 'youtube':
                self.__afters.append(Youtube.search(query))
            case 'soundcloud':
                self.__afters.append(SoundCloud.search(query))
                
    async def with_channel(self):
        assert self.__interaction is not None
        channel = self.bot.get_channel(self.__interaction.user.voice.channel.id)
        assert isinstance(channel, discord.VoiceChannel) or \
               isinstance(channel, discord.StageChannel)
        
        self.__connection = await channel.connect(self_deaf=True)
                
    async def start(self):
        assert self.__interaction is not None
        if self.__current is None:
            self.__current = self.__afters.pop(0)
            self.__current_source = TimedableAudioSource(self.__current.to_source(), self.__volume)
            
        self.__connection.play(
            self.__current_source,
            after=lambda err: asyncio.ensure_future(self.__error_process(err), loop=self.bot.loop))
        
        await self.__interaction.edit_original_response(
            embed=to_embed(self.__interaction, self, self.__current))
        
    async def next(self):
        self.__prevs.append(self.__current)
        self.__current = None
        self.__current_source = None
        
        if len(self.__afters) > 0:
            await self.start()
        else:
            await self.reset()

class Manager:
    logger: Logger
    __gourps: set[GuildController]
    
    def __init__(self):
        self.__gourps = set()
        self.logger = Logger('bot')
        
    def __contains__(self, __value: int) -> bool:
        return GuildController(__value) in self.__gourps
    
    def __getitem__(self, id: int) -> Optional[GuildController]:
        for controller in self.__gourps:
            if controller.id == id:
                return controller
            
        return None
        
    def add_controller(self, controller: GuildController) -> bool:
        length = len(self.__gourps)
        self.__gourps.add(controller)
        self.logger.info(f"add controller: {controller.id}")
        return len(self.__gourps) == length + 1
    
    def remove_controller(self, id: int) -> bool:
        length = len(self.__gourps)
        self.__gourps.remove(GuildController(id))
        self.logger.info(f"remove controller: {id}")
        return len(self.__gourps) == length - 1
    
@dataclass
class Bot(commands.Bot):
    manager: Manager
        