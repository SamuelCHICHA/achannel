from discord.ext import commands
import logging


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Il manque des paramètres.")
            await ctx.send_help()
        elif isinstance(error, commands.TooManyArguments):
            await ctx.reply("Trop de paramètres.")
        elif isinstance(error, commands.BotMissingPermissions):
            logging.error(f"Bot doesn't have the right: {error.missing_perms} [{ctx.guild.name} ({ctx.guild.id})]")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"Vous n'avez pas la permission de faire ça. {error.missing_perms}")
        else:
            original_exception = error.original
            if isinstance(original_exception, commands.CommandError):
                logging.warning(f"Discord error: {original_exception}")
            else:
                # Not a discord error
                if isinstance(original_exception, KeyboardInterrupt):
                    logging.critical("Shutting down.")
                elif isinstance(original_exception, NameError):
                    logging.error(original_exception)
                elif isinstance(original_exception, AttributeError):
                    logging.error(original_exception)
                else:
                    logging.warning(original_exception)
