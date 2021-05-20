from discord.ext import commands
import discord
from ErrorHandler import ErrorHandler


class Bot(commands.Bot):
    def __init__(self, prefix, description, mother_category, good_reaction, bad_reaction):
        super().__init__(
            command_prefix=prefix,
            description=description,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{prefix}"
            )
        )
        self.mother_category = mother_category
        self.good_reaction = good_reaction
        self.bad_reaction = bad_reaction
        self.add_cog(ErrorHandler(self))
