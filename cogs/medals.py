import discord
import aiosqlite
import aiohttp
from discord import app_commands
from discord.ext import commands

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
        print(f"medals command initiated - {interaction.user.display_name}")

        result_text = await self.get_medals_data(type, username)

        place_emoji = ""
        embed_title = ""

        if type == "Gold":
            place_emoji = "🥇"
        elif type == "Silver":
            place_emoji = "🥈"
        elif type == "Bronze":
            place_emoji = "🥉"
        else:
            place_emoji = "🏅"

        if type != '' and username != '':
            embed_title = f"{place_emoji} {username}'s {type} Medals"
        elif type != '' and username == '':
            embed_title = f"{place_emoji} {type} Leaderboard"
        elif type == '' and username == '':
            embed_title = f"{place_emoji} Total Medals Leaderboard"
        elif type == '' and username != '':
            embed_title = f"{place_emoji} {username}'s Total Medals"

        embed = discord.Embed(title=embed_title, description=result_text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.followup.send(embed=embed)

    async def fetch_badge_info(self, session, badgeID):
        url = f"https://badges.roblox.com/v1/badges/{badgeID}"
        async with session.get(url) as response:
            return await response.json()

    async def get_medals_data(self, type: str, username: str) -> str:
        async with aiosqlite.connect("medals_backup.db") as connection:
            cursor = await connection.cursor()

            text = ""

            if type == "Gold" and username == '':
                await cursor.execute("""
                    SELECT username, COUNT(*) as gold_count
                    FROM medals
                    WHERE place = 1
                    GROUP BY username
                    ORDER BY gold_count DESC
                """)

                results = await cursor.fetchall()

                count = 1
                for row in results:
                    user, gold_count = row
                    if count <= 3:
                        text += f"__{count}. {user} - {gold_count}__ \n"
                    else:
                        text += f"{count}. {user} - {gold_count} \n"
                    count += 1

            elif type == "Gold" and username != '':
                place = 1
                await cursor.execute("""
                    SELECT *
                    FROM medals
                    WHERE username = ? AND place = ?
                """, (username, place))

                results = await cursor.fetchall()

                async with aiohttp.ClientSession() as session:
                    for row in reversed(results):
                        badgeID = row[1]

                        badge_info = await self.fetch_badge_info(session, badgeID)
                        badgeName = badge_info["name"]
                        badgeGame = badge_info["awardingUniverse"]["name"]
                        gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                        gameURL = f"https://www.roblox.com/games/{gameID}/"

                        entry = f"[{badgeGame}: {badgeName}]({gameURL}) 🥇\n"

                        if len(text) + len(entry) > 4050:
                            text += "More entries found but not displayed."
                            break
                        text += entry

            elif type == "Silver" and username == '':
                await cursor.execute("""
                    SELECT username, COUNT(*) as silver_count
                    FROM medals
                    WHERE place = 2
                    GROUP BY username
                    ORDER BY silver_count DESC
                """)

                results = await cursor.fetchall()

                count = 1
                for row in results:
                    user, silver_count = row
                    if count <= 3:
                        text += f"__{count}. {user} - {silver_count}__ \n"
                    else:
                        text += f"{count}. {user} - {silver_count} \n"
                    count += 1

            elif type == "Silver" and username != '':
                place = 2
                await cursor.execute("""
                    SELECT *
                    FROM medals
                    WHERE username = ? AND place = ?
                """, (username, place))

                results = await cursor.fetchall()

                async with aiohttp.ClientSession() as session:
                    for row in reversed(results):
                        badgeID = row[1]

                        badge_info = await self.fetch_badge_info(session, badgeID)
                        badgeName = badge_info["name"]
                        badgeGame = badge_info["awardingUniverse"]["name"]
                        gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                        gameURL = f"https://www.roblox.com/games/{gameID}/"

                        entry = f"[{badgeGame}: {badgeName}]({gameURL}) 🥈\n"
                        
                        if len(text) + len(entry) > 4050:
                            text += "More entries found but not displayed."
                            break
                        text += entry

            elif type == "Bronze" and username == '':
                await cursor.execute("""
                    SELECT username, COUNT(*) as bronze_count
                    FROM medals
                    WHERE place = 3
                    GROUP BY username
                    ORDER BY bronze_count DESC
                """)

                results = await cursor.fetchall()

                count = 1
                for row in results:
                    user, bronze_count = row
                    if count <= 3:
                        text += f"__{count}. {user} - {bronze_count}__ \n"
                    else:
                        text += f"{count}. {user} - {bronze_count} \n"
                    count += 1

            elif type == "Bronze" and username != '':
                place = 3
                await cursor.execute("""
                    SELECT *
                    FROM medals
                    WHERE username = ? AND place = ?
                """, (username, place))

                results = await cursor.fetchall()

                async with aiohttp.ClientSession() as session:
                    for row in reversed(results):
                        badgeID = row[1]

                        badge_info = await self.fetch_badge_info(session, badgeID)
                        badgeName = badge_info["name"]
                        badgeGame = badge_info["awardingUniverse"]["name"]
                        gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                        gameURL = f"https://www.roblox.com/games/{gameID}/"

                        entry = f"[{badgeGame}: {badgeName}]({gameURL}) 🥉\n"
                        
                        if len(text) + len(entry) > 4050:
                            text += "More entries found but not displayed."
                            break
                        text += entry

            elif type == '' and username == '':
                await cursor.execute("""
                        SELECT username, 
                            SUM(CASE WHEN place = 1 THEN 1 ELSE 0 END) as gold_count,
                            SUM(CASE WHEN place = 2 THEN 1 ELSE 0 END) as silver_count,
                            SUM(CASE WHEN place = 3 THEN 1 ELSE 0 END) as bronze_count
                        FROM medals
                        GROUP BY username
                        ORDER BY (gold_count + silver_count + bronze_count) DESC
                    """)

                results = await cursor.fetchall()

                count = 1
                for row in results:
                    user, gold_count, silver_count, bronze_count = row
                    total_count = gold_count + silver_count + bronze_count
                    if count <= 3:
                        text += f"__{count}. {user} - {total_count} Medals (🥇 {gold_count}, 🥈 {silver_count}, 🥉 {bronze_count})__\n"
                    else:
                        text += f"{count}. {user} - {total_count} Medals (🥇 {gold_count}, 🥈 {silver_count}, 🥉 {bronze_count})\n"
                    count += 1

                    if count > 50:
                        break

            elif type == '' and username != '':
                await cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN place = 1 THEN 1 ELSE 0 END) as gold_count,
                        SUM(CASE WHEN place = 2 THEN 1 ELSE 0 END) as silver_count,
                        SUM(CASE WHEN place = 3 THEN 1 ELSE 0 END) as bronze_count
                    FROM medals
                    WHERE username = ?
                """, (username,))

                result = await cursor.fetchone()
                gold_count, silver_count, bronze_count = result

                if gold_count is None:
                    text += f"{username} has no medals."
                else:
                    total_count = gold_count + silver_count + bronze_count
                    text += f"{username} has a total of {total_count} Medals:\n🥇 {gold_count} Gold\n🥈 {silver_count} Silver\n🥉 {bronze_count} Bronze"

        return text

async def setup(client: commands.Bot) -> None:
    await client.add_cog(medals(client))
