import discord
from time import sleep
from discord.ext import commands
from datetime import datetime, timezone
from json import load

with open('config.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code) 
  config = load(cfg) 

# Replace 'your_bot_token_here' with your bot token
TOKEN = config['phanbot-token']

# Replace 'user_id_here' with the ID of the user you want the bot to react to
#TARGET_USER_ID = 536453025028374529 #ja
TARGET_USER_ID = int(config['phantom-id'])  # Replace with the user's Discord ID
TARGET_CHANNEL_ID = int(config['help-pls-id'])
#TARGET_CHANNEL_ID = 784423146728063000 #skj

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    if message.author.id == TARGET_USER_ID:
        # React with an emoji (e.g., thumbs up)
        emoji = '<:blahaj:1173983591785578547>'  # Replace with any emoji you want
        await message.add_reaction(emoji)
        print(message.content)
        if '?' in str(message.content) and message.channel.id == TARGET_CHANNEL_ID:
            history = [msg async for msg in message.channel.history(limit=200)]
        
            # Find the last message by the target user (excluding the current one)
            last_message = None
            for msg in history:
                if msg.author.id == TARGET_USER_ID and msg.id != message.id:
                    last_message = msg
                    break
            
            if last_message:
                # Calculate the time difference
                now = datetime.now(timezone.utc)
                time_difference = now - last_message.created_at
                
                # Send a message with the time difference
                if time_difference.total_seconds() // 3600 > -1:
                    await message.channel.send(
                        f"cg, {message.author.mention}! Naposledy ses tady ozval pred vice jak {time_difference.total_seconds() // 3600} hodinami :D"
                    )
        
while True:
	client.run(TOKEN)
	sleep(30)
