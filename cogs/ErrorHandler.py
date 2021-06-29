import logging

from discord.ext import commands

from Bot import Bot


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        await self.bot.send_bad_reaction(ctx)
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply("Cette commande n'existe pas.")
            await ctx.send_help()
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Il manque des paramètres.")
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.TooManyArguments):
            await ctx.reply("Trop de paramètres.")
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.BotMissingPermissions):
            logging.error(f"Bot doesn't have the right: {error.missing_perms} [{ctx.guild.name} ({ctx.guild.id})]")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"Vous n'avez pas la permission de faire ça. {error.missing_perms}")
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f"Le(s) paramètre(s) sont incorrectes.")
            await ctx.send_help(ctx.command)
        else:
            if isinstance(error, commands.CommandInvokeError):
                original_exception = error.original
                if isinstance(original_exception, commands.CommandError):
                    logging.error(f"Discord error: {original_exception}")
                else:
                    # Not a discord error
                    if isinstance(original_exception, KeyboardInterrupt):
                        logging.critical("Shutting down.")
                    else:
                        logging.error(f"Other error: {original_exception}")
            else:
                logging.error(f"Unexpected error: {error}")


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
