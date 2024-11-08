############################################
### abandon hope all ye who read further ###
############################################


from file_utils import ReactionData, Config
import image_utils

import discord
from time import sleep
from discord.ext import commands
import os
import io
from tabulate import tabulate
from random import randint


SHOP_OFFERS: dict[str: int] =  {'phannerd': 32,
                                'phanmoon': 20,
                                'phanspinner': 45,
                                'susenka nebo ekvivalent': 12}


CONFIG_FILE = 'config.json'
config = Config()

REACTIONS_FILE = 'reactions.json'
reaction_data = ReactionData(REACTIONS_FILE)

# constants for custom error handling
DATA_RECOVERY = -1
DATA_SAVING = -2
REACTION_READ = -3
PHANBOMB_USER_FETCH = -4


##################################################################################################
#                                   Bot setup and error handler                                  #
##################################################################################################

async def error_handler(error_code: int) -> None:
    global config
    try:
        admin = await client.fetch_user(config.admin_id)
    
    # todo - log fails into some file
    except discord.HTTPException:
        return
    except discord.NotFound:
        return

    if error_code == DATA_RECOVERY:
        await admin.send("Data recovery failed")
    elif error_code == DATA_SAVING:
        await admin.send("Data saving failed")
    elif error_code == REACTION_READ:
        await admin.send("Reaction reading failed")
    elif error_code == PHANBOMB_USER_FETCH:
        await admin.send("Fetching user for PhanBomb failed")
    await admin.send("Spadlo to, asi vítr ne?")


def set_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.reactions = True
    intents.message_content = True
    intents.dm_messages = True
    intents.dm_reactions = True
    return intents


client = commands.Bot(command_prefix="!", intents=set_intents())


@client.event
async def on_ready():
    global config
    print(f'Logged in as {client.user.name}')

    # Send a greeting message to admin when the bot starts
    admin = await client.fetch_user(config.admin_id)
    if admin is not None:
        await admin.send("Hi, I'm ready to bully :)")



##################################################################################################
#                                   Event handlers                                               #
##################################################################################################


# Function return number of rections of user on message
async def reaction_count(msg, user):
    count = 0
    for reaction in msg.reactions:
        async for react_user in reaction.users():
            if user.id == react_user.id:
                count += 1
    return count




last_payload = None

@client.event
async def on_raw_reaction_add(reaction):
    print("triggered")
    global reaction_data, last_payload

    # Ignore reactions from bot and duplicates
    if reaction.user_id == client.user.id:
        return
    if last_payload != None and reaction == last_payload:
        return
    last_payload = reaction


    msg = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)
    reaction_author = await client.fetch_user(reaction.user_id)

    if msg.author.id != config.target_user_id:
        return

    count = await reaction_count(msg, reaction_author)
    print(count)
    if count > 3:
        if count == 4:
            await reaction_author.send("Do skóre se ti započítávají pouze první tři reakce na jednu zprávu") 
        return

    # updating data in reactions_data
    reaction_data.change_reaction_count(reaction.user_id, 1)

    if reaction_data.get_val(reaction.user_id, 'total') % 10 == 0:
        await image_utils.send_cat(reaction_author.dm_channel) # can fail, dont care

    await reaction_data.save_data() # can fail, might be a problem


@client.event
async def on_raw_reaction_remove(reaction):
    global reaction_data, last_payload

    # Ignore reactions from bot and duplicates
    if reaction.user_id == client.user.id:
        return
    if last_payload != None and reaction == last_payload:
        return
    last_payload = reaction

    # Ignore reactions from the target user (Phantom)
    if reaction.user_id == config.target_user_id:
        return


    msg = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)
    user = await client.fetch_user(reaction.user_id)
    msg_author = await client.fetch_user(msg.author.id)

    if msg_author.id != config.target_user_id:
        return

    if await reaction_count(msg, user) >= 3:
        return

    # updating data in reactions_data
    reaction_data.change_reaction_count(reaction.user_id, 1)

    await reaction_data.save_data()





##################################################################################################
#                                   Command handlers                                             #
##################################################################################################

async def print_leaderboard(params: dict):
    tuples = []
    for user_id in reaction_data.data:
        tuples.append((reaction_data.get_val(user_id, 'total'), user_id, reaction_data.get_val(user_id, 'since_bomb')))

    tuples.sort(reverse=True)

    headers = ['Poradi', 'Jmeno', 'Celkem bodu', 'Od posledni PhanBomby']
    data = []

    for i, (total, user_id, since_last_phanbomb) in enumerate(tuples):
        this = []
        user = await client.fetch_user(user_id)
        this.append(f"{i + 1}.")
        this.append(user.display_name if user is not None else str(user_id)) # to check - lazy eval??
        this.append(str(total))
        this.append(str(since_last_phanbomb))
        data.append(this.copy())

    table = tabulate(data, headers)

    image = image_utils.render_as_pic(table, len(tuples))

    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await params["message"].channel.send(file=discord.File(fp=image_binary, filename='image.png'))



