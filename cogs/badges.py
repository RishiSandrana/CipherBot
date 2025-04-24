import aiohttp
import discord
import asyncio
import logging
import os
import json

from datetime import datetime
from discord import app_commands
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.environ.get('medals_api_key')
BASE_URL = "https://medals-4193.restdb.io/rest/medals"
HEADERS = {
    'content-type': "application/json",
    'x-apikey': API_KEY,
    'cache-control': "no-cache"
}

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
            logger.info(f"badges command initiated - {interaction.user.display_name}")

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
                                logger.info(badgeData)
                                if badgeData.get('data'):
                                    awardedDate = badgeData['data'][0]['awardedDate']
                                    dictOfUsernames[username] = awardedDate
                                    logger.info(f"{username} added")
                                elif badgeData.get('errors'):
                                    await asyncio.sleep(10)
                                    continue
                                listOfUserIDs.append(userId)
                                count += 1
                                logger.info(f"Count: {count}, User: {username}, Author: {interaction.user.display_name}")
                                success = True
                        except Exception as e:
                            logger.exception(f"Error occurred while processing {username}. Retrying in 60 seconds...")
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
                elif medalCount == 2:
                    text += f"Username: {username} :second_place: \nDate: {date}\n\n"
                elif medalCount == 3:
                    text += f"Username: {username} :third_place: \nDate: {date}\n\n"
                else:
                    text += f"Username: {username}\nDate: {date}\n\n"

                if medalCount in (1, 2, 3):
                    query = json.dumps({
                        "username": username,
                        "badgeID": int(badge_id),
                        "place": medalCount
                    })

                    fields = json.dumps({
                        "$fields": {
                            "username": 1,
                            "badgeID": 1,
                            "place": 1
                        }
                    })

                    GET_URL = f"https://medals-4193.restdb.io/rest/medals?q={query}&h={fields}"

                    async with session.get(GET_URL, headers=HEADERS) as response:
                        json_data = await response.json()
                        logger.info(json_data)

                        if response.status == 200 and json_data:
                            logger.info(f"Duplicate found for {username}, badgeID {badge_id}, place {medalCount}. Skipping insert.")
                        else:
                            async with session.post(BASE_URL, json={
                                "username": username,
                                "badgeID": badge_id,
                                "place": medalCount
                            }, headers=HEADERS) as insert_response:
                                if insert_response.status != 201:
                                    logger.warning(f"Failed to insert data for {username} into restdb.io")
                medalCount += 1
                if len(text) > 4020:
                    break

            embed = discord.Embed(title=f"{badgeGame}: {badgeName}", url=gameURL, description=text, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            logger.info(f"sent badges embed - {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Badges(client))
