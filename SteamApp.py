import json
from bs4 import BeautifulSoup as Soup
from tryget import tryget
import discord


class SteamApp:

    def __init__(self, url, client):
        self.url = url
        self.name = None
        self.nurl = None
        self.last = None
        self.news = None
        self.found = None
        self.soup = None
        self.client = client

    def fetchjson(self):
        with open('updates.json') as updates:
            updatesdict = json.load(updates)
        self.last = (updatesdict[self.url])

    async def acquire(self):
        storepage = await tryget(self.url)
        self.soup = Soup(storepage, 'html.parser')
        self.name = self.soup.find('div', {'class': 'apphub_AppName'}).text
        gameid = self.url.split('/')[4]
        self.nurl = 'https://store.steampowered.com/news/?appids=' + gameid

    async def parse(self):
        newspage = await tryget(self.nurl)
        newssoup = Soup(newspage, 'html.parser')
        news = newssoup.find('div', {'class': 'newsPostBlock'})
        self.found = news.find('a').text

    async def trigger(self):
        if self.found != self.last:
            message = f"""**New announcement from {self.name}:**
'{self.found}'
<{self.nurl}>"""
            with open('updates.json') as updates:
                updatesdict = json.load(updates)
            updatesdict[self.url] = self.found
            with open('updates.json', 'w') as newupdates:
                json.dump(updatesdict, newupdates)
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await self.client.send_message(discord.Object(id=channel), message)

    async def saletrigger(self):
        with open('sale.json') as sale:
            saledict = json.load(sale)
        tagline = self.soup.find('title').text
        check = self.name + ' on Steam'
        if saledict[self.url] == 'False' and len(tagline.replace(check, '')) != 0:
            splices = tagline.split(' ')
            message = f"""**{self.name} is one sale for {splices[1]} off!** :fire: :moneybag:
<{self.url}>"""
            saledict[self.url] = 'True'
            with open('sale.json', 'w') as newsale:
                json.dump(saledict, newsale)
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await self.client.send_message(discord.Object(id=channel), message)
        if saledict[self.url] == 'True' and len(tagline.replace(check, '')) == 0:
            saledict[self.url] = 'False'
            with open('sale.json', 'w') as newsale:
                json.dump(saledict, newsale)

