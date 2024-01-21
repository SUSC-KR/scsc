import discord
import asyncio
from discord.ext.commands import Cog
from discord.commands import slash_command, Option
from discord.ui import Select, View

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
            
    @slash_command(description="원하는 스터디에 참여합니다.", guild_ids=[GUILD_ID])
    async def join(self, ctx):
        studies = requests.get("http://localhost:8000/studies/").json()
        
        select = Select(placeholder="스터디를 선택하세요.", 
                        options=[discord.SelectOption(label=study["name"], 
                                                      description=ctx.guild.get_member(study["mentor"]).name,
                                                      value=f"{study['name']}-{ctx.guild.get_member(study['mentor']).name}"
                                                      )
                                 for study in studies
                                 ])
        
        async def callback(interaction):
            if interaction.user == ctx.author:
                role = discord.utils.get(ctx.guild.roles, name=interaction.data["values"][0])
                
                select.disabled = True
                select.placeholder = interaction.data["values"][0]
                
                if role in interaction.user.roles:
                    await interaction.message.edit(view=view, content="이미 스터디에 참여하고 있습니다.")
                    return await interaction.response.defer(ephemeral=True)
                    
                await interaction.user.add_roles(role)
                
                await interaction.message.edit(view=view, content="스터디에 참여했습니다.")
                await interaction.response.defer(ephemeral=True)
            
        select.callback = callback
        
        view = View(timeout=60)
        view.add_item(select)
        
        await ctx.respond(view=view)
            
def setup(bot):
    bot.add_cog(User(bot))
    