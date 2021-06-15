import logging

import discord
from discord.ext import commands

from Bot import Bot
from converters.StringConverter import StringConverter
import api_handler


class ChannelCategory(commands.Cog, name="Channel", description="Commands to handle the voice channel names."):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        name="add-f",
        description="This command will take the (mandatory) attached text file and will take each line to "
                    "register new channel names. e.g. add-f \"among us\"",
        brief="Register new channel names for an auto-channel via a text file.",
        usage="[auto-channel]",
        require_var_positional=True
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(
        read_message_history=True,
        add_reactions=True
    )
    @commands.guild_only()
    async def add_channel_names_file(self, ctx: commands.Context, activity: StringConverter.convert):
        channel_names = []
        activities = await api_handler.get_activities(ctx.guild.id)
        if activities and activity in activities:
            if len(ctx.message.attachments) != 1:
                await ctx.reply("J'ai besoin d'un fichier.")
                await ctx.send_help()
            else:
                file = ctx.message.attachments[0]
                if "text/plain" in file.content_type:
                    raw_content = await file.read()
                    content = raw_content.decode()
                    lines = content.split("\n")
                    if len(lines) < 1:
                        await ctx.reply("Il m'en faut plus.")
                        await ctx.send_help()
                    else:
                        lines = list(lines)
                        for cn in lines:
                            cn = cn.strip().lower()
                            if cn != "":
                                channel_names.append(cn)
                        if await api_handler.register_voice_channel_names(ctx.guild.id, activity, channel_names):
                            logging.info(
                                f"Registering channel names for {activity} [{ctx.guild.name} ({ctx.guild.id})] (File)."
                            )
                            await self.bot.send_good_reaction(ctx)
                else:
                    await ctx.reply("Mauvais format de fichier.")
                    await ctx.send_help()
        else:
            logging.info(f"No auto-channel named {activity} [{ctx.guild.name} ({ctx.guild.id})].")

    @commands.command(
        name="add",
        brief="Register new channel names for an auto-channel.",
        description="With this command, you can add several channel names for the chosen auto-channel. e.g. add "
                    "\"among us\" office laboratory",
        usage="[auto-channel] [channel name(s)]",
        require_var_positional=True
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(
        read_message_history=True,
        add_reactions=True
    )
    @commands.guild_only()
    async def add_channel_names(self, ctx: commands.Context, activity: StringConverter.convert,
                                *channel_names: StringConverter.convert):
        activities = await api_handler.get_activities(ctx.guild.id)
        channel_names = list(channel_names)
        if activities and activity in activities:
            channel_names = [cn.strip() for cn in channel_names]
            await api_handler.register_voice_channel_names(ctx.guild.id, activity, channel_names)
            logging.info(f"Registering channel names for {activity} [{ctx.guild.name} ({ctx.guild.id})].")
            await self.bot.send_good_reaction(ctx)
        else:
            logging.info(f"No auto-channel named {activity} [{ctx.guild.name} ({ctx.guild.id})].")
            await ctx.reply("Vous devez d'abord enregistrer l'activité.")

    @commands.command(
        name="list-cn",
        brief="List the channel names for an auto-channel",
        description="This command will allow you to see the list of channel names for the given auto-channel. e.g. "
                    "list-cn \"among us\"",
        usage="[auto-channel]",
        require_var_positional=True
    )
    @commands.guild_only()
    async def list_channel_names(self, ctx: commands.Context, activity: StringConverter.convert):
        if activity:
            channel_names = await api_handler.get_voice_channel_names(ctx.guild.id, activity)
            value = ""
            embed = discord.Embed(title=f"Liste des noms de channel vocaux pour {activity.title()}")
            if channel_names:
                for channel_name in channel_names:
                    value += f"- {channel_name.title()}\n"
            else:
                value += "Aucun"
            embed.add_field(name="Noms", value=value, inline=False)
            await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(ChannelCategory(bot))
