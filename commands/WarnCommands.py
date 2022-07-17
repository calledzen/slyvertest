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


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def getWarnNumber(self, userid: str):
        _d = db.convertData(
            db.executeGet(f"SELECT warnnumber FROM warns WHERE userid = '{userid}' ORDER BY warnnumber DESC LIMIT 1;"),
            "int")
        if _d == None:
            return 0
        else:
            return _d



    @slash_command(name="warn", description="Verwarne einen User")
    async def _warn(self, ctx: discord.ApplicationContext, user: discord.Option(discord.Member, required=True), reason: discord.Option(str, required=False)):

        if not ctx.guild.get_role(int(os.getenv("TEAM_ID"))) in ctx.author.roles:
            return await ctx.send_response(embed=buildErrorMessage(text="Du hast keine Rechte auf diesen Command"), ephemeral=True)

        # Set reason value if not set
        if reason is None:
            reason = "Keine Begründung"

        #Check if reason is too long for database text entry
        if len(reason) > 1000:
            return await ctx.send_response(embed=buildErrorMessage(text="Die Begründung darf maximal 1000 Zeichen lang sein"), ephemeral=True)

        #Check if User is invalid for Warning
        if user.id == ctx.author.id:
            return await ctx.send_response(embed=buildErrorMessage(text="Du kannst dich nicht selbst verwarnen"), ephemeral=True)
        if user.bot:
            return await ctx.send_response(embed=buildErrorMessage(text="Du kannst Bots nicht verwarnen"), ephemeral=True)


        _warnsnumber = (int(self.getWarnNumber(user.id)) + 1)
        db.insertData("warns", "userid, warnnumber, modid, timestamp, reason", f"{user.id}, {_warnsnumber}, {ctx.author.id}, {datetime.datetime.now().timestamp()}, '{reason}'")



        #Mod Stats
        if (db.checkData("modstats", "*", f"userid = '{ctx.author.id}'")):
            db.updateData("modstats", "warns = warns + 1", f"userid = '{ctx.author.id}'")
        else:
            db.insertData("modstats", "warns, removedwarns, userid", f"1, 0, {ctx.author.id}")


        #Information, Logging and Respond
        await ctx.send_response(embed=buildEmbed(title="Warn System", text=f"Du hast den User <@{str(user.id)}> erfolgreich verwarnt.\nWarn Nummer: `{_warnsnumber}`\nGrund: `{reason}`"), ephemeral=True)
        await ctx.guild.get_channel(
            int(os.getenv("LOGCHANNEL_ID"))).send(embed=buildEmbed(title="Warn System | Verwarnt", text=f"User: <@{str(user.id)}>\nModerator: <@{str(ctx.author.id)}> \nWarn Nummer: `{_warnsnumber}`\nGrund: `{reason}`", color=0x6BFF6B))

        try:
            await user.send(embed=buildEmbed(title="Warn System", text=f"Du wurdest auf SlyversWorld von **{str(ctx.author.name)}#{str(ctx.author.discriminator)}** verwarnt.\nWarn Nummer: `{_warnsnumber}`\nGrund: `{reason}`"))

        except:
            pass

    @slash_command(name="removewarn", description="Entfernt einen Warn von einem User")
    async def _removewarn(self, ctx: discord.ApplicationContext, user: discord.Option(discord.Member, required=True), warnnumber: discord.Option(int, required=True), reason: discord.Option(str, required=False)):

        if not ctx.guild.get_role(int(os.getenv("TEAM_ID"))) in ctx.author.roles:
            return await ctx.send_response(embed=buildErrorMessage(text="Du hast keine Rechte auf diesen Command"), ephemeral=True)

        # Set reason value if not set
        if reason is None:
            reason = "Keine Begründung"

        #Check if reason is too long for database text entry
        if len(reason) > 1000:
            return await ctx.send_response(embed=buildErrorMessage(text="Die Begründung darf maximal 1000 Zeichen lang sein"), ephemeral=True)

        #Check if User is invalid for Warning
        if user.bot:
            return await ctx.send_response(embed=buildErrorMessage(text="Du kannst Bots nicht entwarnen, da sie nicht verwarnt werden können"), ephemeral=True)


        if not str(warnnumber) in db.convertData(db.getData("warns", "warnnumber", f"userid='{user.id}'"), "list"):
            return await ctx.send_response(embed=buildErrorMessage(text="Die Warn Nummer konnte nicht gefunden werden"), ephemeral=True)


        db.execute(f"DELETE FROM warns WHERE warnnumber={warnnumber} AND userid='{user.id}';")


        for i in db.getData("warns", "warnnumber", f"userid = '{user.id}' AND warnnumber > {warnnumber}"):
            db.updateData("warns", "warnnumber = warnnumber - 1", f"userid = '{user.id}' AND warnnumber = '{i[0]}'")


        #Mod Stats
        if (db.checkData("modstats", "*", f"userid = '{ctx.author.id}'")):
            db.updateData("modstats", "removedwarns = removedwarns + 1", f"userid = '{ctx.author.id}'")
        else:
            db.insertData("modstats", "warns, removedwarns, userid", f"0, 1, {ctx.author.id}")


        #Information, Logging and Respond
        await ctx.send_response(embed=buildEmbed(title="Warn System", text=f"Du hast den User <@{str(user.id)}> einen Warn entfernt.\nWarn Nummer: `{warnnumber}`\nGrund: `{reason}`"), ephemeral=True)
        await ctx.guild.get_channel(
            int(os.getenv("LOGCHANNEL_ID"))).send(embed=buildEmbed(title="Warn System | Entfernt", text=f"User: <@{str(user.id)}>\nModerator: <@{str(ctx.author.id)}> \nWarn Nummer: `{warnnumber}`\nGrund: `{reason}`", color=0xFF5050))

        try:
            await user.send(embed=buildEmbed(title="Warn System", text=f"Dir wurde auf SlyversWorld der Warn {warnnumber} von **{str(ctx.author.name)}#{str(ctx.author.discriminator)}** entfernt.\nGrund: `{reason}`"))

        except:
            pass





    @slash_command(name="warns", description="Sehe alle Warns eines Users")
    async def _warns(self, ctx: discord.ApplicationContext, user: discord.Option(discord.Member, required=True)):

        if not ctx.guild.get_role(int(os.getenv("TEAM_ID"))) in ctx.author.roles:
            return await ctx.send_response(embed=buildErrorMessage(text="Du hast keine Rechte auf diesen Command"), ephemeral=True)

        _warndata = db.executeGet(f"SELECT * FROM warns WHERE userid = '{user.id}' ORDER BY warnnumber DESC;")

        if len(_warndata) == 0:
            return await ctx.send_response(
                embed=buildEmbed(title=f"Warns von {user.name}#{user.discriminator}", text="Der User hat keine Warns."),
                ephemeral=True)


        text = f""
        for item in _warndata:
            _mod = ctx.guild.get_member(int(item[2]))
            text += f"Warn Nummer: `{item[1]}`\nGrund: `{item[4]}`\nModerator: `{_mod.name}#{_mod.discriminator}`\nUhrzeit: `{datetime.datetime.fromtimestamp(float(item[3])).astimezone(tz.gettz('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
        await ctx.send_response(embed=buildEmbed(title=f"Warns von {user.name}#{user.discriminator} [{len(_warndata)}]", text=text), ephemeral=True)



def setup(bot):
    bot.add_cog(Commands(bot))