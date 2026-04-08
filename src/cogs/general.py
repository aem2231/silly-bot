import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
  group: app_commands.Group = app_commands.Group(name="utility", description="Utility commands")

  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot

  @group.command(name="ping", description="Get the bot's latency")
  async def ping(self, inter: discord.Interaction) -> None:
    _ = await inter.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms") # the _ stops your linter/type checker from being a crybaby bitch

  @group.command(name="echo", description="Echoes a message.")
  @app_commands.describe(message="The message to echo.")
  async def echo(self, inter: discord.Interaction, message: str) -> None:
    _ = await inter.response.send_message(message)

  @app_commands.command(name="help", description="Get help with available commands")
  async def help(self, inter: discord.Interaction) -> None:
    embed = discord.Embed(
      title="Bot Commands Help",
      description="Here are all the available commands:",
      color=discord.Color.blue()
    )

    embed.add_field(
      name="Utility Commands",
      value="`/utility ping` - Get the bot's latency\n`/utility echo <message>` - Echo a message",
      inline=False
    )

    embed.add_field(
      name="Economy Commands",
      value="`/economy balance` - Check your balance\n`/economy daily` - Claim daily coins\n`/economy work` - Work for coins\n`/economy beg` - Beg for money\n`/economy gamble <amount>` - Gamble your coins\n`/economy bankrob` - Rob the bank",
      inline=False
    )

    embed.add_field(
      name="Media Commands",
      value="`/image_search <query>` - Search for an image\n`/hug <user>` - Hug a user\n`/kiss <user>` - Kiss a user\n`/kill <user>` - Kill a user\n`/slap <user>` - Slap a user",
      inline=False
    )

    embed.add_field(
        name="Levelling",
        value="`/level` - Check your level\n`/leaderboard` - Check the leaderboard",
        inline=False
    )

    _ = await inter.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(General(bot))
