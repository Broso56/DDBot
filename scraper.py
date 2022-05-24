import requests # To connect to site
import urllib.parse # To convert text to user encoded url (e.g a space is now '%20')
#from cmdprofile import player_name


li_top5 = []
li_top1 = []
li_maps_fin = []
li_map_total = []


def scrape(): # To get data from ddnet.tw's JSON API
    player_name = 'Shinoa' # Testing purposes, player_name is likely to be imported from cmdprofile.py 
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
        print(f'{cat} Finished: {maps_fin}/{map_total}\nTop5s: {top5}\nTop1s: {top1}') # For testing if the scraping was working

        li_top5.append(top5)
        li_top1.append(top1)
        li_maps_fin.append(maps_fin)
        li_map_total.append(map_total)

        i += 1

scrape()