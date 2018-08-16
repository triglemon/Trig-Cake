import discord
import asyncio
import copy


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Embed:
    def __init__(self, title, description, bot,  ctx=None, url=None):
        message = discord.Embed(title=title, url=url, description=description, color=0xebbe23)
        message.set_footer(text="Request an action by reacting with the relevant emojis")
        self.message = message
        self.ctx = ctx
        self.bot = bot
        self.groupedlist = None
        self.messagelist = None

    def prepare(self, resultlist):
        self.groupedlist = [x for x in chunks(resultlist, 9)]
        self.messagelist = []
        for group in self.groupedlist:
            newmessage = copy.copy(self.message)
            for entry in group:
                place = group.index(entry) + 1
                newmessage.add_field(name=f"Entry #{place}", value=entry, inline=False)
            self.messagelist.append(newmessage)

    async def launchcontrols(self, index, timeout=None):
        currentmessage = self.messagelist[index]
        currentgroup = self.groupedlist[index]
        post = await self.ctx.send(embed=currentmessage)
        commandlist = [f'{currentgroup.index(entry)+1}\u20e3' for entry in currentgroup]
        for command in commandlist:
            await post.add_reaction(command)
        if index > 0:
            await post.add_reaction('⬅')
        if index < len(self.messagelist) - 1:
            await post.add_reaction('➡')
        await post.add_reaction('🇽')

        def check(reaction, user):
            emojibool = reaction.emoji in ['🇽', '➡', '⬅'] or (reaction.emoji in commandlist)
            userbool = user == self.ctx.message.author
            postbool = reaction.message.id == post.id
            return emojibool and userbool and postbool
        try:
            reaction = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            await post.delete()
            await self.ctx.send('Function has timed out')
        else:
            await post.delete()
            return reaction[0].emoji

    async def launchspecial(self):
        index = 0
        while True:
            launched = await self.launchcontrols(index, timeout=60.0)
            if not launched:
                break
            if launched == '⬅':
                index = int(index - 1)
                pass
            elif launched == '➡':
                index = int(index + 1)
                pass
            else:
                return index, launched

    async def launchnormal(self):
        if self.messagelist:
            self.message = self.messagelist[0]
        post = await self.ctx.send(embed=self.message)
        await post.add_reaction('🇽')

        def check(reaction, user):
            emojibool = reaction.emoji == '🇽'
            userbool = user == self.ctx.message.author
            postbool = reaction.message.id == post.id
            return emojibool and userbool and postbool
        try:
            await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await post.delete()
            error = Embed("Error", "Function has timed out.", self.bot, self.ctx)
            await error.launchnormal()
        else:
            await post.delete()


    # async def launchstoregame(self, timeout=None):