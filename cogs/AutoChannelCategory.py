import logging

import discord
from discord.ext import commands

from Bot import Bot
from converters.StringConverter import StringConverter
import api_handler


class AutoChannelCategory(commands.Cog, name="AutoChannel", description="Commands to handle auto-channels."):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        name='create',
        brief="Create one or many auto-channel for the guild.",
        description="This command will create one or many new auto-channel, along with their associated roles. e.g. "
                    "create \"fall guys\" \"among us\"",
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
    @commands.guild_only()
    async def create_auto_channel(self, ctx: commands.Context, *auto_channels: StringConverter.convert):
        auto_channels = list(auto_channels)
        if await api_handler.register_activities(ctx.guild.id, auto_channels):
            category = discord.utils.get(ctx.guild.categories, name=self.bot.mother_category)
            if category is None:
                category = await ctx.guild.create_category(self.bot.mother_category)
            for auto_channel in auto_channels:
                logging.info(f"Registering auto-channel {auto_channel} [{ctx.guild.name} ({ctx.guild.id})]")
                role = discord.utils.get(ctx.guild.roles, name=auto_channel.title())
                if role is None:
                    role = await ctx.guild.create_role(name=auto_channel.title())
                    logging.info(f"Creating role {role.name} [{ctx.guild.name} ({ctx.guild.id})]")
                channel = discord.utils.get(ctx.guild.voice_channels, name=auto_channel.title())
                if channel:
                    if channel not in category.voice_channels:
                        await channel.move(category=category, beginning=True)
                        logging.info(
                            f"Moving voice channel {channel.name}({channel.id}) [{ctx.guild.name}  ({ctx.guild.id})]")
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
                    logging.info(f"Creating voice channel {auto_channel} [{ctx.guild.name} ({ctx.guild.id})]")
            await self.bot.send_good_reaction(ctx)

    @commands.command(
        name="delete",
        brief="Delete one or many auto-channels inside your guild.",
        description="Delete auto-channels from the guild, along with their associated roles. e.g. delete \"fall guys\" "
                    "\"among us\"",
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
    @commands.guild_only()
    async def delete_auto_channels(self, ctx: commands.Context, *p_activities: StringConverter.convert):
        p_activities = list(p_activities)
        activities = await api_handler.get_activities(ctx.guild.id)
        if activities:
            if await api_handler.delete_activities(ctx.guild.id, p_activities):
                for activity in p_activities:
                    if activity in activities:
                        vc = discord.utils.get(ctx.guild.voice_channels, name=activity.title())
                        if vc:
                            await vc.delete()
                            logging.info(f"Deleting voice channel {vc.name} [{ctx.guild.name} ({ctx.guild.id})]")
                        role = discord.utils.get(ctx.guild.roles, name=activity.title())
                        if role:
                            await role.delete()
                            logging.info(f"Deleting role {role.name} [{ctx.guild.name} ({ctx.guild.id})]")
                        await self.bot.send_good_reaction(ctx)
                    else:
                        logging.info(f"No auto-channel named {activity} [{ctx.guild.name} ({ctx.guild.id})].")
                        await ctx.reply(f"Il n'y a pas d'auto-channel nommé {activity}")

    @commands.command(
        name='list-ac',
        description="This command will allow you to see all the auto-channels that have been created inside your "
                    "guild. e.g. list-ac",
        brief="List all the auto-channels of the guild"
    )
    @commands.guild_only()
    async def list_activities(self, ctx: commands.Context):
        embed = discord.Embed(title=f"Liste des auto-channels de {ctx.guild.name}", color=discord.Colour.green())
        value = ""
        activities = await api_handler.get_activities(ctx.guild.id)
        if activities:
            for activity in activities:
                value += f"- {activity.title()}\n"
        else:
            value += "Il n'y a aucune activité sur ce serveur."
        embed.add_field(name="Activités:", value=value, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(
        name="join",
        brief="Add a role.",
        description="This command allow you to gain access to the auto-channels associated to these roles. e.g. join "
                    "@Among Us @Fall Guys",
        usage="[role(s)]",
        require_var_positional=True
    )
    @commands.bot_has_guild_permissions(
        manage_roles=True,
        add_reactions=True,
        read_message_history=True
    )
    @commands.guild_only()
    async def join_role(self, ctx: commands.Context, *roles: discord.Role):
        activities = await api_handler.get_activities(ctx.guild.id)
        if activities:
            for role in roles:
                if role.name.lower() in activities:
                    await ctx.author.add_roles(role)
                    await self.bot.send_good_reaction(ctx)
                    logging.info(f"{ctx.author.name} ({ctx.author.id}) got role {role.name} ({role.id}).")
                else:
                    await ctx.reply(f"Il n'y a pas d'auto-channel nommé {role.name} sur ce serveur.")


def setup(bot: Bot) -> None:
    bot.add_cog(AutoChannelCategory(bot))
