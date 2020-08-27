""" Discord bot """

#! /usr/bin/env python3

#TODO: Improve markdown formatting
#TODO: Offer option to show only specific milestone
#TODO: Allow for roles changes/rankups on specific milestones

import os
import subprocess
import json
import requests
import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv('DISCORD_GUILD')
ROLE_ADMIN = os.getenv('ROLE_ADMIN')

SSURL = "https://new.scoresaber.com/api/player/{}/full"
BSD_LOGS_DIR = "../BSDlogs/"

# UTILS (NON-BOT FUNCTIONS)

def load_accounts():
    """ Loads registered discord ids & ss accs from files and return the associated dicts """
    id_accounts = {}
    ss_accounts = {}

    with open('id_accounts_list', 'r') as facc:
        id_accounts = json.load(facc)
    with open('ss_accounts_list', 'r') as facc:
        ss_accounts = json.load(facc)
    
    return id_accounts, ss_accounts

def get_pname_from_ssid(ssid):
    req = requests.get(SSURL.format(ssid))
    if req.status_code != 200:
        return None
    else:
        return req.json()['playerInfo']['playerName']

def paginate(lines, chars=2000):
    """ Paginate long outputs since discord limits to 2000 chars... """
    size = 0
    message = []
    for line in lines:
        if len(line) + size > chars:
            yield message
            message = []
            size = 0
        message.append(line)
        size += len(line)
    yield message

async def record_usage(ctx):
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild} at {ctx.message.created_at}")

# BOT FUNCTIONS START HERE
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord and ready to get cmds')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send("Sorry, this command is not available in DMs.")
        return
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Sorry, you do not have the correct role for this command.')
        return
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("Sorry, because of SS rate-limiting, we have to limit this command to 1 use every 60 seconds...")
        return
        
@bot.command(name='topAcc', help='Shows the current top15 of Average Ranked Accuracy \n (Limiting the use to once every 60 secs since SS rate-limits us a lot... >_<)')
@commands.before_invoke(record_usage)
@commands.cooldown(1, 60)
async def topAcc(ctx): #, nb_to_show: int = 50):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print("Starting to generate Acc leaderboard")
    await ctx.send("Starting to generate Acc leaderboard, please wait...(thanks Umbranox for rate-limiting)")
    topacc_return = subprocess.run(["python3", "../ssapi/topAcc/top_accu.py"], capture_output=True, text=True)
    print(topacc_return.stdout)
    for message in paginate(topacc_return.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='list-runs', help='List all your runs')
@commands.before_invoke(record_usage)
async def list_runs(ctx):

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Account not registered. Please use !link YourSSaccountID to register. Exple : `!link 76561197964179685` ")
        return

    runs_dir = f"{BSD_LOGS_DIR}{ssacc}"

    try:
        runs = os.listdir(runs_dir)
    except FileNotFoundError:
        await ctx.send("No runs saved for this account")
        return

    if not runs:
        await ctx.send("No runs saved for this account")
        return

    await ctx.send("Here are your save runs : ")
    output = ""
    for run in runs:
        output += f"{run} \n"
    
    for message in paginate(output):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='runs', help='Process and returns details from all your runs')
@commands.before_invoke(record_usage)
async def runs(ctx):

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Account not registered. Please use !link YourSSaccountID to register. Exple : `!link 76561197964179685` ")
        return

    runs_dir = f"{BSD_LOGS_DIR}{ssacc}"

    try:
        runs = os.listdir(runs_dir)
    except FileNotFoundError:
        await ctx.send("No runs saved for this account")
        return

    if not runs:
        await ctx.send("No runs saved for this account")
        return

    print("Starting to get all runs")
    await ctx.send("Starting to process all runs, please wait...")

    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-d", f"{runs_dir}", "-c", "True", "-nc", "True"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='run', help='process and returns details from the run you specified')
