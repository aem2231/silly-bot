import discord
from discord.app_commands.commands import Error
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from core.config import settings
import random
import requests

class Media(commands.Cog):

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.GIPHY_KEY: str = settings.GIPHY_KEY

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
        return None
    except Exception as e:
      return None

async def send_gif_embed(self, inter: discord.Interaction, user: discord.Member, action: str, gif_url: str | None, color: discord.Color) -> None:
    _ = await inter.response.defer()

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
    gif_url: str | None = await self.fetch_giphy_gif("anime hug")
    await self.send_gif_embed(inter, user, "hugs", gif_url, discord.Color.pink())

  @app_commands.command(name="kiss", description="Kiss a user")
  @app_commands.describe(user="user")
  async def kiss(self, inter: discord.Interaction, user: discord.Member):
    gif_url: str | None = await self.fetch_giphy_gif("anime kiss")
    await self.send_gif_embed(inter, user, "kisses", gif_url, discord.Color.red())

  @app_commands.command(name="kill", description="Kill a user")
  @app_commands.describe(user="user")
  async def kill(self, inter: discord.Interaction, user: discord.Member):
    gif_url: str | None = await self.fetch_giphy_gif("anime kill")
    await self.send_gif_embed(inter, user, "killed", gif_url, discord.Color.dark_red())

  @app_commands.command(name="slap", description="Slap a user")
  @app_commands.describe(user="user")
  async def slap(self, inter: discord.Interaction, user: discord.Member):
    gif_url: str | None = await self.fetch_giphy_gif("anime slap")
    await self.send_gif_embed(inter, user, "slaps", gif_url, discord.Color.orange())

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Media(bot))
