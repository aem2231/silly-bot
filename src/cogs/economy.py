import discord
from discord.ext import commands
from discord import app_commands
from DatabaseRefactor import EconomyDatabase
import random
import time

class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    # id types and cooldowns to be passed to database functions when needed
    self.user_column = "user_id"
    self.guild_column = "guild_id"
    self.user_table = "users"
    self.guild_table = "server"
    self.daily_column = "last_daily"
    self.bank_rob_columnn = "last_bank_rob"
    self.work_column = "last_work"
    self.cooldowns = {
      "bank_rob": 1800,
      "work": 21600,
      "daily": 86400
    }

    self.job_list = [
      "cleaner",
      "cashier",
      "uber driver",
      "bartender",
      "binman",
      "twitch streamer",
      "delivery driver",
      "bus driver"
    ]

    self.bot: commands.Bot = bot
    self.db = EconomyDatabase()


  def build_embed(self, embed_title, embed_description, embed_color):
    embed = discord.Embed(
      title=embed_title,
      description=embed_description,
      color=embed_color
    )
    return embed

  @group.command(name="daily", description="Claim your daily coins!")
  async def daily(self, inter: discord.Interaction) -> None:
    remaining_cooldown = self.db.check_cooldown(self.daily_column, self.user_table, self.cooldowns["daily"], self.user_column, inter.user.id)
    if remaining_cooldown == 0:
      _ = await inter.response.send_message("daily allowed")
      return
    _ = await inter.response.send_message("daily blocked")

  @group.command(name="work", description="Work a random job for some dabloons.")
  async def work(self, inter: discord.Interaction) -> None:
    pass

  @group.command(name="balance", description="Check your balance.")
  async def balance(self, inter: discord.Interaction) -> None:
    pass

  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    pass

  #@group.command(name="coinflip", description="Flip a coin for a chance to double your money!")
 # @app_commands.describe(amount="Amount of money to gamble.")
  #async def coinflip(self, inter: discord.Interaction) -> None:
  #  pass

  @group.command(name="bankrob", description="Try and rob the bak for some coins!")
  async def bankrob(self, inter: discord.Interaction) -> None:
    pass

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
