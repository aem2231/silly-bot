import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
  group: app_commands.Group = app_commands.Group(name="utility", description="Utility commands")

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  @group.command(name="ping", description="Get the bot's latency")
  async def ping(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms") # the _ stops your linter/type checker from being a crybaby bitch

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(General(bot))
