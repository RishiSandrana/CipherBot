import discord
from discord import app_commands
from discord.ext import commands

punc = '''!()-[]{};:'"<>/@#$%^&*_~'''

class cara(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "cara", description = "Translate a message from the Cara'okhwa language to English")
  async def cara(self, interaction: discord.Interaction, message: str):
    for ele in message:
      if ele in punc:
        message = message.replace(ele, "")

    message = list(message)
    NewMessage = ""

    for index, character in enumerate(message):
      try:
        if message[index] == "h" and message[index-1] == "k":
          NewMessage = NewMessage

        elif message[index + 1] == "a" and message[index] != "a":
          NewMessage = NewMessage + message[index]
        elif message[index + 1] == "k" and message[index + 2] == "h":
          NewMessage = NewMessage + message[index]
        elif message[index] == " " or message[index] == ".":
          NewMessage = NewMessage + message[index]
      except:
        print("") 

    embed=discord.Embed(title="The translated message is:", description=NewMessage, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(cara(client))