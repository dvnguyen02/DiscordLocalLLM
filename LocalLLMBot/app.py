import ollama


import os 
from dotenv import load_dotenv
import discord
from discord.ext import commands
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

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
    messages = [msg.content async for msg in ctx.channel.history(limit=5000)]

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
            'content': 'You are Goku Black who provides summary of the past 5000 messages to the users.'
        },
        {
            'role': 'user',
            'content': summarise_prompt,
        },
    ])
    await ctx.send(response["message"]["content"])


# """
# Give a summary of youtube video"""
@bot.command(name="youtube_summary")
async def youtube_summary(ctx, url: str):
    """Summarize a YouTube video based on its transcript"""
    try:
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            await ctx.send("Invalid YouTube URL. Please provide a valid YouTube video URL.")
            return
        
        video_id = video_id_match.group(1)
        
        # Get the transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            await ctx.send("Could not fetch transcript. The video might not have subtitles/CC available.")
            return
            
        # Convert transcript to text
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript)
        
        # If transcript is too long, take first and last parts
        if len(transcript_text) > 4000:  # Adjust this value based on your needs
            transcript_text = transcript_text[:2000] + "\n...\n" + transcript_text[-2000:]
        
        # Create the summarization prompt
        summary_prompt = f"""
        Summarize this YouTube video transcript delimited by triple backticks. Focus on the main points and key takeaways:
        ```
        {transcript_text}
        ```
        Provide a concise summary in less than 200 words.
        """
        
        # Send a message to indicate processing
        await ctx.send("*Processing this mortal's video... Stand by.*")
        
        # Get summary from llama
        response = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': 'You are Goku Black. Provide a summary of this video transcript while maintaining your villainous character.'
            },
            {
                'role': 'user',
                'content': summary_prompt,
            },
        ])
        
        await ctx.send(response["message"]["content"])
        
    except Exception as e:
        await ctx.send(f"An error occurred while processing the video: {str(e)}")

# """TO DO:

#     ADD MORE FEATURES/COMMANDS (Summarise based off user prompt)
#     DOCKERISE THE BOT"""
bot.run(os.getenv("DISCORD_BOT_TOKEN"))