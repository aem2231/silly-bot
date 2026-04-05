import discord
from discord.ext import commands
from discord import app_commands
from db.database import AsyncSessionLocal
from db import crud
from core import constants as const
import random
import datetime

class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

 # helpers

  def percentage_chance(self, percentage):
    return random.choices([True, False], weights=[percentage, 100 - percentage], k=1)[0]

  def format_remaining_time(self, remaining_time):
    remaining_time_hours = int(remaining_time // 3600)
    remaining_time_minutes = int((remaining_time % 3600) // 60)

    return (remaining_time_hours, remaining_time_minutes)

  def calculate_remaining_time(self, cooldown_length, cooldown_start):
    current_time = datetime.datetime.now().timestamp()
    return (cooldown_start + cooldown_length) - current_time

  def get_random_job(self):
    job_index = random.randint(0, len(const.JOB_LIST) - 1)
    return const.JOB_LIST[job_index]

  def get_random_payout(self, min, max):
    return random.randint(min, max)

# commands

  @group.command(name="balance", description="Check your balance.")
  async def balance(self, inter: discord.Interaction) -> None:
    async with AsyncSessionLocal() as db:
      balance = await crud.get_user_balance(db, str(inter.user.id))

    embed = discord.Embed(
      title="Balance",
      description=f"You have {balance} coins.",
      color=discord.Color.green()
    )

    await inter.response.send_message(embed=embed)

  @group.command(name="daily", description="Claim your daily coins!")
  async def daily(self, inter: discord.Interaction) -> None:
    payout = const.DAILY_PAYOUT
    user_id = str(inter.user.id)

    async with AsyncSessionLocal() as db:
      cooldown_start = await crud.get_daily_cooldown(db, user_id)

      if cooldown_start + const.COOLDOWNS["daily"] < datetime.datetime.now().timestamp():
        balance = await crud.get_user_balance(db, user_id)
        new_balance = balance + payout
        await crud.update_user_balance(db, user_id, payout)
        await crud.update_daily_cooldown(db, user_id)

        embed = discord.Embed(
          title="Daily :coin:",
          description=f"{payout} collected! Your balance is now {new_balance}.",
          color=discord.Color.green()
        )
        await inter.response.send_message(embed=embed)
        return

    remaining_time = self.calculate_remaining_time(const.COOLDOWNS["daily"], cooldown_start)
    hours, minutes = self.format_remaining_time(remaining_time)
    embed = discord.Embed(
      title="Daily :coin:",
      description=f"You can't claim your daily for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)

  @group.command(name="work", description="Work a random job for some coins.")
  async def work(self, inter: discord.Interaction) -> None:
    payout = self.get_random_payout(const.MIN_WORK_PAYOUT, const.MAX_WORK_PAYOUT)
    job = self.get_random_job()
    user_id = str(inter.user.id)

    async with AsyncSessionLocal() as db:
      cooldown_start = await crud.get_work_cooldown(db, user_id)

      if cooldown_start + const.COOLDOWNS["work"] < datetime.datetime.now().timestamp():
        balance = await crud.get_user_balance(db, user_id)
        new_balance = balance + payout
        await crud.update_user_balance(db, user_id, payout)
        await crud.update_work_cooldown(db, user_id)

        embed = discord.Embed(
          title="Work",
          description=f"You worked as a {job} and earned {payout} coins. Your new balance is {new_balance} coins."
        )
        await inter.response.send_message(embed=embed)
        return

    remaining_time = self.calculate_remaining_time(const.COOLDOWNS["work"], cooldown_start)
    hours, minutes = self.format_remaining_time(remaining_time)
    embed = discord.Embed(
      title="Work",
      description=f"You can't work for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)

  @group.command(name="bankrob", description="Try and rob the bank for some coins!")
  async def bankrob(self, inter: discord.Interaction) -> None:
    guild_id = str(inter.guild.id)
    user_id = str(inter.user.id)

    async with AsyncSessionLocal() as db:
      cooldown_start = await crud.get_bank_rob_cooldown(db, guild_id)

      if cooldown_start + const.COOLDOWNS["bank_rob"] >= datetime.datetime.now().timestamp():
          remaining_time = self.calculate_remaining_time(const.COOLDOWNS["bank_rob"], cooldown_start)
          hours, minutes = self.format_remaining_time(remaining_time)
          embed = discord.Embed(
              title="Bank Robbery :bank:",
              description=f"The bank has recently been robbed. You can try again in {hours}hrs and {minutes}m.",
              color=discord.Color.red()
          )
          await inter.response.send_message(embed=embed)
          return

      await crud.update_bank_rob_cooldown(db, guild_id)

      success = self.percentage_chance(40)
      balance = await crud.get_user_balance(db, user_id)

      if success:
          payout = self.get_random_payout(const.MIN_BANK_ROB_PAYOUT, const.MAX_BANK_ROB_PAYOUT)
          new_balance = balance + payout
          await crud.update_user_balance(db, user_id, payout)

          embed = discord.Embed(
              title="Bank Robbery :bank:",
              description=f"You successfully robbed the bank and stole {payout} coins! Your new balance is {new_balance} coins.",
              color=discord.Color.green()
          )
          await inter.response.send_message(embed=embed)
      else:
          fine = balance // 10
          new_balance = balance - fine
          await crud.update_user_balance(db, user_id, -fine)

          embed = discord.Embed(
              title="Bank Robbery :bank:",
              description=f"You were caught trying to rob the bank! You were fined {fine} coins. Your new balance is {new_balance} coins.",
              color=discord.Color.red()
          )
          await inter.response.send_message(embed=embed)

  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    success = self.percentage_chance(15)
    user_id = str(inter.user.id)

    if success:
      payout = random.randint(const.MIN_BEG_PAYOUT, const.MAX_BEG_PAYOUT)
      async with AsyncSessionLocal() as db:
        balance = await crud.get_user_balance(db, user_id)
        new_balance = balance + payout
        await crud.update_user_balance(db, user_id, payout)

      embed = discord.Embed(
        title="Beg :pray:",
        description=f"Someone felt bad for you and gave you {payout} coins. Your new balance is {new_balance} coins.",
        color=discord.Color.green()
      )
      await inter.response.send_message(embed=embed)
      return

    embed = discord.Embed(
      title="Beg :pray:",
      description="You acted homeless, but no one cared,",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)

  @group.command(name="gamble", description="Gamble for a chance to double your money!")
  @app_commands.describe(amount="Amount of money to gamble.")
  async def gamble(self, inter: discord.Interaction, amount: int) -> None:
    user_id = str(inter.user.id)

    async with AsyncSessionLocal() as db:
      balance = await crud.get_user_balance(db, user_id)

      if amount > balance:
        embed = discord.Embed(
          title="Gambling :game_die:",
          description=f"You cannot gamble more than you have. Your balance is {balance}.",
          color=discord.Color.red()
        )
        await inter.response.send_message(embed=embed)
        return

      success = self.percentage_chance(30)

      if success:
        payout = amount * 2
        color = discord.Color.green()
      else:
        payout = -amount
        color = discord.Color.red()

      new_balance = balance + payout
      await crud.update_user_balance(db, user_id, payout)

    embed = discord.Embed(
      title="Gambling :game_die:",
      description=f"You gambled {amount} and {'won' if success else 'lost'} {abs(payout)} coins. Your new balance is {new_balance}.",
      color=color
    )

    await inter.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
