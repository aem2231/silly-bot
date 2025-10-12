import discord
from discord.ext import commands
from discord import app_commands
from Database import Database
import random

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
      self.db.update_coins(inter.user.id, payout)
      embed.description=f"You worked as as {job} and got paid {payout}! Your balance is now {new_balance}"
      _ = await inter.response.send_message(embed=embed)




  @group.command(name="gamble", description="Gamble some money.")
  async def gamble(self, inter: discord.Interaction) -> None:
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
