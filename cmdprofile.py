import discord #testing testing
from discord.ui import Button, View, Select
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio
import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')

intents = discord.Intents.default() # Required intent stuff
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="^", help_command=None, case_insensitive=True, intents=intents.all())

class UserProfile(commands.Cog): # Cog initiation
    def __init__(self, client):
        self.client = client

    @client.tree.command(name="profile", description='A summary for a DDNet profile.')
    async def profile(self, interaction: discord.Interaction, player: str):
        global em
        user = interaction.user
        player_name = player

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

        player_url = urllib.parse.quote(player_name) # Converts text to user encoded url
        url = f'https://ddnet.tw/players/?json2={player_url}'

        data = requests.get(url).json()
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

            # Getting the name of all the maps in x category for later use
            for map in maps:
                maps_name.append(map)

            # Searches in those maps for details (rank, finishes, etc)
            for __map__ in maps:
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
            print(f'{cat} Finished: {maps_fin}/{map_total}\nTop5s: {top5}\nTop1s: {top1}') # For testing if the scraping works

            li_top5.append(top5)
            li_top1.append(top1)
            li_maps_fin.append(maps_fin)
            li_map_total.append(map_total)

            i += 1


        i = 0
        userava = user.avatar # Avatar that appears in top right of embeds

        em_map = discord.Embed( # Embed initiation for Map Statistics
            title=f'{categories[i]} Map Statistics for {player_name}', 
            description=f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})',
            timestamp=datetime.datetime.now()
            )

        em_map.add_field(name=f'{categories[i]} Maps Completed:', value=f'{li_maps_fin[i]}/{li_map_total[i]}', inline=False)
        em_map.add_field(name='\u200B', value='\u200B', inline=False) # Invisible Field
        em_map.add_field(name='Global Top 5s:', value=f'{li_top5[i]}', inline=True)
        em_map.add_field(name='World Records:', value=f'{li_top1[i]}', inline=True)
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
            em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
            em_map.timestamp = datetime.datetime.now()
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
            em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
            em_map.timestamp = datetime.datetime.now()
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
            em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
            em_map.timestamp = datetime.datetime.now()
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
                em_map.description = f'[{player_name}\'s Profile](https://ddnet.tw/players/{player_name})'
                em_map.timestamp = datetime.datetime.now()
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
