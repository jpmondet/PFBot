""" Discord bot """

#! /usr/bin/env python3

#TODO: add markdown formatting
#TODO: remove unnecessary infos
#TODO: Offer different versions of the output
#TODO: Add unregister command
#TODO: On registering : check if ssAccount is also already used
#TODO: Add command to list runs
#TODO: Add command to choose 1 specific run

import os
import json
import subprocess
import requests
import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv('DISCORD_GUILD')

ssurl = "https://new.scoresaber.com/api/player/{}/full"


bot = commands.Bot(command_prefix='!')

def load_accounts():
    id_accounts = {}
    ss_accounts = {}

    with open('id_accounts_list', 'r') as facc:
        id_accounts = json.load(facc)
    with open('ss_accounts_list', 'r') as facc:
        ss_accounts = json.load(facc)
    
    return id_accounts, ss_accounts

def check_and_get_ss_account(discord_id):
    pass


def paginate(lines, chars=2000):
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

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord and ready to get cmds')

@bot.command(name='topAcc', help='Shows the current top50 of Average Ranked Accuracy')
#@commands.has_role('admin')
async def topAcc(ctx): #, nb_to_show: int = 50):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    print("Starting to generate Acc leaderboard")
    await ctx.send("Starting to generate Acc leaderboard, please wait...(thanks Umbranox for rate-limiting)")
    topacc_return = subprocess.run(["python3", "../ssapi/topAcc/top_accu.py"], capture_output=True, text=True)
    print(topacc_return.stdout)
    for message in paginate(topacc_return.stdout):
        msg_to_send = ''.join(message)

@bot.command(name='list-runs', help='List all your runs')
#@commands.has_role('admin')
async def list_runs(ctx):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Account not registered. Please use !ss YourSSaccountID to register. Exple : `!ss 76561197964179685` ")
        return

    runs_dir = f"../BSDlogs/{ssacc}"

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


@bot.command(name='runs', help='Process and returns details from all your runs')
#@commands.has_role('admin')
async def runs(ctx):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Account not registered. Please use !ss YourSSaccountID to register. Exple : `!ss 76561197964179685` ")
        return

    runs_dir = f"../BSDlogs/{ssacc}"

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

@bot.command(name='run', help='Process and returns details from the run you specified')
#@commands.has_role('admin')
async def show_run(ctx, run_to_process):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")

    if not run_to_process:
        await ctx.send("Please, indicate which run you want to show. For exple : `!run 2020-08-02-19-30-45`")
        return

    author = str(ctx.author.id)

    id_accounts, ss_accounts = load_accounts()

    ssacc = id_accounts.get(author)

    if not ssacc:
        await ctx.send("Account not registered. Please use !ss YourSSaccountID to register. Exple : `!ss 76561197964179685` ")
        return

    run_file = f"../BSDlogs/{ssacc}/{run_to_process}"

    if not os.access(run_file, os.R_OK):
        await ctx.send("This run cannot be found. You can check which runs you have with `!runs`")
        return

    print(f"Starting to process run {run_file}")

    output = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-f", f"{run_file}", "-c", "True", "-nc", "True"], capture_output=True, text=True)
    print(output.stdout)
    for message in paginate(output.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='ss', help='Register with your SS account')
async def ss(ctx, ssa):
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    if not ssa:
        await ctx.send("Please, indicate your SS account. For example `!ss 76561197964179685`")
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

    req = requests.get(ssurl.format(ssa))

    if req.status_code != 200:
        await ctx.send("Invalid SS account")
        return

    player_id = req.json()['playerInfo']['playerId']
    id_accounts[author] = player_id
    ss_accounts[player_id] = author
    print(id_accounts)
    print(ss_accounts)

    with open('id_accounts_list', 'w') as fidacc:
        json.dump(id_accounts, fidacc)

    with open('ss_accounts_list', 'w') as fssacc:
        json.dump(ss_accounts, fssacc)

    await ctx.send("Account correctly registered :+1:")

@bot.command(name='unlink', help='Unlink SS account from your discord account')
async def unlink(ctx):
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)
