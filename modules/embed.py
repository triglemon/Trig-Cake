import discord


class Embed:
    def __init__(self, title, url, description, ctx):
        self.title = title
        self.url = url
        self.description = description
        self.ctx = ctx
        self.embed = discord.Embed(title=self.title, url=self.url, description=self.description, color=0xebbe23)
        self.embed.set_footer(text="Request an action by reacting with the relevant emojis")

    async def launch(self, *commands):
        message = self.ctx.send(self.embed)
        await message
        for command in commands:
            await message.add_reaction(next(iter(command)))


