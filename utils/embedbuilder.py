import asyncio
import discord
from datetime import datetime



def buildEmbed(title, text, color = None, emojiu = None):
    coloru = discord.Color.embed_background() if color == None else color
    if emojiu != None:
        e = discord.Embed(title=f"`{emojiu}` ┃ " + title, colour=coloru, description=text, timestamp=datetime.utcnow())
        e.set_footer(text="Slyver Test",
                     icon_url="https://slyverworld.com/assets/img/slyverworldlogo2.png")
        return e
    else:
        e = discord.Embed(title=title, colour=coloru, description=text, timestamp=datetime.utcnow())
        e.set_footer(text="Slyver Test",
                     icon_url="https://slyverworld.com/assets/img/slyverworldlogo2.png")
        return e




def buildErrorMessage(text):
    e = discord.Embed(title="`❌` ┃ Error", colour=0xF44F4F, description=f"_{text}_", timestamp=datetime.utcnow())
    e.set_footer(text="Slyver Test",
                 icon_url="https://slyverworld.com/assets/img/slyverworldlogo2.png")
    return e


async def sendErrorMessage(ctx, text):
    e = discord.Embed(title="`❌` ┃ Error", colour=0xF44F4F, description=f"_{text}_", timestamp=datetime.utcnow())
    e.set_footer(text="Slyver Test",
                 icon_url="https://slyverworld.com/assets/img/slyverworldlogo2.png")
    errmsg = await ctx.reply(embed=e)
    await asyncio.sleep(7)
    await errmsg.delete()
