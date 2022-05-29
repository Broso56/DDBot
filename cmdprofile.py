import discord
from discord.ui import Button, View, Select
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio
import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())


def scrape(): # Web Scrapes + Sorts Data
    global data
    player_url = urllib.parse.quote(player_name) # Converts text to user encoded url
    url = f'https://ddnet.tw/players/?json2={player_url}'
    data = requests.get(url).json()

    def PointStats():
        global points_total, points_rank, points_lm, points_lw, pointavg_lm, pointavg_lw

        points_total = data['points']['points']
        points_rank = data['points']['rank']
        points_lm = data['points_last_month']['points'] # lm = last month
        points_lw = data['points_last_week']['points'] # lw = last week
        pointavg_lm = points_lm / 30
        pointavg_lw = points_lw / 7
    
        # Rounds the decimals to full number // Removes the last 2 numbers (e.g So it shows as 1 instead of 1.0 cause it does that for some reason)
        pointavg_lm = str(round(pointavg_lm, 0))[:-2]
        pointavg_lw = str(round(pointavg_lw, 0))[:-2]

    def FavoritePartner():
        global li_fp_names, li_fp_finishes

        fp = data['favoritePartners'] # fp = Favorite Partner
        li_fp_names = []
        li_fp_finishes = []
        i = 0

        for p in fp:

            fp_name = fp[i]['name']
            fp_finishes = fp[i]['finishes']

            li_fp_names.append(fp_name)
            li_fp_finishes.append(fp_finishes)

            i += 1

        li_fp_names = li_fp_names[:-7]
        li_fp_finishes = li_fp_finishes[:-7]

    def JoinDate():
        global bday, ff_date

        # Bday Checker
        ff_date = data['first_finish']['timestamp']
        ff_date = datetime.fromtimestamp(ff_date) #ff = first finish
        ff_month = ff_date.month
        ff_day = ff_date.day
        ff_date = f'<t:{int(datetime.timestamp(ff_date))}:R>'

        current_year = datetime.now().year
        player_birthday = datetime(current_year, ff_month, ff_day)
        today = datetime.now()

        if today > player_birthday:
            current_year += 1
            player_birthday = datetime(current_year, ff_month, ff_day)

        days_til_bday = today - player_birthday
        days_til_bday = int(str(days_til_bday.days).replace('-', ''))

        if days_til_bday == 0:
            bday = f'`It\'s {player_name}\'s DDNet Birthday today!`'

        else:
            player_birthday = datetime.timestamp(player_birthday)
            bday = f'<t:{int(player_birthday)}:R>'

    def MapStats():
        global categories, li_top5, li_top1, li_maps_fin, li_map_total

        li_top5 = []
        li_top1 = []
        li_maps_fin = []
        li_map_total = []

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
            category = data['types'][cat]
            maps = category['maps']
            map_total = len(maps)

            maps_name = []
            maps_unfin = 0
            maps_fin = 0
            m = 0
            top5 = 0
            top1 = 0 

            for map in maps: # Getting the name of all the maps in x category for later use
                maps_name.append(map)

            for __map__ in maps: # Searches in those maps for details (rank, finishes, etc)
                name = maps_name[m]
                if 'rank' not in maps[name]: # There is no 'rank' key for maps that you have not finished.
                    maps_unfin += 1

                else: # If there is a 'rank' key then you've beaten the map before.
                    maps_fin += 1
                    rank = maps[name]['rank'] # To see what rank you are

                    if rank <= 5: # Checks if you're in the top5
                        top5 += 1

                        if rank == 1: # Checks if you hold the current rank 1
                            top1 += 1
                m += 1

            i += 1
            li_top5.append(top5)
            li_top1.append(top1)
            li_maps_fin.append(maps_fin)
            li_map_total.append(map_total)

    def LastSeen():
        global li_lf_ts, li_lf_map, li_lf_type, types
        types = {
            'Novice' : 'https://ddnet.tw/ranks/novice/',
            'Moderate' : 'https://ddnet.tw/ranks/moderate/',
            'Brutal' : 'https://ddnet.tw/ranks/brutal/',
            'Insane' : 'https://ddnet.tw/ranks/insane/',
            'Dummy' : 'https://ddnet.tw/ranks/dummy/',
            'DDMaX' : 'https://ddnet.tw/ranks/ddmax/',
            'Oldschool' : 'https://ddnet.tw/ranks/oldschool/',
            'Solo' : 'https://ddnet.tw/ranks/solo/',
            'Race' : 'https://ddnet.tw/ranks/race/',
            'Fun' : 'https://ddnet.tw/ranks/fun/',
        }
        lf = data['last_finishes'] # lf = Last Finishes
        li_lf_ts = []
        li_lf_map = []
        li_lf_type = []

        i = 0
        for f in lf:

            lf_ts = lf[i]['timestamp'] # ts = timestamp
            lf_map = lf[i]['map']
            lf_type = lf[i]['type']

            lf_ts = f'<t:{int(lf_ts)}:R>'

            li_lf_ts.append(lf_ts)
            li_lf_map.append(lf_map)
            li_lf_type.append(lf_type)

            i += 1

        li_lf_ts = li_lf_ts[:-7]
        li_lf_map = li_lf_map[:-7]
        li_lf_type = li_lf_type[:-7] 

    PointStats()
    MapStats()
    FavoritePartner()
    JoinDate()
    LastSeen()


