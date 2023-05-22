from __future__ import annotations

import discord

from datetime import datetime

from .utils import *
from ..translator import Translator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .manager import GuildController
    from .song import Song

def to_embed(interaction: discord.Interaction, controller: GuildController, song: Song) -> discord.Embed:
    guild_id = interaction.guild_id
    embed = discord.Embed(
        color=discord.Colour.random(),
        title=song.name,
        url=song.target_url,
        timestamp=datetime.now())
    
    embed.add_field(name=Translator.translate(guild_id, 'title'),
                    value=f'```\n{song.name}\n```',
                    inline=True)
    embed.add_field(name=Translator.translate(guild_id, 'uploader'),
                    value=f'```\n{song.uploader}\n```',
                    inline=True)
    embed.add_field(name=Translator.translate(guild_id, 'duration'),
                    value=f'```\n{duration_to_length(song.duration)}\n```',
                    inline=False)
    embed.add_field(name=Translator.translate(guild_id, 'loop mode'),
                    value=f'```\n{controller.repeat_mode}\n```',
                    inline=False)
    embed.add_field(name=Translator.translate(guild_id, 'volume'),
                    value=f'```\n{controller.volume}\n```',
                    inline=True)
    embed.add_field(name=Translator.translate(guild_id, 'position'),
                    value=f'```\n{controller.position}/{controller.length}\n```',
                    inline=True)
    
    embed.set_footer(text=interaction.user.nick, icon_url=interaction.user.avatar.url)
    embed.set_image(url=song.thumbnail)
    
    return embed

def to_append_embed(interaction: discord.Interaction, song: Song) -> discord.Embed:
    embed = discord.Embed(
        color=discord.Colour.random(),
        title=song.name,
        url=song.target_url,
        timestamp=datetime.now(),
        description=f'{song.name} append.'
    )
    
    embed.set_author(name='add to queue')
    embed.set_footer(text=interaction.user.nick, icon_url=interaction.user.avatar.url)
    embed.set_thumbnail(url=song.thumbnail)
    
    return embed
    