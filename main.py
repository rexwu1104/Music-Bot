from discord import *
from discord.ext import commands

from modules.music import load_bot, GuildController, Bot

bot: Bot = commands.Bot(command_prefix="m!", intents=Intents.all())

@bot.event
async def on_ready():
    await load_bot(bot)
    print("bot is ready.")
        
# await controller._GuildController__play(bot, 1055391043148841080, SoundCloud("https://soundcloud.com/leftalivemecha71/oshi-no-ko-op-opening-full-6"))
# await controller._GuildController__play(bot, 1055391043148841080, Spotify("https://open.spotify.com/track/6MCjmGYlw6mQVWRFVgBRvB"))
# await controller._GuildController__play(bot, 1055391043148841080, Youtube("https://www.youtube.com/watch?v=EoxRhxsTmNg"))
    
bot.run("MTA1NzI5MjU2MDQyMDMyMzM2OA.GMFDzs.5eFtDIEx0LPmjbcowesvehQyqcsDBBPrIxKHIY")