class UserProfile(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client

    @client.tree.command(name="profile", description='A summary for a DDNet profile.')
    async def profile(self, interaction: discord.Interaction, player: str):
        global em, player_name
        user = interaction.user
        player_name = player
        player_url = f'https://ddnet.tw/players/{player_name}'

        scrape()
        em = 0
        thumbnail = user.avatar # Avatar that appears in top right of embeds

        em_map = discord.Embed( # Embed initiation for Map Statistics
            title=f'{categories[em]} Map Statistics for {player_name}', 
            description=f'[`{player_name}\'s Profile`]({player_url})',
            timestamp=datetime.now()
            )

        em_map.add_field(name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
        em_map.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
        em_map.add_field(name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
        em_map.add_field(name='World Records:', value=f'{li_top1[em]}', inline=True)
        em_map.set_author(name=f'Reqeusted by {user.name}')
        em_map.set_thumbnail(url=thumbnail)


        em_point = discord.Embed( # Embed initiation for Point Statistics
            title=f'Point Statistics for {player_name}',
            description=f'[`{player_name}\'s Profile`]({player_url})',
            timestamp=datetime.now()
        )

        em_point.add_field(name='Total Points:', value=f'`{points_total}` (Rank: `{points_rank}`)')
        em_point.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
        em_point.add_field(name='Points (30d):', value=f'`{points_lm}`')
        em_point.add_field(name='Points (7d):', value=f'`{points_lw}`')
        em_point.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
        em_point.add_field(name='Avg Points per Day (30d):', value=f'`{pointavg_lm}`')
        em_point.add_field(name='Avg Points per Day (7d):', value=f'`{pointavg_lw}`')
        em_point.set_author(name=f'Reqeusted by {user.name}')
        em_point.set_thumbnail(url=thumbnail)

        em_other = discord.Embed(
            title=f'Misc Statistics for {player_name}',
            description=f'[`{player_name}\'s Profile`]({player_url})',
            timestamp=datetime.now()
        )

        em_other.add_field(name='Joined DDNet:', value=f'{ff_date}')
        em_other.add_field(name='DDBirthday:', value=f'{bday}')

        em_other.add_field(name='Favorite Partners:', value=f'''
        
        1. [`{li_fp_names[0]}`](https://ddnet.tw/players/{li_fp_names[0]}) with `{li_fp_finishes[0]}` finishes.
        2. [`{li_fp_names[1]}`](https://ddnet.tw/players/{li_fp_names[1]}) with `{li_fp_finishes[1]}` finishes.
        3. [`{li_fp_names[2]}`](https://ddnet.tw/players/{li_fp_names[2]}) with `{li_fp_finishes[2]}` finishes.
        
        ''', inline=False)

        em_other.add_field(name='Last Seen:', value=f'''
        
        [[`{li_lf_type[0]}`]({types[li_lf_type[0]]})] [`{player_name}`]({player_url}), playing [`{li_lf_map[0]}`](https://ddnet.tw/maps/{urllib.parse.quote(li_lf_map[0])}) {li_lf_ts[0]}
        [[`{li_lf_type[1]}`]({types[li_lf_type[1]]})] [`{player_name}`]({player_url}), playing [`{li_lf_map[1]}`](https://ddnet.tw/maps/{urllib.parse.quote(li_lf_map[1])}) {li_lf_ts[1]}
        [[`{li_lf_type[2]}`]({types[li_lf_type[2]]})] [`{player_name}`]({player_url}), playing [`{li_lf_map[2]}`](https://ddnet.tw/maps/{urllib.parse.quote(li_lf_map[2])}) {li_lf_ts[2]}


        ''')

        em_other.set_author(name=f'Reqeusted by {user.name}')
        em_other.set_thumbnail(url=thumbnail)

        # Button/Dropdown Initiations. Buttons are for the 'pages', specifically in 'Map Statistics'.
        button1 = (Button(label='<<', style=discord.ButtonStyle.primary)) # Button 1 brings you to the FIRST page
        button2 = (Button(label='<', style=discord.ButtonStyle.primary)) # Button 2 brings you one page back
        button3 = (Button(label='>', style=discord.ButtonStyle.primary)) # Button 3 brings you one page forward
        button4 = (Button(label='>>', style=discord.ButtonStyle.primary)) # Button 4 brings you to the LAST page
        dropdown = Select(
            placeholder='Select what kind of stats you want', # To select between 'Map Statistics', 'Point Statistics', and 'Other Statistics' 
            options=[
                discord.SelectOption(
                    label='Map Statistics',
                    description='Statistics related to maps and map difficulties'
                ),
                discord.SelectOption(
                    label='Point Statistics',
                    description='Statistics related to points and rank/teamrank points.'
                ),
                discord.SelectOption(
                    label='Other Statistics',
                    description='Miscellaneous Statistics, For things like Favorite Parthers, etc'
                )
            ]

        )

        # Disabling first 2 buttons since it starts on page 1. No point in having a button to go back a page if you are on the first page
        button1.disabled = True
        button2.disabled = True

        em = 0

        async def button1_callback(interaction): # Edits the embed to go to the FIRST page. Disables the 'back' buttons and Enables the 'forward' buttons.
            global em
            button1.disabled = True
            button2.disabled = True
            button3.disabled = False
            button4.disabled = False

            em = 0

            em_map.title = f'{categories[em]} Map Statistics for {player_name}'
            em_map.description = f'[`{player_name}\'s Profile`]({player_url})'
            em_map.timestamp = datetime.now()
            em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
            em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
            em_map.set_field_at(index=3, name='World Records:', value=f'{li_top1[em]}', inline=True)

            await interaction.response.edit_message(embed=em_map, view=view)

        async def button2_callback(interaction): # Edits the embed to go back one page. Checks if its on the FIRST page after, and if so, disable the 'back buttons'
            global em

            if em == 1:
                button1.disabled = True
                button2.disabled = True
            else: 
                button2.disabled = False
            button3.disabled = False
            button4.disabled = False

            em -= 1

            em_map.title = f'{categories[em]} Map Statistics for {player_name}'
            em_map.description = f'[`{player_name}\'s Profile`]({player_url})'
            em_map.timestamp = datetime.now()
            em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
            em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
            em_map.set_field_at(index=3, name='World Records:', value=f'{li_top1[em]}', inline=True)

            await interaction.response.edit_message(embed=em_map, view=view)

        async def button3_callback(interaction): # Edits the embed to go forward one page. Checks if its on the LAST page after, and if so, disable the 'forward' buttons
            global em

            if em == 8:
                button3.disabled = True
                button4.disabled = True
            else:
                button3.disabled = False
            button1.disabled = False
            button2.disabled = False

            em += 1

            em_map.title = f'{categories[em]} Map Statistics for {player_name}'
            em_map.description = f'[`{player_name}\'s Profile`]({player_url})'
            em_map.timestamp = datetime.now()
            em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
            em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
            em_map.set_field_at(index=3, name='World Records:', value=f'{li_top1[em]}', inline=True)

            await interaction.response.edit_message(embed=em_map, view=view)

        async def button4_callback(interaction): # Edits the embed to go to the LAST page. Disables the 'forward' buttons and Enables the 'back' buttons.
            global em
            button1.disabled = False
            button2.disabled = False
            button3.disabled = True
            button4.disabled = True

            em = 9

            em_map.title = f'{categories[em]} Map Statistics for {player_name}'
            em_map.description = f'[`{player_name}\'s Profile`]({player_url})'
            em_map.timestamp = datetime.now()
            em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
            em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
            em_map.set_field_at(index=3, name='World Records:', value=f'{li_top1[em]}', inline=True)

            await interaction.response.edit_message(embed=em_map, view=view)

        async def dropdown_callback(interaction): # Changes what type of statistic the user sees.
            if dropdown.values[0] == 'Map Statistics':
                global em
                button2.disabled = True
                button1.disabled = True
                button3.disabled = False
                button4.disabled = False

                em = 0

                em_map.title = f'{categories[em]} Map Statistics for {player_name}'
                em_map.description = f'[`{player_name}\'s Profile`]({player_url})'
                em_map.timestamp = datetime.now()
                em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_maps_fin[em]}/{li_map_total[em]}', inline=False)
                em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_top5[em]}', inline=True)
                em_map.set_field_at(index=3, name='World Records:', value=f'{li_top1[em]}', inline=True)

                await interaction.response.edit_message(embed=em_map, view=view)

            if dropdown.values[0] == 'Point Statistics':
                button1.disabled = True
                button2.disabled = True
                button3.disabled = True
                button4.disabled = True

                await interaction.response.edit_message(embed=em_point, view=view)

            if dropdown.values[0] == 'Other Statistics':
                button1.disabled = True
                button2.disabled = True
                button3.disabled = True
                button4.disabled = True

                await interaction.response.edit_message(embed=em_other, view=view)

        # Callbacks for the Buttons/Dropdown
        button1.callback = button1_callback
        button2.callback = button2_callback
        button3.callback = button3_callback
        button4.callback = button4_callback
        dropdown.callback = dropdown_callback

        view = View() # Making the Buttons/Dropdown actually appear in the message
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        view.add_item(dropdown)

        await interaction.response.send_message(embed=em_map, view=view)
        await asyncio.sleep(150.0) # Waits 2.5 Minutes, then deletes message to clear up spam.
        await interaction.delete_original_message()

async def setup(client): # Adding the class as a cog
    await client.add_cog(UserProfile(client))
