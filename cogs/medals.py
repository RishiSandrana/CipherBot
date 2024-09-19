import discord
import sqlite3
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
    async def medals(self, interaction: discord.Interaction, type: str, username: str = ''):
        await interaction.response.defer()

        result_text = await self.get_medals_data(type, username)

        place_emoji = ""
        if type == "Gold":
            place_emoji = "🥇"
        elif type == "Silver":
            place_emoji = "🥈"
        elif type == "Bronze":
            place_emoji = "🥉"

        embed_title = f"{place_emoji} {username}'s {type} Medals" if username else f"{place_emoji} {type} Leaderboard"
        embed = discord.Embed(title=embed_title, description=result_text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.followup.send(embed=embed)

    async def fetch_badge_info(self, session, badgeID):
        url = f"https://badges.roblox.com/v1/badges/{badgeID}"
        async with session.get(url) as response:
            return await response.json()

    async def get_medals_data(self, type: str, username: str) -> str:
        connection = sqlite3.connect("medals.db")
        cursor = connection.cursor()

        text = ""

        if type == "Gold" and username == '':
            cursor.execute("""
                SELECT username, COUNT(*) as gold_count
                FROM medals
                WHERE place = 1
                GROUP BY username
                ORDER BY gold_count DESC
            """)

            results = cursor.fetchall()

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
            cursor.execute("""
                SELECT *
                FROM medals
                WHERE username = ? AND place = ?
            """, (username, place))

            results = cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for row in reversed(results):
                    badgeID = row[1]

                    badge_info = await self.fetch_badge_info(session, badgeID)
                    badgeName = badge_info["name"]
                    badgeGame = badge_info["awardingUniverse"]["name"]
                    gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                    gameURL = f"https://www.roblox.com/games/{gameID}/"

                    text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥇\n"

        elif type == "Silver" and username == '':
            cursor.execute("""
                SELECT username, COUNT(*) as silver_count
                FROM medals
                WHERE place = 2
                GROUP BY username
                ORDER BY silver_count DESC
            """)

            results = cursor.fetchall()

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
            cursor.execute("""
                SELECT *
                FROM medals
                WHERE username = ? AND place = ?
            """, (username, place))

            results = cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for row in reversed(results):
                    badgeID = row[1]

                    badge_info = await self.fetch_badge_info(session, badgeID)
                    badgeName = badge_info["name"]
                    badgeGame = badge_info["awardingUniverse"]["name"]
                    gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                    gameURL = f"https://www.roblox.com/games/{gameID}/"

                    text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥈\n"

        elif type == "Bronze" and username == '':
            cursor.execute("""
                SELECT username, COUNT(*) as bronze_count
                FROM medals
                WHERE place = 3
                GROUP BY username
                ORDER BY bronze_count DESC
            """)

            results = cursor.fetchall()

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
            cursor.execute("""
                SELECT *
                FROM medals
                WHERE username = ? AND place = ?
            """, (username, place))

            results = cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for row in reversed(results):
                    badgeID = row[1]

                    badge_info = await self.fetch_badge_info(session, badgeID)
                    badgeName = badge_info["name"]
                    badgeGame = badge_info["awardingUniverse"]["name"]
                    gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                    gameURL = f"https://www.roblox.com/games/{gameID}/"

                    text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥉\n"

        connection.commit()
        connection.close()

        return text

async def setup(client: commands.Bot) -> None:
    await client.add_cog(medals(client))

# import discord
# import sqlite3
# import requests
# import asyncio
# from discord import app_commands
# from discord.ext import commands
#
# class medals(commands.Cog):
#     def __init__(self, client: commands.Bot):
#         self.client = client
#
#     @app_commands.command(name="medals", description="Find people with the most medals")
#     @app_commands.describe(type="Select your scope")
#     @app_commands.choices(type=[
#         discord.app_commands.Choice(name="Gold", value="Gold"),
#         discord.app_commands.Choice(name="Silver", value="Silver"),
#         discord.app_commands.Choice(name="Bronze", value="Bronze")
#     ])
#     async def medals(self, interaction: discord.Interaction, type: str, username: str = ''):
#         await interaction.response.defer()
#         await asyncio.sleep(4)
#
#         connection = sqlite3.connect("medals.db")
#         cursor = connection.cursor()
#
#         text = ""
#
#         if type == "Gold" and username == '':
#             cursor.execute("""
#                 SELECT username, COUNT(*) as gold_count
#                 FROM medals
#                 WHERE place = 1
#                 GROUP BY username
#                 ORDER BY gold_count DESC
#             """)
#
#             results = cursor.fetchall()
#
#             count = 1
#             for row in results:
#                 username, gold_count = row
#                 if count <= 3:
#                     text += f"__{count}. {username} - {gold_count}__ \n"
#                 else:
#                     text += f"{count}. {username} - {gold_count} \n"
#                 count += 1
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title="🥇 Leaderboard", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Gold" and username != '':
#             place = 1
#             cursor.execute(f"""
#                 SELECT *
#                 FROM medals
#                 WHERE username = ? AND place = ?
#             """, (username, place))
#
#             results = cursor.fetchall()
#
#             for row in reversed(results):
#                 badgeID = row[1]
#
#                 badgeName = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["name"]
#                 badgeGame = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "name"]
#                 gameID = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "rootPlaceId"]
#                 gameURL = f"https://www.roblox.com/games/{gameID}/"
#
#                 text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥇\n"
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title = f"{username}'s Gold Medals", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Silver" and username == '':
#             cursor.execute("""
#                 SELECT username, COUNT(*) as silver_count
#                 FROM medals
#                 WHERE place = 2
#                 GROUP BY username
#                 ORDER BY silver_count DESC
#             """)
#
#             results = cursor.fetchall()
#
#             count = 1
#             for row in results:
#                 username, silver_count = row
#                 if count <= 3:
#                     text += f"__{count}. {username} - {silver_count}__ \n"
#                 else:
#                     text += f"{count}. {username} - {silver_count} \n"
#                 count += 1
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title="🥈 Leaderboard", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Silver" and username != '':
#             place = 2
#             cursor.execute(f"""
#                 SELECT *
#                 FROM medals
#                 WHERE username = ? AND place = ?
#             """, (username, place))
#
#             results = cursor.fetchall()
#
#             for row in reversed(results):
#                 badgeID = row[1]
#
#                 badgeName = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["name"]
#                 badgeGame = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "name"]
#                 gameID = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "rootPlaceId"]
#                 gameURL = f"https://www.roblox.com/games/{gameID}/"
#
#                 text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥈\n"
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title = f"{username}'s Silver Medals", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Bronze" and username == '':
#             cursor.execute("""
#                 SELECT username, COUNT(*) as bronze_count
#                 FROM medals
#                 WHERE place = 3
#                 GROUP BY username
#                 ORDER BY bronze_count DESC
#             """)
#
#             results = cursor.fetchall()
#
#             count = 1
#             for row in results:
#                 username, bronze_count = row
#                 if count <= 3:
#                     text += f"__{count}. {username} - {bronze_count}__ \n"
#                 else:
#                     text += f"{count}. {username} - {bronze_count} \n"
#                 count += 1
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title="🥉 Leaderboard", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Bronze" and username != '':
#             place = 3
#             cursor.execute(f"""
#                 SELECT *
#                 FROM medals
#                 WHERE username = ? AND place = ?
#             """, (username, place))
#
#             results = cursor.fetchall()
#
#             for row in reversed(results):
#                 badgeID = row[1]
#
#                 badgeName = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["name"]
#                 badgeGame = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "name"]
#                 gameID = requests.get(f"https://badges.roblox.com/v1/badges/{badgeID}").json()["awardingUniverse"][
#                     "rootPlaceId"]
#                 gameURL = f"https://www.roblox.com/games/{gameID}/"
#
#                 text += f"[{badgeGame}: {badgeName}]({gameURL}) 🥉\n"
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title = f"{username}'s Bronze Medals", description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             await interaction.followup.send(embed=embed)
#
# async def setup(client: commands.Bot) -> None:
#     await client.add_cog(medals(client))