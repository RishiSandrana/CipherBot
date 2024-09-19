import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import string as strng

def generateKey(string, key):
    key = list(key)
    for i in range(len(string) - len(key)):
        key.append(key[i % len(string)])
    for i in range(len(string)):
        if (string[i] in strng.punctuation + ' ') or (string[i].isdigit()):
            key.insert(i, string[i])
    return "".join(key)

english_words_set = set(line.strip() for line in open('EnglishWords.txt'))

class vigenere(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="vigenere", description="Encode/Decode a message in Vigenere Cipher")
    @app_commands.describe(type="Would you like to encode or decode?")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="Encode", value="Encode"),
        discord.app_commands.Choice(name="Decode", value="Decode")
    ])
    async def vigenere(self, interaction: discord.Interaction, message: str, type: str, key: str = ""):
        if type == "Decode" and key != "":
            end_text = ""
            generatedKey = generateKey(message, key)
            for i, char in enumerate(message):
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shift = ord(generatedKey[i].upper()) - ord('A')
                    decoded_char = chr((ord(char) - base - shift) % 26 + base)
                    end_text += decoded_char
                else:
                    end_text += char

            embed = discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed=embed)

        if type == "Decode" and key == "":
            await interaction.response.defer()
            asyncio.create_task(self.decode_without_key(interaction, message))

        elif type == "Encode" and key != "":
            end_text = ""
            generatedKey = generateKey(message, key)
            for i, char in enumerate(message):
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shift = ord(generatedKey[i].upper()) - ord('A')
                    encoded_char = chr((ord(char) - base + shift) % 26 + base)
                    end_text += encoded_char
                else:
                    end_text += char

            embed = discord.Embed(title="The encoded message is:", description=end_text, color=0x1ba300)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed=embed)

        elif type == "Encode" and key == "":
            error_embed = discord.Embed(title="You need a key to encode!", color=0xff0000)
            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed=error_embed)

    async def decode_without_key(self, interaction, message):
        count = 0
        found = False

        for testWord in english_words_set:
            decodedWord = ""
            generatedKey = generateKey(message, testWord)
            word_count = 0
            count += 1

            for i, char in enumerate(message):
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shift = ord(generatedKey[i].upper()) - ord('A')
                    decoded_char = chr((ord(char) - base - shift) % 26 + base)
                    decodedWord += decoded_char
                else:
                    decodedWord += char

            no_punctuation_word = decodedWord
            for punctuation in strng.punctuation:
                no_punctuation_word = no_punctuation_word.replace(punctuation, '')

            final_decoded_list = no_punctuation_word.split()
            total_words = len(final_decoded_list)

            for word in final_decoded_list:
                if word.isalpha():
                    word2 = word.lower()
                    if word2 in english_words_set:
                        word_count += 1

            if (word_count / total_words) >= 0.85:
                found = True
                embed = discord.Embed(title="The decoded message is:", description=decodedWord, color=0x1ba300)
                embed.set_footer(text="The key was: " + testWord)
                embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
                await interaction.followup.send(embed=embed)
                break

        if not found:
            error_embed = discord.Embed(title="No match in Vigenere could be found! It's possible that your key is not in the scope of this program.", color=0xff0000)
            error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            await interaction.followup.send(embed=error_embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(vigenere(client))

# import discord
# from discord import app_commands
# from discord.ext import commands
# import asyncio
# import string as strng
#
# def generateKey(string, key):
#       key = list(key)
#       for i in range(len(string) - len(key)):
#         key.append(key[i % len(string)])
#       for i in range(len(string)):
#         if (string[i] in strng.punctuation + ' ') or (string[i].isdigit()):
#           key.insert(i, string[i])
#       return("".join(key))
#
# english_words_set = set(line.strip() for line in open('EnglishWords.txt'))
#
# class vigenere(commands.Cog):
#   def __init__(self, client):
#     self.client = client
#
#   @app_commands.command(name = "vigenere", description = "Encode/Decode a message in Vigenere Cipher")
#   @app_commands.describe(type="Would you like to encode or decode?")
#   @app_commands.choices(type = [
#     discord.app_commands.Choice(name="Encode", value="Encode"),
#     discord.app_commands.Choice(name="Decode", value="Decode")
#   ])
#   async def vigenere(self, interaction: discord.Interaction, message: str, type: str, key: str = ""):
#     if type == "Decode" and key != "":
#       end_text = ""
#       generatedKey = generateKey(message, key)
#       for i, char in enumerate(message):
#         if char.isalpha():
#             base = ord('A') if char.isupper() else ord('a')
#             shift = ord(generatedKey[i].upper()) - ord('A')
#             decoded_char = chr((ord(char) - base - shift) % 26 + base)
#             end_text += decoded_char
#         else:
#             end_text += char
#
#       embed=discord.Embed(title="The decoded message is:", description=end_text, color=0x1ba300)
#       embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#       await interaction.response.send_message(embed=embed)
#
#     if type == "Decode" and key == "":
#       await interaction.response.defer()
#       await asyncio.sleep(4)
#       count = 0
#       found = False
#
#       for testWord in english_words_set:
#         decodedWord = ""
#         generatedKey = generateKey(message, testWord)
#         word_count = 0
#         count += 1
#         #print("The program has run through this many keys: " + str(count))
#
#         for i, char in enumerate(message):
#           if char.isalpha():
#             base = ord('A') if char.isupper() else ord('a')
#             shift = ord(generatedKey[i].upper()) - ord('A')
#             decoded_char = chr((ord(char) - base - shift) % 26 + base)
#             decodedWord += decoded_char
#           else:
#             decodedWord += char
#
#         no_punctuation_word = decodedWord
#         for punctuation in strng.punctuation:
#           no_punctuation_word = no_punctuation_word.replace(punctuation, '')
#
#         final_decoded_list = no_punctuation_word.split()
#         total_words = len(final_decoded_list)
#
#         for word in final_decoded_list:
#           if word.isalpha() == True:
#             word2 = word.lower()
#             if word2 in english_words_set:
#               word_count += 1
#
#         if (word_count/total_words) >= 0.85:
#           found = True
#           embed = discord.Embed(title="The decoded message is:", description=decodedWord, color=0x1ba300)
#           embed.set_footer(text="The key was: " + testWord)
#           embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#           await interaction.followup.send(embed=embed)
#           break
#
#       if found == False:
#         error_embed = discord.Embed(title="No match in Vigenere could be found! It's possible that your key is not in the scope of this program.", color=0xff0000)
#         error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#         await interaction.followup.send(embed=error_embed)
#
#     elif type == "Encode" and key != "":
#       end_text = ""
#       generatedKey = generateKey(message, key)
#       for i, char in enumerate(message):
#         if char.isalpha():
#           base = ord('A') if char.isupper() else ord('a')
#           shift = ord(generatedKey[i].upper()) - ord('A')
#           encoded_char = chr((ord(char) - base + shift) % 26 + base)
#           end_text += encoded_char
#         else:
#           end_text += char
#
#       embed=discord.Embed(title="The encoded message is:", description=end_text, color=0x1ba300)
#       embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#       await interaction.response.send_message(embed=embed)
#
#     elif type == "Encode" and key == "":
#       error_embed = discord.Embed(title="You need a key to encode!", color=0xff0000)
#       error_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
#       await interaction.response.send_message(embed=error_embed)
#
# async def setup(client: commands.Bot) -> None:
#   await client.add_cog(vigenere(client))