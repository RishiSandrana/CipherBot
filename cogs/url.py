import discord
import aiohttp
import os

from discord import app_commands
from discord.ext import commands

websiteTable = ["pastebin", "imgur", "youtube", "bit", "discord"]
client_id = os.environ.get("imgur_token")

async def url_checker(path):
    async with aiohttp.ClientSession() as session:
        for website in websiteTable:
            if website == "youtube":
                url = f"https://{website}.com/watch?v={path}"
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        if "This video isn't available anymore" not in text:
                            return f"The website is:\n{url}"

            elif website == "imgur":
                imgur_url = f"https://api.imgur.com/3/album/{path}/images"
                headers = {"Authorization": f"Client-ID {client_id}"}

                async with session.get(imgur_url, headers=headers) as img_response:
                    if img_response.status == 200:
                        return f"The website is:\nhttps://imgur.com/a/{path}"

            elif website == "bit":
                url = f"https://{website}.ly/{path}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return f"The website is:\n{url}"

            elif website == "discord":
                url = f"https://discord.com/api/v8/invites/{path}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return f"The website is:\nhttps://discord.gg/{path}"

            else:
                url = f"https://{website}.com/{path}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return f"The website is:\n{url}"

    return None

class url(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="url", description="Find a URL link given a URL fragment")
    async def url(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()

        finalMessage = await url_checker(message)
        if finalMessage:
            embed = discord.Embed(title="Your website link is:", description=finalMessage, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=embed)
        else:
            error_embed = discord.Embed(title="Sorry, no URL could be found!", color=0xff0000)
            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=error_embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(url(client))
