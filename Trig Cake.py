#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import requests
import json


# Creating Discord Client and grabbing token
client = discord.Client()
token = open('token').read()
age = {'birthtime': '283993201', 'mature_content': '1'}


class SteamApp:

    # Each game is represented by a Game object
    def __init__(self, url):
        self.url = url
        with requests.get(url, cookies=age) as doc:
            storepage = doc.content
        storesoup = Soup(storepage, 'html.parser')
        self.name = storesoup.find('div', {'class': 'apphub_AppName'}).text
        self.id = url.split('/')[4]
        self.nurl = 'https://store.steampowered.com/news/?appids=' + self.id
        self.last = None
        self.news = []
        self.found = None
        self.message = None

    def fetchjson(self):
        with open('updates.json') as updates:
            updatesdict = json.load(updates)
        self.last = (updatesdict[self.name])

    def parse(self):
        with requests.get(self.nurl, cookies=age) as doc:
            newspage = doc.content
        newssoup = Soup(newspage, 'html.parser')
        for block in newssoup('div', {'class': 'newsPostBlock'}):
            if 'newsPostBlock' in block['class']:
                self.news.append(block)
        self.found = self.news[0].find('a').text

    async def trigger(self):
        if self.found != self.last:
            line1 = "**New announcement from" + self.name + ":**\n"
            line2 = "'" + self.found + "'" + "\n"
            line3 = "<" + self.nurl + ">"
            self.message = line1 + line2 + line3
            with open('updates.json') as updates:
                updatesdict = json.load(updates)
            updatesdict[self.name] = self.found
            with open('updates.json', 'w') as newupdates:
                json.dump(updatesdict, newupdates)
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await client.send_message(discord.Object(id=channel), self.message)


@client.event
async def on_message(message):

    if message.content.startswith('!cake'):
        info = """**I'm tasked with checking Steam games for announcements.**
The following commands are available at your perusal (minus brackets):
**!add <url of store page>** — Subscribes channel to a game
**!remove <url of store page>** — Unsubscribes channel to a game"""
        await client.send_message(message.channel, info)

    if message.content.startswith('!add'):
        id = message.channel.id
        url = message.content.replace('!add ', "")
        prefix = 'https://store.steampowered.com/app/'

        if prefix not in url:
            await client.send_message(message.channel, "Not a valid url.")

        else:
            with requests.get(url, cookies=age) as doc:
                storepage = doc.content
            storesoup = Soup(storepage, 'html.parser')
            metatag = storesoup.find('meta', {'property': 'og:url'})
            urlcheck = metatag['content']

            if urlcheck == 'https://store.steampowered.com/':
                await client.send_message(message.channel, "Game does not exist")

            else:
                with open('steam.json') as steam:
                    steamdict = json.load(steam)

                    if url not in steamdict:
                        steamdict[url] = []
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        newgame = SteamApp(url)
                        newgame.parse()
                        with open('updates.json') as updates:
                            updatesdict = json.load(updates)
                            updatesdict[newgame.name] = newgame.found
                        with open('updates.json', 'w') as newupdates:
                            json.dump(updatesdict, newupdates)

                    if id in steamdict[url]:
                        await client.send_message(message.channel, "Channel already subscribed to game.")

                    else:
                        steamdict[url].append(id)
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                        await client.send_message(message.channel, "Channel is now subscribed to " + gamename + "!")


@client.event
async def background_loop():
    await client.wait_until_ready()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    currentgames = []

    while not client.is_closed:
        with open('steam.json') as steam:
            steamdict = json.load(steam)
        for keys in steamdict.keys():
            if keys not in currentgames:
                currentgames.append(keys)
        for url in currentgames:
            splices = url.split('/')
            appid = splices[3] + splices[4]
            vars()[appid] = SteamApp(url)
            vars()[appid].parse()
            vars()[appid].fetchjson()
            await vars()[appid].trigger()

        print("looped")
        await asyncio.sleep(60*5)


client.loop.create_task(background_loop())
client.run(token)
