import discord
from discord.app_commands.commands import Error
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import random

class Media(commands.Cog):
  group: app_commands.Group = app_commands.Group(name="media", description="Media commands")

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    self.ENGINE_ID = os.getenv("ENGINE_ID")

  @group.command(name="image_search", description="Returns an image based on a search term")
  @app_commands.describe(query="Search term")
  async def imagesearch(self, inter: discord.Interaction, query: str) -> None:
    if not self.GOOGLE_API_KEY or not self.ENGINE_ID:
      _ = await inter.response.send_message("Google API key or Engine ID is not configured.")
      return

    _ = await inter.response.defer()

    try:
      service = build("customsearch", "v1", developerKey=self.GOOGLE_API_KEY)  # pyright: ignore[reportUnknownVariableType]
      res = service.cse().list(q=query, cx=self.ENGINE_ID, searchType="image").execute()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
      items = res.get("items", [])  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
      number = random.randint(0, len(items))
      data = items[number]
      image = data['link']
      source = data['image']['contextLink']
      embed = discord.Embed(
        title=f"Result for {query}",
        color=discord.Color.random()
      )
      embed.set_image(url=image)
      embed.add_field(name="Source", value=f"{source}")

      _ = await inter.followup.send(embed=embed)
    except Exception as e:
      _ = await inter.followup.send(f"Something went wrong: {e}")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Media(bot))
