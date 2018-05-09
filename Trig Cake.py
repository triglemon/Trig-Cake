#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as soup
import urllib.request
from datetime import datetime as dt


client = discord.Client()
token = 'NDM4NDI5MDYzODc5NzIwOTYw.DdJ4LQ.9Bl_wH1B5XL2B3o2QlyDOsxlaKw'

# Documentation:
# [game]u = url
# [game] = soup object
# [game]ud = updates list
# [game]1r = latest update raw
# [game]1 = latest update text
# [game]0 = last referred update text
# [game]h = subtitles/headers
# [game]ht = summary of headers
# [game]m = message in discord

@client.event
async def background_loop():
    await client.wait_until_ready()
    print("All hands on deck!")
    while not client.is_closed:

        """Overwatch"""

        # assigning variables
        overwatchurl = 'https://playoverwatch.com/en-us/game/patch-notes/pc/'
        with urllib.request.urlopen(overwatchurl) as doc:
            page = doc.read()
        overwatch = soup(page, "html.parser")
        overwatchud = overwatch.find_all("div", class_="patch-notes-body")
        overwatch1r = (overwatchud[0])
        overwatch1 = overwatch1r.text
        try:
            overwatch0
        except NameError:
            overwatch0 = overwatch1
        # message trigger
        if overwatch1 != overwatch0:
            overwatchh = overwatch1r.find_all("h2")
            overwatchht = "contents:"
            for x in overwatchh:
                overwatchht += (" " + x.text.lower() + ",")
            overwatchht = overwatchht[:-1] + "."
            overwatchm = "Overwatch patch " + overwatchht + "\n<" + overwatchurl + ">"
            overwatch0 = overwatch1
            await client.send_message(discord.Object(id="328295970246754304"), overwatchm)

        """Fortnite"""

        # assigning variables
        fortniteurl = 'https://www.youtube.com/feeds/videos.xml?channel_id=UClG8odDC8TS6Zpqk9CGVQiQ'
        with urllib.request.urlopen(fortniteurl) as doc:
            page = doc.read()
        fortnite = soup(page, "html.parser")
        fortnite1r = fortnite.find("media:group")
        fortnite1 = fortnite1r.find("media:title").text
        try:
            fortnite0
        except NameError:
            fortnite0 = fortnite1
        # message trigger
        if fortnite1 != fortnite0:
            fortnitem = "Fortnite: " + fortnite1 + "\n<https://www.youtube.com/user/epicfortnite/videos>"
            fortnite0 = fortnite1
            await client.send_message(discord.Object(id="328295970246754304"), fortnitem)
        # print("looped")

        await asyncio.sleep(60*10)

client.loop.create_task(background_loop())
client.run(token)
# /opt/vc/bin/vcgencmd measure_temp