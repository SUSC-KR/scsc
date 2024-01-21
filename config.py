import os
from dotenv import load_dotenv

load_dotenv()

BOT_Name = 'SCSC'
BOT_ID = 1167322596681981952
BOT_COLOR = 0x6D71F9
BOT_VER = 'SCSC#3697 | v0.0.1'
EXTENSIONS = ['cogs.admin', 'cogs.user', 'cogs.music']

GUILD_ID = os.getenv("GUILD_ID")
