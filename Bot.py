import random
import sys

import discord

from AutoChannel import AutoChannel


class Bot(discord.Client):
    def __init__(self, prefix: str, bot_commands: list[dict[str]], supported_activities: list[dict[str]]):
        if not isinstance(prefix, str) \
                or not isinstance(bot_commands, list) \
                or not isinstance(supported_activities, list):
            print(f"Prefix : {type(prefix)}")
            print(f"Commands : {type(bot_commands)}")
            print(f"Activities : {type(supported_activities)}")
            raise TypeError("Expects a string, a dictionary and a list of dictionary.")
        super().__init__()
        self.auto_channels = []
        for supported_activity in supported_activities:
            self.auto_channels.append(AutoChannel(supported_activity))
        self.prefix = prefix
        self.commands = bot_commands

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
            # TODO Generalize
            # Getting the matching auto channel
            auto_channel = next(filter(lambda ac: ac.name.lower() == after.channel.name.lower(), self.auto_channels),
                                None)
            if after.channel.category.name.lower() == after.channel.name.lower() \
                    and auto_channel is not None:
                try:
                    # TODO Overwrite
                    voice_channel_name = random.choice(auto_channel.voice_channel_names)
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
            auto_channel_names = [ac.name.lower() for ac in self.auto_channels]
            print(auto_channel_names)
            if before.channel.category.name.lower() in auto_channel_names \
                    and before.channel.name.lower() not in auto_channel_names \
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
            request = message.content[len(self.prefix):].strip()
            if request == "help":
                await self.display_help(message.channel)
            elif request.startswith("create auto-channel"):
                options = request[len("create auto-channel"):].strip()
                activities = [ac.name.lower() for ac in self.auto_channels]
                activity = next(filter(lambda act: act.lower() == options.lower(), activities), None)
                if activity:
                    await message.channel.send(f"Creation de l'auto-channel pour {activity}.")
                    await Bot.create_auto_channel(message.guild, activity)
                else:
                    await message.channel.send("Je ne supporte pas cette catégorie.")
            else:
                await message.channel.send("Je n'ai pas compris votre requête.")

    @staticmethod
    async def create_auto_channel(guild: discord.Guild, name: str) -> None:
        category = next(filter(lambda cat: cat.name.lower() == name.lower(), guild.categories), None)
        if category is None:
            try:
                # TODO Overwrite
                await guild.create_category(name.title())
            except discord.Forbidden:
                print("You don't have the rights to create a category.", file=sys.stderr)
            except discord.InvalidArgument:
                print("The overwrite information is not well formatted.", file=sys.stderr)
            except discord.HTTPException:
                print("Failed creating the category.", file=sys.stderr)
        channel = next(filter(lambda ch: ch.name.lower() == name.lower(), guild.voice_channels), None)
        if channel and channel not in category.voice_channels:
            await channel.move(category=category, beginning=True)
        else:
            try:
                # TODO Overwrite
                await category.create_voice_channel(name.title())
            except discord.Forbidden:
                print("You don't have the rights to create a voice channel in this category.", file=sys.stderr)
            except discord.InvalidArgument:
                print("The overwrite information is not well formatted.", file=sys.stderr)
            except discord.HTTPException:
                print("Failed creating the voice channel.", file=sys.stderr)

    async def display_help(self, channel: discord.TextChannel) -> None:
        embed = discord.Embed(title="Informations",
                              url="https://github.com/SamuelCHICHA/desagreable",
                              color=discord.Colour.purple(),
                              description="Récapitulatif des commandes et du fonctionnement.")
        # TODO Add an image of the bot as thumbnail
        # embed.set_thumbnail("")
        embed.add_field(name="Préfixe", value=f"Pour m'appeler, tu peux utiliser \"{self.prefix}\"", inline=False)
        for command in self.commands:
            embed.add_field(name=f'{command["name"]} : {command["command"]}', value=f'{command["description"]}', inline=False)
        try:
            await channel.send(embed=embed, delete_after=60)
        except discord.Forbidden:
            print("You don't have the rights to send a message in this channel.")
        except discord.HTTPException:
            print("Failed sending message.")
