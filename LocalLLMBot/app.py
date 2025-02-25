import discord
from discord import app_commands
from discord.ext import commands
import ollama
import os
import json
import time
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()
ollama.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.messages = True

class GokuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.channel_messages = defaultdict(list)
        self.channel_listening = defaultdict(bool)
        self.listening_start_time = defaultdict(float)

    async def setup_hook(self):
        await self.tree.sync()
        print("Commands synced!")

bot = GokuBot()

def load_personality(character: str):
    """Load personality settings from JSON file."""
    try:
        with open("personality.json", "r", encoding="utf-8") as f:
            personalities = json.load(f)
        return personalities.get(character.lower(), {
            "system_prompt": "I am a neutral AI assistant.",
            "default_response": "I don't understand."
        })
    except FileNotFoundError:
        return {"system_prompt": "I am a neutral AI assistant.", "default_response": "I don't understand."}

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.tree.command(name="ask", description="Ask a character a question")
async def ask(interaction: discord.Interaction, character: str, question: str):
    await interaction.response.defer()
    
    personality = load_personality(character)
    response = ollama.chat(model='llama3.2', messages=[
        {"role": "system", "content": personality["system_prompt"]},
        {"role": "user", "content": question},
    ])
    
    await interaction.followup.send(response.get("message", {}).get("content", personality["default_response"]))

@bot.tree.command(name="listen", description="Start tracking conversation in this channel")
async def listen(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    
    if bot.channel_listening[channel_id]:
        await interaction.response.send_message("*I am already observing this realm.*")
        return
    
    bot.channel_messages[channel_id] = []
    bot.channel_listening[channel_id] = True
    bot.listening_start_time[channel_id] = time.time()
    
    await interaction.response.send_message("*I shall observe this conversation. Use `/summarize` for an analysis.*")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    channel_id = message.channel.id
    
    if bot.channel_listening[channel_id]:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        bot.channel_messages[channel_id].append({
            'author': message.author.display_name,
            'content': message.content,
            'timestamp': timestamp
        })
    
    await bot.process_commands(message)

@bot.tree.command(name="summarize", description="Get a summary of the tracked conversation")
async def summarize(interaction: discord.Interaction, character: str):
    await interaction.response.defer()
    
    channel_id = interaction.channel_id
    
    if not bot.channel_listening[channel_id]:
        await interaction.followup.send("*Use `/listen` first.*")
        return
    
    if not bot.channel_messages[channel_id]:
        await interaction.followup.send("*There is nothing to analyze.*")
        return
    
    duration = time.time() - bot.listening_start_time[channel_id]
    duration_minutes = round(duration / 60, 1)
    
    formatted_messages = "\n".join([
        f"{msg['timestamp']} - {msg['author']}: {msg['content']}"
        for msg in bot.channel_messages[channel_id]
    ])
    
    summary_prompt = f"""
    Summarize this conversation that lasted {duration_minutes} minutes.
    Focus on key discussion points, main participants, and important conclusions.
    
    Conversation:
    ```
    {formatted_messages}
    ```
    Keep the summary under 200 words.
    """
    
    personality = load_personality(character)
    response = ollama.chat(model='llama3.2', messages=[
        {"role": "system", "content": personality["system_prompt"]},
        {"role": "user", "content": summary_prompt},
    ])
    
    await interaction.followup.send(response.get("message", {}).get("content", personality["default_response"]))
    bot.channel_listening[channel_id] = False
    bot.channel_messages[channel_id] = []

@bot.tree.command(name="stop", description="Stop tracking conversation in this channel")
async def stop_listening(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    
    if not bot.channel_listening[channel_id]:
        await interaction.response.send_message("*I wasn't observing this realm anyway.*")
        return
    
    bot.channel_listening[channel_id] = False
    bot.channel_messages[channel_id] = []
    await interaction.response.send_message("*I shall no longer waste my time observing these mundane interactions.*")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
