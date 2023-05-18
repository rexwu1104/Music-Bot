from dataclasses import dataclass
from discord.ext import commands

from .manager import *
from .song import *
from .backend import *

async def load_bot(bot: commands.Bot):
    bot.manager = Manager()
    for guild in bot.guilds:
        bot.manager.add_controller(GuildController(bot, guild))
        
    await setup(bot)