import discord
import asyncio
from discord.ext.commands import Cog

import json
import requests

from config import *

class User(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @Cog.listener()
    async def on_member_join(self, member):
        requests.post("http://localhost:8000/users/", 
                      data={
                          "id": member.id, 
                          "name": member.name, 
                          "nickname": member.nick if member.nick is not None else "None"
                          })
            
    @Cog.listener()
    async def on_member_remove(self, member):
        requests.delete(f"http://localhost:8000/users/{member.id}/")
    
    @Cog.listener()
    async def on_member_update(self, before, after):    
        if before.roles != after.roles:
            if len(before.roles) < len(after.roles):
                role = [role for role in after.roles if role not in before.roles][0]
                
                study_name = role.name.split("-")[0]
                study = discord.utils.get(after.guild.categories, name=study_name)
                
                requests.post(f"http://localhost:8000/studies/{study.id}/", 
                                    data=json.dumps({"id": before.id}), 
                                    headers={"Content-Type": "application/json"})
            else:
                role = [role for role in before.roles if role not in after.roles][0]
                
                study_name = role.name.split("-")[0]
                study = discord.utils.get(after.guild.categories, name=study_name)
                
                requests.delete(f"http://localhost:8000/studies/{study.id}/{before.id}/")
                
        elif before.nick != after.nick:
            requests.put(f"http://localhost:8000/users/{before.id}/", data={"nickname": after.nick})
            
def setup(bot):
    bot.add_cog(User(bot))
    