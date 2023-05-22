import discord

from discord.ext import commands

from .manager import Bot
from ..translator import Translator

class MusicCog(commands.Cog):
    bot: Bot
    
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        
    def __is_user_in_channel(self, interaction: discord.Interaction) -> bool:
        return interaction.user.voice is not None
            
    def __is_bot_not_in_channel(self, interaction: discord.Interaction) -> bool:
        return interaction.guild.voice_client is None
    
    def __is_bot_not_in_user_channel(self, interaction: discord.Interaction) -> bool:
        return interaction.guild.voice_client is not None and \
            interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id
    
    def __is_channel_only_have_bot(self, interaction: discord.Interaction) -> bool:
        return len(interaction.guild.voice_client.channel.members) == 1
                
    @discord.app_commands.guild_only()
    @discord.app_commands.command()
    @discord.app_commands.describe(query='query for search, can be url')
    async def play(self, interaction: discord.Interaction, query: str):
        if self.__is_user_in_channel(interaction):
            controller = self.bot.manager[interaction.guild_id]
            if controller.is_locked(interaction.user.id):
                return await interaction.response.send_message(
                    f"**{Translator.translate(interaction.guild_id, 'Please complete your prev action.')}**"
                )
            
            controller.lock(interaction.user.id)
            await controller.set_interaction(interaction)
            await interaction.response.defer(thinking=True)
            if self.__is_bot_not_in_channel(interaction) or \
                (self.__is_bot_not_in_user_channel(interaction) and \
                 self.__is_channel_only_have_bot(interaction)):
                await controller.with_channel()
            elif not self.__is_channel_only_have_bot(interaction) and \
                self.__is_bot_not_in_user_channel(interaction):
                controller.unlock(interaction.user.id)
                return await interaction.edit_original_response(
                    content="**{}**".format(Translator.translate(interaction.guild_id, 'I can\'t join another channel when my channel has other people')))
                
            await controller.append(query)
            if not controller.is_playing:
                await controller.start()
                
            controller.unlock(interaction.user.id)
        else:
            await interaction.response.send_message(Translator.translate(interaction.guild_id, 'Please join a channel before you use the command'))
        
async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))