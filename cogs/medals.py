import discord
import aiohttp
import urllib.parse
import os
import logging

from discord import app_commands
from discord.ext import commands
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.environ.get('medals_api_key')
BASE_URL = "https://medals-4193.restdb.io/rest/medals"
HEADERS = {
    'content-type': "application/json",
    'x-apikey': API_KEY,
    'cache-control': "no-cache"
}

class medals(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

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

        place_emoji = "🏅"
        if type == "Gold":
            place_emoji = "🥇"
        elif type == "Silver":
            place_emoji = "🥈"
        elif type == "Bronze":
            place_emoji = "🥉"

        if type and username:
            embed_title = f"{place_emoji} {username}'s {type} Medals"
        elif type:
            embed_title = f"{place_emoji} {type} Leaderboard"
        elif username:
            embed_title = f"{place_emoji} {username}'s Total Medals"
        else:
            embed_title = f"{place_emoji} Total Medals Leaderboard"

        embed = discord.Embed(title=embed_title, description=result_text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.followup.send(embed=embed)

    async def fetch_badge_info(self, session, badgeID):
        url = f"https://badges.roblox.com/v1/badges/{badgeID}"
        async with session.get(url) as response:
            return await response.json()

    async def get_medals_data(self, type: str, username: str) -> str:
        async with aiohttp.ClientSession() as session:
            query = {}
            if username:
                query["username"] = username
            if type in ["Gold", "Silver", "Bronze"]:
                query["place"] = {"Gold": 1, "Silver": 2, "Bronze": 3}[type]
            
            query_string = urllib.parse.quote(str(query).replace("'", '"'))
            url = f"{BASE_URL}?q={query_string}"

            async with session.get(url, headers=HEADERS) as response:
                data = await response.json()

            text = ""

            if type and not username:
                # Leaderboard by medal type
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
                # Specific user's medals
                for entry in reversed(data):
                    badgeID = entry["badgeID"]
                    badge_info = await self.fetch_badge_info(session, badgeID)
                    badgeName = badge_info["name"]
                    badgeGame = badge_info["awardingUniverse"]["name"]
                    gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                    gameURL = f"https://www.roblox.com/games/{gameID}/"

                    medal_icon = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[type]
                    entry_line = f"[{badgeGame}: {badgeName}]({gameURL}) {medal_icon}\n"
                    if len(text) + len(entry_line) > 4050:
                        text += "More entries found but not displayed."
                        break
                    text += entry_line
            elif not type and not username:
                # Global total leaderboard
                count_map = defaultdict(lambda: [0, 0, 0])  # gold, silver, bronze
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
                # Specific user's total medals
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
