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
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Creating Discord Client and grabbing token
token = open('/home/pi/Desktop/token').read()
age = {'birthtime': '283993201', 'mature_content': '1'}
client = commands.Bot(command_prefix='!cake', description="Type !cakeask in chat for a list of commands and more info.")


async def tryget(url, c):
    async with aiohttp.ClientSession(cookies=c) as cs:
        async with cs.get(url) as doc:
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
        self.id = None
        self.nurl = None
        self.last = None
        self.news = []
        self.found = None
        self.message = None

    async def acquire(self):
        storepage = await tryget(self.url, age)
        storesoup = Soup(storepage, 'html.parser')
        self.name = storesoup.find('div', {'class': 'apphub_AppName'}).text
        self.id = self.url.split('/')[4]
        self.nurl = 'https://store.steampowered.com/news/?appids=' + self.id

    def fetchjson(self):
        with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
            updatesdict = json.load(updates)
        self.last = (updatesdict[self.url])

    async def parse(self):
        newspage = await tryget(self.nurl, age)
        newssoup = Soup(newspage, 'html.parser')
        for block in newssoup('div', {'class': 'newsPostBlock'}):
            if 'newsPostBlock' in block['class']:
                self.news.append(block)
        self.found = self.news[0].find('a').text

    async def trigger(self):
        if self.found != self.last:
            line1 = "**New announcement from " + self.name + ":**\n"
            line2 = "'" + self.found + "'" + "\n"
            line3 = "<" + self.nurl + ">"
            self.message = line1 + line2 + line3
            with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
                updatesdict = json.load(updates)
            updatesdict[self.url] = self.found
            with open('/home/pi/Desktop/Trig-Cake/updates.json', 'w') as newupdates:
                json.dump(updatesdict, newupdates)
            with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await client.send_message(discord.Object(id=channel), self.message)


@client.command()
async def ask():
    info = """**I'm tasked with checking Steam games for announcements.**
The following commands are available for users with Administrator perms (minus brackets):
**!cakesub <url of store page>** — Subscribes channel to a game.
**!cakeunsub <url of store page>** — Unsubscribes channel to a game."""
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
            storepage = await tryget(url, age)
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
                    await client.send_message(ctx.message.channel, "Channel is now subscribed to " + gamename + "!")


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


async def background_loop():
    await client.wait_until_ready()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    currentgames = []

    while not client.is_closed:
        with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
            steamdict = json.load(steam)
        for keys in steamdict.keys():
            if keys not in currentgames:
                currentgames.append(keys)
        for url in currentgames:
            splices = url.split('/')
            appid = splices[3] + splices[4]
            vars()[appid] = SteamApp(url)
            await vars()[appid].acquire()
            await vars()[appid].parse()
            vars()[appid].fetchjson()
            await vars()[appid].trigger()

        print("looped")
        await asyncio.sleep(60*5)


client.loop.create_task(background_loop())
client.run(token)
