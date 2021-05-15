import os
from discord.ext import commands
from dotenv import load_dotenv
import discord
from api_handler import *

with open("bot_config.json", "r") as config_file:
    config = json.load(config_file)
    prefix = config["prefix"]
    bot = commands.Bot(command_prefix=prefix, description=config["description"])

CHECK_REACTION = u'\u2705'
CHANNEL_NAME = "gaming"

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
async def on_guild_join(guild):
    await register_guild(guild.id)
    if CHANNEL_NAME.lower() not in guild.categories.name:
        await guild.create_category(CHANNEL_NAME)


@bot.event
async def on_guild_remove(guild):
    await delete_guild(guild.id)


@bot.event
@commands.bot_has_guild_permissions(
    move_members=True,
    manage_channels=True
)
async def on_voice_state_update(member, before, after):
    # Entering voice channel
    if after.channel:
        activities = await get_activities(after.channel.guild.id)
        # If the channel the user is entering bears the same name as the category and
        # as one of the supported activity for the auto channel feature
        # create a new voice channel and moves the user on it
        if activities is not None and after.channel.name.lower() in activities and \
                after.channel.category.name.lower() == CHANNEL_NAME.lower():
            voice_channel_name = await get_voice_channel_name(after.channel.guild.id, after.channel.name.lower())
            if voice_channel_name is not None:
                overwrites = after.channel.overwrites
                new_channel = await after.channel.category.create_voice_channel(voice_channel_name.title(), overwrites=overwrites)
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
        if activities is not None and before.channel.name.lower() not in activities \
                and before.channel.category.name.lower() == CHANNEL_NAME.lower() \
                and len(before.channel.members) == 0:
            await before.channel.delete()


"""
Commands
"""


@bot.command(
    name="list-cn",
    brief="List the channel names for an activity",
    usage="[auto-channel]",
    require_var_positional=True
)
@commands.has_permissions(administrator=True)
async def list_channel_names(ctx, activity: lower = None):
    print(activity)
    if activity:
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


@bot.command(
    name="add",
    brief="Register new channel names for an auto-channel.",
    description="With this command, you can add several channel names for the chosen auto-channel.",
    usage="[auto-channel] [channel name(s)]",
    require_var_positional=True
)
@commands.has_permissions(administrator=True)
@commands.bot_has_guild_permissions(
    read_message_history=True,
    add_reactions=True
)
async def add_channel_names(ctx, activity: lower, *channel_names: lower):
    activities = await get_activities(ctx.guild.id)
    channel_names = list(channel_names)
    if activities is not None and activity in activities:
        channel_names = [cn.strip() for cn in channel_names]
        await register_voice_channel_names(ctx.guild.id, activity, channel_names)
        await ctx.message.add_reaction(CHECK_REACTION)
    else:
        await ctx.reply("Vous devez d'abord enregistrer l'activité.")


@bot.command(
    name="add-f",
    description="This command will take the (mandatory) attached text file and will take each line to "
                "register new channel names",
    brief="Register new channel names for an activity via a text file.",
    usage="[auto-channel]",
    require_var_positional=True
)
@commands.has_permissions(administrator=True)
@commands.bot_has_guild_permissions(
    read_message_history=True,
    add_reactions=True
)
async def add_channel_names_file(ctx, activity: lower):
    channel_names = []
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
                lines = list(lines)
                for cn in lines:
                    cn = cn.strip().lower()
                    if cn != "":
                        channel_names.append(cn)
                await register_voice_channel_names(ctx.guild.id, activity, channel_names)
                await ctx.message.add_reaction(CHECK_REACTION)
        else:
            await ctx.reply("Mauvais format de fichier.")
            ctx.send_help()


@bot.command(
    name='list-ac',
    brief="List all the activities of the guild"
)
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


@bot.command(
    name='create',
    brief="Create one or many auto-channel for the guild.",
    usage="[auto-channel(s)]",
    require_var_positional=True
)
@commands.bot_has_guild_permissions(
    manage_channels=True,
    manage_roles=True,
    move_members=True,
    read_message_history=True,
    add_reactions=True
)
@commands.has_permissions(administrator=True)
async def create_auto_channel(ctx, *auto_channels: lower):
    auto_channels = list(auto_channels)
    if await register_activities(ctx.guild.id, auto_channels):
        category = discord.utils.get(ctx.guild.categories, name=CHANNEL_NAME)
        if category is None:
            category = await ctx.guild.create_category(CHANNEL_NAME)
        for auto_channel in auto_channels:
            role = discord.utils.get(ctx.guild.roles, name=auto_channel.title())
            if role is None:
                role = await ctx.guild.create_role(name=auto_channel.title())
            channel = discord.utils.get(ctx.guild.voice_channels, name=auto_channel.title())
            if channel:
                if channel not in category.voice_channels:
                    await channel.move(category=category, beginning=True)
                await channel.set_permissions(role,
                                              connect=True,
                                              view_channel=True
                                              )
                await channel.set_permissions(ctx.guild.default_role,
                                              view_channel=False
                                              )
                await channel.set_permissions(ctx.me,
                                              connect=True,
                                              view_channel=True,
                                              manage_channels=True
                                              )
            else:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        connect=False,
                        view_channel=False
                    ),
                    role: discord.PermissionOverwrite(
                        connect=True,
                        view_channel=True
                    ),
                    ctx.me: discord.PermissionOverwrite(
                        connect=True,
                        view_channel=True,
                        manage_channels=True
                    )
                }
                await category.create_voice_channel(auto_channel.title(), overwrites=overwrites)
        await ctx.message.add_reaction(CHECK_REACTION)


@bot.command(
    name="delete",
    description="Delete activities from the guild.",
    usage="[auto-channel(s)]",
    require_var_positional=True
)
@commands.has_permissions(administrator=True)
@commands.bot_has_guild_permissions(
    manage_channels=True,
    manage_roles=True,
    move_members=True,
    read_message_history=True,
    add_reactions=True
)
async def delete_auto_channels(ctx, *p_activities: lower):
    p_activities = list(p_activities)
    activities = await get_activities(ctx.guild.id)
    if activities is not None:
        if await delete_activities(ctx.guild.id, p_activities):
            for activity in p_activities:
                if activity in activities:
                    vc = discord.utils.get(ctx.guild.voice_channels, name=activity.title())
                    if vc is not None:
                        await vc.delete()
                    role = discord.utils.get(ctx.guild.roles, name=activity.title())
                    if role:
                        await role.delete()
                    await ctx.message.add_reaction(CHECK_REACTION)
                else:
                    await ctx.reply(f"Il n'y a pas d'auto-channel nommé {activity}")


def main():
    load_dotenv()
    bot.run(os.getenv("BOT-TOKEN"))


if __name__ == '__main__':
    main()
