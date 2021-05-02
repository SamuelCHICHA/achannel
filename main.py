import sys
import os
import discord
import json
from discord.ext import commands
from api_handler import *
from dotenv import load_dotenv

with open("bot_config.json", "r") as config_file:
    config = json.load(config_file)
    bot = commands.Bot(command_prefix=config["prefix"], description=config["description"])

"""
Some small tools 
"""


def lower(arg: str):
    return arg.lower().strip()


"""
Events
"""


@bot.event
async def on_ready():
    print("You're good to go !")


@bot.event
async def on_guild_join(guild: discord.Guild):
    if len(guild.text_channels) > 0:
        await guild.text_channels[0].send("Salut poufiasse !")
    await register_guild(guild.id)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    await delete_guild(guild.id)


@bot.event
@commands.bot_has_guild_permissions(move_members=True, manage_channels=True)
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Entering voice channel
    if after.channel:
        activities = await get_activities(after.channel.guild.id)
        # If the channel the user is entering bears the same name as the category and
        # as one of the supported activity for the auto channel feature
        # create a new voice channel and moves the user on it
        if activities is not None and after.channel.name.lower() in activities and \
                after.channel.category.name.lower() == after.channel.name.lower():
            voice_channel_name = await get_voice_channel_name(after.channel.guild.id, after.channel.name.lower())
            if voice_channel_name is not None:
                new_channel = await after.channel.category.create_voice_channel(voice_channel_name.title())
                await member.move_to(new_channel)
            else:
                await member.move_to(None)
        # Leaving voice channel
    if before.channel:
        activities = await get_activities(before.channel.guild.id)
        # If the channel the last user is leaving bears the same name as the category and
        # as one of the supported activity for the auto channel feature
        # delete it
        # Delete the voice channel when there is no one left
        if activities is not None and before.channel.category.name.lower() in activities \
                and before.channel.name.lower() not in activities \
                and len(before.channel.members) == 0:
            await before.channel.delete()


"""
Commands
"""


@bot.command(name="list-cn", description="List the channel names for an activity", require_var_positional=True)
@commands.has_permissions(administrator=True)
async def list_channel_names(ctx, *args: lower):
    if len(args) != 1:
        await ctx.reply("J'ai besoin d'une activité.")
        ctx.send_help()
    else:
        activity = args[0]
        channel_names = await get_voice_channel_names(ctx.guild.id, activity)
        value = ""
        embed = discord.Embed(title=f"Liste des noms de channel vocaux pour {activity.title()}")
        if channel_names is not None:
            for channel_name in channel_names:
                value += f"- {channel_name.title()}\n"
        else:
            value += "Aucun"
        embed.add_field(name="Noms", value=value, inline=False)
        await ctx.reply(embed=embed)


@bot.command(name="add", description="Register new channel names for an activity")
@commands.has_permissions(administrator=True)
async def add_channel_names(ctx, *args: lower):
    if len(args) < 2:
        await ctx.reply("Il m'en faut plus")
        await ctx.send_help()
    else:
        activity = args[0]
        activities = await get_activities(ctx.guild.id)
        if activities is not None and activity in activities:
            channel_names = list(args[1:])
            channel_names = [cn.strip() for cn in channel_names]
            await register_voice_channel_names(ctx.guild.id, activity, channel_names)
        else:
            await ctx.reply("Vous devez d'abord enregistrer l'activité.")


@bot.command(name="add-f", description="Register new channel names for an activity via a text file",
             require_var_postional=True)
async def add_channel_names_file(ctx, *args: lower):
    if len(args) != 1:
        await ctx.reply("J'ai besoin d'une activité")
    else:
        activity = args[0]
        if len(ctx.message.attachments) != 1:
            await ctx.reply("J'ai besoin d'un fichier.")
            ctx.send_help()
        else:
            file = ctx.message.attachments[0]
            if "text/plain" in file.content_type:
                raw_content = await file.read()
                content = raw_content.decode()
                lines = content.split("\n")
                if len(lines) < 1:
                    ctx.reply("Il m'en faut plus.")
                    ctx.send_help()
                else:
                    channel_names = list(lines)
                    channel_names = [cn.strip() for cn in channel_names]
                    channel_names.remove("")
                    await register_voice_channel_names(ctx.guild.id, activity, channel_names)
            else:
                await ctx.reply("Mauvais format de fichier.")
                ctx.send_help()


@bot.command(name='list-ac', description="List all the activities of the guild")
@commands.has_permissions(administrator=True)
async def list_activities(ctx):
    embed = discord.Embed(title=f"Liste des activités de {ctx.guild.name}", color=discord.Colour.green())
    value = ""
    activities = await get_activities(ctx.guild.id)
    if activities is not None:
        for activity in activities:
            value += f"- {activity.title()}\n"
    else:
        value += "Il n'y a aucune activité sur ce serveur."
    embed.add_field(name="Activités:", value=value, inline=False)
    await ctx.reply(embed=embed)


@bot.command(name='create', description="Create one or many auto-channel for the guild.")
@commands.bot_has_guild_permissions(manage_channels=True, move_members=True)
@commands.has_permissions(administrator=True)
async def create_auto_channel(ctx, *args: lower):
    if await register_activities(ctx.guild.id, list(args)):
        for arg in args:
            category = discord.utils.get(ctx.guild.categories, name=arg)
            if category is None:
                category = await ctx.guild.create_category(arg)
            channel = discord.utils.get(ctx.guild.voice_channels, name=arg.title())
            if channel:
                if channel not in category.voice_channels:
                    await channel.move(category=category, beginning=True)
            else:
                # TODO Overwrite
                await category.create_voice_channel(arg.title())


@bot.command(name="delete", description="Delete an activity from the guild.", require_var_positional=True)
@commands.has_permissions(administrator=True)
@commands.bot_has_guild_permissions(manage_channels=True, move_members=True)
async def delete_auto_channel(ctx, *args: lower):
    if len(args) == 1:
        activity = args[0]
        activities = await get_activities(ctx.guild.id)
        if activities is not None and activity in activities:
            await delete_activity(ctx.guild.id, activity)
            vc = discord.utils.get(ctx.guild.voice_channels, name=activity.title())
            if vc is not None:
                await vc.delete()
            else:
                for vc in ctx.guild.voice_channels:
                    print(vc.name)
                print("1")
            cat = discord.utils.get(ctx.guild.categories, name=activity)
            if cat is not None:
                await cat.delete()
            else:
                for cat in ctx.guild.categories:
                    print(cat.name)
                print("2")
        else:
            await ctx.reply("Il n'y a pas d'auto-channel portant ce nom.")


def main():
    load_dotenv()
    bot.run(os.getenv("BOT-TOKEN"))


if __name__ == '__main__':
    main()
