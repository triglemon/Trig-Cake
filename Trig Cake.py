#!/usr/bin/python3


import discord
import asyncio
from bs4 import BeautifulSoup as Soup
import urllib.request
import json

# Creating Discord Client and grabbing token
client = discord.Client()
token = open("/home/pi/Desktop/token").read()


class Game:

    # Each game is represented by a Game object
    def __init__(self, name, url, key):
        self.json = "/home/pi/Desktop/soupjson.json"
        self.name = name
        self.url = url
        # This grabs the json strings as the last update
        with open(self.json) as file:
            soupdict = json.load(file)
        self.last = (soupdict[key])
        self.updates = None
        self.found = None
        self.message = None

    # This parses the url for a list of updates
    def parse(self, element, attribute=None, subelement=None):
        with urllib.request.urlopen(self.url) as doc:
            page = doc.read()
        soupobject = Soup(page, "html.parser")
        self.updates = soupobject(element, attribute)
        self.found = self.updates[0]
        if subelement is not None:
            self.found = self.found.find(subelement)

    # Stores the fresh update for later batches
    def store(self):
        self.last = self.found.text


# This event happens at launch and is the main loop of the script
@client.event
async def background_loop():
    await client.wait_until_ready()

    # Creating Game objects and obtaining json strings
    ow = Game("Overwatch",
              "https://playoverwatch.com/en-us/game/patch-notes/pc/",
              "overwatchlast")
    fn = Game("Fortnite",
              "https://www.youtube.com/feeds/videos.xml?channel_id=UClG8odDC8TS6Zpqk9CGVQiQ",
              "fortnitelast")
    csgo = Game("Counter Strike: Global Offensive",
                "http://blog.counter-strike.net/index.php/category/updates/",
                "csgolast")

    print("All hands on deck!")
    # Loop code
    while not client.is_closed:
        # Parsing
        ow.parse("div", {"class": "patch-notes-body"})
        fn.parse("entry", subelement="title")
        csgo.parse("div", {"class": "inner_post"})

        # Message triggers (If the last update online matches the last stored update)

        # Overwatch message trigger

        if ow.found.text != ow.last:
            headers = ow.found("h2")
            ow.message = "Overwatch:"
            for x in headers:
                ow.message += (" " + x.text.lower() + ",")
            ow.message = ow.message[:-1] + "."
            ow.message += "\n<" + ow.url + ">"
            # Writing File
            newdict = {"overwatchlast": ow.found.text, "fortnitelast": fn.found.text, "csgolast": csgo.found.text}
            with open("/home/pi/Desktop/soupjson.json", "w") as file:
                json.dump(newdict, file)
            ow.store()
            await client.send_message(discord.Object(id="328295970246754304"), ow.message)

        # Fortnite message trigger
        if fn.found.text != fn.last:
            fn.message = fn.found.text
            fn.message = "Fortnite: " + fn.message + "\n<https://www.youtube.com/user/epicfortnite/videos>"
            # Writing File
            newdict = {"overwatchlast": ow.found.text, "fortnitelast": fn.found.text, "csgolast": csgo.found.text}
            with open("/home/pi/Desktop/soupjson.json", "w") as file:
                json.dump(newdict, file)
            fn.store()
            await client.send_message(discord.Object(id="328295970246754304"), fn.message)

        if csgo.found.text != csgo.last:
            csgo.message = "CSGO: " + csgo.found.find("h2").text
            newdict = {"overwatchlast": ow.found.text, "fortnitelast": fn.found.text, "csgolast": csgo.found.text}
            with open("/home/pi/Desktop/soupjson.json", "w") as file:
                json.dump(newdict, file)
            csgo.store()
            await client.send_message(discord.Object(id="328295970246754304"), csgo.message)
        # print("looped")

        await asyncio.sleep(60*10)

client.loop.create_task(background_loop())
client.run(token)

# /opt/vc/bin/vcgencmd measure_temp
