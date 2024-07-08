import discord
import asyncio
from discord.ext.commands import Cog, has_permissions
from discord.commands import slash_command, Option

import requests

from config import *
from cogs.study import *

from dotenv import load_dotenv
import os

load_dotenv()
        
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @slash_command(description="스터디 관련 명령어입니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def study(self, ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토"), command: Option(str, "명령", choices=["개설", "조회", "수정", "삭제"])):
        if command == "개설":
            await open_study(ctx, study_name, study_mentor)
        elif command == "조회":
            await query_study_info(ctx, study_name, study_mentor)
        elif command == "수정":
            await edit_study(ctx, study_name, study_mentor)
        elif command == "삭제":
            await close_study(ctx, study_name, study_mentor)

    @slash_command(description="사용자 정보를 확인합니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def userinfo(self, ctx, user: Option(discord.Member, "사용자", required=False)):
        if user is None:
            user = ctx.author
            
        user_embed = discord.Embed(title=f"{user}의 정보", 
                                   description=f"**이름**: {user.name}\n \
                                   **아이디**: {user.id}\n \
                                   **상태**: {user.status}\n \
                                   **역할**: {', '.join([role.mention for role in user.roles])}\n \
                                   **서버 참가일**: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}", \
                                   color=BOT_COLOR)
        user_embed.set_thumbnail(url=user.avatar)
        user_embed.set_footer(text=BOT_VER)
        
        await ctx.respond(embed=user_embed)
        
    @slash_command(description="사용자의 역할을 수동 추가합니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def addrole(self, ctx, user: Option(discord.Member, "사용자"), role: Option(discord.Role, "역할")):
        if role in user.roles:
            await ctx.respond(f"{user.name}은(는) 이미 {role.name} 역할을 가지고 있습니다.")
        else:
            try:
                await user.add_roles(role)
            except discord.Forbidden:
                await ctx.respond(f"{user.name}에게 역할을 부여할 수 없습니다.")
            else:
                await ctx.respond(f"{user.name}에게 {role.name} 역할을 부여했습니다.")           
        
    @slash_command(description="사용자의 역할을 수동 제거합니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def removerole(self, ctx, user: Option(discord.Member, "사용자"), role: Option(discord.Role, "역할")):
        if role not in user.roles:
            await ctx.respond(f"{user.name}은(는) {role.name} 역할을 가지고 있지 않습니다.")
        else:
            try:
                await user.remove_roles(role)
            except discord.Forbidden:
                await ctx.respond(f"{user.name}의 역할을 제거할 수 없습니다.")
            else:
                await ctx.respond(f"{user.name}의 {role.name} 역할을 제거했습니다.")
               
    @slash_command(description="서버의 상태를 확인합니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def server(self, ctx):
        try:
            response = requests.get(f"{HOST}:{PORT}/users/")
        except requests.exceptions.ConnectionError:
            await ctx.respond("서버에 연결할 수 없습니다.")
        else:
            await ctx.respond(f"서버에 연결할 수 있습니다. ({response.status_code})")
     
    @slash_command(description="DB를 재작성합니다.", guild_ids=[GUILD_ID])
    @has_permissions(administrator=True)
    async def resetdb(self, ctx):
        await ctx.defer()
        
        everyone = ctx.guild.members
        
        for member in everyone:
            if requests.put(f"{HOST}:{PORT}/users/{member.id}/", 
                            data={
                                "id": member.id,
                                "nickname": member.display_name,
                                "name": member.name
                            }).status_code == 404:
                requests.post(f"{HOST}:{PORT}/users/", 
                              data={
                                  "id": member.id,
                                  "nickname": member.display_name,
                                  "name": member.name
                              })
            
        await ctx.respond("DB를 재작성했습니다.")
            
def setup(bot):
    bot.add_cog(Admin(bot))
    