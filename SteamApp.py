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
        self.lastsale = None
        self.foundsale = None
        self.saleoff = None
        self.saledesc = None
        self.client = client

    def fetchupdate(self):
        with open('update.json') as update:
            updatedict = json.load(update)
        self.last = updatedict[self.url]

    def fetchsale(self):
        with open('sale.json') as sale:
            saledict = json.load(sale)
        self.lastsale = saledict[self.url]

    def gaben(self):
        tagline = self.soup.find('title').text
        check = self.name + ' on Steam'
        self.foundsale = len(tagline.replace(check, '')) != 0
        if self.foundsale:
            splices = tagline.split(' ')
            self.saleoff = splices[1]
            self.saledesc = self.soup.find('p', {'class': 'game_purchase_discount_countdown'})

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
            with open('update.json') as update:
                updatedict = json.load(update)
            updatedict[self.url] = self.found
            with open('update.json', 'w') as newupdate:
                json.dump(updatedict, newupdate)
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await self.client.send_message(discord.Object(id=channel), message)

    async def saletrigger(self):
        if not self.lastsale and self.foundsale:
            message = f"""**{self.name} is on sale for {self.saleoff} off!** :fire: :moneybag:
"{self.saledesc}"
<{self.url}>"""
            with open('sale.json') as sale:
                saledict = json.load(sale)
            saledict[self.url] = 'True'
            with open('sale.json', 'w') as newsale:
                json.dump(saledict, newsale)
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for channel in steamdict[self.url]:
                await self.client.send_message(discord.Object(id=channel), message)
        if self.lastsale and not self.foundsale:
            with open('sale.json') as sale:
                saledict = json.load(sale)
            saledict[self.url] = 'False'
            with open('sale.json', 'w') as newsale:
                json.dump(saledict, newsale)

