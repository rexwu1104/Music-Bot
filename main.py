from discord import *
from discord.ext import commands

from modules.music import load_bot, Bot, get_token

bot: Bot = commands.Bot(command_prefix="m!", intents=Intents.all())

@bot.event
async def on_ready():
    await load_bot(bot)
    bot.manager.logger.info("bot is ready.")
    
bot.run(get_token())