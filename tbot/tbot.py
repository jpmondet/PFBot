#! /usr/bin/env python3

from os import getenv
import asyncio

from dotenv import load_dotenv
from twitchio.ext import commands
from discord.ext import tasks
from discord import Client as dClient
from discord.ext import commands as dcommands

load_dotenv()

TOKEN: str = getenv("IRC_TOKEN")
CLIENT_ID: str = getenv('CLIENT_ID')
CHANNEL: str = getenv('CHANNEL')
CMD_PREFIX: str = getenv('CMD_PREFIX')
COMPACT_NICK: str = getenv('COMPACT_NICK')
BOT_NICK: str = getenv('BOT_NICK')
DISCORD_CHANNEL: str = getenv('DISCORD_CHANNEL')
DISCORD_TOKEN: str = getenv('DISCORD_TOKEN')
DISCORD_ID: str = getenv('DISCORD_ID')

DISCORD_CLIENT = dClient()
TWITCH_CHANNEL = None

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            irc_token=TOKEN,
            client_id=CLIENT_ID,
            nick=BOT_NICK,
            prefix=CMD_PREFIX,
            initial_channels=[CHANNEL,],
        )
        self.first = True
        self.nuser = []
        self.discord_channel = None

    # Events don't need decorators when subclassed
    async def event_ready(self):
        await asyncio.sleep(5)
        print(f'Ready | {self.nick}')
        #self.infoloop.start()
        global TWITCH_CHANNEL
        TWITCH_CHANNEL = self.get_channel(BOT_NICK)
        self.discord_channel = DISCORD_CLIENT.get_channel(int(DISCORD_CHANNEL))

    async def event_message(self, msg):
        print(msg.author.name, ':', msg.content)
        await self.discord_channel.send(f"**{msg.author.name}**: {msg.content}")
        if msg.content[0] != '!':
            if msg.author.name == BOT_NICK:
                pass
            elif msg.author.id in self.nuser:
                pass
            else:
                self.nuser.append(msg.author.id)
                channel = self.get_channel(BOT_NICK)
                await channel.send(f"Hey @{msg.author.name} ! :D
If you want, you can ask for a song with !bsr code and I'll play it if it's not too speedy. Else, enjoy the music! ")
        else:
            await self.handle_commands(msg)

    @commands.command(name='bsr')
    async def bsr_cmd(self, ctx, code):
        # TODO: Get song from bsaver with code
        # If too speedy, don't do it.
        await ctx.send(f"Sorry {ctx.author.name}, I'm not accepting requests to avoid injuries (old joints here xD )")

    @commands.command(name='info')
    async def info(self, ctx):
        await ctx.send(f"Heya {ctx.author.name} <3 ! I'm {COMPACT_NICK}, I'm not using a mic right now and I'm not very fast at writing, but I'll answer eventually, don't worry x) \nMeanwhile, please enjoy the music ^^")

    @tasks.loop(minutes=5)
    async def infoloop(self):
        channel = self.get_channel(BOT_NICK)
        await channel.send(f"Heya ! I'm {COMPACT_NICK}, I'm not using a mic right now and I'm not very fast at writing, but I'll answer eventually, don't worry x) \nMeanwhile, please enjoy the music ^^")


@DISCORD_CLIENT.event
async def on_ready():
    await asyncio.sleep(5)
    print("Discord bot ready!")

@DISCORD_CLIENT.event
async def on_message(ctx):
    if ctx.author.id == int(DISCORD_ID):
        print(ctx)
        await TWITCH_CHANNEL.send(ctx.content)

def main():
    loop = asyncio.get_event_loop()
    bot = Bot()
    loop.run_until_complete(asyncio.wait((DISCORD_CLIENT.start(DISCORD_TOKEN), bot.start())))

if __name__ == "__main__":
    main()
