import aiohttp
import discord
import asyncio
import sqlite3
from datetime import datetime
from discord import app_commands
from discord.ext import commands

class Badges(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="badges", description="Find people who have a certain badge")
    @app_commands.describe(type="Select your scope")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="RMH", value="RMH"),
        discord.app_commands.Choice(name="Zenith", value="Zenith"),
        discord.app_commands.Choice(name="All", value="All")
    ])
    async def badges(self, interaction: discord.Interaction, badge_id: str, type: str):
        await interaction.response.defer()

        connection = sqlite3.connect("medals.db")
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medals (
                username TEXT,
                badgeID INTEGER,
                place INTEGER,
                UNIQUE(username, badgeID, place)
            )
        ''')

        print("badges command initiated")
        count = 0

        def get_datetime(item):
            return datetime.fromisoformat(item[1].rstrip('Z'))

        listOfRMHRoleIDs = [3627780, 19516868, 25919204, 4059372, 26957538, 3927521, 3627781, 36896118, 36747671,
                            19962820, 3704753, 3720799, 36896024, 26492648, 4165630]
        listOfZenithRoleIDs = [103251082, 107169908, 103251083, 107169897, 103252134, 103252127, 103252121, 106119371]
        listOfZenithRoleIDs2 = [107169832, 107169682, 107169683]
        listOfExtraIDs = [55493551, 111675779, 158320913, 181682441, 153490353, 93955375, 113251596, 418574311,
                          907853597, 6120765759, 60187320, 1852170503]
        dictOfUsernames = {}
        listOfUserIDs = []
        text = ""

        async with aiohttp.ClientSession() as session:
            badge_info = await (await session.get(f"https://badges.roblox.com/v1/badges/{badge_id}")).json()
            badgeName = badge_info["name"]
            badgeGame = badge_info["awardingUniverse"]["name"]
            gameID = badge_info["awardingUniverse"]["rootPlaceId"]
            gameURL = f"https://www.roblox.com/games/{gameID}/"

            async def fetch_users(roleID, groupID):
                nonlocal count
                async with session.get(f'https://groups.roblox.com/v1/groups/{groupID}/roles/{roleID}/users?limit=100&sortOrder=Asc') as response:
                    userResponse = await response.json()
                    for user in userResponse['data']:
                        userId = user['userId']
                        username = user['username']
                        if userId not in listOfUserIDs:
                            success = False
                            while not success:
                                try:
                                    async with session.get(f'https://badges.roproxy.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}') as badgeResponse:
                                        badgeData = await badgeResponse.json()
                                        if len(badgeData['data']) > 0:
                                            awardedDate = badgeData['data'][0]['awardedDate']
                                            dictOfUsernames[username] = awardedDate
                                        listOfUserIDs.append(userId)
                                        count += 1
                                        print(f"{count} - {interaction.user.display_name}")
                                        success = True
                                except Exception as e:
                                    print(f"Error occurred: {e}. Waiting for 60 seconds before retrying...")
                                    await asyncio.sleep(60)

            if type == "RMH":
                tasks = [fetch_users(roleID, 619142) for roleID in listOfRMHRoleIDs]
            elif type == "Zenith":
                tasks = [fetch_users(roleID, 33427879) for roleID in listOfZenithRoleIDs]
                tasks.extend([fetch_users(roleID, 34140587) for roleID in listOfZenithRoleIDs2])
            elif type == "All":
                tasks = [fetch_users(roleID, 619142) for roleID in listOfRMHRoleIDs]
                tasks.extend([fetch_users(roleID, 33427879) for roleID in listOfZenithRoleIDs])
                tasks.extend([fetch_users(roleID, 34140587) for roleID in listOfZenithRoleIDs2])

            await asyncio.gather(*tasks)

            if type in ["RMH", "All"]:
                for userID in listOfExtraIDs:
                    success = False
                    async with session.get(f'https://users.roblox.com/v1/users/{userID}') as usernameResponse:
                        usernameData = await usernameResponse.json()
                        username = usernameData['name']
                        while not success:
                            try:
                                async with session.get(f'https://badges.roproxy.com/v1/users/{userID}/badges/awarded-dates?badgeIds={badge_id}') as badgeResponse:
                                    badgeData = await badgeResponse.json()
                                    if len(badgeData['data']) > 0:
                                        awardedDate = badgeData['data'][0]['awardedDate']
                                        dictOfUsernames[username] = awardedDate
                                    listOfUserIDs.append(userID)
                                    count += 1
                                    print(f"{count} - {interaction.user.display_name}")
                                    success = True
                            except Exception as e:
                                print(f"Error occurred: {e}. Waiting for 60 seconds before retrying...")
                                await asyncio.sleep(60)

        sorted_data = dict(sorted(dictOfUsernames.items(), key=get_datetime))

        medalCount = 1
        for username, date in sorted_data.items():
            if medalCount == 1:
                text += "Username: " + username + " :first_place: \n"
                text += "Date: " + str(date) + "\n\n"
                cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 1)")
            elif medalCount == 2:
                text += "Username: " + username + " :second_place: \n"
                text += "Date: " + str(date) + "\n\n"
                cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 2)")
            elif medalCount == 3:
                text += "Username: " + username + " :third_place: \n"
                text += "Date: " + str(date) + "\n\n"
                cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 3)")
            else:
                text += "Username: " + username + "\n"
                text += "Date: " + str(date) + "\n\n"
            medalCount += 1
            if len(text) > 4020:
                break

        connection.commit()
        connection.close()

        embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        print("sent badges embed")
        await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Badges(client))

# import requests
# import discord
# import time
# import asyncio
# import sqlite3
# from datetime import datetime
# from discord import app_commands
# from discord.ext import commands
#
# class badges(commands.Cog):
#     def __init__(self, client: commands.Bot):
#         self.client = client
#
#     @app_commands.command(name="badges", description="Find people who have a certain badge")
#     @app_commands.describe(type="Select your scope")
#     @app_commands.choices(type=[
#         discord.app_commands.Choice(name="RMH", value="RMH"),
#         discord.app_commands.Choice(name="Zenith", value="Zenith"),
#         discord.app_commands.Choice(name="All", value="All")
#     ])
#     async def badges(self, interaction: discord.Interaction, badge_id: str, type: str):
#         await interaction.response.defer()
#         await asyncio.sleep(4)
#
#         connection = sqlite3.connect("medals.db")
#         cursor = connection.cursor()
#
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS medals (
#                 username TEXT,
#                 badgeID INTEGER,
#                 place INTEGER,
#                 UNIQUE(username, badgeID, place)
#             )
#         ''')
#
#         print("badges command initiated")
#         count = 0
#
#         def get_datetime(item):
#             return datetime.fromisoformat(item[1].rstrip('Z'))
#
#         listOfRMHRoleIDs = [3627780, 19516868, 25919204, 4059372, 26957538, 3927521, 3627781, 36896118, 36747671,
#                             19962820, 3704753, 3720799, 36896024, 26492648, 4165630]
#         listOfZenithRoleIDs = [103251082, 107169908, 103251083, 107169897, 103252134, 103252127, 103252121, 106119371]
#         listOfZenithRoleIDs2 = [107169832, 107169682, 107169683]
#         listOfExtraIDs = [55493551, 111675779, 158320913, 181682441, 153490353, 93955375, 113251596, 418574311,
#                           907853597, 6120765759]
#         dictOfUsernames = {}
#         listOfUserIDs = []
#         text = ""
#
#         badgeName = requests.get(f"https://badges.roblox.com/v1/badges/{badge_id}").json()["name"]
#         badgeGame = requests.get(f"https://badges.roblox.com/v1/badges/{badge_id}").json()["awardingUniverse"]["name"]
#         gameID = requests.get(f"https://badges.roblox.com/v1/badges/{badge_id}").json()["awardingUniverse"]["rootPlaceId"]
#         gameURL = f"https://www.roblox.com/games/{gameID}/"
#
#         # rolesetResponse = requests.get("https://groups.roblox.com/v1/groups/619142/roles").json()
#         # for role in rolesetResponse['roles']:
#         #     listOfRoleIDs.append(role['id'])
#         #
#         # listOfRoleIDs.reverse()
#         # print(listOfRoleIDs)
#
#         if type == "RMH":
#             for roleID in listOfRMHRoleIDs:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/619142/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             for userID in listOfExtraIDs:
#                 success = False
#                 usernameResponse = requests.get(f'https://users.roblox.com/v1/users/{userID}').json()
#                 username = usernameResponse['name']
#
#                 while not success:
#                     try:
#                         badgeResponse = requests.get(
#                             f'https://badges.roblox.com/v1/users/{userID}/badges/awarded-dates?badgeIds={badge_id}').json()
#                         if len(badgeResponse['data']) > 0:
#                             awardedDate = badgeResponse['data'][0]['awardedDate']
#                             dictOfUsernames[username] = awardedDate
#                             # print(username)
#                             # print(badgeResponse)
#
#                         listOfUserIDs.append(userID)
#                         count += 1
#                         print(count)
#                         success = True
#                     except Exception as e:
#                         print("Error occurred: Waiting for 30 seconds before retrying...")
#                         time.sleep(30)
#                         continue  # Skip the rest of the loop and retry the same code
#
#             sorted_data = dict(sorted(dictOfUsernames.items(), key=get_datetime))
#
#             medalCount = 1
#             for username, date in sorted_data.items():
#                 if medalCount == 1:
#                     text += "Username: " + username + " :first_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 1)")
#                 elif medalCount == 2:
#                     text += "Username: " + username + " :second_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 2)")
#                 elif medalCount == 3:
#                     text += "Username: " + username + " :third_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 3)")
#                 else:
#                     text += "Username: " + username + "\n"
#                     text += "Date: " + str(date) + "\n\n"
#                 medalCount += 1
#                 if len(text) > 4020:
#                     break
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             print("sent badges embed")
#             await interaction.followup.send(embed=embed)
#
#         elif type == "Zenith":
#             for roleID in listOfZenithRoleIDs:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/33427879/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             for roleID in listOfZenithRoleIDs2:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/34140587/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             sorted_data = dict(sorted(dictOfUsernames.items(), key=get_datetime))
#
#             medalCount = 1
#             for username, date in sorted_data.items():
#                 if medalCount == 1:
#                     text += "Username: " + username + " :first_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 1)")
#                 elif medalCount == 2:
#                     text += "Username: " + username + " :second_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 2)")
#                 elif medalCount == 3:
#                     text += "Username: " + username + " :third_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 3)")
#                 else:
#                     text += "Username: " + username + "\n"
#                     text += "Date: " + str(date) + "\n\n"
#                 medalCount += 1
#                 if len(text) > 4020:
#                     break
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             print("sent badges embed")
#             await interaction.followup.send(embed=embed)
#
#         elif type == "All":
#             for roleID in listOfRMHRoleIDs:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/619142/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             for roleID in listOfZenithRoleIDs:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/33427879/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             for roleID in listOfZenithRoleIDs2:
#                 userResponse = requests.get(
#                     f'https://groups.roblox.com/v1/groups/34140587/roles/{roleID}/users?limit=100&sortOrder=Asc').json()
#                 for user in userResponse['data']:
#                     userId = user['userId']
#                     username = user['username']
#                     success = False
#
#                     if userId not in listOfUserIDs:
#                         while not success:
#                             try:
#                                 badgeResponse = requests.get(
#                                     f'https://badges.roblox.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}').json()
#
#                                 if len(badgeResponse['data']) > 0:
#                                     awardedDate = badgeResponse['data'][0]['awardedDate']
#                                     dictOfUsernames[username] = awardedDate
#                                     # print(username)
#                                     # print(badgeResponse)
#
#                                 listOfUserIDs.append(userId)
#                                 count += 1
#                                 print(count)
#                                 success = True  # Mark success if no exception occurred
#
#                             except Exception as e:
#                                 print("Error occurred: Waiting for 30 seconds before retrying...")
#                                 time.sleep(30)
#                                 continue  # Skip the rest of the loop and retry the same code
#
#             for userID in listOfExtraIDs:
#                 success = False
#                 usernameResponse = requests.get(f'https://users.roblox.com/v1/users/{userID}').json()
#                 username = usernameResponse['name']
#
#                 while not success:
#                     try:
#                         badgeResponse = requests.get(
#                             f'https://badges.roblox.com/v1/users/{userID}/badges/awarded-dates?badgeIds={badge_id}').json()
#                         if len(badgeResponse['data']) > 0:
#                             awardedDate = badgeResponse['data'][0]['awardedDate']
#                             dictOfUsernames[username] = awardedDate
#                             # print(username)
#                             # print(badgeResponse)
#
#                         listOfUserIDs.append(userID)
#                         count += 1
#                         print(count)
#                         success = True
#                     except Exception as e:
#                         print("Error occurred: Waiting for 30 seconds before retrying...")
#                         time.sleep(30)
#                         continue  # Skip the rest of the loop and retry the same code
#
#             sorted_data = dict(sorted(dictOfUsernames.items(), key=get_datetime))
#
#             medalCount = 1
#             for username, date in sorted_data.items():
#                 if medalCount == 1:
#                     text += "Username: " + username + " :first_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 1)")
#                 elif medalCount == 2:
#                     text += "Username: " + username + " :second_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 2)")
#                 elif medalCount == 3:
#                     text += "Username: " + username + " :third_place: \n"
#                     text += "Date: " + str(date) + "\n\n"
#                     cursor.execute(f"INSERT OR IGNORE INTO medals VALUES ('{username}', {badge_id}, 3)")
#                 else:
#                     text += "Username: " + username + "\n"
#                     text += "Date: " + str(date) + "\n\n"
#                 medalCount += 1
#                 if len(text) > 4020:
#                     break
#
#             connection.commit()
#             connection.close()
#
#             embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
#             embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#             print("sent badges embed")
#             await interaction.followup.send(embed=embed)
#
# async def setup(client: commands.Bot) -> None:
#     await client.add_cog(badges(client))