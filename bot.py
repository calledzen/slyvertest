import random
import os
import discord
import asyncio
from dotenv import load_dotenv
from utils.database import connect, disconnect, tableSetup

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all(), debug_guilds=[990724201105227898])



@bot.event
async def on_ready():
    print("-----------")
    print("bot system loaded.")
    print("name: " + bot.user.name)
    print("-----------")
    connect("sqlite")
    tableSetup()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"💚┃SlyverTest System"))




print("COMMANDS")
for filename in os.listdir('commands'):
    if filename.endswith('.py'):
        if filename != "__init__.py":
            bot.load_extension(f'commands.{filename[:-3]}')
            print(f'[+] {filename[:-3]}')

bot.run(str(os.getenv('TOKEN')))

