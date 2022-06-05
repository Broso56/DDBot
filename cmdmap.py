import discord
from discord.ui import Button, View, Select
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')
import random
import json

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())
tree = app_commands

def linkcheck(user_id):
    with open('links.json') as jf:
        data = json.load(jf)
        links = data['links']
        link_profile = None

        for link in links:
            link_key = link.keys()
            if user_id in link_key:
                link_profile = link[user_id]
        
        return link_profile

def scrape(mapname, link_profile):
    global pl_rank, pl_time, pl_link

    scrape.map_exists = True
    map_url = urllib.parse.quote(mapname) # Converts text to user encoded url
    map_url = f'https://ddnet.tw/maps/?json={map_url}'
    data = requests.get(map_url).json()
    if str(data) == '{}':
        scrape.map_exists = False
        return
    
    if link_profile != None:
        pl_url = urllib.parse.quote(link_profile)
        pl_url = f'https://ddnet.tw/players/?json2={pl_url}'
        pl_data = requests.get(pl_url).json()
        categories = { # Map difficulties/categories
        0 : 'Novice',
        1 : 'Moderate',
        2 : 'Brutal',
        3 : 'Insane',
        4 : 'Dummy',
        5 : 'DDmaX',
        6 : 'Oldschool',
        7 : 'Solo',
        8 : 'Race',
        9 : 'Fun'
        }

        i = 0
        while i <= 9: # Loop to sort through the data for each category
            # Searches in the current category for maps
            cat = categories[i]
            category = pl_data['types'][cat]
            maps = category['maps']
            
            m = 0
            maps_name = []
            for map in maps:
                maps_name.append(map)

            for map in maps:
                if map == mapname:
                    name = maps_name[m]
                    if 'rank' in maps[name]:
                        pl_rank = maps[name]['rank']
                        pl_rank = f'`{pl_rank}.`'

                        pl_time = int(maps[name]['time'])
                        hour = False
                        if pl_time >= 3600:
                            hour = True

                        pl_time = str(timedelta(seconds=pl_time))

                        if not hour:
                           pl_time = pl_time[2:]

                        pl_time = f'`{pl_time}`'

                    else:
                        pl_rank = '`-.`'
                        pl_time = '`Unranked`'

                m += 1
            i += 1

        pl_link = f'[`{link_profile}`](https://ddnet.tw/players/{link_profile}),'

    else:
        pl_rank = ''
        pl_time = ''
        pl_link = ''



    def CoreStats():
        nonlocal data
        global map_name, map_site, stars, map_img, type, mapper, release, median_time, first_finish, last_finish, finishes, finishers, dimensions, replay_rate, points
        has_release = True
        map_name = data['name']
        map_site = data['website']
        stars = data['difficulty']
        map_img = data['thumbnail']
        type = data['type']
        mapper = data['mapper']

        try:
            release = data['release']
        except:
            release = '`Unknown.`'
            has_release = False
        median_time = int(data['median_time'])
        first_finish = data['first_finish']
        last_finish = data['last_finish']
        finishes = data['finishes']
        finishers = data['finishers']
        dimensions = data['width'], data['height']
        points = data['points']

        if has_release:
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
        nonlocal data
        global li_r_rank, li_r_player, li_r_time, li_r_timestamp, li_r_url, li_tr_rank, li_tr_players, li_tr_time, li_tr_timestamp, li_tr_url
        team_ranks = data['team_ranks']
        ranks = data['ranks']

        li_r_rank = []
        li_r_player = []
        li_r_time = []
        li_r_timestamp = []
        li_r_url = []

        li_tr_rank = []
        li_tr_players = []
        li_tr_time = []
        li_tr_timestamp = []
        li_tr_url = []

        for r in ranks:
            r_rank = r['rank']
            r_player = r['player']
            r_time = int(r['time'])
            r_url = f'[`{r_player}`](https://ddnet.tw/players/{urllib.parse.quote(r_player)}),'
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
            li_r_time.append(f'`{r_time}`')
            li_r_timestamp.append(r_timestamp)
            li_r_url.append(r_url)

        for tr in team_ranks:
            tr_rank = tr['rank']
            tr_players = tr['players']
            tr_time = int(tr['time'])
            tr_url = [f'[`{tr_players[0]}`](https://ddnet.tw/players/{urllib.parse.quote(tr_players[0])}) &', f'[`{tr_players[1]}`](https://ddnet.tw/players/{urllib.parse.quote(tr_players[1])}),']
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
            li_tr_time.append(f'`{tr_time}`')
            li_tr_timestamp.append(tr_timestamp)
            li_r_url.append(r_url)
            li_tr_url.append(tr_url)

        r_len = len(li_r_player)
        tr_len = len(li_tr_players)

        while 9 >= r_len:
            li_r_player.append('')
            li_r_rank.append('-')
            li_r_time.append('')
            li_r_url.append('')
            r_len = len(li_r_player)

        while 9 >= tr_len:
            li_tr_players.append(['', ''])
            li_tr_rank.append('-')
            li_tr_time.append('')
            li_tr_url.append(['', ''])
            tr_len = len(li_tr_players)

    CoreStats()
    RankStats()

