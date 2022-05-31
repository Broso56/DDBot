from clienttoken import token # Client token. NEVER share this with anyone, as it gives them access to your bot.
import discord                      # ^ Changed file name from 'bottoken' to 'clienttoken' locally to avoid my token file from being tracked + committed
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
import pytz
import asyncio

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands


@client.event
async def on_ready():
    pst = pytz.timezone('US/Pacific')
    psttime = datetime.datetime.now(pst)
    current_time = psttime.strftime('%I:%M %p PST.')
    print(f"READY: Bot readied at {current_time}")

@client.tree.command(name='reload')
@tree.choices(
    command=[
            Choice(name='Profile', value='profile'),
            Choice(name='Map', value='map'),
            Choice(name='Sync', value='sync')
        ]
)
@commands.is_owner()
async def reload(interaction: discord.Interaction, command: Choice[str]):
    await client.reload_extension(f"cmd{command.value}")
    await interaction.response.send_message(f'{command.name} command reloaded!', ephemeral=True)

async def setup(): # Loading cogs from other files

    async with client:
        await client.load_extension('cmdprofile')
        await client.load_extension('cmdsync')
        await client.load_extension('cmdmap')
        await client.start(token) # Client token. NEVER share this with anyone, as it gives them access to your bot.

asyncio.run(setup())
