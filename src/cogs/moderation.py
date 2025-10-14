import discord
from discord import app_commands
from discord.ext import commands
import os

class Moderation(commands.Cog):
    group: app_commands.Group = app_commands.Group(name="moderation", description="Moderation commands")
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        
    @group.command(name="addrestriction", description="Add a word to the restriction list")
    @app_commands.describe(message="The message to echo.")
    async def addrestriction(self, inter: discord.Interaction, message: str) -> None:
        
        path = "data/badwords.txt"
        # Read existing words
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read().strip()
                words = [w.strip() for w in content.split(",") if w.strip()]
        else:
            words = []
        # Add word
        new_word = message.lower()
        if new_word not in words:
            words.append(new_word)
            with open(path, "w") as f:
                f.write(",".join(words))
            confirm_message = f"Added {new_word} to list of bad words"
        else:
            confirm_message = f"{new_word} is already in the list of bad words"
        _ = await inter.response.send_message(confirm_message)
        
  
async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Moderation(bot))