def map_random(category, link_profile):
    url = 'https://ddnet.tw/players/?json2=Broso56'
    data = requests.get(url).json()
    
    def find_map(category):
        nonlocal data
        if category == 'All':
            categories = [
                'Novice',
                'Moderate',
                'Brutal',
                'Insane',
                'Dummy',
                'DDmaX',
                'Oldschool',
                'Solo',
                'Race',
                'Fun'
            ]
            category = random.choice(categories)
        cat = data['types'][category]
        maps = cat['maps']
        maps_name = []

        for map in maps:
            maps_name.append(map)

        ran_map = random.choice(maps_name)
        return(ran_map)

    ran_map = find_map(category)

    scrape(ran_map, link_profile)

def map_unfinished(category, sort, player_name, link_profile):
    url = urllib.parse.quote(player_name)
    url = f'https://ddnet.tw/players/?json2={url}'
    data = requests.get(url).json()
    found = True

    def find_ran_unfin(category):
        nonlocal data, found
        cat_all = False
        no_cat = False
        maps_list = []
        if category == 'All':
            categories = [
                'Novice',
                'Moderate',
                'Brutal',
                'Insane',
                'Dummy',
                'DDmaX',
                'Oldschool',
                'Solo',
                'Race',
                'Fun'
            ]
            cat_all = True
            category = random.choice(categories)

        def ranmaploop():
            nonlocal data, category, categories, cat_all
            cat = data['types'][category]
            maps = cat['maps']
            maps_name = []
            maps_list = []
            m = 0
            for map in maps:
                maps_name.append(map)
        
            for __map__ in maps: # Searches in those maps for details (rank, finishes, etc)
                    name = maps_name[m]
                    if 'rank' not in maps[name]: # There is no 'rank' key for maps that you have not finished.
                        maps_list.append(name)
            

        
                    m += 1
            return maps_list
        while maps_list == []:
            maps_list = ranmaploop()

            if maps_list == []:
                if cat_all:
                    categories.remove(category)
                    if categories == []:
                        no_cat = True
                        found = False
                        break
                    else:
                        category = random.choice(categories)
                else:
                    found = False
                    break
        
        if found:
            ran_unfin_map = random.choice(maps_list)
            return ran_unfin_map
            
        else:
            if no_cat:
                print(f'{player_name} has finished every map!')
                return
            else:
                print(f'{player_name} has finished every map on this category!')
                return

    def find_mf_unfin(category):
        nonlocal data
        cat_all = False
        if category == 'All':
            categories = [
                'Novice',
                'Moderate',
                'Brutal',
                'Insane',
                'Dummy',
                'DDmaX',
                'Oldschool',
                'Solo',
                'Race',
                'Fun'
            ]
            cat_all = True

        def unfmaploop():
            nonlocal data, category, categories, cat_all
            if cat_all:
                categories = { # Map difficulties/categories
                    0 : 'Novice',
                    1 : 'Moderate',
                    2 : 'Brutal',
                    3 : 'Insane',
                    4 : 'Dummy',
                    5 : 'DDmaX',
                    6 : 'Oldschool',
                    7 : 'Solo',
                    8 : 'Race',
                    9 : 'Fun'
            }
            i = 0
            maps_name = []
            maps_fin = []
            maps_list = []
            maps_finlist = []

            if cat_all:

                while i <= 9:
                    maps_name = []
                    maps_fin = []
                    cat = categories[i]
                    cat = data['types'][cat]
                    maps = cat['maps']
                    m = 0
    
                    for map in maps:
                        maps_name.append(map)
                        maps_fin.append(maps[map]['total_finishes'])
                        m += 1
    
                    m = 0
                    for __map__ in maps: # Searches in those maps for details (rank, finishes, etc)
                            name = maps_name[m]
                            fins = maps_fin[m]
    
                            if 'rank' not in maps[name]: # There is no 'rank' key for maps that you have not finished.
                                maps_list.append(name)
                                maps_finlist.append(fins)
    
                            m += 1
                    i += 1
            else:
                cat = data['types'][category]
                maps = cat['maps']
                m = 0

                for map in maps:
                    maps_name.append(map)
                    maps_fin.append(maps[map]['total_finishes'])
                    m += 1

                m = 0
                for __map__ in maps: # Searches in those maps for details (rank, finishes, etc)
                        name = maps_name[m]
                        fins = maps_fin[m]

                        if 'rank' not in maps[name]: # There is no 'rank' key for maps that you have not finished.
                            maps_list.append(name)
                            maps_finlist.append(fins)

                        m += 1

            if maps_list != []:
                most_finished = max(maps_finlist)
                index = maps_finlist.index(most_finished)
                mf_unfin_map = maps_list[index]
            else:
                mf_unfin_map = None
            
            return mf_unfin_map

        mf_unfin_map = unfmaploop()
        return mf_unfin_map

    if sort == 'Random':
        ran_unfin_map = find_ran_unfin(category)
        if ran_unfin_map != None:
            scrape(ran_unfin_map, link_profile)
            return found
        else:
            found = False
            return found

    if sort == 'Most Finished':
        mf_unfin_map = find_mf_unfin(category)
        if mf_unfin_map != None:
            scrape(mf_unfin_map, link_profile)
            return found
        else:
            found = False
            return found

