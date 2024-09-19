import discord
from discord import app_commands
from discord.ext import commands

english_words_set = set(line.strip() for line in open('fiveLetterWords.txt'))

class wordle(commands.Cog):
  def __init__(self, client):
    self.client = client

  @app_commands.command(name = "wordle", description = "Attempts to solve your wordle")
  async def wordle(self, interaction: discord.Interaction, guess: str, colors: str, excluded_letters: str = "", excluded_positions: str = ""):
    if len(guess) != 5 or len(colors) != 5:
      error_embed = discord.Embed(title="This is not a valid input!", color=0xff0000)
      error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
      await interaction.response.send_message(embed=error_embed)
    else:
      for word in english_words_set.copy():
        if excluded_letters != "" and excluded_positions != "":
          for i, char in enumerate(excluded_positions):
            if char.isalpha() == True:
              number = int(excluded_positions[i+1])
              if word.find(char) == (number - 1):
                english_words_set.discard(word)
          for char in excluded_letters:
            if char in word:
              english_words_set.discard(word)
        elif excluded_letters != "" and excluded_positions == "":
          for char in excluded_letters:
            if char in word:
              english_words_set.discard(word)
        for i in range(5):
          if colors[i] == "w" and guess[i] in word:
            if guess.count(guess[i]) == 1:
              english_words_set.discard(word)
          elif colors[i] == "g" and guess[i] != word[i]:
            english_words_set.discard(word)
          elif colors[i] == "y" and guess[i] not in word:
            english_words_set.discard(word)
          elif colors[i] == "y" and guess[i] == word[i]:
            english_words_set.discard(word)

      if 1 <= len(english_words_set) <= 499:
        embed = discord.Embed(title="These are the remaining words!", description=english_words_set, color=0x1ba300)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed)
      elif len(english_words_set) > 499:
        error_embed = discord.Embed(title="Too many remaining words!", color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)
      else:
        error_embed = discord.Embed(title="No words could be found!", color=0xff0000)
        error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=error_embed)

async def setup(client):
  await client.add_cog(wordle(client))