import discord

from discord.ext import commands

from .manager import *
from .song import *
from .cog import *

async def load_bot(bot: commands.Bot):
    bot.manager = Manager()
    for guild in bot.guilds:
        bot.manager.add_controller(GuildController(bot, guild))
        
    await setup(bot)  
    synced = await bot.tree.sync()
    bot.manager.logger.info(f'{len(synced)} application commands synced')