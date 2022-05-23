# Imports. Mostly for the discord bot, but also for Time stuff and Web Scraping.
# NOTE: Currently in progress of making a 'Points Statistics' and 'Other Statistics' pages but the webscraping for it has not been set up yet. So the embed "em_point" just has values set to "UNKNOWN"


from DDToken import token
from bs4 import BeautifulSoup
import requests
import discord
from discord.ui import Button, View, Select
from discord import app_commands
import datetime
import pytz
import asyncio

# Required intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())

tree = app_commands.CommandTree(client)

# Bot Ready Event
@client.event
async def on_ready():
    await tree.sync()
    pst = pytz.timezone('US/Pacific')
    psttime = datetime.datetime.now(pst)
    current_time = psttime.strftime('%I:%M %p PST.')
    print(f"READY: Bot readied at {current_time}")

# Profile command. Web Scrapes the user's profile ( DDNet.tw/players/ ) for stats.
@tree.command(name="profile", description='A summary for a DDNet profile.')
@app_commands.describe(player='Name of the player you want to search for')
async def profile(interaction: discord.Interaction, player: str):
    global em
    user = interaction.user
    player_name = player
    i = 0

    categories = {
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


    # Connects to users profile
    html_text = requests.get(f'https://ddnet.tw/players/{player_name}')
    soup = BeautifulSoup(html_text.content, 'lxml')

    # li = list, fin/fins = finish, cat = category, t1 = top1, t5 = top5. Probably not the best way to go about naming variables but whatever
    li_map_fin = []
    li_map_cat = []
    li_time = []
    li_fins = []
    li_cat_ranks = []
    li_cat_tranks = []
    li_t1 = []
    li_t5 = []

    # Loop for web scraping through all the map categories (Novice, Moderate, etc...)
    while i <= 9:
        li_trank = []
        li_rank = []
        r = 0 # r = rank. Just another iterable like 'i'
        t5 = 0
        t1 = 0


        category = categories[i]


        try:

            difficulty = soup.find('div', class_ = 'block div-ranks', id = f'{category}') # Searches for category
            total_maps = difficulty.find('h3', class_ = 'inline').text.replace('(', '').split(' ')[0] # Searches for how many maps are completed out of the total in current category (e.g 50/100)

        except AttributeError: # Error Handler for invalid profiles
            er = discord.Embed(title='Invalid User!', description=f'```\nMake sure the spelling is 100% correct, and try again.\nName Used: {player_name}\n```', timestamp=datetime.datetime.now())
            await interaction.response.send_message(embed=er, ephemeral=True)
            return

        try:

            maps_finished = difficulty.find('div', style = 'overflow: auto;') # Searches for every map finished in current category
            mapfin_info = maps_finished.find_all('td', class_ = 'rank') # Searches for info in every map (e.g rank, time, finishes, etc...)


            for finfo in mapfin_info: # f = finish, short for finish info. Gathers all the data into lists
                if r == 0:
                    trank = finfo.text # t = team, short for team rank
                    li_trank.append(f'{trank}')
                    r += 1
                elif r == 1:
                    rank = finfo.text
                    li_rank.append(f'{rank}')
                    r += 1
                elif r == 2:
                    time = finfo.text
                    li_time.append(f'{time}')
                    r += 1
                elif r == 3:
                    fins = finfo.text # fins = finishes
                    li_fins.append(f'{fins}')
                    r += 1
                elif r == 4:
                    r = 0


            ranks = 0
            while('' in li_trank): # Removes all the empty strings in team rank list, since maps that dont have a team rank get counted as an empty string
                ranks += 1 # For each empty string removed, it counts it as a T0 rank (since the rank tab on the site counts BOTH T0 Ranks and Team Ranks.)
                li_trank.remove('')

            teamranks = len(li_trank) # Counts all the entries left as team ranks.
            ''.join(li_trank)

            for t in li_rank: # Searches for any Top 5 or Top 1 ranks on each map
                t = int(t.replace('.', ''))
                if t <= 5:
                    t5 += 1
                if t <= 1:
                    t1 += 1

        except AttributeError: # Error handler for when someone has no maps finished in a category
            t5 = 0
            t1 = 0
            ranks = 0
            teamranks = 0

        li_t5.append(t5)
        li_t1.append(t1)
        li_map_fin.append(total_maps)
        li_map_cat.append(category)
        li_cat_ranks.append(ranks)
        li_cat_tranks.append(teamranks)

        i += 1
    i = 0

    userava = user.avatar # Avatar that appears in top right of embeds
    
    em_map = discord.Embed( # Embed initiation for Map Statistics
        title=f'{categories[i]} Map Statistics for {player_name}', 
        description=f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})', 
        timestamp=datetime.datetime.now()
        )

    em_map.add_field(name=f'{categories[i]} Maps Completed:', value=f'{li_map_fin[i]}', inline=False)
    em_map.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
    em_map.add_field(name='Global Top 5s:', value=f'{li_t5[i]}', inline=True)
    em_map.add_field(name='World Records:', value=f'{li_t1[i]}', inline=True)
    em_map.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
    em_map.add_field(name='Team Ranks:', value=f'{li_cat_tranks[i]}', inline=True)
    em_map.add_field(name='Team 0 Ranks:', value=f'{li_cat_ranks[i]}', inline=True)
    em_map.set_author(name=f'Reqeusted by {user.name}')
    em_map.set_thumbnail(url=userava)


    em_point = discord.Embed( # Embed initiation for Point Statistics
        title=f'Point Statistics for {player_name}',
        description=f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})',
        timestamp=datetime.datetime.now()
    )

    em_point.add_field(name='Total Points:', value='UNKNOWN (Rank: UNKNOWN)')
    em_point.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
    em_point.add_field(name='Points (365d):', value='UNKNOWN')
    em_point.add_field(name='Points (7d):', value='UNKNOWN')
    em_point.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
    em_point.add_field(name='Avg Points per Day (365d):', value='UNKNOWN')
    em_point.add_field(name='Avg Points per Day (7d):', value='UNKNOWN')

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
                description='Statistics related to maps and map difficulties',
                default=True
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

    async def button1_callback(interaction): # Edits the embed to 'go back' to the FIRST page. Disables the 'back' buttons and Enables the 'forward' buttons.
        global em
        button1.disabled = True
        button2.disabled = True
        button3.disabled = False
        button4.disabled = False

        em = 0

        em_map.title = f'{categories[em]} Map Statistics for {player_name}'
        em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
        em_map.timestamp = datetime.datetime.now()
        em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_map_fin[em]}', inline=False)
        em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_t5[em]}', inline=True)
        em_map.set_field_at(index=3, name='World Records:', value=f'{li_t1[em]}', inline=True)
        em_map.set_field_at(index=5, name='Team Ranks:', value=f'{li_cat_tranks[em]}', inline=True)
        em_map.set_field_at(index=6, name='Team 0 Ranks:', value=f'{li_cat_ranks[em]}', inline=True)

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
        em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
        em_map.timestamp = datetime.datetime.now()
        em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_map_fin[em]}', inline=False)
        em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_t5[em]}', inline=True)
        em_map.set_field_at(index=3, name='World Records:', value=f'{li_t1[em]}', inline=True)
        em_map.set_field_at(index=5, name='Team Ranks:', value=f'{li_cat_tranks[em]}', inline=True)
        em_map.set_field_at(index=6, name='Team 0 Ranks:', value=f'{li_cat_ranks[em]}', inline=True)

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
        em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
        em_map.timestamp = datetime.datetime.now()
        em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_map_fin[em]}', inline=False)
        em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_t5[em]}', inline=True)
        em_map.set_field_at(index=3, name='World Records:', value=f'{li_t1[em]}', inline=True)
        em_map.set_field_at(index=5, name='Team Ranks:', value=f'{li_cat_tranks[em]}', inline=True)
        em_map.set_field_at(index=6, name='Team 0 Ranks:', value=f'{li_cat_ranks[em]}', inline=True)

        await interaction.response.edit_message(embed=em_map, view=view)

    async def button4_callback(interaction): # Edits the embed to go to the LAST page. Disables the 'forward' buttons and Enables the 'back' buttons.
        global em
        button1.disabled = False
        button2.disabled = False
        button3.disabled = True
        button4.disabled = True

        em = 9

        em_map.title = f'{categories[em]} Map Statistics for {player_name}'
        em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
        em_map.timestamp = datetime.datetime.now()
        em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_map_fin[em]}', inline=False)
        em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_t5[em]}', inline=True)
        em_map.set_field_at(index=3, name='World Records:', value=f'{li_t1[em]}', inline=True)
        em_map.set_field_at(index=5, name='Team Ranks:', value=f'{li_cat_tranks[em]}', inline=True)
        em_map.set_field_at(index=6, name='Team 0 Ranks:', value=f'{li_cat_ranks[em]}', inline=True)

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
            em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
            em_map.timestamp = datetime.datetime.now()
            em_map.set_field_at(index=0, name=f'{categories[em]} Maps Completed:', value=f'{li_map_fin[em]}', inline=False)
            em_map.set_field_at(index=2, name='Global Top 5s:', value=f'{li_t5[em]}', inline=True)
            em_map.set_field_at(index=3, name='World Records:', value=f'{li_t1[em]}', inline=True)
            em_map.set_field_at(index=5, name='Team Ranks:', value=f'{li_cat_tranks[em]}', inline=True)
            em_map.set_field_at(index=6, name='Team 0 Ranks:', value=f'{li_cat_ranks[em]}', inline=True)

            await interaction.response.edit_message(embed=em_map, view=view)

        if dropdown.values[0] == 'Point Statistics':
            button1.disabled = True
            button2.disabled = True
            button3.disabled = True
            button4.disabled = True

            await interaction.response.edit_message(embed=em_point, view=view)

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



client.run(token)