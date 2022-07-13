# NFT OPENSEA FLOOR DISCORD NOTIFIER

Function of this bot includes 
1. notifying its user when the floor price of an NFT reaches a specified threshold by its user 
2. checking of the floor price of a collection
3. saving a list of slug of the collection the user is interested in

Features of the bot includes:
1. Checking the vaidity of the slug to make sure only valid and the right collections are being monitored
2. Checking that price target set by user is not equal to the current floor price of the collection the user is interested in monitoring
3. Checking that the commands issued are correect

Limitations of the bot:
1. Using opensea pubilc API with a rate limit of 4 requests per second and the actual rate limit is lower than that
2. Not compatible with multiple users at the moment
3. List of monitored collections and list of slugs user is interested in are not saved once program stops running

# HOW TO USE BOT - COMMANDS

To greet bot:
!hello

To monitor collections:
!add {slug} {price target}
e.g. !add hapeprime 1

To remove monitored collections:
!dlt (slug}
e.g. !dlt hapeprime

To view your monitored collections:
$view

To save slugs to your personalised list:
!save {slug}
e.g. !save hapeprime

To remove collections from personalised list:
!rmv (slug}
e.g. !rmv hapeprime

To view your personalised list:
!list

To check the live floor price of a collection:
!check {slug}
e.g. !check hapeprime 

# TOKENS.PY
TOKEN refers to the discord token of your discord bot 
channel_id refers to the ID of the channel you want the alerts to be sent to (turn on developer mode in order to copy channel id)
