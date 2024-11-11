# Install Dependencies
to install necessary dependencies using Poetry: 
```python
poetry install
```

# Environment
Create a .env file with your Discord bot token:
```python
DISCORD_BOT_TOKEN=your_discord_token
```

# Commands
Currently it only has 2 commands:
```python
/t ask # Allow user to ask questions
/t listen #  Starts tracking messages in the current channel
/t stop Stops tracking messages
/t sum Provides a summary of all messages since the listen command was used
```