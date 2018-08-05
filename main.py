#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import aiohttp
import json
from discord.ext import commands
import logging


startup_extensions = ['ask', 'sub', 'unsub', 'subbed', 'last', 'found']
description = "Type !cakeask in chat for a list of commands and more info."
client = commands.Bot(command_prefix='!cake', description=description, hidden=False)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def load(extension_name: str):
    try:
        client.load_extension(extension_name)
    except (AttributeError, ImportError) as error:
        await client.say("```py\n{}: {}\n```".format(type(error).__name__, str(error)))
        return
    await client.say("{} loaded.".format(extension_name))


@client.command()
async def unload(extension_name: str):
    client.unload_extension(extension_name)
    await client.say("{} unloaded.".format(extension_name))


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    with open('token') as file:
        token = file.read()
    client.run(token)
