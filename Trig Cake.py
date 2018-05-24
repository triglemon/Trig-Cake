#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import urllib.request
import json


# Creating Discord Client and grabbing token
client = discord.Client()
token = open('token').read()


class SteamApp:

    # Each game is represented by a Game object
    def __init__(self, url):
        self.url = url
        with urllib.request.urlopen(url) as doc:
            storepage = doc.read()
        storesoup = Soup(storepage, 'html.parser')
        self.name = storesoup.find('div', {'class': 'apphub_AppName'}).text
        self.id = url.split('/')[4]
        self.nurl = 'https://store.steampowered.com/news/?appids=' + self.id
        self.last = None
        self.news = None
        self.found = None

    def fetchjson(self, channelid):
        with open('steam.json') as file:
            steamdict = json.load(file)
        self.last = (steamdict[channelid])

    def parse(self):
        with urllib.request.urlopen(self.nurl) as doc:
            newspage = doc.read()
        newssoup = Soup(newspage, 'html.parser')
        self.news = newssoup('div', class_='newsPostBlock rps')
        self.found = self.news[0].find('a').text

    def trigger(self):
        pass



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


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
        print(url)
        if prefix not in url:
            await client.send_message(message.channel, "Not a valid url.")
        else:
            with urllib.request.urlopen(url) as doc:
                storepage = doc.read()
            storesoup = Soup(storepage, 'html.parser')
            metatag = storesoup.find('meta', {'property': 'og:url'})
            urlcheck = metatag['content']
            if urlcheck == 'https://store.steampowered.com/':
                await client.send_message(message.channel, "Game does not exist")
            else:
                with open('steam.json', 'w+') as file:
                    dict = json.load(file)
                if url not in dict:
                    dict[url] = []
                if id in dict[url]:
                    await client.send_message(message.channel, "Channel already subscribed to game.")
                else:
                    dict[url].append(id)
                    gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                    await client.send_message(message.channel, "Channel is now subscribed to " + gamename + "!")

        await client.send_message(message.channel, "Added")



client.run(token)
