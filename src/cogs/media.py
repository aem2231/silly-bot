import discord
from discord.ext import commands
from discord import app_commands

class Media(commands.Cog):
  group: app_commands.Group = app_commands.Group(name="media", description="Media commands")

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  @group.command(name="image search", description="Returns an image based on a search term")
  @app_commands.describe(message="Search term")
  async def imagesearch(self, inter: discord.Interaction) -> None:
