async def background_loop():

    while not client.is_closed:
        with open('steam.json') as steam:
            steamdict = json.load(steam)
        for url in steamdict:
            splices = url.split('/')
            appid = splices[3] + splices[4]
            vars()[appid] = SteamApp(url)
            await vars()[appid].acquire()
            await vars()[appid].parse()
            vars()[appid].fetchjson()
            await vars()[appid].trigger()
            await vars()[appid].saletrigger()

        print("looped")
        await asyncio.sleep(60*5)


client.loop.create_task(background_loop())
