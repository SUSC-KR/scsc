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
    
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.respond("명령을 실행할 권한이 없습니다.")
    else:
        await ctx.respond(f"예상치 못한 오류가 발생했습니다. {error}")
    
access_token = os.getenv("SCSC_TOKEN")
bot.run(access_token)