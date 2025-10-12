import discord
from discord.ext import commands
from discord import app_commands
from Database import Database
import random
import time

class Economy(commands.Cog):
  group = app_commands.Group(name="economy", description="Economy commands")
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.db = Database()
    self.job_list = [
      "Cleaner",
      "Cashier",
      "Uber Driver",
      "Bartender",
      "Binman",
      "Twitch streamer"
    ]

  @group.command(name="work", description="Work a random job for some dabloons.")
  async def work(self, inter: discord.Interaction) -> None:

    embed = discord.Embed(
      title="Work",
      description=""
    )

    can_work = self.db.check_work(inter.user.id)
    if can_work is None:
      embed.description = "Database error occurred. Please try again later."
      _ = await inter.response.send_message(embed=embed)
      return

    if can_work[0] == False:
      six_hours_seconds = 21600
      time_since_last_work = can_work[1]
      time_to_work = six_hours_seconds - time_since_last_work

      time_to_work = max(0, time_to_work)

      hours_to_work = time_to_work // 3600
      minutes_to_work = (time_to_work % 3600) // 60

      embed.description=f"You cannot work for another {int(hours_to_work)}hrs {int(minutes_to_work)}m"
      _ = await inter.response.send_message(embed=embed)
    else:
      payout = random.randint(100, 250)
      balance = self.db.get_balance(inter.user.id)
      job = self.job_list[random.randint(0, (len(self.job_list)-1))]
      if balance == None:
        _ = await inter.response.send_message("Something went wrong :(")
        return
      new_balance = payout+balance
      self.db.update_coins(inter.user.id, new_balance)
      embed.description=f"You worked as as {job} and got paid {payout}! Your balance is now {new_balance}"
      _ = await inter.response.send_message(embed=embed)

  @group.command(name="daily", description="Claim daily reward")
  async def daily(self, inter: discord.Interaction) -> None:
    embed = discord.Embed(
      title="Daily",
      description=""
    )

    can_claim_daily = self.db.check_daily(inter.user.id)
    if can_claim_daily == None:
      embed.description = "Database error occured. Please try again later."
      _ = await inter.response.send_message(embed=embed)
      return

    if can_claim_daily[0] == False:
      day_seconds = 86400
      time_since_last_daily = can_claim_daily[1]
      time_to_daily = day_seconds - time_since_last_daily

      time_to_daily = max(0, time_to_daily)

      hours_to_daily = time_to_daily // 3600
      minutes_to_daily = (time_to_daily % 3600) // 60

      embed.description=f"You already claimed your daily today. Claim your next daily in {int(hours_to_daily)}hrs {int(minutes_to_daily)}m"
      _ = await inter.response.send_message(embed=embed)
      return

    else:
      payout = 1000
      balance = self.db.get_balance(inter.user.id)
      if balance == None:
        _ = await inter.response.send_message("Something went wrong, try again later.")
        return
      new_balance = balance + payout
      self.db.update_coins(inter.user.id, new_balance)
      embed.description=f"You claimed {payout}. Your new balance is {new_balance}"
      _ = await inter.response.send_message(embed=embed)
      return

  @group.command(name="gamble", description="Gamble some money.")
  @app_commands.describe(amount="amount")
  async def gamble(self, inter: discord.Interaction, amount: int) -> None:
    balance = self.db.get_balance(inter.user.id)
    chances = (True, False)

    embed = discord.Embed(
      title="Gambling",
      description=""
    )

    if balance == None:
      _ = await inter.response.send_message("Something went wrong, try again later.")
      return

    if amount > balance:
      embed.description= f"You cannot gamble more than your balance. Your balance is {balance} coins."
      _ = await inter.response.send_message(embed=embed)
      return

    win = chances[random.randint(0,1)]
    if win:
      winnings = amount*2
      new_balance = winnings + balance
      self.db.update_coins(inter.user.id, new_balance)
      embed.description = f"You won {winnings} coins! Your new balance is {new_balance}."
      _ = await inter.response.send_message(embed=embed)
      return

    new_balance = balance - amount
    self.db.update_coins(inter.user.id, new_balance)
    embed.description = f"You lost {amount} coins. Your new balance is {new_balance}"
    _ = await inter.response.send_message(embed=embed)

  @group.command(name="rob-bank", description="Rob the bank!")
  async def rob_bank(self, inter: discord.Interaction) -> None:
    chances = [False, False, False, False, False, False, False, True, True, True, True] # 0 means not caught
    caught = chances[random.randint(0,10)]
    payout = random.randint(5000, 10000)
    can_bank_rob = self.db.check_bank(inter.guild.id)
    balance = self.db.get_balance(inter.user.id)

    embed = discord.Embed(
      title="Bank rob",
      description=""
    )

    if can_bank_rob == None or balance == None:
      _ = await inter.response.send_message("Something went wrong, try again later.")
      return

    if can_bank_rob[0] and not caught:
      new_balance = balance + payout
      self.db.update_coins(inter.user.id, new_balance)
      description = f"You stole {payout} coins from the vault! Your new balance is {new_balance}"
      embed.description=description
    elif can_bank_rob[0] and caught:
      fine = balance//10
      new_balance = balance - fine
      self.db.update_coins(inter.user.id, new_balance)
      description = f"You were caughtand fined {fine} coins. Your new balance is {new_balance}"
    else:
      half_hour_seconds = 1800  # 30 minutes

      last_rob_time = can_bank_rob[1]  # Unix timestamp of last rob
      now = time.time()

      # Time passed since last rob
      time_since_last_rob = now - last_rob_time

      # Time left before next rob allowed
      time_to_bank = max(0, half_hour_seconds - time_since_last_rob)

      # Convert seconds to rounded minutes
      minutes_to_bank = round(time_to_bank / 60)

      description = f"The bank has recently been robbed. It can next be robbed in {minutes_to_bank}m"

    embed.description=description
    _ = await inter.response.send_message(embed=embed)

  @group.command(name="beg", description="Beg for money.")
  async def beg(self, inter: discord.Interaction) -> None:
    chances = [True, True, True, False, False]
    won = chances[random.randint(0,4)]
    balance = self.db.get_balance(inter.user.id)

    embed = discord.Embed(
      title="Beg",
      description=""
    )

    if balance == None:
      _ = await inter.response.send_message("Something went wrong, try again later.")
      return

    if won:
      coins = random.randint(5,50)
      new_balance = coins + balance
      self.db.update_coins(inter.user.id, new_balance)
      description = f"A kind stranger gave you {coins}! Your new balance is {new_balance}"
    else:
      description = "You pretented to be homeless, but no one cared."

    embed.description=description
    _ = await inter.response.send_message(embed=embed)

  @group.command(name="balance", description="Check your balance.")
  async def balance(self, inter: discord.Interaction) -> None:
    balance = self.db.get_balance(inter.user.id)
    if balance == None:
      description = "Something went wrong, try again later."
    else:
      description = f"Your balance is {balance} coins."

    embed = discord.Embed(
      title="Balance",
      description=description
    )

    _ = await inter.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Economy(bot))
