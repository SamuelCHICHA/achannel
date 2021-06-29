import logging

import discord
from discord.ext import commands

import api_handler
from Bot import Bot


class Listener(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("I'm up !")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await api_handler.register_guild(guild.id)
        logging.info(f"Registering guild {guild.name} ({guild.id}).")
        if not discord.utils.get(guild.categories, name=self.bot.mother_category):
            await guild.create_category(self.bot.mother_category)
            logging.info(f"Creating the \"{self.bot.mother_category}\" category [{guild.name} ({guild.id})].")
        if guild.system_channel:
            guild.system_channel.send("Salut !")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await api_handler.delete_guild(guild.id)
        logging.info(f"Leaving guild {guild.name} ({guild.id}).")

    @commands.Cog.listener()
    @commands.bot_has_guild_permissions(
        move_members=True,
        manage_channels=True
    )
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # Entering voice channel
        if after.channel:
            activities = await api_handler.get_activities(after.channel.guild.id)
            # If the channel the user is entering bears the same name as the category and
            # as one of the supported activity for the auto channel feature
            # create a new voice channel and moves the user on it
            if activities and after.channel.name.lower() in activities and \
                    after.channel.category.name.lower() == self.bot.mother_category.lower():
                voice_channel_name = await api_handler.get_voice_channel_name(after.channel.guild.id,
                                                                              after.channel.name.lower())
                if voice_channel_name is not None:
                    overwrites = after.channel.overwrites
                    new_channel = await after.channel.category.create_voice_channel(voice_channel_name.title(),
                                                                                    overwrites=overwrites)
                    await member.move_to(new_channel)
                else:
                    await member.move_to(None)
            # Leaving voice channel
        if before.channel:
            activities = await api_handler.get_activities(before.channel.guild.id)
            # If the channel the last user is leaving bears the same name as the category and
            # as one of the supported activity for the auto channel feature
            # delete it
            # Delete the voice channel when there is no one left
            if activities and before.channel.name.lower() not in activities \
                    and before.channel.category.name.lower() == self.bot.mother_category.lower() \
                    and len(before.channel.members) == 0:
                await before.channel.delete()


def setup(bot: Bot):
    bot.add_cog(Listener(bot))
