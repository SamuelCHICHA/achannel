import discord
from VChannel import VChannel


class Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.vc = VChannel()

    async def on_ready(self):
        print("You're good to go !")

    async def on_guild_join(self, guild: discord.Guild):
        pass

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # Create new voice channel from the main voice channel
        if after.channel:
            if after.channel.category.name == "Among Us" and after.channel.name == "Among Us":
                try:
                    voice_channel_name = VChannel.get_voice_channel_name(self.vc.among_us_voice_channel_names)
                    new_channel = await after.channel.category.create_voice_channel(voice_channel_name)
                    await member.move_to(new_channel)
                except discord.Forbidden:
                    print("Bot is not allowed to create a new voice channel.")
                except discord.InvalidArgument:
                    print("Overwrite information is not well formatted.")
                except discord.HTTPException:
                    print("Failed creating the channel.")
        # Delete the voice channel when there is no one left
        if before.channel:
            if before.channel.category.name == "Among Us" \
                    and before.channel.name != "Among Us" \
                    and len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except discord.Forbidden:
                    print("Bot is not allowed to delete the voice channel.")
                except discord.NotFound:
                    print("The channel was not found and therefor could not be deleted.")
                except discord.HTTPException:
                    print("Failed deleting the channel.")
