import discord
from discord import app_commands
from discord.ext import commands
import ollama
import os 
from dotenv import load_dotenv
from collections import defaultdict
import time

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

class GokuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.channel_messages = defaultdict(list)
        self.channel_listening = defaultdict(bool)
        self.listening_start_time = defaultdict(float)

    async def setup_hook(self):
        # This will sync the commands with Discord
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
    await interaction.response.send_message("Hello, I'm Goku Black!")

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

# """
# Give a summary of youtube video"""
@bot.command(name="ytsum")
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


channel_messages = defaultdict(list)
channel_listening = defaultdict(bool)
listening_start_time = defaultdict(float)

@bot.command(name="listen")
async def listen(ctx):
    """Start listening to the conversation in this channel"""
    channel_id = ctx.channel.id
    
    if channel_listening[channel_id]:
        await ctx.send("*I am already observing this chat.*")
        return
    
    channel_messages[channel_id] = []  # Clear previous messages
    channel_listening[channel_id] = True
    listening_start_time[channel_id] = time.time()
    
    await ctx.send("* AI Goku is listening. Use `/t summarise` to get the summary.*")

@bot.event
async def on_message(message):
    """Event handler to capture messages while listening"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    channel_id = message.channel.id
    
    # If we're listening in this channel, store the message
    if channel_listening[channel_id]:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        channel_messages[channel_id].append({
            'author': message.author.display_name,
            'content': message.content,
            'timestamp': timestamp
        })
    
    # This is necessary to make commands work
    await bot.process_commands(message)

@bot.command(name="sum")
async def summarise_chat(ctx):
    """Summarize the conversation since the listen command was used"""
    channel_id = ctx.channel.id
    
    if not channel_listening[channel_id]:
        await ctx.send("*I wasn't observing this realm. Use `/t listen` first.*")
    
    if not channel_messages[channel_id]:
        await ctx.send("*There is nothing to analyze. These mortals have been surprisingly quiet.*")
    
    # Calculate duration
    duration = time.time() - listening_start_time[channel_id]
    duration_minutes = round(duration / 60, 1)
    
    # Format messages for summarization
    formatted_messages = "\n".join([
        f"{msg['timestamp']} - {msg['author']}: {msg['content']}"
        for msg in channel_messages[channel_id]
    ])
    
    summary_prompt = f"""
    Analyze and summarize this conversation that lasted {duration_minutes} minutes.
    Focus on key discussion points, main participants, and important conclusions and keep it less than 200 words.
    
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
    
    # Send processing message
    await ctx.send("*Analyzing these mortal interactions...*")
    
    # Get summary from llama
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'Provide a summary of the conversation.'
        },
        {
            'role': 'user',
            'content': summary_prompt,
        },
    ])
    
    # Send summary and reset
    await ctx.send(response["message"]["content"])
    
    # Optional: Stop listening after summarizing
    channel_listening[channel_id] = False
    channel_messages[channel_id] = []
    
@bot.command(name="stop")
async def stop_listening(ctx):
    """Stop listening to the conversation in this channel"""
    channel_id = ctx.channel.id
    
    if not channel_listening[channel_id]:
        await ctx.send("*I wasn't observing this realm anyway.*")
        return
    
    channel_listening[channel_id] = False
    channel_messages[channel_id] = []
    await ctx.send("*I shall no longer waste my time observing these mundane interactions.*")
# """TO DO:

#     ADD MORE FEATURES/COMMANDS (Summarise based off user prompt)
#     DOCKERISE THE BOT"""
bot.run(os.getenv("DISCORD_BOT_TOKEN"))