@commands.before_invoke(record_usage)
async def show_run(ctx, run_to_process = ""):

    if not run_to_process:
        await ctx.send("please, indicate which run you want to show. for exple : `!run 2020-08-02-19-30-45`")
        return

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("account not registered. please use !link yourssaccountid to register. exple : `!link 76561197964179685` ")
        return

    run_file = f"{BSD_LOGS_DIR}{ssacc}/{run_to_process}"

    if not os.access(run_file, os.R_OK):
        await ctx.send("this run cannot be found. you can check which runs you have with `!runs`")
        return

    print(f"starting to process run {run_file}")

    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-f", f"{run_file}", "-c", "true", "-nc", "true"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='runs-map', help='Get all runs on a specific map')
@commands.before_invoke(record_usage)
async def show_runs_map(ctx, map_to_process = ""):

    if not map_to_process:
        await ctx.send("Please, indicate which map you want to show. for exple : `!runs-map melancholia`")
        return

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("account not registered. please use !link yourssaccountid to register. exple : `!link 76561197964179685` ")
        return

    runs_dir = f"{BSD_LOGS_DIR}{ssacc}"

    try:
        runs = os.listdir(runs_dir)
    except FileNotFoundError:
        await ctx.send("No runs saved for this account")
        return

    if not runs:
        await ctx.send("No runs saved for this account")
        return

    print("Starting to get all runs")
    await ctx.send("Starting to process all runs, please wait...")

    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-d", f"{runs_dir}", "-c", "True", "-nc", "True", "-r", f"{map_to_process}"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='link', help='Register with your SS account')
@commands.before_invoke(record_usage)
@commands.guild_only()
async def link(ctx, ssa = ""):
    if not ssa:
        await ctx.send("Please, indicate your SS account. For example `!link 76561197964179685`")
        return

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)
    iddisc = ss_accounts.get(ssa)

    if ssacc:
        await ctx.send("Nice (re)try but account already registered")
        return

    if iddisc:
        await ctx.send("Hmm, this SS account is already registered to another account...o.0")
        return
    
    print("Validating that the account exist")

    req = requests.get(SSURL.format(ssa))

    if req.status_code != 200:
        #TODO : Improve error checking to determine if SS is really dead
        await ctx.send("Invalid SS account (or SS dead...)")
        return

    player_id = req.json()['playerInfo']['playerId']
    id_accounts[author] = player_id
    ss_accounts[player_id] = req.json()['playerInfo']['playerName']
    print(id_accounts)
    print(ss_accounts)

    with open('id_accounts_list', 'w') as fidacc:
        json.dump(id_accounts, fidacc)

    with open('ss_accounts_list', 'w') as fssacc:
        json.dump(ss_accounts, fssacc)

    await ctx.send("Account correctly registered :+1:")

@bot.command(name='unlink', help='Unlink SS account from your discord account')
@commands.before_invoke(record_usage)
@commands.guild_only()
async def unlink(ctx):

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Wait, you didn't register your SS account in the first place..")
        return

    print(f"Unlinking {ssacc} from {author}")

    del(id_accounts[author])
    del(ss_accounts[ssacc])
    print(id_accounts)
    print(ss_accounts)

    with open('id_accounts_list', 'w') as fidacc:
        json.dump(id_accounts, fidacc)

    with open('ss_accounts_list', 'w') as fssacc:
        json.dump(ss_accounts, fssacc)

    await ctx.send("Account correctly unlinked... So sad :crying_cat_face:")

@bot.command(name='list-players', help='List all the players registered')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def list_players(ctx):
    id_accounts, ss_accounts = load_accounts()

    await ctx.send("Players currently registered : ")
    output = ""
    for iddisc, ssacc in id_accounts.items():
        output += f"{iddisc} -> {ssacc} ({ss_accounts[ssacc]})\n"
    
    for message in paginate(output):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)


