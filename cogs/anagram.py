import discord
from discord import app_commands
from discord.ext import commands

import itertools

english_words_set = set(line.strip() for line in open('EnglishWords.txt'))

class anagram(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "anagram", description = "Unscramble a word given a group of letters")
  async def anagram(self, interaction: discord.Interaction, message: str):
    message = message.lower()
    message = message.split()
    finalList = []

    for word in message:
      newList = []
      sortedWord = sorted(word)
      for x in english_words_set:
        if sorted(x) == sortedWord:
          #print(x)
          newList.append(x)
      finalList.append(newList)

    y = list(itertools.product(*finalList))

    string = "" 
    for z in y: 
      for w in z:
        string += w + " "
      string += "\n"

    embed=discord.Embed(title="The possible solutions are:",description=string, color=0x1ba300)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
    await interaction.response.send_message(embed=embed)

async def setup(client: commands.Bot) -> None:
  await client.add_cog(anagram(client))