import discord
import asyncpg
import logging
import aiohttp
import os

from discord import app_commands
from discord.ext import commands
from collections import defaultdict
from discord.ui import View, Button
from discord import Interaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.environ.get('DB_URL')

class MedalUserView(View):
    def __init__(self, medals, title, author_name, author_icon):
        super().__init__(timeout=180)
        self.medals = medals  # list of medal lines, each a string
        self.page = 0
        self.title = title
        self.author_name = author_name
        self.author_icon = author_icon
        self.page_size = 50  # 50 medals per page

        # Pre-chunk medals into pages
        self.pages = []
        for i in range(0, len(self.medals), self.page_size):
            chunk = "".join(self.medals[i:i+self.page_size])
            self.pages.append(chunk or "No medals on this page.")

    def get_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.page + 1}/{len(self.pages)})",
            description=self.pages[self.page],
            color=0x1ba300
        )
        embed.set_author(name=self.author_name, icon_url=self.author_icon)
        return embed

    async def update_message(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: Interaction, button: Button):
        if self.page < len(self.pages) - 1:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

class MedalLeaderboardView(View):
    def __init__(self, sorted_users, place_emoji, medal_type=None):
        super().__init__(timeout=180)
        self.sorted_users = sorted_users  # list of (username, (g,s,b)) or (username, count)
        self.page = 0
        self.place_emoji = place_emoji
        self.page_size = 50
        self.medal_type = medal_type  # "Gold", "Silver", "Bronze", or None

    def get_page_content(self):
        start = self.page * self.page_size
        end = start + self.page_size
        entries = self.sorted_users[start:end]
        text = ""
        for i, entry in enumerate(entries, start=start + 1):
            if self.medal_type:
                # When medal_type is specified, entries are (username, count)
                user, count = entry
                line = f"{i}. {user} - {count} {self.medal_type} Medals\n"
                if i <= 3:
                    line = f"__{line.strip()}__\n"
            else:
                # When medal_type is None, entries are (username, (g, s, b))
                user, (g, s, b) = entry
                total = g + s + b
                line = f"{i}. {user} - {total} Medals (🥇 {g}, 🥈 {s}, 🥉 {b})\n"
                if i <= 3:
                    line = f"__{line.strip()}__\n"
            text += line
        return text or "No entries found on this page."

    async def update_message(self, interaction: Interaction):
        type_str = f" {self.medal_type}" if self.medal_type else ""
        embed = discord.Embed(
            title=f"{self.place_emoji} Total{type_str} Medals Leaderboard (Page {self.page + 1})",
            description=self.get_page_content(),
            color=0x1ba300
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: Interaction, button: Button):
        max_page = (len(self.sorted_users) - 1) // self.page_size
        if self.page < max_page:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

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

        result = await self.get_medals_data(type, username)

        if isinstance(result, tuple):
            # Global leaderboard with pagination (total or filtered by type)
            sorted_users, place_emoji = result
            if not sorted_users:
                await interaction.followup.send("No medals found.")
                return

            medal_type = None
            emoji_to_type = {"🥇": "Gold", "🥈": "Silver", "🥉": "Bronze"}
            if place_emoji in emoji_to_type:
                medal_type = emoji_to_type[place_emoji]

            view = MedalLeaderboardView(sorted_users, place_emoji, medal_type=medal_type)
            embed = discord.Embed(
                title=f"{place_emoji} Total{' ' + medal_type if medal_type else ''} Medals Leaderboard (Page 1)",
                description=view.get_page_content(),
                color=0x1ba300
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)

        elif isinstance(result, list):
            # Username + type: paginate user medals
            place_emoji = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[type]
            title = f"{place_emoji} {username}'s {type} Medals"
            medals_list = result
            view = MedalUserView(
                medals_list,
                title,
                interaction.user.display_name,
                interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=view.get_embed(), view=view)

        else:
            # Simple string result (other cases)
            place_emoji = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}.get(type, "🏅")
            embed = discord.Embed(title=f"{place_emoji} Leaderboard", description=result, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)

    async def fetch_badge_info(self, badgeID):
        async with aiohttp.ClientSession() as session:
            url = f"https://badges.roblox.com/v1/badges/{badgeID}"
            async with session.get(url) as response:
                return await response.json()

    async def get_medals_data(self, type: str, username: str):
        async with self.pool.acquire() as conn:
            conditions, params = [], []
            if username:
                params.append(username)
                conditions.append(f"username = ${len(params)}")
            if type in ["Gold", "Silver", "Bronze"]:
                medal_map = {"Gold": 1, "Silver": 2, "Bronze": 3}
                params.append(medal_map[type])
                conditions.append(f"place = ${len(params)}")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            rows = await conn.fetch(f"SELECT username, badgeid, place FROM medals {where_clause};", *params)

        data = [dict(r) for r in rows]

        if type and not username:
            # Filtered global leaderboard by medal type with pagination
            count_map = defaultdict(int)
            medal_place = {"Gold": 1, "Silver": 2, "Bronze": 3}[type]
            for entry in data:
                if entry["place"] == medal_place:
                    count_map[entry["username"]] += 1
            sorted_users = sorted(count_map.items(), key=lambda x: x[1], reverse=True)
            return sorted_users, {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[type]

        elif type and username:
            # Build list of medal entries (strings), one per medal
            medals_list = []
            for entry in reversed(data):
                badge_info = await self.fetch_badge_info(entry["badgeid"])
                name = badge_info.get("name", "Unknown Badge")
                game_info = badge_info.get("awardingUniverse", {})
                game_name = game_info.get("name", "Unknown Game")
                game_id = game_info.get("rootPlaceId", 0)
                url = f"https://www.roblox.com/games/{game_id}/"
                medal_icon = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[type]
                line = f"[{game_name}: {name}]({url}) {medal_icon}\n"
                medals_list.append(line)
            return medals_list

        elif not type and not username:
            # Global total medals leaderboard with pagination
            count_map = defaultdict(lambda: [0, 0, 0])
            for entry in data:
                u, p = entry["username"], entry["place"]
                if p == 1: count_map[u][0] += 1
                elif p == 2: count_map[u][1] += 1
                elif p == 3: count_map[u][2] += 1
            sorted_users = sorted(count_map.items(), key=lambda x: sum(x[1]), reverse=True)
            return sorted_users, "🏅"

        elif not type and username:
            # Single user summary string
            g = s = b = 0
            for entry in data:
                if entry["place"] == 1: g += 1
                elif entry["place"] == 2: s += 1
                elif entry["place"] == 3: b += 1
            return f"{username} has a total of {g + s + b} Medals:\n🥇 {g} Gold\n🥈 {s} Silver\n🥉 {b} Bronze" \
                   if g + s + b else f"{username} has no medals."

async def setup(client: commands.Bot) -> None:
    await client.add_cog(medals(client))