@bot.command(name='list-players-with-saved-runs', help='List all the players that already saved runs (even those that arent registered anymore')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def list_saved_players(ctx):
    id_accounts, ss_accounts = load_accounts()
    await ctx.send("Players that have already saved a run :")
    dirs = os.listdir(BSD_LOGS_DIR)

    output = ""
    for pdir in dirs:
        if pdir == 'Unknown':
            continue
        if '-' in pdir:
            continue
        try:
            pname = ss_accounts[pdir]
        except KeyError:
            pname = get_pname_from_ssid(pdir)
            if not pname:
                pname = "Name not found"

        output += f"{pdir} ({pname}) \n"
    
    for message in paginate(output):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='list-all-runs', help='List all runs saved for all players')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def list_all_runs(ctx):
    id_accounts, ss_accounts = load_accounts()
    await ctx.send("All runs :")
    dirs = os.listdir(BSD_LOGS_DIR)

    output = ""
    for pdir in dirs:
        if pdir == 'Unknown':
            continue
        if '-' in pdir:
            continue
        try:
            pname = ss_accounts[pdir]
        except KeyError:
            pname = get_pname_from_ssid(pdir)
            if not pname:
                pname = "Name not found"

        output += f"**{pdir} ({pname})** \n"
        pruns = os.listdir(f"{BSD_LOGS_DIR}/{pdir}")
        for prun in pruns:
            output += f"{prun} \n"
    
    for message in paginate(output):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='list-runs-of-player', help='List all runs of 1 specific player')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def list_runs_player(ctx, ssacc = ""):
    if not ssacc:
        await ctx.send("Please provide the SS account of the player you wanna list runs. Exple : `!list-runs-of-player 76561197964179685` ")
        return

    id_accounts, ss_accounts = load_accounts()

    runs_dir = f"{BSD_LOGS_DIR}{ssacc}"

    try:
        runs = os.listdir(runs_dir)
    except FileNotFoundError:
        await ctx.send("No runs saved for this account")
        return

    if not runs:
        await ctx.send("No runs saved for this account")
        return

    try:
        pname = ss_accounts[ssacc]
    except KeyError:
        pname = get_pname_from_ssid(ssacc)
        if not pname:
            pname = "Name not found"

    await ctx.send(f"Here are the saved runs of {ssacc} ({pname}): ")
    output = ""
    for run in runs:
        output += f"{run} \n"
    
    for message in paginate(output):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='compare', help='Compare runs of 2 players')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def compare(ctx, ssacc1 = "", ssacc2 = ""):

    if not (ssacc1 and ssacc2):
        await ctx.send(f"Please, provide the 2 SS accounts. Exple : !compare 76561197964179685 76561198084634262")  
        return

    # Not checking if the account is still registered since we could still have some saved runs from an
    # unlink account

    #author = str(ctx.author.id)
    #id_accounts, ss_accounts = load_accounts()
    #if ssacc1 not in ss_accounts:
    #    await ctx.send(f"Account {ssacc1} not found")
    #    return
    #if ssacc2 not in ss_accounts:
    #    await ctx.send(f"Account {ssacc2} not found")
    #    return

    runs_dir_1 = f"{BSD_LOGS_DIR}{ssacc1}"
    runs_dir_2 = f"{BSD_LOGS_DIR}{ssacc2}"

    try:
        runs1 = os.listdir(runs_dir_1)
    except FileNotFoundError:
        await ctx.send(f"No runs saved for account {ssacc1}")
        return
    if not runs1:
        await ctx.send(f"No runs saved for account {ssacc1}")
        return

    try:
        runs2 = os.listdir(runs_dir_2)
    except FileNotFoundError:
        await ctx.send(f"No runs saved for account {ssacc2}")
        return
    if not runs1:
        await ctx.send(f"No runs saved for account {ssacc2}")
        return

    print("Starting to get all runs")
    await ctx.send("Starting to process all runs, please wait...")

    print("Copying runs to a comparaison directory")
    #TODO : Use python libs instead of relying on linux cmds...
    comp_dir = f"{BSD_LOGS_DIR}{ssacc1}-{ssacc2}"
    if os.access(comp_dir, os.R_OK):
        output = subprocess.run(["rm", "-rf", f"{comp_dir}"], capture_output=True, text=True)
        print(output.stdout)
    output = subprocess.run(["mkdir", f"{comp_dir}"], capture_output=True, text=True)
    print(output.stdout)
    print("cp", f"{runs_dir_1}/*", f"{comp_dir}")
    output = subprocess.run(f"cp {runs_dir_1}/* {comp_dir}/", shell=True)
    print(output.stdout)
    output = subprocess.run(f"cp {runs_dir_2}/* {comp_dir}/", shell=True)
    print(output.stdout)

    print("Start processing the runs")
    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-d", f"{comp_dir}", "-c", "True", "-nc", "True"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='compare-specific', help='Compare specific runs of 2 players')
