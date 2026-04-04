import discord
from discord.app_commands.commands import Error
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from ddgs import DDGS
import random
import requests

class Media(commands.Cog):

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.GIPHY_KEY: str | None = os.getenv("GIPHY_KEY")

  @app_commands.command(name="image_search", description="Returns an image based on a search term")
  @app_commands.describe(query="Search term")
  async def imagesearch(self, inter: discord.Interaction, query: str) -> None:
    _ = await inter.response.defer()

    try:
      results = DDGS().images(
        query=query,
        keywords=query,
        region="wt-wt",
        safesearch="off",
        size=None,
        color=None,
        type_image=None,
        layout=None,
        license_image=None,
        max_results=10,
      )

      items = list(results)
      if not items:
        await inter.followup.send("No results found.")
        return

      number = random.randint(0, len(items) - 1)
      data: dict = items[number]
      image: str = data.get('image', '')
      source: str = data.get('url', '')

      embed = discord.Embed(
        title=f"Result for {query}",
        color=discord.Color.random()
      )
      embed.set_image(url=image)
      embed.add_field(name="Source", value=f"{source}")

      _ = await inter.followup.send(embed=embed)
    except Exception as e:
      print(f"Error in imagesearch: {e}")
      _ = await inter.followup.send("An error occurred while searching for the image.")

  async def fetch_giphy_gif(self, query: str) -> str | None:
    try:
      response = requests.get(
        "https://api.giphy.com/v1/gifs/search",
        params={
          "api_key": self.GIPHY_KEY,
          "q": query,
          "limit": 25
        }
      )
      if response.status_code == 200:
        data: list[dict] = response.json().get("data", [])
        if data:
          gif: dict = random.choice(data)
          return gif["images"]["original"]["url"]
        else:
          return None
      else:
        print(f"Giphy API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
      return None

  async def send_gif_embed(self, inter: discord.Interaction, user: discord.Member, action: str, query: str, color: discord.Color) -> None:
    _ = await inter.response.defer()

    gif_url = await self.fetch_giphy_gif(query)
    if gif_url:
      embed = discord.Embed(
        description=f"{inter.user.mention} {action} {user.mention}!",
        color=color
      )
      embed.set_image(url=gif_url)
      await inter.followup.send(embed=embed)
    else:
      await inter.followup.send(f"Sorry, I couldn't find any anime GIFs for '{action}'.")

  @app_commands.command(name="hug", description="Hug a user")
  @app_commands.describe(user="user")
  async def hug(self, inter: discord.Interaction, user: discord.Member):
    await self.send_gif_embed(inter, user, "hugs", "anime hug", discord.Color.pink())

  @app_commands.command(name="kiss", description="Kiss a user")
  @app_commands.describe(user="user")
  async def kiss(self, inter: discord.Interaction, user: discord.Member):
    await self.send_gif_embed(inter, user, "kisses", "anime kiss", discord.Color.red())

  @app_commands.command(name="kill", description="Kill a user")
  @app_commands.describe(user="user")
  async def kill(self, inter: discord.Interaction, user: discord.Member):
    await self.send_gif_embed(inter, user, "killed", "anime kill", discord.Color.dark_red())

  @app_commands.command(name="slap", description="Slap a user")
  @app_commands.describe(user="user")
  async def slap(self, inter: discord.Interaction, user: discord.Member):
    await self.send_gif_embed(inter, user, "slaps", "anime slap", discord.Color.orange())

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Media(bot))
