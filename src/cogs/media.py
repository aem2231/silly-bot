import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build

class Media(commands.Cog):
  group: app_commands.Group = app_commands.Group(name="media", description="Media commands")

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    self.ENGINE_ID = os.getenv("ENGINE_ID")

  @group.command(name="image_search", description="Returns an image based on a search term")
  @app_commands.describe(query="Search term")
  async def imagesearch(self, inter: discord.Interaction, query: str) -> None:
    service = build("customsearch", "v1", developerKey=self.GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=self.ENGINE_ID)
    print(res)
    _ = await inter.response.send_message("working")

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Media(bot))
