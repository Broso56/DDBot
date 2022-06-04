import discord
from discord.ui import Button, View, Select
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio
import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')
import json

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())

def scrape(player_profile):
    scrape.player_exists = True
    player_url = urllib.parse.quote(player_profile)
    url = f'https://ddnet.tw/players/?json2={player_url}'
    data = requests.get(url).json()

    if str(data) == '{}':
        scrape.player_exists = False

    return

def writejson(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

class UserLink(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client

    @client.tree.command(name="link", description='Link a DDNet profile to your Discord account')
    async def link(self, interaction: discord.Interaction, player: str):
        player_id = str(interaction.user.id)
        player_profile = player
        filename = 'links.json'

        with open(filename) as jf:
            data = json.load(jf)
            links = data['links']
            for link in links:
                link_key = link.keys()
                if player_id in link_key:
                    link_profile = link[player_id]
                    if link_profile == player:
                        await interaction.response.send_message(f'```arm\nERROR: Already linked with \'{player_profile}\'.\n```', ephemeral=True)
                        return
                    index = links.index(link)
                    links.pop(index)

        player_link = {player_id: player_profile}
        scrape(player_profile)
        if scrape.player_exists:
            links.append(player_link)
            writejson(data, filename)
            await interaction.response.send_message(f'You have been linked with `{player_profile}`.', ephemeral=True)
            return

        else:
            await interaction.response.send_message(f'```arm\nERROR: Player \'{player_profile}\' does not exist.\n```', ephemeral=True)
            return

async def setup(client): # Adding the class as a cog
    await client.add_cog(UserLink(client))