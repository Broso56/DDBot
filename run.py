from bottoken import token # Client token. NEVER share this with anyone, as it gives them access to your bot.
import discord
from discord.ext import commands
import datetime
import pytz
import asyncio

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())


@client.event
async def on_ready():
    pst = pytz.timezone('US/Pacific')
    psttime = datetime.datetime.now(pst)
    current_time = psttime.strftime('%I:%M %p PST.')
    print(f"READY: Bot readied at {current_time}")

async def setup(): # Loading cogs from other files

    async with client:
        await client.load_extension('cmdprofile')
        await client.load_extension('cmdsync')
        await client.start(token) # Client token. NEVER share this with anyone, as it gives them access to your bot.

asyncio.run(setup())
