import os
import discord
from discord import app_commands
from discord.ext import commands
from core.config import settings
from db.database import Base, engine

intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

@client.event
async def on_ready():
    print("Client is running!")
    cog_list = os.listdir(settings.COGS_PATH)
    for cog in cog_list:  # load all cogs in cogs/ directory
        if cog.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{cog[:-3]}")
                print(f"{cog[:-3]} cog loaded successfully.")
            except Exception as e:
                print(f"Failed to load {cog[:-3]} cog: {e}")

    # create all tables in database after cogs load
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _ = await tree.sync()


async def is_developer(interaction: discord.Interaction):
    return interaction.user.id == settings.DEV_ID


@client.tree.command(name="reload-extension")
@app_commands.check(is_developer)
async def reload_extension(interaction: discord.Interaction, extension: str):
    try:
        await client.reload_extension(f"cogs.{extension}")
        _ = await interaction.response.send_message(
            f"{extension} extension reloaded successfully."
        )
    except Exception as e:
        _ = await interaction.response.send_message(
            f"Failed to reload {extension} extension: {e}"
        )

client.run(settings.BOT_TOKEN)
