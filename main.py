import discord
import asyncio

import os

bot = discord.Bot()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    
    await bot.change_presence(activity=discord.Game(name="성장"))
    
access_token = os.environ["SCSC_TOKEN"]
bot.run(access_token)