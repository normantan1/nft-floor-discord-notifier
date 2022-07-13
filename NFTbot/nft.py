import discord, requests
from tokens import TOKEN,channel_id
import json
from discord.ext import tasks


slug_price_increase = {} #dictionary of slugs where price target of collection is higher than the current floor price
slug_price_decrease = {} #dictionary of slugs where price target of collection is lower than the current floor price
list = [] #list of slugs user is interested in

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    if not ping.is_running(): #prevents RuntimeError: Task is already launched and is not completed
        ping.start()
    
@tasks.loop(seconds= 3) # time cannot be set too low to prevent being rate limited by openseaa public api
async def ping(): #task repeats every 3 seconds to check if floor has reached the specified threshold set by the user

    channel = client.get_channel(channel_id)

    for slug in slug_price_decrease.copy(): # .copy prevents RuntimeError: dictionary changed size during iteration
        curr_floor = check_floor(slug)
        if slug_price_decrease[slug] >= curr_floor:
            await channel.send(f'{slug} has reached your price target of {curr_floor}')
            del slug_price_decrease[slug]


    for slug in slug_price_increase.copy():
        curr_floor = check_floor(slug)
        if slug_price_increase[slug] <= curr_floor:
            await channel.send(f'{slug} has reached your price target of {curr_floor}')
            del slug_price_increase[slug]


@client.event
async def on_message(message):

    if message.author == client.user: #prevents message from bot from triggering command
        return
    

    if message.content.startswith('!hello'):
        await message.reply(f"Hello {message.author.name}")
        

    if message.content.startswith('!add'):
        user = message.author.id
        slug_price = message.content.split()
        

        if len(slug_price) == 3:

            slug = slug_price[1]
            price = slug_price[2]

            #check that the price target is a number
            if check_float(price) == True:
                
                price = float(price)
            
                #check that slug is valid and that collection has activity
                if check_slug_validity(slug) == False or check_floor_validity(slug) == False:
                    await message.channel.send('Slug is invalid, please try again.')
                    pass

                else:
                    curr_floor = check_floor(slug)
                    
                    #check to make sure floor is not equal to price target
                    if curr_floor == price:
                        await message.channel.send('Price target is same as current price, please set a valid price target.')
                        pass
                

                    elif slug in slug_price_decrease or slug in slug_price_increase:
                        if slug in slug_price_increase:
                            del slug_price_increase[slug]
                        
                        if slug in slug_price_decrease:
                            del slug_price_decrease[slug]
                            
                        if price < curr_floor:
                            slug_price_decrease[slug] = price
                            print(slug_price_decrease)
                            await message.channel.send(f"Collection '{slug}' price target has been successfully updated")
                        else:
                            slug_price_increase[slug] = price
                            print(slug_price_increase)
                            await message.channel.send(f"Collection '{slug}' price target has been successfully updated")
                        
                    else:
                        if price < curr_floor:
                            slug_price_decrease[slug] = price
                            print(slug_price_decrease)
                            await message.channel.send(f"Collection '{slug}' is being monitored")
                        else:
                            slug_price_increase[slug] = price
                            print(slug_price_increase)
                            await message.channel.send(f"Collection '{slug}' is being monitored")
            
            else:
                await message.channel.send("Please follow this format '!add {Slug} {Price target}'")


        
        else:
            await message.channel.send("Please follow this format '!add {Slug} {Price target}'")
        

    if message.content.startswith('!dlt'):

        delete = message.content.split()
    
        if len(delete) == 2:
            slug = delete[1]

            if slug in slug_price_decrease:
                del slug_price_decrease[slug]
                await message.channel.send(f'{slug} has been successfully removed from the monitored list')

            if slug in slug_price_increase:
                del slug_price_increase[slug]
                await message.channel.send(f'{slug} has been successfully removed from the monitored list')

            else:
                await message.channel.send(f'{slug} is not being monitored')
        
        else:
            await message.channel.send("Please follow this format !dlt {slug}")

        

    if message.content.startswith('!view'):

        total_slug = Merge(slug_price_increase,slug_price_decrease)

        if len(total_slug) == 0:
            await message.channel.send('You are not monitoring any collection')
            
        else:
            await message.channel.send(total_slug)

    if message.content.startswith('!check'):

        check = message.content.split()
        slug = check[1]

        if len(check) == 2:

            if check_slug_validity(slug) == False or check_floor_validity(slug) == False:
                await message.channel.send("Please input a valid slug")
                pass

            else:
                price = check_floor(slug)
                await message.channel.send(f'{slug} floor price is {price} ethereum') 

        else:
            await message.channel.send("Please follow this format !check {slug}")

    if message.content.startswith('!save'):

        save = message.content.split()
        slug = save[1]

        if len(save) == 2:

            if check_slug_validity(slug) == False or check_floor_validity(slug) == False:
                await message.channel.send("Please input a valid slug")
                pass

            else:
                list.append(slug)
                await message.channel.send(f'{slug} has been added to the saved list') 

        else:
            await message.channel.send("Please follow this format !check {slug}")

    
    if message.content.startswith('!list'):
        if len(list) == 0:
            await message.channel.send('You do not have any collection in your list')
        else:
            await message.channel.send(list)

    if message.content.startswith('!rmv'):

        delete = message.content.split()
    
        if len(delete) == 2:
            slug = delete[1]

            if slug in list:
                list.remove(slug)
                await message.channel.send(f'{slug} has been successfully removed from the personalised list')


            else:
                await message.channel.send(f'{slug} is not found in personalised list')
        
        else:
            await message.channel.send("Please follow this format !rmv {slug}")



    if not message.content.startswith('!'):
        await message.channel.send('Please check pinned message on how to interact with the bot')




def check_slug_validity(slug): #check slug exists

    url = f'https://api.opensea.io/api/v1/collection/{slug}/stats'

    response = requests.get(url)

    response = response.text

    if "false" in response:
        return False



def check_floor_validity(slug): #check that collection has a floor price and has activty as there are some dead collections that have slugs

    url = f'https://api.opensea.io/api/v1/collection/{slug}/stats'

    response = requests.get(url)

    response = response.text

    res = json.loads(response)

    floor = res['stats']['average_price']

    if floor == 0.0:
        return False


def check_float(price):
    try:
        float(price)
        return True
    except ValueError:
        return False
        


def check_floor(slug):

    url = f'https://api.opensea.io/api/v1/collection/{slug}/stats'

    response = requests.get(url)

    response = response.text

    res = json.loads(response)

    floor = res['stats']['floor_price']

    return floor


def Merge(dict1, dict2):
    res = dict1 | dict2
    return res


try:
    client.run(TOKEN)
except Exception as e:
    print('Unable to connect to discord client')
