import discord
from VChannel import VChannel
from Data import Data
import sys


class Bot(discord.Client):
    def __init__(self, prefix: str):
        super().__init__()
        self.vc = VChannel()
        self.prefix = prefix

    async def on_ready(self):
        print("You're good to go !")

    async def on_guild_join(self, guild: discord.Guild):
        try:
            await guild.text_channels[0].send("Salut poufiasse !")
        except AttributeError:
            print("There are no text channels in this guild", file=sys.stderr)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # Create new voice channel from the main voice channel
        if after.channel:
            if after.channel.category.name == "Among Us" and after.channel.name == "Among Us":
                try:
                    # TODO Overwrite
                    voice_channel_name = VChannel.get_voice_channel_name(self.vc.among_us_voice_channel_names)
                    new_channel = await after.channel.category.create_voice_channel(voice_channel_name)
                    await member.move_to(new_channel)
                except discord.Forbidden:
                    print("Bot is not allowed to create a new voice channel.", file=sys.stderr)
                except discord.InvalidArgument:
                    print("Overwrite information is not well formatted.", file=sys.stderr)
                except discord.HTTPException:
                    print("Failed creating the channel.", file=sys.stderr)
        # Delete the voice channel when there is no one left
        if before.channel:
            if before.channel.category.name == "Among Us" \
                    and before.channel.name != "Among Us" \
                    and len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except discord.Forbidden:
                    print("Bot is not allowed to delete the voice channel.", file=sys.stderr)
                except discord.NotFound:
                    print("The channel was not found and therefore could not be deleted.", file=sys.stderr)
                except discord.HTTPException:
                    print("Failed deleting the channel.", file=sys.stderr)

    async def on_message(self, message: discord.Message):
        if message.content.startswith(self.prefix):
            print("Someone is talking to me.")
            request = message.content[len(self.prefix):].strip()
            if request == "help":
                await message.channel.send("Appelez les secours !")
                # TODO implement help function
            elif request.startswith("create auto-channel"):
                options = request[len("create auto-channel"):].strip()
                if options == "among us":
                    await message.channel.send("Creation de l'auto-channel pour among us.")
                    # TODO implement creation of the auto-channel for among us
                    await Bot.create_auto_channel(message.guild, Data.Supported_Games.AMONG_US)
                elif options == "général":
                    # TODO implement creation of the auto-channel for general purposes
                    await message.channel.send("Création de l'auto-channel général.")
                    await Bot.create_auto_channel(message.guild)
                else:
                    await message.channel.send("Je ne supporte pas cette catégorie.")
            else:
                await message.channel.send("Je n'ai pas compris votre requête.")

    @staticmethod
    async def create_auto_channel(guild: discord.Guild, name: str = Data.Supported_Games.GENERAL) -> None:
        if name in Data.Supported_Games.__dict__.values():
            category = list(filter(lambda cat: cat.name == name, guild.categories))
            if len(category) == 1:
                category = category[0]
            else:
                try:
                    # TODO Overwrite
                    await guild.create_category(name)
                except discord.Forbidden:
                    print("You don't have the rights to create a category.", file=sys.stderr)
                except discord.InvalidArgument:
                    print("The overwrite information is not well formatted.", file=sys.stderr)
                except discord.HTTPException:
                    print("Failed creating the category.", file=sys.stderr)
            channel = list(filter(lambda ch: ch.name == name, guild.voice_channels))
            if len(channel) == 1:
                channel = channel[0]
                if channel not in category.voice_channels:
                    await channel.move(category=category, beginning=True)
            else:
                try:
                    # TODO Overwrite
                    await category.create_voice_channel(name)
                except discord.Forbidden:
                    print("You don't have the rights to create a voice channel in this category.", file=sys.stderr)
                except discord.InvalidArgument:
                    print("The overwrite information is not well formatted.", file=sys.stderr)
                except discord.HTTPException:
                    print("Failed creating the voice channel.", file=sys.stderr)




