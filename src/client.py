import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

cogs_path = "./src/cogs"

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

def setup_config():
  if not os.path.exists("data/"):
    os.mkdir("data")
setup_config()

@client.event
async def on_ready():
  print("Client is running!")
  cog_list = os.listdir(cogs_path)
  for cog in cog_list: # load all cogs in cogs/ directory
    if cog.endswith(".py"):
      try:
        await client.load_extension(f"cogs.{cog[:-3]}")
        print(f"{cog[:-3]} cog loaded successfully.")
      except Exception as e:
        print(f"Failed to load {cog[:-3]} cog: {e}")
  _ = await tree.sync()

async def is_developer(interaction: discord.Interaction):
  return interaction.user.id in [708680864728350790, 432799156440924160]

@client.tree.command(name='reload-extension')
@app_commands.check(is_developer)
async def reload_extension(interaction: discord.Interaction, extension: str):
  try:
    await client.reload_extension(f"cogs.{extension}")
    _ = await interaction.response.send_message(f"{extension} extension reloaded successfully.")
  except Exception as e:
    _ = await interaction.response.send_message(f"Failed to reload {extension} extension: {e}")

client.run(os.getenv("BOT_TOKEN"))
