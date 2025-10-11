import discord
from discord.ext import commands
from discord import app_commands
from discord.types.interactions import Interaction
import random
import sqlite3
import requests

class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  @group.command(name="work", description="Work a random job for some dabloons.")
  async def work(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="gamble", description="Gamble some money.")
  async def gamble(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="buy", description="Buy something")
  async def buy(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="rob-bank", description="Rob the bank!")
  async def rob_bank(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="daily", description="Claim daily reward")
  async def daily(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="balance", description="Check your balance.")
  async def balance(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message("working")

  @group.command(name="gift", description="Gift coins to a specified user")
  @app_commands.describe(user="user")
  async def gift(self, inter: discord.Interaction, user: discord.Member) -> None:
    _ = await inter.response.send_message("working")

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
