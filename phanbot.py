import discord
from time import sleep, time
from discord.ext import commands, tasks
from datetime import datetime, timezone
from json import load, dump
import os
from sys import argv
from collections import defaultdict
import requests
from tabulate import tabulate
from random import randint

CONFIG_FILE = 'config.json'
REACTIONS_FILE = 'reactions.json'

os.system("git pull main --no-edit")

with open(CONFIG_FILE, 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code) 
  config = load(cfg) 

reactions_data = defaultdict(lambda: defaultdict(int))
try:
    with open(REACTIONS_FILE, 'r') as file:
        data = load(file)
        reactions_data = defaultdict(
                lambda: defaultdict(int),
                {int(user): defaultdict(int, {emoji: count for emoji, count in emojis.items()}) for user, emojis in data.items()}
            )
except OSError:
    pass


# Replace 'your_bot_token_here' with your bot token
TOKEN = config['phanbot-token']

# Replace 'user_id_here' with the ID of the user you want the bot to react to
TARGET_USER_ID = int(config['phantom-id'])  # Replace with the user's Discord ID
TARGET_CHANNEL_ID = int(config['help-pls-id'])
TRUSTED_USER = int(config['trusted-user-id'])
TRUSTED_CHANNEL = int(config['trusted-user-channel'])
CAT_KEY = config['cat_key']

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.dm_messages = True
client = commands.Bot(command_prefix="!", intents=intents)
bot_id = 0
to_terminate = False
last_payload = None

if len(argv) > 1:
    bot_id = int(argv[1])


def save_reactions():
    with open(REACTIONS_FILE, 'w+') as file:
        dump(reactions_data, file)

@client.event
async def on_ready():
    global bot_id
    print(f'Logged in as {client.user.name}')
        # Send a greeting message to the trusted channel when the bot starts
    trusted_channel = await client.fetch_channel(TRUSTED_CHANNEL)
    if trusted_channel:
        await trusted_channel.send(f"Nazdar! PhanBot {str(bot_id)} ready {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")


async def cat(ctx):
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": CAT_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        cat_url = response.json()[0]["url"]
        await ctx.send("Tady mas kocicku <3")
        await ctx.send(cat_url)


@client.event
async def on_raw_reaction_add(payload):
    if last_payload != None and payload == last_payload:
        return
    if payload.message_author_id != TARGET_USER_ID:
        return
    user = await client.fetch_user(payload.user_id)
    if user.bot:
        return
    reactions_data[payload.user_id][payload.emoji.id] += 1
    reactions_data[payload.user_id]['total'] += 1
    if reactions_data[payload.user_id]['total'] > reactions_data[payload.user_id].get('highest', 0):
        reactions_data[payload.user_id]['highest'] = reactions_data[payload.user_id]['total']
        num = reactions_data[payload.user_id]['total']
        first = True

        if reactions_data[payload.user_id]['total'] == 1:
            await user.send(f"Eeeej, nice! Tohle je tvoje prvni reakce na PhanToma. Reaguj vic a prekonej vsechny ostatni ve PhanBoardu :D\npomoci !phantop si PhanBoard zobrazis ;-)")

        while num > 0:
            if num % 10 == 0:
                if first:
                    await user.send(f"Ooooo, cg, {num} reakci si zaslouzi odmenu :D")
                first = False
                await cat(user)
                num //= 10
            else:
                break
    
    save_reactions()


@client.event
async def on_raw_reaction_remove(payload):
    global last_payload
    if last_payload != None and payload == last_payload:
        return
    print(payload.channel_id)
    channel = await client.fetch_channel(payload.channel_id)
    print(payload.message_id)
    msg = await channel.fetch_message(payload.message_id)
    print(msg.author.id)
    if msg.author.id != TARGET_USER_ID:
        return
    user = await client.fetch_user(payload.user_id)
    if user.bot:
        return
    reactions_data[payload.user_id][payload.emoji.id] -= 1
    reactions_data[payload.user_id]['total'] -= 1
    save_reactions()

