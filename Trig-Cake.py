#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import aiohttp
import json


# Creating Discord Client and grabbing token
client = discord.Client()
token = open('/home/pi/Desktop/token').read()
age = {'birthtime': '283993201', 'mature_content': '1'}


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


@client.event
async def on_message(message):

    if message.content.startswith('!cake'):
        typocheck = message.content.replace("!cake", "")
        if len(typocheck) == 0:
            info = """**I'm tasked with checking Steam games for announcements.**
The following commands are available for users with Administrator perms (minus brackets):
**!cakesub <url of store page>** — Subscribes channel to a game.
**!cakeunsub <url of store page>** — Unsubscribes channel to a game."""
            await client.send_message(message.channel, info)

    if message.content.startswith('!cakesub'):
        if message.author.server_permissions.administrator:
            channelid = message.channel.id
            url = message.content.replace('!cakesub ', "")
            prefix = 'https://store.steampowered.com/app/'

            if prefix not in url:
                await client.send_message(message.channel, "Not a valid url.")

            else:
                storepage = await tryget(url, age)
                storesoup = Soup(storepage, 'html.parser')
                metatag = storesoup.find('meta', {'property': 'og:url'})
                urlcheck = metatag['content']

                if urlcheck == 'https://store.steampowered.com/':
                    await client.send_message(message.channel, "Game does not exist.")

                else:
                    with open('/home/pi/Desktop/Trig-Cake/steam.json') as steam:
                        steamdict = json.load(steam)

                    if url not in steamdict:
                        steamdict[url] = []
                        with open('/home/pi/Desktop/Trig-Cake/steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        newgame = SteamApp(url)
                        newgame.parse()
                        with open('/home/pi/Desktop/Trig-Cake/updates.json') as updates:
                            updatesdict = json.load(updates)
                        updatesdict[newgame.url] = newgame.found
                        with open('/home/pi/Desktop/Trig-Cake/updates.json', 'w') as newupdates:
                            json.dump(updatesdict, newupdates)

                    if channelid in steamdict[url]:
                        await client.send_message(message.channel, "Channel is already subscribed to game.")

                    else:
                        steamdict[url].append(channelid)
                        with open('/home/pi/Desktop/Trig-Cake/steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                        await client.send_message(message.channel, "Channel is now subscribed to " + gamename + "!")

    if message.content.startswith('!cakeunsub'):
        if message.author.server_permissions.administrator:
            url = message.content.replace('!cakeunsub ', "")
            channelid = message.channel.id
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

                    await client.send_message(message.channel, "Channel is now unsubscribed from that game.")
                else:
                    await client.send_message(message.channel, "Channel is not subscribed to that game.")
            else:
                await client.send_message(message.channel, "Channel is not subscribed to that game.")


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
            vars()[appid].parse()
            vars()[appid].fetchjson()
            await vars()[appid].trigger()

        print("looped")
        await asyncio.sleep(60*5)


client.loop.create_task(background_loop())
client.run(token)