async def phanbomb(trigger: str, params = {}):

    points_per_user = []

    for user_id, data in reaction_data.data.items():
        points_per_user.append((data["since_bomb"], user_id))
    points_per_user.sort(reverse=True)

    for index, (points, user_id) in enumerate(points_per_user):

        reaction_data.set_val(user_id, "points", reaction_data.get_val(user_id, "points") + max(0, len(points_per_user) - 2 * index))
        reaction_data.set_val(user_id, "since_bomb", 0)

        try:
            user = await client.fetch_user(user_id)
            await user.send(f"PhanBomba vybuchlaaa, protoze {trigger}. Umistil/a ses na {index + 1}. miste z {len(points_per_user)}, od posledni PhanBomby jsi dal/a PhanTomovi {points} reakci.\n Dostavas tedy +{max(0, len(points_per_user) - 2 * index)} PhanPointu (ted mas {reaction_data.get_val(user_id, 'points')})")

        except discord.errors.NotFound:
            error_handler(PHANBOMB_USER_FETCH)
            continue

    await reaction_data.save_data()


async def reboot(params: dict):
    if not params["is_admin"]:
        return
    await params["message"].channel.send("Rebooting :)")
    os.system("sudo /sbin/reboot")

    # this might run, idk
    await client.close()
    exit(0)
    

async def call_phanbomb(params: dict):
    if not params["is_admin"]:
        return
    await phanbomb("idk, lol")


async def admin_gib_points(params: dict):
    if not params["is_admin"]:
        return
    try:
        reaction_data.set_val(config.admin_id, "points", int(params['args'][1]))
    except TypeError:
        error_handler()
        return
    except IndexError:
        error_handler()
        return
    

async def update_bot(params: dict):
    if not params["is_admin"]:
        return
    os.system("git pull main --no-edit")
    os.system("python3 phanbot.py &")
    exit(0)


async def ping_bot(params: dict):
    await params["message"].channel.send("bot says hi! :D")

async def kill_bot(params: dict):
    await reaction_data.save_data()
    await client.close()
    exit(0)

async def phanwords_handler(message, content):
    key_words = {'?': (1, "Sice ti neporadim, aaale tady mas macicku :)"),
                 'nechápu': (2, "Sice se nepostaram o to, abys to chapal, aaale tady mas macicku :)"),
                 'nechapu': (2, "Sice se nepostaram o to, abys to chapal, aaale tady mas macicku :)"),
                 'xd': (3, "PhanTom napsal 'xd' xd"),
                 'pls': (2, "Netreba prosit, tady mas macku :)"),
                 'prosim': (2, "Netreba prosit, tady mas macku :)")}
    
    random_num = randint(1, 9)
    for keyword, (chance, reply) in key_words:
        if keyword in content and random_num < chance:
            await message.channel.send(reply)
            await image_utils.send_cat(message.channel, False)
            await phanbomb(f"PhanTom napsal {keyword} a stesti nebylo na jeho strane")

async def print_points(params: dict):
    await params["message"].channel.send(f'{params["message"].author.display_name}, mas {reaction_data.get_val(params["user_id"], "points")} phanpointu')


async def shop(params: dict):
    if len(params["args"]) == 2 and params["args"][1] == 'list':
            msg = 'Nabidka v obchode:\n'
            for offer, price in SHOP_OFFERS.items():
                msg += f"{offer} za {price} PhanPoints\n"
            await params["message"].channel.send(msg)
    elif len(params["args"]) == 3 and params["args"][1] == 'buy' and params["args"][2] in SHOP_OFFERS.keys():
        if reaction_data.get_val(params["message"].author.id, "points") < SHOP_OFFERS[params["args"][2]]:
            return
        reaction_data.set_val(params["message"].author.id, "points", reaction_data.get_val(params["message"].author.id, "points") - SHOP_OFFERS[params["args"][2]])
        await params["message"].channel.send(f"koupil sis {params['args'][2]}")
        admin = await client.fetch_user(config.admin_id)
        if admin is not None:
            await admin.send(f'{params["message"].author.id}, {params["message"].author.display_name}, just bought {params["args"][2]}')
    else:
        await params["message"].channel.send('pouzij "!shop list" pro vypis nabidky, nebo "!shop buy NAZEV_POLOZKY" pro nakup v obchode')


##################################################################################################
#    Frankensteins monster of a bot, it's alive, it's not pretty, but it's alive, I think...     #
##################################################################################################


@client.event
async def on_message(message):

    if message.author.bot:
        return
    
    content = message.content.lower()
    if content == '':
        return

    parsed = content.split() 
    first_word = parsed[0]

    # commands
    if first_word in command_handlers_list:
         # this will be given to every command handler function 
        params = {"is_admin": message.author.id == config.admin_id,
                "message": message,
                "user_id": message.author.id,
                "args": parsed}
        await command_handlers_list[first_word](params)


    # phantoms keywords that can trigger send_cat and phanbomb 
    if message.author.id == config.target_user_id:
        await phanwords_handler(message, content)




# "main"

config.load_config(CONFIG_FILE)

reaction_data.load_data()


command_handlers_list = {'!reboot': reboot, 
                         '!bomb': call_phanbomb,
                         '!give': admin_gib_points,
                         '!update': update_bot,
                         '!ping': ping_bot,
                         '!kill': kill_bot,
                         '!phantop': print_leaderboard,
                         '!top': print_leaderboard,
                         '!points': print_points,
                         '!shop': shop}

while True:
    try:
        client.run(config.discord_token)
    except:
        continue
    sleep(10)