async def print_leaderboard(channel):
    tuples = []
    for user in reactions_data:
        tuples.append((reactions_data[user]['total'], user, reactions_data[user].get('phanbomb', 0), reactions_data[user]['phanpoints']))
    tuples.sort(reverse=True)
    # mesg = "----PhanBoard----\nporadi. jmeno -> celkem | od posledni PhanBomby\n"
    headers = ['Poradi', 'Jmeno', 'Celkem bodu', 'Od posledni PhanBomby']
    data = []
    for i, (total, user, phanbomb, phanpoints) in enumerate(tuples):
        this = []
        usr = await client.fetch_user(user)
        this.append(f"{i + 1}.")
        this.append(usr.display_name)
        this.append(str(total))
        this.append(str(total - phanbomb))
        data.append(this.copy())
        # this += f"{i + 1}. {usr.display_name} -> {total} | {phanbomb}\n"
    mesg = '```'
    mesg += tabulate(data, headers)
    mesg += '```'

    if mesg == '':
        await channel.send("No data :(")
        return

    await channel.send(mesg)

async def phanbomb():
    tuples = []
    for user_id in reactions_data:
        tuples.append((reactions_data[user_id].get('total', 0) - reactions_data[user_id].get('phanbomb', 0), user_id, reactions_data[user_id]['phanpoints']))
    tuples.sort(reverse=True)
    reward = len(tuples)
    users = []
    for i, (since_last, user_id, phanpoints) in enumerate(tuples):
        user = await client.fetch_user(user_id)
        users.append(user)
        reactions_data[user_id]['phanpoints'] += max(0, reward)
        reactions_data[user_id]['phanbomb'] += since_last
        await user.send(f"Umistil/a ses na {i + 1}. miste z {len(tuples)}, od posledni PhanBomby jsi dal/a PhanTomovi {since_last} reakci.\n Dostavas tedy +{reward} PhanPointu (ted mas {phanpoints + reward})\nTakto ted vypada PhanBoard:")
        await print_leaderboard(user)
        reward -= 1
    save_reactions()




@client.event
async def on_message(message):
    global bot_id
    if message.author.id == TARGET_USER_ID:
        await message.channel.send("Insufisnt prava bro")
    if isinstance(message.channel, discord.DMChannel):
        if message.author.bot and message.channel.id == TRUSTED_CHANNEL:
            global to_terminate
            if to_terminate:
                await message.channel.send("Bot " + str(bot_id) + " terminated")
                exit(0)
        if message.author.id == TARGET_USER_ID:
            message.channel.send("Nice try, Tome xd")
            return
        if message.author.id == TRUSTED_USER:
            if message.content.lower() == "reboot":
                await message.channel.send("Rebooting :)")
                exit(0)
                os.system("sudo /sbin/reboot")
            elif message.content.lower() == "bomb":
                await phanbomb()
            elif message.content.lower() == "pull":
                await message.channel.send("pulling")
                os.system("git pull main --no-edit")
            elif message.content.lower() == "update":
                to_terminate = True
                os.system("git pull main --no-edit")
                os.system("python3 phanbot.py " + str(bot_id + 1) + " &")
            elif message.content.lower() == "ping":
                await message.channel.send("bot " + str(bot_id) + " says hi! :D")
            elif message.content.lower() == "kill":
                exit(0)
            elif message.content.lower() == "help":
                await message.channel.send("reboot\npull\nupdate\nping\n")
        
    if message.content.lower() == "!phantop":
        await print_leaderboard(message.channel)

    if message.author.id == TARGET_USER_ID:
        # await message.add_reaction('<:phannerd:1208806780818432063>')
        # await message.add_reaction('<:blahaj:1173983591785578547>')
        if '?' in str(message.content) and message.channel.id == TARGET_CHANNEL_ID:
            if randint(0, 9) == 5:
                await phanbomb()
        #     history = [msg async for msg in message.channel.history(limit=200)]
        
        #     # Find the last message by the target user (excluding the current one)
        #     last_message = None
        #     for msg in history:
        #         if msg.author.id == TARGET_USER_ID and msg.id != message.id and '?' in msg.content:
        #             last_message = msg
        #             break
            
        #     if last_message:
        #         # Calculate the time difference
        #         now = datetime.now(timezone.utc)
        #         time_difference = now - last_message.created_at
                
        #         # Send a message with the time difference
        #         if time_difference.total_seconds() // 3600 > 12:
        #             await message.channel.send(
        #                 f"cg, {message.author.mention}! Naposledy ses tady zeptat pred vic jak {time_difference.total_seconds() // 60} minutama :D"
        #             )


while True:
    client.run(TOKEN)
    sleep(10)
