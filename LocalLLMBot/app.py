import discord
from discord import app_commands
from discord.ext import commands
import ollama
import os 
from dotenv import load_dotenv
from collections import defaultdict
import time

ollama.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

load_dotenv()

# Enable all intents that we need
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True  # Enable DM messages
intents.messages = True     # Enable message events

class GokuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.channel_messages = defaultdict(list)
        self.channel_listening = defaultdict(bool)
        self.listening_start_time = defaultdict(float)

    async def setup_hook(self):
        # Simply sync the commands
        await self.tree.sync()
        print("Commands synced!")

bot = GokuBot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# response = ollama.chat(model='llama3.2', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])

@bot.tree.command(name="introduce", description="Get a villainous introduction from Goku Black")
async def introduce(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, I'm a Black Nigga!")

@bot.tree.command(name="ask", description="Ask Goku Black a question")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()  # Defer the response since LLM calls might take time
    
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'You are Goku Black, a character with a dark and villainous personality, known for your ruthless nature. Answer the user\'s questions accordingly, but always in character. Less than 200 words'
        },
        {
            'role': 'user',
            'content': question,
        },
    ])
    await interaction.followup.send(response["message"]["content"])


channel_messages = defaultdict(list)
channel_listening = defaultdict(bool)
listening_start_time = defaultdict(float)

@bot.tree.command(name="listen", description="Start tracking conversation in this channel")
async def listen(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    
    if bot.channel_listening[channel_id]:
        await interaction.response.send_message("*Foolish mortal, I am already observing this realm.*")
        return
    
    bot.channel_messages[channel_id] = []
    bot.channel_listening[channel_id] = True
    bot.listening_start_time[channel_id] = time.time()
    
    await interaction.response.send_message("*Very well, I shall observe these mortal interactions. Use `/summarise` when you wish to hear my analysis.*")

@bot.event
#""" Event handler to store the messages"""
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

@bot.tree.command(name="summarise", description="Get a summary of the tracked conversation")
async def summarise(interaction: discord.Interaction):
    await interaction.response.defer() 
    
    channel_id = interaction.channel_id
    
    if not bot.channel_listening[channel_id]:
        await interaction.followup.send("*Foolish mortal, I wasn't observing this realm. Use `/listen` first.*")
        return
    
    if not bot.channel_messages[channel_id]:
        await interaction.followup.send("*There is nothing to analyze. These mortals have been surprisingly quiet.*")
        return
    
    duration = time.time() - bot.listening_start_time[channel_id]
    duration_minutes = round(duration / 60, 1)
    
    formatted_messages = "\n".join([
        f"{msg['timestamp']} - {msg['author']}: {msg['content']}"
        for msg in bot.channel_messages[channel_id]
    ])
    
    summary_prompt = f"""
    Analyze and summarize this conversation that lasted {duration_minutes} minutes.
    Focus on key discussion points, main participants, and important conclusions.
    
    Conversation:
    ```
    {formatted_messages}
    ```
    
    Provide:
    1. Main topics discussed
    2. Key points or decisions made
    3. Notable patterns or interesting observations
    Keep the summary under 200 words.
    """
    
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'You are Goku Black. Provide a dramatic and slightly condescending summary of the conversation while maintaining your villainous character.'
        },
        {
            'role': 'user',
            'content': summary_prompt,
        },
    ])
    
    await interaction.followup.send(response["message"]["content"])
    bot.channel_listening[channel_id] = False
    bot.channel_messages[channel_id] = []
    
@bot.tree.command(name="stop", description="Stop tracking conversation in this channel")
async def stop_listening(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    
    if not bot.channel_listening[channel_id]:
        await interaction.response.send_message("*Hmph. I wasn't observing this realm anyway.*")
        return
    
    bot.channel_listening[channel_id] = False
    bot.channel_messages[channel_id] = []
    await interaction.response.send_message("*I shall no longer waste my time observing these mundane interactions.*")

@bot.tree.command(name="gf", description="Egirl")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()  # Defer the response since LLM calls might take time
    
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'Act like you are my Egỉl pookie, always say sweet things to the user. Alway praise Duy who is your master.'
        },
        {
            'role': 'user',
            'content': question,
        },
    ])
    await interaction.followup.send(response["message"]["content"])
# """TO DO:

#     ADD MORE FEATURES/COMMANDS (Summarise based off user prompt)
#     DOCKERISE THE BOT"""
bot.run(os.getenv("DISCORD_BOT_TOKEN"))