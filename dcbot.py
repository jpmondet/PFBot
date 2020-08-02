""" Discord bot """

#! /usr/bin/env python3


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
        await ctx.send(msg_to_send)

@bot.command(name='runs', help='Get all your runs')
#@commands.has_role('admin')
async def runs(ctx):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    accounts = {}
    with open('accounts_list', 'r') as facc:
        accounts = json.load(facc)

    if not accounts.get(ctx.author.id):
        await ctx.send("Account not registered. Please use !ss YourSSaccountID to register. Exple : `!ss 76561197964179685` ")
        return

    ssacc = accounts.get(ctx.author.id) 

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

    topacc_return = subprocess.run(["python3", "../bsdlp/parse_logs.py", "-d", f"{runs_dir}", "-c", "True"], capture_output=True, text=True)
    print(topacc_return.stdout)
    for message in paginate(topacc_return.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.command(name='ss', help='Register with your SS account')
async def ss(ctx, ssa):
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    if not ssa:
        await ctx.send("Please, indicate your SS account. For example `!ss 76561197964179685`")
        return
    
    accounts = {}
    with open('accounts_list', 'r') as facc:
        accounts = json.load(facc)

    if accounts.get(ctx.author.id):
        await ctx.send("Nice (re)try but account already registered")
        return

    
    print("Validating that the account exist")

    req = requests.get(ssurl.format(ssa))

    if req.status_code != 200:
        await ctx.send("Invalid SS account")
        return

    accounts[ctx.author.id] = req.json()['playerInfo']['playerId']
    print(accounts)

    with open('accounts_list', 'w') as facc:
        json.dump(accounts, facc)

    await ctx.send("Account correctly registered :+1:")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)
