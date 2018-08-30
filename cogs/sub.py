"""
This module contains commands to subscribe to and interact with subscribed
Steam games.
"""
from discord.ext import commands
from bs4 import BeautifulSoup as Soup
from modules.tryget import TryGet
from modules.steamapp import SteamApp
from modules.embed import Embed
from modules.json import async_load
from modules.json import delete_dump
from modules.json import new_value_dump
from modules.json import append_value_dump


class Sub:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sub')
    @commands.has_permissions(manage_channels=True)
    async def sub(self, ctx, *search_terms):
        """Subscribe to Steam games (only in single channel)"""
        search_url = 'https://store.steampowered.com/search/?term='
        search_line = ""
        for term in search_terms:
            search_line = search_line + " " + term
            search_url = search_url + f'{term}+'
        search_url = search_url[:-1]
        search_result = TryGet()
        search_request = await search_result.get_request(search_url)
        search_soup = Soup(search_request, 'html.parser')
        top_5 = [title for title in search_soup('span', {'class': 'title'})[0:5]]
        entry_list = [entry.text for entry in top_5]
        message = Embed(f"Searching for {search_line}.",
                        "The following search results were found...",
                        self.bot,
                        ctx)
        message.prepare(entry_list)
        decision = await message.launch_special()
        # Finding the decision made by getting the emoji and subtracting to get
        # index in top_5
        entry = top_5[int(decision[1][0]) - 1]
        game_name = entry.text
        app_id = entry.parent.parent.parent['data-ds-appid']
        steam_dict = await async_load('steam')
        no_announcements = False
        if app_id not in steam_dict:
            name_dict = await async_load('name')
            print(name_dict, app_id, game_name)
            await new_value_dump(name_dict, app_id, game_name, 'name')
            steam_dict[app_id] = []
            new_game = SteamApp(app_id, self.bot)
            await new_game.fetch_name()
            try:
                await new_game.parse_news()
            except AttributeError:
                await delete_dump(name_dict, app_id, 'name')
                no_announcements = True
                error = Embed("Error",
                              "This game doesn't have announcements yet.",
                              self.bot,
                              ctx)
                await ctx.send(embed=error.message)
            else:
                await new_game.gaben_pls()
                update_dict = await async_load('update')
                await new_value_dump(update_dict,
                                     app_id,
                                     new_game.found_news,
                                     'update')
                await new_value_dump(name_dict, app_id, game_name, 'name')
                sale_dict = await async_load('sale')
                await new_value_dump(sale_dict,
                                     app_id,
                                     new_game.found_sale,
                                     'sale')
        if ctx.message.channel.id in steam_dict[app_id]:
            unsuccessful_post = Embed(
                "Unsuccessful.",
                f"This channel is already subscribed to {game_name}.",
                self.bot,
                ctx)
            await unsuccessful_post.launch_normal()
        else:
            if not no_announcements:
                subbed_dict = await async_load('subbed')
                if str(ctx.message.channel.id) not in subbed_dict:
                    subbed_dict[str(ctx.message.channel.id)] = []
                await append_value_dump(subbed_dict,
                                        str(ctx.message.channel.id),
                                        app_id,
                                        'subbed')
                await append_value_dump(steam_dict,
                                        app_id,
                                        ctx.message.channel.id,
                                        'steam')
                successful_post = Embed(
                    "Success!",
                    f"This channel is now subscribed to {game_name}!",
                    self.bot,
                    ctx)
                await successful_post.launch_normal()

    @commands.command(name='subbed')
    @commands.has_permissions(manage_channels=True)
    async def subbed(self, ctx):
        """Shows list of subscribed Steam Games in channel"""
        channel_id = ctx.message.channel.id
        subbed_dict = await async_load('subbed')
        name_dict = await async_load('name')
        try:
            game_list = [name_dict[app_id]
                         for app_id in subbed_dict[str(channel_id)]]
        except KeyError:
            error = Embed("Error",
                          "Channel is not subscribed to any games.",
                          self.bot,
                          ctx)
            await error.launch_normal()
        else:
            id_list = [app_id for app_id in subbed_dict[str(channel_id)]]
            discord_post = Embed(
                f"Searching for {self.bot.get_channel(channel_id)}'s "
                "subscribed games.",
                "The following search results were found...",
                self.bot,
                ctx)
            discord_post.prepare(game_list)
            reaction_tup = await discord_post.launch_special()
            # Finding app based on index in chunk and index of chunk in
            # chunk list
            app_id = id_list[int(reaction_tup[1][0]) - 1 + reaction_tup[0] * 9]
            steam_game = SteamApp(app_id, self.bot)
            await steam_game.fetch_name()
            discord_post = Embed(steam_game.name,
                                 "What would you like to do?",
                                 self.bot,
                                 ctx,
                                 steam_game.url)
            await discord_post.launch_game(steam_game)


def setup(bot):
    bot.add_cog(Sub(bot))
