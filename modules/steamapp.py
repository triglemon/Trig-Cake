import json
from bs4 import BeautifulSoup as Soup
from modules.tryget import tryget
from modules.embed import *


class SteamApp:

    def __init__(self, appid, bot):
        self.id = appid
        self.url = f'https://store.steampowered.com/app/{self.id}/'
        self.nurl = f'https://store.steampowered.com/news/?appids={self.id}'
        self.bot = bot
        self.name = None
        self.last = None
        self.found = None
        self.soup = None
        self.lastsale = None
        self.foundsale = None
        self.saleoff = None
        self.saledesc = None
        self.newslink = None
        self.thumbnail = None
        self.postauthor = None

    def fetchupdate(self):
        with open('json/update.json') as update:
            updatedict = json.load(update)
        self.last = updatedict[self.id]

    def fetchsale(self):
        with open('json/sale.json') as sale:
            saledict = json.load(sale)
        self.lastsale = saledict[self.id]

    def fetchname(self):
        with open('json/name.json') as name:
            namedict = json.load(name)
        self.name = namedict[self.id]

    async def gaben(self):
        storepage = await tryget(self.url)
        soup = Soup(storepage, 'html.parser')
        tagline = soup.find('title').text
        check = self.name + ' on Steam'
        self.foundsale = len(tagline.replace(check, '')) != 0
        if self.foundsale:
            splices = tagline.split(' ')
            self.saleoff = splices[1]
            self.saledesc = self.soup.find('p', {'class': 'game_purchase_discount_countdown'}).text

    async def parse(self):
        newspage = await tryget(self.nurl)
        newssoup = Soup(newspage, 'html.parser')
        news = newssoup.find('div', {'class': 'newsPostBlock'})
        self.found = news.find('a').text
        self.newslink = news.find('a')['href']
        self.thumbnail = news.find('img')['src']
        self.postauthor = news.find('div', {'class': 'feed'}).text

    async def trigger(self):
        if self.found != self.last:
            message = embed(self.found, f"New Steam announcement from {self.name}!", self.newslink)
            message.set_author(name=self.postauthor)
            message.set_image(url=self.thumbnail)
            with open('json/update.json') as update:
                updatedict = json.load(update)
            updatedict[self.id] = self.found
            with open('json/update.json', 'w') as newupdate:
                json.dump(updatedict, newupdate)
            with open('json/steam.json') as steam:
                steamdict = json.load(steam)
            for channelid in steamdict[self.id]:
                channel = self.bot.get_all_channels().get_channel(channelid)
                await channel.send(embed=message)

    async def saletrigger(self):
        if not self.lastsale and self.foundsale:
            message = embed(self.name, self.url, self.saledesc)
            message.set_image(url=self.thumbnail)
            with open('json/sale.json') as sale:
                saledict = json.load(sale)
            saledict[self.id] = True
            with open('json/sale.json', 'w') as newsale:
                json.dump(saledict, newsale)
            with open('json/steam.json') as steam:
                steamdict = json.load(steam)
            for channelid in steamdict[self.id]:
                print(channelid)
                channel = self.bot.get_channel(channelid)
                await channel.send(embed=message)
        if self.lastsale and not self.foundsale:
            with open('json/sale.json') as sale:
                saledict = json.load(sale)
            saledict[self.id] = False
            with open('json/sale.json', 'w') as newsale:
                json.dump(saledict, newsale)