class UserMap(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client

    @tree.command(name='map', description='Searches for a map')
    @tree.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def map(self, interaction: discord.Interaction, map: str):
        mapname = map
        user = interaction.user
        user_id = str(interaction.user.id)
        link_profile = linkcheck(user_id)
        scrape(mapname, link_profile)
        if not scrape.map_exists:
            await interaction.response.send_message(f'```arm\nERROR: M\u200bap \'{map}\' does not exist.\n```', ephemeral=True) # Invis character is so that 'Map' doesnt get highlighted in red.
            return

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
            `{li_r_rank[0]}.` {li_r_url[0]} {li_r_time[0]}
            `{li_r_rank[1]}.` {li_r_url[1]} {li_r_time[1]}
            `{li_r_rank[2]}.` {li_r_url[2]} {li_r_time[2]}
            `{li_r_rank[3]}.` {li_r_url[3]} {li_r_time[3]}
            `{li_r_rank[4]}.` {li_r_url[4]} {li_r_time[4]}

            {pl_rank} {pl_link} {pl_time} 
            ''', inline=False
        )
        em.add_field(
            name='Top 5 Team Ranks:',
            value=
            f'''
            `{li_tr_rank[0]}.` {li_tr_url[0][0]} {li_tr_url[0][1]} {li_tr_time[0]}
            `{li_tr_rank[1]}.` {li_tr_url[1][0]} {li_tr_url[1][1]} {li_tr_time[1]}
            `{li_tr_rank[2]}.` {li_tr_url[2][0]} {li_tr_url[2][1]} {li_tr_time[2]}
            `{li_tr_rank[3]}.` {li_tr_url[3][0]} {li_tr_url[3][1]} {li_tr_time[3]}
            `{li_tr_rank[4]}.` {li_tr_url[4][0]} {li_tr_url[4][1]} {li_tr_time[4]}
            ''', inline=False
        )
        em.set_author(name=f'Reqeusted by {user.name}')
        em.set_thumbnail(url=thumbnail)
        em.set_image(url=f'{map_img}')
        
        await interaction.response.send_message(embed=em)
        await asyncio.sleep(150.0) # Waits 2.5 Minutes, then deletes message to clear up spam.
        await interaction.delete_original_message()

    @map.error
    async def on_map_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f'```arm\nERROR: {str(error)}\n```', ephemeral=True)
            return

    @tree.command(name='maprandom', description='Searches for a random map')
    @tree.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    @tree.choices(
        category=[
            Choice(name='All', value= 'All'),
            Choice(name='Novice', value='Novice'),
            Choice(name='Moderate', value='Moderate'),
            Choice(name='Brutal', value='Brutal'),
            Choice(name='Insane', value='Insane'),
            Choice(name='Dummy', value='Dummy'),
            Choice(name='DDmaX', value='DDmaX'),
            Choice(name='Oldschool', value='Oldschool'),
            Choice(name='Solo', value='Solo'),
            Choice(name='Race', value='Race'),
            Choice(name='Fun', value='Fun')
        ]
    )

    async def maprandom(self, interaction: discord.Interaction, category: Choice[str]):
        user = interaction.user
        user_id = str(interaction.user.id)
        link_profile = linkcheck(user_id)
        map_random(category.value, link_profile)

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
            `{li_r_rank[0]}.` {li_r_url[0]} {li_r_time[0]}
            `{li_r_rank[1]}.` {li_r_url[1]} {li_r_time[1]}
            `{li_r_rank[2]}.` {li_r_url[2]} {li_r_time[2]}
            `{li_r_rank[3]}.` {li_r_url[3]} {li_r_time[3]}
            `{li_r_rank[4]}.` {li_r_url[4]} {li_r_time[4]}

            {pl_rank} {pl_link} {pl_time} 
            ''', inline=False
        )
        em.add_field(
            name='Top 5 Team Ranks:',
            value=
            f'''
            `{li_tr_rank[0]}.` {li_tr_url[0][0]} {li_tr_url[0][1]} {li_tr_time[0]}
            `{li_tr_rank[1]}.` {li_tr_url[1][0]} {li_tr_url[1][1]} {li_tr_time[1]}
            `{li_tr_rank[2]}.` {li_tr_url[2][0]} {li_tr_url[2][1]} {li_tr_time[2]}
            `{li_tr_rank[3]}.` {li_tr_url[3][0]} {li_tr_url[3][1]} {li_tr_time[3]}
            `{li_tr_rank[4]}.` {li_tr_url[4][0]} {li_tr_url[4][1]} {li_tr_time[4]}
            ''', inline=False
        )
        em.set_author(name=f'Reqeusted by {user.name}')
        em.set_thumbnail(url=thumbnail)
        em.set_image(url=f'{map_img}')
        
        await interaction.response.send_message(embed=em)
        await asyncio.sleep(150.0) # Waits 2.5 Minutes, then deletes message to clear up spam.
        await interaction.delete_original_message()

    @maprandom.error
    async def on_maprandom_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f'```arm\nERROR: {str(error)}\n```', ephemeral=True)
            return

    @tree.command(name='mapunfinished', description='Searches for an unfinished map')
    @tree.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    @tree.choices(
        sort=[
            Choice(name='Random', value='Random'),
            Choice(name='Most Finished', value='Most Finished')
        ],
        category=[
            Choice(name='All', value= 'All'),
            Choice(name='Novice', value='Novice'),
            Choice(name='Moderate', value='Moderate'),
            Choice(name='Brutal', value='Brutal'),
            Choice(name='Insane', value='Insane'),
            Choice(name='Dummy', value='Dummy'),
            Choice(name='DDmaX', value='DDmaX'),
            Choice(name='Oldschool', value='Oldschool'),
            Choice(name='Solo', value='Solo'),
            Choice(name='Race', value='Race'),
            Choice(name='Fun', value='Fun')
        ]
    )
    async def mapunfinished(self, interaction: discord.Interaction, profile: str, category: Choice[str], sort: Choice[str]):
        user = interaction.user
        player_name = profile
        user_id = str(interaction.user.id)
        link_profile = linkcheck(user_id)
        if sort.value == 'Random':
            found = map_unfinished(category.value, sort.value, player_name, link_profile)
            if not found:
                await interaction.response.send_message(f'{player_name} has finished all maps on this category.', ephemeral=True)
                return

        if sort.value == 'Most Finished':
            found = map_unfinished(category.value, sort.value, player_name, link_profile)
            if not found:
                await interaction.response.send_message(f'{player_name} has finished all maps on this category.', ephemeral=True)
                return

        user = interaction.user

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
            `{li_r_rank[0]}.` {li_r_url[0]} {li_r_time[0]}
            `{li_r_rank[1]}.` {li_r_url[1]} {li_r_time[1]}
            `{li_r_rank[2]}.` {li_r_url[2]} {li_r_time[2]}
            `{li_r_rank[3]}.` {li_r_url[3]} {li_r_time[3]}
            `{li_r_rank[4]}.` {li_r_url[4]} {li_r_time[4]}
            
            {pl_rank} {pl_link} {pl_time} 
            ''', inline=False
        )
        em.add_field(
            name='Top 5 Team Ranks:',
            value=
            f'''
            `{li_tr_rank[0]}.` {li_tr_url[0][0]} {li_tr_url[0][1]} {li_tr_time[0]}
            `{li_tr_rank[1]}.` {li_tr_url[1][0]} {li_tr_url[1][1]} {li_tr_time[1]}
            `{li_tr_rank[2]}.` {li_tr_url[2][0]} {li_tr_url[2][1]} {li_tr_time[2]}
            `{li_tr_rank[3]}.` {li_tr_url[3][0]} {li_tr_url[3][1]} {li_tr_time[3]}
            `{li_tr_rank[4]}.` {li_tr_url[4][0]} {li_tr_url[4][1]} {li_tr_time[4]}
            ''', inline=False
        )
        em.set_author(name=f'Reqeusted by {user.name}')
        em.set_thumbnail(url=thumbnail)
        em.set_image(url=f'{map_img}')
        
        await interaction.response.send_message(embed=em)
        await asyncio.sleep(150.0) # Waits 2.5 Minutes, then deletes message to clear up spam.
        await interaction.delete_original_message()

    @mapunfinished.error
    async def on_mapunfinished_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f'```arm\nERROR: {str(error)}\n```', ephemeral=True)
            return

async def setup(client): # Adding the class as a cog
    await client.add_cog(UserMap(client))
