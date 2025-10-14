import discord
from discord.ext import commands
from discord import app_commands
from functools import wraps
from DatabaseRefactor import Database
import constants as const
import random
import datetime

class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  def percentage_chance(self, percentage):
    return random.choices([True, False], weights=[percentage, 100 - percentage], k=1)[0]

  def format_remaining_time(self, remaining_time):
    remaining_time_hours = int(remaining_time // 3600)
    remaining_time_minutes = int((remaining_time % 3600) // 60)

    return (remaining_time_hours, remaining_time_minutes)

  def calculate_remaining_time(self, cooldown_length, cooldown_start):
    current_time = datetime.datetime.now().timestamp()
    return (cooldown_start + cooldown_length) - current_time

  async def check_cooldown(self, cooldown_column, table, id_column, id, cooldown_length):
    async with Database() as db:
      cooldown_start_time = await db.get_cooldown_start(cooldown_column, table, id_column, id)

    if cooldown_start_time + cooldown_length < datetime.datetime.now().timestamp():
      return True
    return cooldown_start_time

  async def payout(self, id, payout):
    async with Database() as db:
      await db.update_balance(id, payout)
      return

  async def update_cooldown(self, column, table, id_column, id):
    async with Database() as db:
      await db.update_cooldown(column, table, id_column, id)

  def get_random_job(self):
    job_index = random.randint(0, len(const.JOB_LIST) - 1)
    return const.JOB_LIST[job_index]

  def get_random_payout(self, min, max):
    return random.randint(min, max)

  async def get_balance(self, id):
    async with Database() as db:
      balance = await db.get_balance(id)
      return balance

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

  @group.command(name="daily", description="Claim your daily coins!")
  async def daily(self, inter) -> None:
    payout = const.DAILY_PAYOUT
    result = await self.check_cooldown(
      const.DAILY_COLUMN,
      const.USER_TABLE,
      const.USER_COLUMN,
      inter.user.id,
      const.COOLDOWNS["daily"]
    )

    if result == True:
      balance = await self.get_balance(inter.user.id)
      new_balance = balance + const.DAILY_PAYOUT
      await self.payout(inter.user.id, new_balance)
      await self.update_cooldown(
        const.DAILY_COLUMN,
        const.USER_TABLE,
        const.USER_COLUMN,
        inter.user.id
      )

      embed = discord.Embed(
        title="Daily :coin:",
        description=f"{const.DAILY_PAYOUT} collected! Your balance is now {new_balance}.",
        color=discord.Color.green())
      await inter.response.send_message(embed=embed)
      return

    remaining_time = await self.calculate_remaining_time(const.COOLDOWNS["daily"], result)
    hours, minutes = await self.format_remaining_time(remaining_time)
    embed = discord.Embed(
      title="Daily :coin:",
      description=f"You can't claim your daily for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)
    return

  @group.command(name="work", description="Work a random job for some coins.")
  async def work(self, inter: discord.Interaction) -> None:
    payout = self.get_random_payout(
      const.MIN_WORK_PAYOUT,
      const.MAX_WORK_PAYOUT
    )

    job = self.get_random_job()
    result = await self.check_cooldown(
      const.WORK_COLUMN,
      const.USER_TABLE,
      const.USER_COLUMN,
      inter.user.id,
      const.COOLDOWNS["work"]
    )

    if result == True:
      balance = await self.get_balance(inter.user.id)
      new_balance = balance + payout
      await self.payout(inter.user.id, new_balance)
      await self.update_cooldown(
        const.WORK_COLUMN,
        const.USER_TABLE,
        const.USER_COLUMN,
        inter.user.id
      )

      embed = discord.Embed(
        title="Work",
        description=f"You worked as a {job} and earned {payout} coins. Your new balance is {new_balance} coins."
      )
      await inter.response.send_message(embed=embed)
      return

    remaining_time = self.calculate_remaining_time(const.COOLDOWNS["work"], result)
    hours, minutes = self.format_remaining_time(remaining_time)
    embed = discord.Embed(
      title="Work",
      description=f"You can't work for another {hours}hrs and {minutes}m",
      color=discord.Color.red()
    )
    await inter.response.send_message(embed=embed)
    return

  @group.command(name="bankrob", description="Try and rob the bank for some coins!")
  async def bankrob(self, inter: discord.Interaction) -> None:
    cooldown_result = await self.check_cooldown(
        const.BANK_ROB_COLUMN,
        const.GUILD_TABLE,
        const.GUILD_COLUMN,
        inter.guild.id,
        const.COOLDOWNS["bank_rob"]
    )

    if cooldown_result != True:
        remaining_time = self.calculate_remaining_time(const.COOLDOWNS["bank_rob"], cooldown_result)
        hours, minutes = self.format_remaining_time(remaining_time)
        embed = discord.Embed(
            title="Bank Robbery :bank:",
            description=f"The bank has recently been robbed. You can try again in {hours}hrs and {minutes}m.",
            color=discord.Color.red()
        )
        await inter.response.send_message(embed=embed)
        return

    await self.update_cooldown(
        const.BANK_ROB_COLUMN,
        const.GUILD_TABLE,
        const.GUILD_COLUMN,
        inter.guild.id
    )

    # 60% chance of getting caught means 40% chance of success
    success = self.percentage_chance(40)
    balance = await self.get_balance(inter.user.id)

    if success:
        payout = self.get_random_payout(
          const.MIN_BANK_ROB_PAYOUT,
          const.MAX_BANK_ROB_PAYOUT
        )
        new_balance = balance + payout
        await self.payout(inter.user.id, new_balance)

        embed = discord.Embed(
            title="Bank Robbery :bank:",
            description=f"You successfully robbed the bank and stole {payout} coins! Your new balance is {new_balance} coins.",
            color=discord.Color.green()
        )
        await inter.response.send_message(embed=embed)
    else:
        # Player is fined 10% of their balance
        fine = balance // 10
        new_balance = balance - fine
        await self.payout(inter.user.id, new_balance)

        embed = discord.Embed(
            title="Bank Robbery :bank:",
            description=f"You were caught trying to rob the bank! You were fined {fine} coins. Your new balance is {new_balance} coins.",
            color=discord.Color.red()
        )
        await inter.response.send_message(embed=embed)


  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    success = await self.percentage_chance(15)

    if success:
      payout = random.randint(const.MIN_BEG_PAYOUT, const.MAX_BEG_PAYOUT)
      balance = await self.get_balance(inter.user.id)
      new_balance = balance + payout
      await self.payout(inter.user.id, new_balance)

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
    return

  @group.command(name="gamble", description="Gamble for a chance to double your money!")
  @app_commands.describe(amount="Amount of money to gamble.")
  async def gamble(self, inter: discord.Interaction, amount: int) -> None:
    balance = await self.get_balance(inter.user.id)

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
      payout = amount*2
      color = discord.Color.green()
    else:
      payout = -amount
      color = discord.Color.red()

    new_balance = balance + payout
    await self.payout(inter.user.id, new_balance)

    embed = discord.Embed(
      title="Gambling :game_die:",
      description=f"You gambled {amount} and {"won" if success else "lost"} {abs(payout)} coins. Your new balance is {new_balance}.",
      color=color
    )

    await inter.response.send_message(embed=embed)
    return

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
