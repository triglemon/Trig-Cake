"""
This module contains commands to subscribe to and interact with subscribed
Steam games.
"""
import json
from discord.ext import commands
from bs4 import BeautifulSoup as Soup
from modules.tryget import try_get
from modules.steamapp import SteamApp
from modules.embed import Embed


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
        search_result = await try_get(search_url)
        search_soup = Soup(search_result, 'html.parser')
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
        with open('json/steam.json') as steam:
            steam_dict = json.load(steam)
        no_announcements = False
        if app_id not in steam_dict:
            with open('json/name.json') as name:
                name_dict = json.load(name)
            name_dict[app_id] = game_name
            with open('json/name.json', 'w') as new_name:
                json.dump(name_dict, new_name)
            steam_dict[app_id] = []
            new_game = SteamApp(app_id, self.bot)
            new_game.fetch_name()
            try:
                await new_game.parse_news()
            except AttributeError:
                del name_dict[app_id]
                with open('json/name.json', 'w') as new_name:
                    json.dump(name_dict, new_name)
                no_announcements = True
                error = Embed("Error",
                              "This game doesn't have announcements yet.",
                              self.bot,
                              ctx)
                await ctx.send(embed=error.message)
            else:
                await new_game.gaben_pls()
                with open('json/update.json') as update:
                    update_dict = json.load(update)
                update_dict[app_id] = new_game.found_news
                with open('json/update.json', 'w') as new_update:
                    json.dump(update_dict, new_update)
                with open('json/sale.json') as sale:
                    sale_dict = json.load(sale)
                sale_dict[app_id] = new_game.found_sale
                with open('json/sale.json', 'w') as new_sale:
                    json.dump(sale_dict, new_sale)
                with open('json/subbed.json') as subbed:
                    subbed_dict = json.load(subbed)
                if str(ctx.message.channel.id) not in subbed_dict:
                    subbed_dict[str(ctx.message.channel.id)] = []
                subbed_dict[str(ctx.message.channel.id)].append(app_id)
                with open('json/subbed.json', 'w') as new_subbed:
                    json.dump(subbed_dict, new_subbed)
        if ctx.message.channel.id in steam_dict[app_id]:
            unsuccessful_post = Embed(
                "Unsuccessful.",
                f"This channel is already subscribed to {game_name}.",
                self.bot,
                ctx)
            await unsuccessful_post.launch_normal()
        else:
            if not no_announcements:
                steam_dict[app_id].append(ctx.message.channel.id)
                with open('json/steam.json', 'w') as new_steam:
                    json.dump(steam_dict, new_steam)
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
        with open('json/subbed.json') as subbed:
            subbed_dict = json.load(subbed)
        with open('json/name.json') as name:
            name_dict = json.load(name)
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
            steam_game.fetch_name()
            discord_post = Embed(steam_game.name,
                                 "What would you like to do?",
                                 self.bot,
                                 ctx,
                                 steam_game.url)
            await discord_post.launch_game(steam_game)


def setup(bot):
    bot.add_cog(Sub(bot))
