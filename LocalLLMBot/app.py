import ollama


import os 
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/t ", intents=intents)


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

@bot.command(name="introduce")
async def hello(ctx):
    await ctx.send("Hello, I'm Goku!")

@bot.command(name="ask")
async def ask(ctx, *, message):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'You are Goku Black, a character with a dark and villainous personality, known for your ruthless nature. Answer the user’s questions accordingly, but always in character. Less than 200 words'
        },
        {
            'role': 'user',
            'content': message,
        },
    ])
    await ctx.send(response["message"]["content"])


@bot.command(name="summarise")
async def ask(ctx):
    messages = [msg.content async for msg in ctx.channel.history(limit=500)]

    # Join the messages together into a single string for summarization
    msgs = "\n".join(messages)

    # Create the summarization prompt
    summarise_prompt = f"""
    Summarise the following messages delimited by 3 backticks:
    ```
    {msgs}
    ```
    """
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'Tóm tắt mọi người đã nói gì.'
        },
        {
            'role': 'user',
            'content': summarise_prompt,
        },
    ])
    await ctx.send(response["message"]["content"])


bot.run(os.getenv("DISCORD_BOT_TOKEN"))