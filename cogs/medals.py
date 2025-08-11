import discord
import asyncpg
import logging
import os

from discord import app_commands
from discord.ext import commands
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.environ.get('DB_URL')

class medals(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.pool = None

    async def cog_load(self):
        self.pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=5)

    async def cog_unload(self):
        await self.pool.close()

    @app_commands.command(name="medals", description="Find people with the most medals")
    @app_commands.describe(type="Select your scope")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="Gold", value="Gold"),
        discord.app_commands.Choice(name="Silver", value="Silver"),
        discord.app_commands.Choice(name="Bronze", value="Bronze")
    ])
    async def medals(self, interaction: discord.Interaction, type: str = '', username: str = ''):
        await interaction.response.defer()
        logger.info(f"medals command initiated - {interaction.user.display_name}")

        result_text = await self.get_medals_data(type, username)

        place_emoji = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}.get(type, "🏅")
        if type and username:
            embed_title = f"{place_emoji} {username}'s {type} Medals"
        elif type:
            embed_title = f"{place_emoji} {type} Leaderboard"
        elif username:
            embed_title = f"{place_emoji} {username}'s Total Medals"
        else:
            embed_title = f"{place_emoji} Total Medals Leaderboard"

        embed = discord.Embed(title=embed_title, description=result_text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)

    async def fetch_badge_info(self, badgeID):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"https://badges.roblox.com/v1/badges/{badgeID}"
            async with session.get(url) as response:
                return await response.json()

    async def get_medals_data(self, type: str, username: str) -> str:
        async with self.pool.acquire() as conn:
            conditions = []
            params = []
            if username:
                params.append(username)
                conditions.append(f"username = ${len(params)}")
            if type in ["Gold", "Silver", "Bronze"]:
                medal_map = {"Gold": 1, "Silver": 2, "Bronze": 3}
                params.append(medal_map[type])
                conditions.append(f"place = ${len(params)}")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            query = f"SELECT username, badgeid, place FROM medals {where_clause};"
            rows = await conn.fetch(query, *params)

        data = [dict(row) for row in rows]
        text = ""

        if type and not username:
            count_map = defaultdict(int)
            for entry in data:
                count_map[entry["username"]] += 1
            sorted_users = sorted(count_map.items(), key=lambda x: x[1], reverse=True)
            for i, (user, count) in enumerate(sorted_users, start=1):
                line = f"{i}. {user} - {count}\n"
                if i <= 3:
                    line = f"__{line.strip()}__ \n"
                text += line

        elif type and username:
            for entry in reversed(data):
                badgeID = entry["badgeid"]
                badge_info = await self.fetch_badge_info(badgeID)
                badgeName = badge_info.get("name", "Unknown Badge")
                awardingUniverse = badge_info.get("awardingUniverse", {})
                badgeGame = awardingUniverse.get("name", "Unknown Game")
                gameID = awardingUniverse.get("rootPlaceId", 0)
                gameURL = f"https://www.roblox.com/games/{gameID}/"
                medal_icon = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[type]
                entry_line = f"[{badgeGame}: {badgeName}]({gameURL}) {medal_icon}\n"
                if len(text) + len(entry_line) > 4050:
                    text += "More entries found but not displayed."
                    break
                text += entry_line

        elif not type and not username:
            count_map = defaultdict(lambda: [0, 0, 0])
            for entry in data:
                u = entry["username"]
                p = entry["place"]
                if p == 1:
                    count_map[u][0] += 1
                elif p == 2:
                    count_map[u][1] += 1
                elif p == 3:
                    count_map[u][2] += 1
            sorted_users = sorted(count_map.items(), key=lambda x: sum(x[1]), reverse=True)
            for i, (user, (g, s, b)) in enumerate(sorted_users, start=1):
                    total = g + s + b
                    line = f"{i}. {user} - {total} Medals (🥇 {g}, 🥈 {s}, 🥉 {b})\n"
                    if i <= 3:
                        line = f"__{line.strip()}__ \n"
                    text += line
                    if i >= 50:
                        break

        elif not type and username:
            g = s = b = 0
            for entry in data:
                p = entry["place"]
                if p == 1:
                    g += 1
                elif p == 2:
                    s += 1
                elif p == 3:
                    b += 1
            if g + s + b == 0:
                text = f"{username} has no medals."
            else:
                text = f"{username} has a total of {g + s + b} Medals:\n🥇 {g} Gold\n🥈 {s} Silver\n🥉 {b} Bronze"

        return text

async def setup(client: commands.Bot) -> None:
    await client.add_cog(medals(client))
