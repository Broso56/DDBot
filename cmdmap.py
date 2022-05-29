import discord
from discord.ui import Button, View, Select
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())

def scrape():
    #TODO: Fix list index errors
    global data
    map_url = urllib.parse.quote(mapname) # Converts text to user encoded url
    url = f'https://ddnet.tw/maps/?json={map_url}'
    data = requests.get(url).json()

    def CoreStats():
        global map_name, map_site, stars, map_img, type, mapper, release, median_time, first_finish, last_finish, finishes, finishers, dimensions, replay_rate, points
        map_name = data['name']
        map_site = data['website']
        stars = data['difficulty']
        map_img = data['thumbnail']
        type = data['type']
        mapper = data['mapper']
        release = data['release']
        median_time = int(data['median_time'])
        first_finish = data['first_finish']
        last_finish = data['last_finish']
        finishes = data['finishes']
        finishers = data['finishers']
        dimensions = data['width'], data['height']
        points = data['points']

        release = f'<t:{str(release)[:-2]}:R>'

        hour = False
        if median_time >= 3600:
            hour = True

        median_time = str(timedelta(seconds=median_time))

        if not hour:
            median_time = median_time[2:]

        replay_rate = finishes / finishers
        replay_rate = str(round(replay_rate, 1))

        d = stars
        stars = []
        i = len(stars)

        while i < 5:
            if i <= d - 1:
                stars.append('★')
            else:
                stars.append('✰')
            i = len(stars)

        stars = ''.join([str(item) for item in stars])


    def RankStats():
        global li_r_rank, li_r_player, li_r_time, li_r_timestamp, li_tr_rank, li_tr_players, li_tr_time, li_tr_timestamp
        team_ranks = data['team_ranks']
        ranks = data['ranks']

        li_r_rank = []
        li_r_player = []
        li_r_time = []
        li_r_timestamp = []

        li_tr_rank = []
        li_tr_players = []
        li_tr_time = []
        li_tr_timestamp = []

        for r in ranks:
            r_rank = r['rank']
            r_player = r['player']
            r_time = int(r['time'])
            r_timestamp = r['timestamp']
            r_timestamp = f'<t:{str(r_timestamp)[:-2]}:R>'

            hour = False
            if r_time >= 3600:
                hour = True

            r_time = str(timedelta(seconds=r_time))

            if not hour:
               r_time = r_time[2:]

            li_r_rank.append(r_rank)
            li_r_player.append(r_player)
            li_r_time.append(r_time)
            li_r_timestamp.append(r_timestamp)

        for tr in team_ranks:
            tr_rank = tr['rank']
            tr_players = tr['players']
            tr_time = int(tr['time'])
            tr_timestamp = tr['timestamp']
            tr_timestamp = f'<t:{str(tr_timestamp)[:-2]}:R>'

            hour = False
            if tr_time >= 3600:
                hour = True

            tr_time = str(timedelta(seconds=tr_time))

            if not hour:
               tr_time = tr_time[2:]

            li_tr_rank.append(tr_rank)
            li_tr_players.append(tr_players)
            li_tr_time.append(tr_time)
            li_tr_timestamp.append(tr_timestamp)

    CoreStats()
    RankStats()


class UserMap(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client

    @client.tree.command(name="map", description='Searches for a map')
    async def map(self, interaction: discord.Interaction, map: str):
        global mapname

        mapname = map
        user = interaction.user

        scrape()

        thumbnail = user.avatar
        em = discord.Embed(
            title=f'{map_name}',
            description=f'**By {mapper}**\n**{type}** {stars} **({points} Points)**',
            url=f'{map_site}',
            timestamp = datetime.now()
        )

        em.add_field(name='Released:', value=release, inline=False)
        em.add_field(name='\u200B', value=
        f'''
        Finished: `{finishers}`, Total Finishes: `{finishes}`
        Replay Rate: `{replay_rate}`
        Median Time: `{median_time}`
        ''', inline=False
        )
        em.add_field(
            name='Top 5 Ranks:',
            value=
            f'''
            1. [`{li_r_player[0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_r_player[0])}), `{li_r_time[0]}`
            2. [`{li_r_player[1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_r_player[1])}), `{li_r_time[1]}`
            3. [`{li_r_player[2]}`](https://ddnet.tw/players/{urllib.parse.quote(li_r_player[2])}), `{li_r_time[2]}`
            4. [`{li_r_player[3]}`](https://ddnet.tw/players/{urllib.parse.quote(li_r_player[3])}), `{li_r_time[3]}`
            5. [`{li_r_player[4]}`](https://ddnet.tw/players/{urllib.parse.quote(li_r_player[4])}), `{li_r_time[4]}`
            ''', inline=False
        )
        em.add_field(
            name='Top 5 Team Ranks:',
            value=
            f'''
            1. [`{li_tr_players[0][0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[0][0])}) & [`{li_tr_players[0][1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[0][1])}), `{li_tr_time[0]}`
            2. [`{li_tr_players[1][0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[1][0])}) & [`{li_tr_players[1][1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[1][1])}), `{li_tr_time[1]}`
            3. [`{li_tr_players[2][0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[2][0])}) & [`{li_tr_players[2][1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[2][1])}), `{li_tr_time[2]}`
            4. [`{li_tr_players[3][0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[3][0])}) & [`{li_tr_players[3][1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[3][1])}), `{li_tr_time[3]}`
            5. [`{li_tr_players[4][0]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[4][0])}) & [`{li_tr_players[4][1]}`](https://ddnet.tw/players/{urllib.parse.quote(li_tr_players[4][1])}), `{li_tr_time[4]}`
            ''', inline=False
        )
        em.set_author(name=f'Reqeusted by {user.name}')
        em.set_thumbnail(url=thumbnail)
        em.set_image(url=f'{map_img}')
        
        await interaction.response.send_message(embed=em)
        await asyncio.sleep(150.0) # Waits 2.5 Minutes, then deletes message to clear up spam.
        await interaction.delete_original_message()

async def setup(client): # Adding the class as a cog
    await client.add_cog(UserMap(client))
