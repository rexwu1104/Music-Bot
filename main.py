import json

from discord import *
from discord.ext import commands

from modules import load_bot, Bot, get_token, Translator

bot: Bot = commands.Bot(command_prefix="m!", intents=Intents.all())

@bot.event
async def on_ready():
    Translator.init('en-us', 'zh-tw')
    with open('modules/translator/settings.json', 'r', encoding='utf-8') as settings:
        settings = json.load(settings)
        
    for guild in bot.guilds:
        Translator.register(guild.id, settings.get(str(guild.id)))
        
    await load_bot(bot)
    bot.manager.logger.info("bot is ready.")
    
bot.run(get_token())