"""
This module holds the class SteamApp, which every Steam game and its Steam
Store interactions are represented by.
"""
from bs4 import BeautifulSoup as Soup
from modules.tryget import TryGet
from modules.embed import Embed
from modules.json import async_load
from modules.json import new_value_dump


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

    async def fetch_update(self):
        """Gets last stored update"""
        update_dict = await async_load('update')
        self.last_news = update_dict[self.app_id]

    async def fetch_sale(self):
        """Gets last stored sale value"""
        sale_dict = await async_load('sale')
        self.last_sale = sale_dict[self.app_id]

    async def fetch_name(self):
        """Gets last stored sale value"""
        name_dict = await async_load('name')
        self.name = name_dict[self.app_id]

    async def parse_news(self):
        """Parses news page to get current headline"""
        news_page = TryGet()
        news_request = await news_page.get_request(self.news_url)
        news_soup = Soup(news_request, 'html.parser')
        news_entry = news_soup.find('div', {'class': 'newsPostBlock'})
        self.found_news = news_entry.find('a').text
        self.news_link = news_entry.find('a')['href']
        self.thumbnail = news_entry.find('img')['src']
        self.post_author = news_entry.find('div', {'class': 'feed'}).text

    async def gaben_pls(self):
        """Parses store page to get current sale value"""
        store_page = TryGet()
        store_request = await store_page.get_request(self.url)
        store_soup = Soup(store_request, 'html.parser')
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
            update_dict = await async_load('update')
            await new_value_dump(update_dict,
                                 self.app_id,
                                 self.found_news,
                                 'update')
            steam_dict = await async_load('steam')
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
            sale_dict = await async_load('sale')
            await new_value_dump(sale_dict,
                                 self.app_id,
                                 True,
                                 'sale')
            steam_dict = await async_load('steam')
            for channel_id in steam_dict[self.app_id]:
                channel = self.bot.get_channel(channel_id)
                await channel.send(embed=discord_post.message)
        if self.last_sale and not self.found_sale:
            sale_dict = await async_load('sale')
            await new_value_dump(sale_dict,
                                 self.app_id,
                                 False,
                                 'sale')
