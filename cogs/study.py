import discord
import asyncio
from discord.ext.commands import Cog, has_permissions
from discord.commands import slash_command, Option
from discord.ui import Modal, InputText

import json
import requests

from config import *

from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

class UpdateModal(Modal):
    def __init__(self, study_name, study_mentor, category):
        super().__init__(title="스터디 정보 수정")
        self.study_name = study_name
        self.study_mentor = study_mentor
        self.category = category
        
        self.add_item(InputText(label="스터디 이름", placeholder="수정할 스터디 이름을 입력하세요."))
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=False)
        
        await self.category.edit(name=self.children[0].value)
        
        study_role = discord.utils.get(interaction.guild.roles, name=f"{self.study_name}-{self.study_mentor.name}")
        await study_role.edit(name=f"{self.children[0].value}-{self.study_mentor.name}")
        
        requests.put(f"{HOST}:{PORT}/studies/{self.category.id}/", 
                                data=json.dumps({
                                    "id": self.category.id,
                                    "name": self.children[0].value,
                                    "mentor": self.study_mentor.id
                                }),
                                headers={"Content-Type": "application/json"})
        
        embed = discord.Embed(title="스터디 정보 수정", color=BOT_COLOR)
        embed.add_field(name="수정 전 스터디 이름", value=self.study_name)
        embed.add_field(name="수정 후 스터디 이름", value=self.children[0].value)
        embed.set_footer(text=BOT_VER)
        
        await interaction.followup.send(embed=embed)

def check_study_verification(func):
    async def wrapper(ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토"), category = None):
        category = discord.utils.get(ctx.guild.categories, name=study_name)
        mentor_id = requests.get(f"{HOST}:{PORT}/studies/{category.id}/").json()["study"]["mentor"]
        
        if category is not None and mentor_id == study_mentor.id:
            return await func(ctx, study_name, study_mentor, category)
        else:
            await ctx.respond("스터디가 존재하지 않거나 멘토가 아닙니다.")
    return wrapper

async def open_study(ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토")):
    study_role = discord.utils.get(ctx.guild.roles, name=f"{study_name}-{study_mentor.name}")
    
    if study_role is None:
        await ctx.defer()
        
        if "-" in study_name:
            await ctx.respond("스터디 이름에 '-'를 포함할 수 없습니다.")
            return
        
        await study_mentor.add_roles(discord.utils.get(ctx.guild.roles, name="스터디 멘토"))
        
        category = await ctx.guild.create_category(name=study_name, position=len(ctx.guild.categories)-2)
        
        study_role = await ctx.guild.create_role(name=f"{study_name}-{study_mentor.name}", color=0xBF00FF)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
            study_mentor:           discord.PermissionOverwrite(read_messages=True, connect=True, 
                                                                manage_channels=True, mute_members=True),
            study_role:             discord.PermissionOverwrite(read_messages=True, connect=True)
        }
        await category.edit(overwrites=overwrites)
        await study_mentor.add_roles(study_role)
        
        chat_channel = [("📢공지",      f"{study_name} 스터디 공지방입니다."), 
                        ("💬자유",      f"{study_name} 스터디 자유방입니다."), 
                        ("📂자료실",    f"{study_name} 스터디 자료실입니다."), 
                        ("❓질문",      f"{study_name} 스터디 질문방입니다. 궁금한 점을 질문해주세요!"),
                        ]
        voice_channel = ["📝스터디방", "📞자유"]
        
        for channel_info in chat_channel:
            channel = await ctx.guild.create_text_channel(name=channel_info[0], category=category)
            await channel.edit(topic=channel_info[1], sync_permissions=True)
        
        for channel_name in voice_channel:
            channel = await ctx.guild.create_voice_channel(name=channel_name, category=category)
            await channel.edit(sync_permissions=True)
            
        requests.post(f"{HOST}:{PORT}/studies/", data={"id": category.id, "name": study_name, "mentor": study_mentor.id})
    
        await ctx.respond(f"{study_name} 스터디를 개설했습니다.")
    
    else:
        await ctx.respond("스터디가 이미 존재합니다.")
        
@check_study_verification
async def edit_study(ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토"), category=None):
    category = discord.utils.get(ctx.guild.categories, name=study_name)
    
    update_modal = UpdateModal(study_name, study_mentor, category)
    
    await ctx.response.send_modal(update_modal)
        
@check_study_verification
async def close_study(ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토"), category):
    await ctx.defer()
    
    category = discord.utils.get(ctx.guild.categories, name=study_name)
    
    for channel in category.channels:
        await channel.delete()
    await category.delete()
    
    study_role = discord.utils.get(ctx.guild.roles, name=f"{study_name}-{study_mentor.name}")
    await study_role.delete()
    
    requests.delete(f"{HOST}:{PORT}/studies/{category.id}/")
    
    await ctx.respond(f"{study_name} 스터디를 폐쇄했습니다.")

@check_study_verification
async def query_study_info(ctx, study_name: Option(str, "스터디 이름"), study_mentor: Option(discord.Member, "스터디 멘토"), category):
    study_student_count = len(requests.get(f"{HOST}:{PORT}/studies/{category.id}/").json()["studyRegistration"])

    study_embed = discord.Embed(title=f"{study_name} 스터디 정보", 
                                description=f"**멘토**: {study_mentor.mention}\n \
                                **학생 수**: {study_student_count}명",
                                color=BOT_COLOR)
    study_embed.set_thumbnail(url=study_mentor.avatar)
    study_embed.set_footer(text=BOT_VER)

    await ctx.respond(embed=study_embed)
    