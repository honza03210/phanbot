import discord
from mcstatus import MinecraftServer
import os
from dotenv import load_dotenv
from time import sleep


load_dotenv()
MC_IP = os.getenv("MC_SERVER")

client = discord.Client()
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

def ServerIsOnline():
    server = MinecraftServer.lookup(MC_IP)
    if server.status():
        return True
    return False


@client.event
async def on_ready():
    print("Bot is ready")
    user = client.get_user(ADMIN)
    await user.send("Bot is ready")
    await check_server()


async def check_server():
    global ONLINE

    while True:
        sleep(30)
        if ServerIsOnline():
            if not ONLINE:
                ONLINE = True
                channel = client.get_channel(CHANNEL_ID)
                role = channel.guild.get_role(MINECRAFT_ROLE)
                await channel.send(f"{role.mention} Server je online!" + 
                                   "Gotta catch 'em all :white_check_mark:")
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