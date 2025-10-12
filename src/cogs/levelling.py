import discord
from discord.ext import commands
from discord import app_commands
from Database import Database
import random

class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()


async def setup(bot: commands.Bot):
    await bot.add_cog(Levelling(bot))
