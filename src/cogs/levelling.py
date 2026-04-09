import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import with_db
from db import crud

class Levelling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def calculate_next_level_xp(self, x: int) -> int:
        return int(50 * (x ** 2) + 100 * x + 200)

    def calculate_multiplier(self, level: int) -> float:
        return 1.0 + (min(level, 50) / 10)

    def calculate_xp_increase(self, message: str, multiplier: float) -> int:
        if len(message) < 3:
            return 0
        base = min(len(message), 200)
        xp = round(base * multiplier) // 2
        return max(xp, 5)

    def check_level_up(self, xp: int, xp_needed: int) -> bool:
        return xp >= xp_needed

    async def get_level_up_embed(self, user_id: str, new_level: int):
        embed = discord.Embed(title="Level Up!", description=f"Level up fire emoji: **{new_level}**!", color=discord.Color.green())
        return embed

    @commands.Cog.listener()
    @with_db
    async def on_message(self, message: discord.Message, db: AsyncSession):
        if message.author.bot:
            return

        user_id = str(message.author.id)

        if not await crud.get_user_by_id(db, user_id):
            await crud.register_user(db, user_id, 0)

        current_level = await crud.get_user_level(db, user_id)
        current_xp = await crud.get_user_xp(db, user_id)

        multiplier = self.calculate_multiplier(current_level)
        xp_increase = self.calculate_xp_increase(message.content, multiplier)
        new_xp = current_xp + xp_increase

        xp_needed = self.calculate_next_level_xp(current_level)

        if self.check_level_up(new_xp, xp_needed):
            new_level = current_level + 1
            await crud.update_user_level(db, user_id, new_level)
            await crud.update_user_xp(db, user_id, new_xp)

            embed = await self.get_level_up_embed(user_id, new_level)
            await message.channel.send(embed=embed)
            await crud.update_user_xp(db, user_id, 0)
        else:
            await crud.update_user_xp(db, user_id, new_xp)

    @app_commands.command(name="level", description="View your level and XP")
    @with_db
    async def level(self, inter: discord.Interaction, db: AsyncSession):
        user_id = str(inter.user.id)

        level = await crud.get_user_level(db, user_id)
        xp = await crud.get_user_xp(db, user_id)
        embed = discord.Embed(title=f"{inter.user.name}'s Level", description=f"Level: {level}\nXP: {xp}\n{xp}/{self.calculate_next_level_xp(level)} for next level.")
        await inter.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the leaderboard")
    @with_db
    async def leaderboard(self, inter: discord.Interaction, db: AsyncSession):
        users = await crud.get_top_users_global(db, 10)
        leaderboard = "\n".join([f"{i+1}. <@{user.user_id}> - Level {user.level}" for i, user in enumerate(users)]) # update db to store usernames eventually
        embed = discord.Embed(title="Leaderboard", description=leaderboard)
        await inter.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Levelling(bot))
