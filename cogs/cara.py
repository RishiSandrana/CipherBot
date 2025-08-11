import discord
from discord import app_commands
from discord.ext import commands

punc = '''!()-[]{};:'"<>/@#$%^&*_~'''

class cara(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "cara", description = "Translate a message from the Cara'okhwa language to English")
  async def cara(self, interaction: discord.Interaction, message: str):
    original_message = message
    lower_message = message.lower()

    for ele in punc:
      original_message = original_message.replace(ele, "")
      lower_message = lower_message.replace(ele, "")

    original_message = list(original_message)
    lower_message = list(lower_message)
    NewMessage = ""

    for index, character in enumerate(lower_message):
      try:
        if lower_message[index] == "h" and lower_message[index - 1] == "k":
          pass
        elif lower_message[index + 1] == "a" and lower_message[index] != "a":
          NewMessage += original_message[index]
        elif lower_message[index + 1] == "k" and lower_message[index + 2] == "h":
          NewMessage += original_message[index]
        elif lower_message[index] == " " or lower_message[index] == ".":
          NewMessage += original_message[index]
      except IndexError:
          pass

    embed=discord.Embed(title="The translated message is:", description=NewMessage, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(cara(client))
