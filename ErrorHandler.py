from discord.ext import commands
import logging


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Il manque des paramètres.")
            await ctx.send_help()
        if isinstance(error, commands.TooManyArguments):
            await ctx.reply("Trop de paramètres.")
        if isinstance(error, commands.BotMissingPermissions):
            logging.error(f"Bot doesn't have the right: {error.missing_perms} [{ctx.guild.name} ({ctx.guild.id})]")
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"Vous n'avez pas la permission de faire ça. {error.missing_perms}")
