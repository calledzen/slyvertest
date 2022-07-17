import asyncio
import datetime
import os
import discord
from discord.ext import commands
from discord.commands import slash_command
from utils.embedbuilder import buildEmbed, buildErrorMessage

import discord.ui as ui
import utils.database as db
import discord.utils
from dateutil import tz



class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="warnstats", description="Siehe die Warn Stats eines Moderators ein")
    async def _warnstats(self, ctx: discord.ApplicationContext, user: discord.Option(discord.Member, required=True)):

        if not ctx.guild.get_role(int(os.getenv("TEAM_ID"))) in ctx.author.roles:
            return await ctx.send_response(embed=buildErrorMessage(text="Du hast keine Rechte auf diesen Command"),
                                           ephemeral=True)

        if db.checkData("modstats", "warns, removewarns", f"userid = {user.id}"):
            _data = db.getData("modstats", "warns, removedwarns", f"userid = {user.id}")
            await ctx.send_response(embed=buildEmbed(title=f"Warn Stats | {user.name}#{user.discriminator}", text=f"Warns: `{_data[0][0] if _data[0][0] != None else str('Keine Daten')}`\nEntfernte Warns: `{_data[0][1] if _data[0][1] != None else str('Keine Daten')}`"), ephemeral=True)
        else:
            await ctx.send_response(embed=buildEmbed(title=f"Warn Stats | {user.name}#{user.discriminator}",
                                                     text=f"Warns: `Keine Daten `\nEntfernte Warns: `Keine Daten`"),
                                    ephemeral=True)

def setup(bot):
    bot.add_cog(Setup(bot))