import discord
import requests
import asyncio
from discord import app_commands
from discord.ext import commands

websiteTable = ["pastebin", "youtube", "bit", "discord"]
client_id = 'f292ad7b2a4a114'

def url_checker(path):
    for website in websiteTable:
        if website == "youtube":
            url = "https://" + website + ".com/watch?v=" + path
            get = requests.get(url)
            # print(get.text)
            if get.status_code == 200 and "Dieses Video ist nicht mehr verfügbar" not in get.text:
                return "The website is: \n" + url
        elif website == "imgur":
            get = requests.get(f"https://api.imgur.com/3/image/{path}", headers={"Authorization": f"Client-ID {client_id}"})
            get2 = requests.get(f"https://api.imgur.com/3/album/{path}/images", headers={"Authorization": f"Client-ID {client_id}"}).json()
            print(get.text)
            if "Zoinks!" not in get.text:
                url = "https://imgur.com/" + path
                return "The website is: \n" + url
            if get2['data'] != []:
                url2 = "https://imgur.com/a/" + path
                return "The website is: \n" + url2
        elif website == "bit":
            url = "https://" + website + ".ly/" + path
            get = requests.get(url)
            if get.status_code == 200:
                return "The website is: \n" + url
        elif website == "discord":
            url = "https://" + website + ".com/invite/" + path
            get = requests.get(url)
        else:
            url = "https://" + website + ".com/" + path
            get = requests.get(url)
            if get.status_code == 200:
                return "The website is: \n" + url

class url(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="url", description="Find a URL link given a URL fragment")
    async def url(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()

        finalMessage = url_checker(message)
        if finalMessage != None:
            embed = discord.Embed(title="Your website link is:", description=finalMessage, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=embed)
        else:
            error_embed = discord.Embed(title="Sorry, no URL could be found!", color=0xff0000)
            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=error_embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(url(client))