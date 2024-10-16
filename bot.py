import discord
from time import sleep
from discord.ext import commands
import asyncio
from json import load

with open('./config.json', 'r') as cfg:
	config = load(cfg)

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print('Bot is ready.')

    # Join the voice channel and start playing the MP3 file on loop
    channel_id = int(config['whip-room-id'])  # Replace with your voice channel ID
    file_path = '/home/honza/24-7-discord-music-bot-main/24-7-discord-music-bot-main/song.mp3'  # Replace with the actual path to your MP3 file

    channel = bot.get_channel(channel_id)
    if not channel:
        return print('Invalid voice channel ID.')

    voice_client = await channel.connect()

    while True:
        voice_client.play(discord.FFmpegPCMAudio(source=file_path))
        await asyncio.sleep(116)
        voice_client.stop()

while True:
	bot.run(config['whip-token'])  # Replace with your Discord bot token
	sleep(30)
