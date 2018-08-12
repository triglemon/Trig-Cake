from discord.ext import commands
import logging
from modules.embed import *


startup_extensions = []
bot = commands.Bot(command_prefix='<&')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}, {bot.user.id}")
    game = discord.Game("Baking in the oven")
    await bot.change_presence(status=discord.Status.idle, activity=game)


@bot.command()
async def load(ctx, extension_name):
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as error:
        await ctx.send(f"```py\n{type(error).__name__}: {str(error)}\n```")
        return
    await ctx.send(f"{extension_name} loaded.")


@bot.command()
async def unload(ctx, extension_name):
    bot.unload_extension(extension_name)
    await ctx.send(f"{extension_name} unloaded.")


@bot.command()
async def yeet(ctx):
    thing = embed("Me", "You")
    listed = ['1\u20e3', '2\u20e3', '3\u20e3', '4\u20e3']
    emoji = await launch(thing, listed, ctx, bot)
    await ctx.send(emoji)


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(f'Failed to load extension {extension}\n{exc}')

    with open('token') as file:
        token = file.read()
    bot.run(token, bot=True, reconnect=True)
