import discord
from time import sleep, time
from discord.ext import commands, tasks
from datetime import datetime, timezone
from json import load
import os
from sys import argv

with open('config.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code) 
  config = load(cfg) 
os.system("git pull main --no-edit")

# Replace 'your_bot_token_here' with your bot token
TOKEN = config['phanbot-token']

# Replace 'user_id_here' with the ID of the user you want the bot to react to
#TARGET_USER_ID = 536453025028374529 #ja
TARGET_USER_ID = int(config['phantom-id'])  # Replace with the user's Discord ID
TARGET_CHANNEL_ID = int(config['help-pls-id'])
#TARGET_CHANNEL_ID = 784423146728063000 #skjiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
TRUSTED_USER = int(config['trusted-user-id'])
TRUSTED_CHANNEL = int(config['trusted-user-channel'])

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True
client = commands.Bot(command_prefix="!", intents=intents)
bot_id = 0
to_terminate = False

if len(argv) > 1:
    bot_id = int(argv[1])

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
        # Send a greeting message to the trusted channel when the bot starts
    trusted_channel = await client.fetch_channel(TRUSTED_CHANNEL)
    if trusted_channel:
        await trusted_channel.send(f"Nazdar! PhanBot ready {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")


@client.event
async def on_reaction():
    pass

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == TRUSTED_USER:
            if message.content.lower() == "reboot":
                await message.channel.send("Rebooting :)")
                os.system("sudo /sbin/reboot")
            elif message.content.lower() == "pull":
                await message.channel.send("pulling")
                os.system("git pull main --no-edit")
            elif message.content.lower() == "update":
                to_terminate = True
                os.system("git pull main --no-edit")
                os.system("python3 phanbot.py " + str(bot_id + 1) + " &")
                await message.channel.send("updated? bot " + str(bot_id) + " terminated")
            elif message.content.lower() == "ping":
                await message.channel.send("bot " + str(bot_id) + " says hi! :D")
                await message.channel.send("we are on channel: " + str(message.channel.id))
                
                await message.channel.send(str(TRUSTED_CHANNEL))

            elif message.content.lower() == "help":
                await message.channel.send("reboot\npull\nupdate\nping\n")


    if message.author.id == TARGET_USER_ID:
        await message.add_reaction('<:phannerd:1208806780818432063>')
        await message.add_reaction('<:blahaj:1173983591785578547>')
        print(message.content)
        if '?' in str(message.content) and message.channel.id == TARGET_CHANNEL_ID:
            history = [msg async for msg in message.channel.history(limit=200)]
        
            # Find the last message by the target user (excluding the current one)
            last_message = None
            for msg in history:
                if msg.author.id == TARGET_USER_ID and msg.id != message.id and '?' in msg.content:
                    last_message = msg
                    break
            
            if last_message:
                # Calculate the time difference
                now = datetime.now(timezone.utc)
                time_difference = now - last_message.created_at
                
                # Send a message with the time difference
                if time_difference.total_seconds() // 3600 > 12:
                    await message.channel.send(
                        f"cg, {message.author.mention}! Naposledy ses tady zeptat pred vic jak {time_difference.total_seconds() // 60} minutama :D"
                    )

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  # Ignore bot reactions

    channel_id = reaction.message.channel
    emoji = str(reaction.emoji)

    await reaction.message.channel.send("reacted")
    await reaction.message.add_reaction(emoji)

 
while True:
	client.run(TOKEN)
	sleep(30)
