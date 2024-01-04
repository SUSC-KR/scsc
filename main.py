import discord
import asyncio

from config import *

import os
import sys
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(e)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print(GUILD_ID)
    print("------")
    
    await bot.change_presence(activity=discord.Game(name="성장"))
    
access_token = os.getenv("SCSC_TOKEN")
bot.run(access_token)