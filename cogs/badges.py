import aiohttp
import discord
import asyncio
import aiosqlite
from datetime import datetime
from discord import app_commands
from discord.ext import commands

listOfRMHRoleIDs = [3627780, 19516868, 25919204, 4059372, 26957538, 3927521, 3627781, 36896118, 36747671,
                    19962820, 3704753, 3720799, 36896024, 26492648, 4165630]
listOfZenithRoleIDs = [103251082, 189814034, 167644058, 107169908, 107169897, 103252134, 163720101, 166496028, 103252127, 103252121]
listOfZenithRoleIDs2 = [107169832, 107169682, 187362061]
listOfExtraIDs = [55493551, 111675779, 158320913, 181682441, 153490353, 93955375, 113251596, 418574311,
                    907853597, 6120765759, 60187320, 1852170503, 1446191679, 1528807067]

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
        async def get_datetime(item):
            return datetime.fromisoformat(item[1].rstrip('Z'))

        async with aiohttp.ClientSession() as session:
            await interaction.response.defer()
            print(f"badges command initiated - {interaction.user.display_name}")

            async with aiosqlite.connect("medals_backup.db") as connection:
                cursor = await connection.cursor()

                count = 0
                dictOfUsernames = {}
                listOfUserIDs = []
                text = ""

                badge_info = await (await session.get(f"https://badges.roblox.com/v1/badges/{badge_id}")).json()
                badgeName = badge_info["name"]
                badgeGame = badge_info["awardingUniverse"]["name"]
                gameID = badge_info["awardingUniverse"]["rootPlaceId"]
                gameURL = f"https://www.roblox.com/games/{gameID}/"

                user_queue = asyncio.Queue()

                async def fetch_users(roleID, groupID):
                    async with session.get(f'https://groups.roblox.com/v1/groups/{groupID}/roles/{roleID}/users?limit=100&sortOrder=Asc') as response:
                        userResponse = await response.json()
                        for user in userResponse.get('data', []):
                            userId = user['userId']
                            username = user['username']
                            if userId not in listOfUserIDs:
                                await user_queue.put((userId, username))

                async def fetch_extra_users():
                    for userId in listOfExtraIDs:
                        if userId not in listOfUserIDs:
                            async with session.get(f"https://users.roblox.com/v1/users/{userId}") as response:
                                user_data = await response.json()
                                username = user_data.get("name")
                            await user_queue.put((userId, username))

                async def process_users():
                    nonlocal count
                    while not user_queue.empty():
                        userId, username = await user_queue.get()
                        success = False
                        while not success:
                            try:
                                async with session.get(f'https://badges.roproxy.com/v1/users/{userId}/badges/awarded-dates?badgeIds={badge_id}') as badgeResponse:
                                    badgeData = await badgeResponse.json()
                                    print(badgeData)
                                    if badgeData.get('data'):
                                        awardedDate = badgeData['data'][0]['awardedDate']
                                        dictOfUsernames[username] = awardedDate
                                        print(f"{username} added")
                                    elif badgeData.get('errors'):
                                        await asyncio.sleep(10)
                                        continue
                                    listOfUserIDs.append(userId)
                                    count += 1
                                    print(f"Count: {count}, User: {username}, Author: {interaction.user.display_name}")
                                    success = True
                            except Exception as e:
                                print(f"Error occurred: {e}. Waiting for 60 seconds before retrying...")
                                await asyncio.sleep(60)
                        await asyncio.sleep(1)

                tasks = []
                if type == "RMH":
                    tasks.extend([fetch_users(roleID, 619142) for roleID in listOfRMHRoleIDs])
                    tasks.append(fetch_extra_users())
                elif type == "Zenith":
                    tasks.extend([fetch_users(roleID, 33427879) for roleID in listOfZenithRoleIDs])
                    tasks.extend([fetch_users(roleID, 34140587) for roleID in listOfZenithRoleIDs2])
                elif type == "All":
                    tasks.extend([fetch_users(roleID, 619142) for roleID in listOfRMHRoleIDs])
                    tasks.extend([fetch_users(roleID, 33427879) for roleID in listOfZenithRoleIDs])
                    tasks.extend([fetch_users(roleID, 34140587) for roleID in listOfZenithRoleIDs2])
                    tasks.append(fetch_extra_users())

                await asyncio.gather(*tasks)

                await process_users()

                sorted_items = await asyncio.gather(*[get_datetime(item) for item in dictOfUsernames.items()])
                sorted_data = dict(sorted(zip(dictOfUsernames.keys(), sorted_items), key=lambda x: x[1]))

                medalCount = 1
                for username, date in sorted_data.items():
                    if medalCount == 1:
                        text += f"Username: {username} :first_place: \nDate: {date}\n\n"
                        await cursor.execute("INSERT OR IGNORE INTO medals VALUES (?, ?, ?)", (username, badge_id, 1))
                    elif medalCount == 2:
                        text += f"Username: {username} :second_place: \nDate: {date}\n\n"
                        await cursor.execute("INSERT OR IGNORE INTO medals VALUES (?, ?, ?)", (username, badge_id, 2))
                    elif medalCount == 3:
                        text += f"Username: {username} :third_place: \nDate: {date}\n\n"
                        await cursor.execute("INSERT OR IGNORE INTO medals VALUES (?, ?, ?)", (username, badge_id, 3))
                    else:
                        text += f"Username: {username}\nDate: {date}\n\n"
                    medalCount += 1
                    
                    if len(text) > 4020:
                        break

                await connection.commit()

        embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        print(f"sent badges embed - {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Badges(client))
