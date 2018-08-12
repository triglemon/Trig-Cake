import discord
import asyncio


def embed(title, description, url=None):
    message = discord.Embed(title=title, url=url, description=description, color=0xebbe23)
    message.set_footer(text="Request an action by reacting with the relevant emojis")
    return message


async def launch(post, commands, ctx, bot):
    message = await ctx.send(embed=post)
    for command in commands:
        await message.add_reaction(command)

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in commands

    try:
        reaction = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        message.delete()
        await ctx.send('Function has timed out')
    else:
        return reaction[0].emoji
