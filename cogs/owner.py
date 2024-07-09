from discord.ext import commands

from dotenv import load_dotenv
import os

load_dotenv()

def has_permissions_or_owner():
    async def predicate(ctx):
        if ctx.author.id == os.getenv('OWNER_ID') or ctx.author.guild_permissions.administrator:
            return True
        else:
            raise commands.CheckFailure()
            
    return commands.check(predicate)
