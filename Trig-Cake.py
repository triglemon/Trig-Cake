#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import aiohttp
import json
from discord.ext import commands
import logging


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='/home/pi/Desktop/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

age = {'birthtime': '283993201', 'mature_content': '1'}
aiosess = aiohttp.ClientSession(cookies=age)
client = commands.Bot(command_prefix='!cake', description="Type !cakeask in chat for a list of commands and more info.")


async def tryget(url, session):
    async with session.get(url) as doc:
        while True:
            if doc.status == 200:
                break
            await asyncio.sleep(5)
        return await doc.text()


class SteamApp:

    # Each game is represented by a SteamApp object
    def __init__(self, url):
        self.url = url
        self.name = None
        self.nurl = None
        self.last = None
        self.news = None
        self.found = None
        self.soup = None

    def fetchjson(self):
        with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
            updatesdict = json.load(updates)
        self.last = (updatesdict[self.url])

    async def acquire(self):
        storepage = await tryget(self.url, aiosess)
        self.soup = Soup(storepage, 'html.parser')
        self.name = self.soup.find('div', {'class': 'apphub_AppName'}).text
        gameid = self.url.split('/')[4]
        self.nurl = 'https://store.steampowered.com/news/?appids=' + gameid

    async def parse(self):
        newspage = await tryget(self.nurl, aiosess)
        newssoup = Soup(newspage, 'html.parser')
        news = newssoup.find('div', {'class': 'newsPostBlock'})
        self.found = news.find('a').text

    async def trigger(self):
        if self.found != self.last:
            message = f"""**New announcement from {self.name}:**
'{self.found}'
<{self.nurl}>"""
            with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
                updatesdict = json.load(updates)
            updatesdict[self.url] = self.found
            with open('/home/pi/Desktop/Trig-Cake/updates.json', 'w') as newupdates:
                json.dump(updatesdict, newupdates)
            with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await client.send_message(discord.Object(id=channel), message)

    async def saletrigger(self):
        with open('/home/pi/Desktop/Trig-Cake/sale.json') as sale:
            saledict = json.load(sale)
        tagline = self.soup.find('title').text
        check = self.name + ' on Steam'
        if saledict[self.url] == 'False' and len(tagline.replace(check, '')) != 0:
            splices = tagline.split(' ')
            message = f"""**{self.name} is one sale for {splices[1]} off!** :fire: :moneybag:
<{self.url}>"""
            saledict[self.url] = 'True'
            with open('/home/pi/Desktop/Trig-Cake/sale.json', 'w') as newsale:
                json.dump(saledict, newsale)
            with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await client.send_message(discord.Object(id=channel), message)
        if saledict[self.url] == 'True' and len(tagline.replace(check, '')) == 0:
            saledict[self.url] = 'False'
            with open('/home/pi/Desktop/Trig-Cake/sale.json', 'w') as newsale:
                json.dump(saledict, newsale)


@client.command()
async def ask():
    info = """**I'm tasked with checking Steam games for announcements.**
The following commands are available for users with Administrator perms (minus brackets):
**!cakesub <url of store page>** — Subscribes channel to a game.
**!cakeunsub <url of store page>** — Unsubscribes channel to a game.
**!cakesubbed** — Prints list of games the channel is subscribed to."""
    await client.say(info)


@client.command(pass_context=True)
async def sub(ctx, link):
    if ctx.message.author.server_permissions.administrator:
        channelid = ctx.message.channel.id
        url = link
        prefix = 'https://store.steampowered.com/app/'
        if prefix not in url:
            await client.send_message(ctx.message.channel, "Not a valid url.")
        else:
            storepage = await tryget(url, aiosess)
            storesoup = Soup(storepage, 'html.parser')
            metatag = storesoup.find('meta', {'property': 'og:url'})
            urlcheck = metatag['content']
            if urlcheck == 'https://store.steampowered.com/':
                await client.send_message(ctx.message.channel, "Game does not exist.")
            else:
                with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
                    steamdict = json.load(steam)
                if url not in steamdict:
                    steamdict[url] = []
                    with open('/home/pi/Desktop/Trig-Cake/steam.json', 'w') as newsteam:
                        json.dump(steamdict, newsteam)
                    newgame = SteamApp(url)
                    await newgame.acquire()
                    await newgame.parse()
                    with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
                        updatesdict = json.load(updates)
                    updatesdict[newgame.url] = newgame.found
                    with open('/home/pi/Desktop/Trig-Cake/updates.json', 'w') as newupdates:
                        json.dump(updatesdict, newupdates)
                if channelid in steamdict[url]:
                    await client.send_message(ctx.message.channel, "Channel is already subscribed to game.")
                else:
                    steamdict[url].append(channelid)
                    with open('/home/pi/Desktop/Trig-Cake/steam.json', 'w') as newsteam:
                        json.dump(steamdict, newsteam)
                    gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                    await client.send_message(ctx.message.channel, f"Channel is now subscribed to {gamename}!")


@client.command(pass_context=True)
async def unsub(ctx, link):
    if ctx.message.author.server_permissions.administrator:
        url = link
        channelid = ctx.message.channel.id
        with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
            steamdict = json.load(steam)
        if url in steamdict:
            if channelid in steamdict[url]:
                steamdict[url].remove(channelid)
                if len(steamdict[url]) == 0:
                    del steamdict[url]
                    with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
                        updatesdict = json.load(updates)
                    del updatesdict[url]
                    with open('/home/pi/Desktop/Trig-Cake/updates.json', 'w') as newupdates:
                        json.dump(updatesdict, newupdates)
                with open('/home/pi/Desktop/Trig-Cake/steam.json', 'w') as newsteam:
                    json.dump(steamdict, newsteam)

                await client.send_message(ctx.message.channel, "Channel is now unsubscribed from that game.")
            else:
                await client.send_message(ctx.message.channel, "Channel is not subscribed to that game.")
        else:
            await client.send_message(ctx.message.channel, "Channel is not subscribed to that game.")


@client.command(pass_context=True)
async def subbed(ctx):
    channelid = ctx.message.channel.id
    with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
        steamdict = json.load(steam)
    subbedlist = [url for url in steamdict if channelid in steamdict[url]]
    if len(subbedlist) == 0:
        await client.send_message(ctx.message.channel, "Channel is not subscribed to any games.")
    else:
        message = "This channel is subbed to:  "
        for url in subbedlist:
            storepage = await tryget(url, aiosess)
            storesoup = Soup(storepage, 'html.parser')
            gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
            message += (gamename + ',  ')
        message = message[:-3] + '.'
        await client.send_message(ctx.message.channel, message)


# Debug stuff
@client.command(pass_context=True)
async def last(ctx, url):
    stm = SteamApp(url)
    stm.fetchjson()
    await client.send_message(ctx.message.channel, stm.last)


@client.command(pass_context=True)
async def found(ctx, url):
    stm = SteamApp(url)
    await stm.acquire()
    await stm.parse()
    await client.send_message(ctx.message.channel, stm.found)


async def background_loop():
    await client.wait_until_ready()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    while not client.is_closed:
        with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
            steamdict = json.load(steam)
        for url in steamdict:
            splices = url.split('/')
            appid = splices[3] + splices[4]
            vars()[appid] = SteamApp(url)
            await vars()[appid].acquire()
            await vars()[appid].parse()
            vars()[appid].fetchjson()
            await vars()[appid].trigger()
            await vars()[appid].saletrigger()

        print("looped")
        await asyncio.sleep(60*5)


client.loop.create_task(background_loop())
with open('/home/pi/Desktop/token') as file:
    token = file.read()
client.run(token)
