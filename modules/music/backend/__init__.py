import discord

from discord.ext import commands

from ..manager import Bot

class MusicCog(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        
    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        if ctx.author.voice:
            controller = self.bot.manager[ctx.guild.id]
            if not ctx.voice_client or ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await controller.with_channel(ctx.author.voice.channel.id)
                
            controller.append(query)
            await controller.start()
        
async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))