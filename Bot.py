import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp


class Bot(commands.Bot):
    extensions = [
        'cogs.AutoChannelCategory',
        'cogs.ChannelCategory',
        'cogs.ErrorHandler',
        'cogs.Listener'
    ]

    def __init__(self, prefix: str, description: str, mother_category: str, good_reaction: str, bad_reaction: str):
        super().__init__(
            command_prefix=prefix,
            description=description,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{prefix}"
            ),
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )
        self.mother_category = mother_category
        self.good_reaction = good_reaction
        self.bad_reaction = bad_reaction

    async def send_good_reaction(self, ctx: commands.Context) -> None:
        await ctx.message.add_reaction(self.good_reaction)

    async def send_bad_reaction(self, ctx: commands.Context) -> None:
        await ctx.message.add_reaction(self.bad_reaction)

    def run(self, *args, **kwargs):
        load_dotenv()
        self.help_command = PrettyHelp(color=discord.Colour.green())
        for extension in self.extensions:
            self.load_extension(extension)
        super().run(os.getenv("BOT-TOKEN"))