@commands.has_role(ROLE_ADMIN)
@commands.before_invoke(record_usage)
async def compare_specific(ctx, ssacc1 = "", run1 = "", ssacc2 = "", run2 = ""):

    if not (ssacc1 and ssacc2 and run1 and run2):
        await ctx.send(f"Please, provide the 2 SS accounts and the 2 runs to compare. Exple : `!compare-specific 76561197964179685 2020-08-02-19-30-45 76561198084634262 02-08-2020-1596347873`")
        return

    # Not checking if the account is still registered since we could still have some saved runs from an
    # unlink account

    #author = str(ctx.author.id)
    #id_accounts, ss_accounts = load_accounts()
    #if ssacc1 not in ss_accounts:
    #    await ctx.send(f"Account {ssacc1} not found")
    #    return
    #if ssacc2 not in ss_accounts:
    #    await ctx.send(f"Account {ssacc2} not found")
    #    return

    runs_dir_1 = f"{BSD_LOGS_DIR}{ssacc1}"
    runs_dir_2 = f"{BSD_LOGS_DIR}{ssacc2}"

    try:
        runs1 = os.listdir(runs_dir_1)
    except FileNotFoundError:
        await ctx.send(f"No runs saved for account {ssacc1}")
        return
    if not runs1:
        await ctx.send(f"No runs saved for account {ssacc1}")
        return
    if run1 not in runs1:
        await ctx.send(f"The run {run1} wasn't found for {ssacc1}")
        return

    try:
        runs2 = os.listdir(runs_dir_2)
    except FileNotFoundError:
        await ctx.send(f"No runs saved for account {ssacc2}")
        return
    if not runs1:
        await ctx.send(f"No runs saved for account {ssacc2}")
        return
    if run2 not in runs2:
        await ctx.send(f"The run {run2} wasn't found for {ssacc2}")
        return

    print("Starting to compare the 2 runs")
    await ctx.send("Starting to process the comparison of the 2 runs, please wait...")

    print("Copying runs to a comparaison directory")
    #TODO : Use python libs instead of relying on linux cmds...
    comp_dir = f"{BSD_LOGS_DIR}{ssacc1}-{ssacc2}"
    if os.access(comp_dir, os.R_OK):
        output = subprocess.run(["rm", "-rf", f"{comp_dir}"], capture_output=True, text=True)
        print(output.stdout)
    output = subprocess.run(["mkdir", f"{comp_dir}"], capture_output=True, text=True)
    print(output.stdout)
    output = subprocess.run(f"cp {runs_dir_1}/{run1} {comp_dir}/", shell=True)
    print(output.stdout)
    output = subprocess.run(f"cp {runs_dir_2}/{run2} {comp_dir}/", shell=True)
    print(output.stdout)

    print("Start processing the runs...")
    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-d", f"{comp_dir}", "-c", "True", "-nc", "True"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

bot.run(TOKEN)
