import ollama


import os 
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/test ", intents=intents)


@bot.event
async def on_ready():
    print(f"Test is ready as {bot.user.name}")

# response = ollama.chat(model='llama3.2', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])

bot.run(os.getenv("DISCORD_BOT_TOKEN"))