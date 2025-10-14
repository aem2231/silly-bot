import discord
from discord.ext import commands
from discord import app_commands
from functools import wraps
from DatabaseRefactor import Database
import constants
import random
import datetime


class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  async def percentage_chance(self, percentage):
    return random.choices([True, False], weights=[percentage, 100 - percentage], k=1)[0]

  async def format_remaining_time(self, remaining_time):
    remaining_time_hours = int(remaining_time // 3600)
    remaining_time_minutes = int((remaining_time % 3600) // 60)

    return (remaining_time_hours, remaining_time_minutes)

  async def check_cooldown(self, id, payout, cooldown):
    async with Database() as db:
      remaining_cooldown = await db.get_cooldown_start(constants.WORK_COLUMN, constants.USER_TABLE, constants.COOLDOWNS[f"{cooldown}"], constants.USER_COLUMN, id)
      if remaining_cooldown == 0:
        new_balance = await self.payout(id, payout)
        return (True, new_balance)
      return (False, remaining_cooldown)

  async def payout(self, id, coins):
    async with Database() as db:
      current_balance = await db.get_balance(id)
      new_balance = current_balance + coins
      await db.update_coins(id, new_balance)
      return new_balance

  async def get_random_job(self):
    job_index = random.randint(0, len(constants.JOB_LIST) - 1)
    return constants.JOB_LIST[job_index]

  @group.command(name="daily", description="Claim your daily coins!")
  async def daily(self, inter) -> None:
    payout = constants.DAILY_PAYOUT
    result = await self.check_cooldown(inter.user.id, payout, constants.COOLDOWNS["daily"])

    if result[0]:
      embed = discord.Embed(
        title="Daily :coin:",
        description=f"{constants.DAILY_PAYOUT} collected! Your balance is now {result[1]}.",
        color=discord.Color.green())
      await inter.response.send_message(embed=embed)
      return

    hours, minutes = await self.format_remaining_time(result[1])
    embed = discord.Embed(
      title="Daily :coin:",
      description=f"You can't claim your daily for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)
    return

  @group.command(name="work", description="Work a random job for some coins.")
  async def work(self, inter: discord.Interaction) -> None:
    payout = random.randint(constants.MIN_WORK_PAYOUT, constants.MAX_WORK_PAYOUT)
    result =  await self.check_cooldown(inter.user.id, payout, constants.COOLDOWNS["work"])

    if result[0]:
      job = await self.get_random_job()
      embed = discord.Embed(
        title="Work",
        description=f"You worked as a {job} and got paid {result[1]} coins.",
        color=discord.Color.green()
      )
      await inter.response.send_message(embed=embed)
      return

    hours, minutes = await self.format_remaining_time(result[1])
    embed = discord.Embed(
      title="Work",
      description=f"You can't work for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)
    return

  @group.command(name="balance", description="Check your balance.")
  async def balance(self, inter: discord.Interaction) -> None:
    async with Database() as db:
      balance = await db.get_balance(inter.user.id)

    embed = discord.Embed(
      title="Balance",
      description=f"You have {balance} coins.",
      color=discord.Color.green()
    )

    await inter.response.send_message(embed=embed)

  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    success = await self.percentage_chance(30)

    if success:
      payout = random.randint(constants.MIN_BEG_PAYOUT, constants.MAX_BEG_PAYOUT)
      balance = self.payout(inter.user.id, payout)

  #@group.command(name="coinflip", description="Flip a coin for a chance to double your money!")
 # @app_commands.describe(amount="Amount of money to gamble.")
  #async def coinflip(self, inter: discord.Interaction) -> None:
  #  pass

  @group.command(name="bankrob", description="Try and rob the bank for some coins!")
  async def bankrob(self, inter: discord.Interaction) -> None:
    pass

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
