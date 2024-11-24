import discord
from discord.ext import commands
from dotenv import load_dotenv
from mcstatus import JavaServer
import os
from time import sleep
import asyncio

load_dotenv()
MC_IP = os.getenv("MC_SERVER")

TOKEN = os.getenv("mcbot_token")

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN = int(os.getenv("ADMIN_ID"))
MINECRAFT_ROLE = int(os.getenv("MINECRAFT_ROLE"))
ONLINE = False

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True

client = commands.Bot(command_prefix = "/", intents = intents)

def ServerIsOnline():
    server = JavaServer.lookup(MC_IP)
    try:
        status = server.status()
        return status
    except:
        print("offline")
        return False



@client.event
async def on_ready():
    print("Bot is ready")
    try:
        user = client.get_user(ADMIN)
        await user.send("Bot is ready")
    except:
        pass
    await check_server()
    await client.close()

async def check_server():
    global ONLINE
    player_count = 0
    while True:
        await asyncio.sleep(5)
        print("slept")
        status = ServerIsOnline()
        if status:
            if not ONLINE:
                ONLINE = True
                channel = client.get_channel(CHANNEL_ID)
                role = channel.guild.get_role(MINECRAFT_ROLE)
                await channel.send(f"{role.mention} Server je online!\n" + 
                                   "Gotta catch 'em all :white_check_mark:\n" + f"{status.players.online} hracu je online")
            if player_count < status.players.online:
                player_count = status.players.online
                await channel.send(f"{status.players.online} hracu online")
        else:
            if ONLINE:
                ONLINE = False
                channel = client.get_channel(CHANNEL_ID)
                role = channel.guild.get_role(MINECRAFT_ROLE)
                await channel.send(f"{role.mention} Server je offline!" + 
                                   "Dnes jste dochytali :x:")         


while True:
    try:
        client.run(TOKEN)
    except Exception as e:
        print(e)
        sleep(5)
