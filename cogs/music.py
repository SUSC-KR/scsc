import discord
import asyncio
from discord.ext.commands import Cog, has_permissions
from discord.commands import slash_command, Option

import yt_dlp as youtube_dl
import os

from config import *

class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @slash_command(description="음악을 재생합니다.", guild_ids=[GUILD_ID])
    async def play(self, ctx, url: Option(str, "URL")):
        if ctx.author.voice is None:
            await ctx.respond("음성 채널에 먼저 들어가주세요.")
        else:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            
            await ctx.defer()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            }
            
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    info = ydl.extract_info(url, download=False)
                    title = info["title"]
                    thumbnail = info["thumbnail"]
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")
                        
                voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
                
                play_embed = discord.Embed(title="음악 재생", description="음악을 재생합니다.", color=BOT_COLOR)
                play_embed.set_thumbnail(url=thumbnail)
                play_embed.add_field(name="제목", value=title, inline=False)
                play_embed.set_footer(text=BOT_VER)
                
                await ctx.respond(embed=play_embed)
                
                voice.play(discord.FFmpegPCMAudio("song.mp3"))
                voice.volume = 100
            except:
                await ctx.respond("음악을 재생할 수 없습니다.")

    @slash_command(description="음악을 일시정지합니다.", guild_ids=[GUILD_ID])
    async def pause(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice.is_playing():
            voice.pause()
            await ctx.respond("음악을 일시정지합니다.")
        else:
            await ctx.respond("음악이 재생 중이 아닙니다.")
            
    @slash_command(description="음악을 다시 재생합니다.", guild_ids=[GUILD_ID])
    async def resume(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice.is_paused():
            voice.resume()
            await ctx.respond("음악을 다시 재생합니다.")
        else:
            await ctx.respond("음악이 일시정지 중이 아닙니다.")
                
    @slash_command(description="재생을 종료합니다.", guild_ids=[GUILD_ID])
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice.is_playing() or voice.is_connected():
            voice.stop()
            await voice.disconnect()
            await ctx.respond("음악을 종료합니다.")
        else:
            await ctx.respond("음악이 재생 중이 아닙니다.")
            
def setup(bot):
    bot.add_cog(Music(bot))
    