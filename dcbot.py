""" Discord bot """

#! /usr/bin/env python3


import os
import subprocess
import discord
from discord.ext import commands
#from top_accu import top_acc

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv('DISCORD_GUILD')

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
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='topAcc', help='Shows the current top50 of Average Ranked Accuracy')
#@commands.has_role('admin')
async def topAcc(ctx, nb_to_show: int = 50):
    #guild = ctx.guild
    #existing_channel = discord.utils.get(guild.channels, name=channel_name)
    #if not existing_channel:
    #    print(f'Creating a new channel: {channel_name}')
    #    await guild.create_text_channel(channel_name)
    #response = "1st : You"
    #accu_rank = top_acc()
    #response = "#"*15 + "Top by Accuracy" + "#"*15 + '\n'
    #for rank, stats in enumerate(accu_rank):
    #    if rank < 50:
    #        print(" {:>2} - {:>30}     (ranked_accu: {:.2f}  ranked_count: {})".format(rank+1, stats[0], stats[1][1], stats[1][0]))

    #print(ctx.__dict__)
    print(f"{ctx.author} asked for {ctx.message.content} on chan {ctx.channel} of {ctx.guild}")
    print("Starting to generate Acc leaderboard")
    topacc_return = subprocess.run(["python3", "../ssapi/topAcc/top_accu.py"], capture_output=True, text=True)
    print(topacc_return.stdout)

    #response = topacc_return.stdout
    for message in paginate(topacc_return.stdout):
        msg_to_send = ''.join(message)
        await ctx.send(msg_to_send)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


bot.run(TOKEN)