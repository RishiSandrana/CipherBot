import discord
import base64
import aiohttp
import os
import logging

from openai import OpenAI
from discord import app_commands
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

class Deepseek(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name = "deepseek", description = "Ask Deepseek a question!")
    async def deepseek(self, interaction: discord.Interaction, message: str, file: discord.Attachment = None):
        await interaction.response.defer()

        try: 
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )

            if file == None:
                completion = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324:free",
                    messages=[
                        {
                        "role": "user",
                        "content": message
                        }
                    ]
                )

                embed = discord.Embed(description=completion.choices[0].message.content, color=0x1ba300)
                embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
                await interaction.followup.send(embed=embed)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(file.url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            content_type = response.headers.get("Content-Type")
                            if not content_type or not content_type.startswith("image/"):
                                error_embed = discord.Embed(title="The uploaded file is not a valid image.", color=0xff0000)
                                error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
                                await interaction.followup.send(embed=error_embed)
                                return

                            file_format = content_type.split("/")[-1]  # Extract "jpeg", "png", etc.
                            image_base64 = base64.b64encode(image_data).decode("utf-8")
                            image_base64_string = f"data:image/{file_format};base64,{image_base64}"

                            logger.info(f"Image completion started - {interaction.user.display_name}")

                            completion = client.chat.completions.create(
                                model="deepseek/deepseek-chat-v3-0324:free",
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": message
                                            },
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": image_base64_string
                                                }
                                            }
                                        ]
                                    }
                                ]
                            )

                            logger.info(f"Image completion finished - {interaction.user.display_name}")

                            embed = discord.Embed(description=completion.choices[0].message.content, color=0x1ba300)
                            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
                            embed.set_image(url=file.url)
                            await interaction.followup.send(embed=embed)
                        else:
                            error_embed = discord.Embed(title="An error occurred while downloading the image. Please try again later.", color=0xff0000)
                            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
                            await interaction.followup.send(embed=error_embed)
        except Exception as e:
            logger.exception("Error in Deepseek command: %s", e)
            error_embed = discord.Embed(title="An error occurred while processing your request. Please try again later.", color=0xff0000)
            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=error_embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Deepseek(client))
