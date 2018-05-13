#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as soup
import urllib.request
import json


client = discord.Client()
token = open("/home/pi/Desktop/token").read()


# Documentation:
# [game]url = url
# [game]ud = updates list
# [game]1 = latest update text
# [game]0 = last referred update text
# [game]h = subtitles/headers
# [game]ht = summary of headers
# [game]m = message in discord


def parse(url, element, attribute={}):
    with urllib.request.urlopen(url) as doc:
        page = doc.read()
    object = soup(page, "html.parser")
    return object(element, attribute)


@client.event
async def background_loop():
    await client.wait_until_ready()
    print("All hands on deck!")
    while not client.is_closed:

        """Parsing"""

        # Overwatch
        overwatchurl = 'https://playoverwatch.com/en-us/game/patch-notes/pc/'
        overwatchud = parse(overwatchurl, "div", {"class": "patch-notes-body"})
        overwatch1 = overwatchud[0].text
        # Fortnite
        fortniteurl = 'https://www.youtube.com/feeds/videos.xml?channel_id=UClG8odDC8TS6Zpqk9CGVQiQ'
        fortniteud = parse(fortniteurl, "entry")
        fortnite1 = fortniteud[0].find("media:title").text

        """Triggers"""

        # Overwatch
        with open('/home/pi/Desktop/soupjson.json') as file:
            soupdict = json.load(file)
        overwatch0 = soupdict['overwatchlast']
        if overwatch1 != overwatch0:
            overwatchh = overwatchud[0].find_all("h2")
            overwatchht = "contents:"
            for x in overwatchh:
                overwatchht += (" " + x.text.lower() + ",")
            overwatchht = overwatchht[:-1] + "."
            overwatchm = "Overwatch patch " + overwatchht + "\n<" + overwatchurl + ">"
            # Writing File
            newdict = {"overwatchlast": overwatch1, "fortnitelast": fortnite1}
            with open("/home/pi/Desktop/soupjson.json", "w") as file:
                json.dump(newdict, file)
                file.close()
            await client.send_message(discord.Object(id="328295970246754304"), overwatchm)

        # Fortnite
        with open('/home/pi/Desktop/soupjson.json') as file:
            soupdict = json.load(file)
        fortnite0 = soupdict['fortnitelast']
        if fortnite1 != fortnite0:
            fortnitem = "Fortnite: " + fortnite1 + "\n<https://www.youtube.com/user/epicfortnite/videos>"
            # Writing File
            newdict = {"overwatchlast": overwatch1, "fortnitelast": fortnite1}
            with open("/home/pi/Desktop/soupjson.json", "w") as file:
                json.dump(newdict, file)
                file.close()
            await client.send_message(discord.Object(id="328295970246754304"), fortnitem)

        # print("looped")

        await asyncio.sleep(60*10)

client.loop.create_task(background_loop())
client.run(token)

# /opt/vc/bin/vcgencmd measure_temp
