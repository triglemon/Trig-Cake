"""
This module holds the class SteamApp, which every Steam game and its Steam
Store interactions are represented by.
"""
import json
from bs4 import BeautifulSoup as Soup
from modules.tryget import try_get
from modules.embed import Embed


class SteamApp:
    def __init__(self, app_id, bot):
        self.app_id = app_id
        self.url = f'https://store.steampowered.com/app/{self.app_id}/'
        self.news_url = ('https://store.steampowered.com'
                         f'/news/?appids={self.app_id}')
        self.bot = bot
        self.name = None
        self.last_news = None
        self.found_news = None
        self.soup = None
        self.last_sale = None
        self.found_sale = None
        self.percentage_off = None
        self.sale_description = None
        self.news_link = None
        self.thumbnail = None
        self.post_author = None

    def fetch_update(self):
        """Gets last stored update"""
        with open('json/update.json') as update:
            update_dict = json.load(update)
        self.last_news = update_dict[self.app_id]

    def fetch_sale(self):
        """Gets last stored sale value"""
        with open('json/sale.json') as sale:
            sale_dict = json.load(sale)
        self.last_sale = sale_dict[self.app_id]

    def fetch_name(self):
        """Gets last stored sale value"""
        with open('json/name.json') as name:
            name_dict = json.load(name)
        self.name = name_dict[self.app_id]

    async def parse_news(self):
        """Parses news page to get current headline"""
        news_page = await try_get(self.news_url)
        news_soup = Soup(news_page, 'html.parser')
        news_entry = news_soup.find('div', {'class': 'newsPostBlock'})
        self.found_news = news_entry.find('a').text
        self.news_link = news_entry.find('a')['href']
        self.thumbnail = news_entry.find('img')['src']
        self.post_author = news_entry.find('div', {'class': 'feed'}).text

    async def gaben_pls(self):
        """Parses store page to get current sale value"""
        store_page = await try_get(self.url)
        store_soup = Soup(store_page, 'html.parser')
        site_tag_line = store_soup.find('title').text
        check_no_sale = self.name + ' on Steam'
        self.found_sale = len(site_tag_line.replace(check_no_sale, '')) != 0
        if self.found_sale:
            tag_splices = site_tag_line.split(' ')
            self.percentage_off = tag_splices[1]
            self.sale_description = store_soup.find(
                'p', {'class': 'game_purchase_discount_countdown'}).text

    async def news_trigger(self):
        """Compares news headlines and announces if it's changed"""
        if self.found_news != self.last_news:
            discord_post = Embed(self.found_news,
                                 f"New Steam announcement from {self.name}!",
                                 self.bot,
                                 url=self.news_link)
            discord_post.message.set_author(name=self.post_author)
            discord_post.message.set_image(url=self.thumbnail)
            with open('json/update.json') as update:
                update_dict = json.load(update)
            update_dict[self.app_id] = self.found_news
            with open('json/update.json', 'w') as new_update:
                json.dump(update_dict, new_update)
            with open('json/steam.json') as steam:
                steam_dict = json.load(steam)
            for channel_id in steam_dict[self.app_id]:
                channel = self.bot.get_channel(channel_id)
                await channel.send(embed=discord_post.message)

    async def sale_trigger(self):
        """Compares sale boolean and announces if changed from false to true"""
        if not self.last_sale and self.found_sale:
            discord_post = Embed(self.name,
                                 self.sale_description,
                                 self.bot,
                                 url=self.url)
            discord_post.message.set_image(url=self.thumbnail)
            with open('json/sale.json') as sale:
                sale_dict = json.load(sale)
            sale_dict[self.app_id] = True
            with open('json/sale.json', 'w') as new_sale:
                json.dump(sale_dict, new_sale)
            with open('json/steam.json') as steam:
                steam_dict = json.load(steam)
            for channel_id in steam_dict[self.app_id]:
                channel = self.bot.get_channel(channel_id)
                await channel.send(embed=discord_post.message)
        if self.last_sale and not self.found_sale:
            with open('json/sale.json') as sale:
                sale_dict = json.load(sale)
            sale_dict[self.app_id] = False
            with open('json/sale.json', 'w') as new_sale:
                json.dump(sale_dict, new_sale)
