import sys
import os
import discord
import sqlite3
from discord.ext import commands
import asyncio
import logging
import logging.config
from balance import Balance
from load_config import load_config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        }
    },
    'loggers': {
        __name__: {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
})

logger = logging.getLogger(__name__)

#Membaca konfigurasi dari file config.txt dengan validasi
config = load_config('config.txt')
logger.debug("Konfigurasi telah dibaca")

#Inisialisasi intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
logger.debug("Intents telah diinisialisasi")

#Definisi kelas Database
class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

#Inisialisasi bot
bot = commands.Bot(command_prefix='!', intents=intents)
logger.debug("Bot telah diinisialisasi")

#Koneksi ke database
try:
    db_path = config.get('LINK_DATABASE')
    if db_path is None:
        logger.error("LINK_DATABASE tidak ditemukan dalam konfigurasi")
        print("LINK_DATABASE tidak ditemukan dalam konfigurasi")
    else:
        db = Database(db_path)
        logger.debug("Koneksi ke database telah berhasil")
except Exception as e:
    logger.error(f'Failed to connect to the database: {type(e).__name__} - {e}')
    print(f'Failed to connect to the database: {type(e).__name__} - {e}')
    raise

#Memuat cogs
initial_extensions = [
    'cog.admin',
    'cog.live',
    'cog.owner',
    'cog.donation'
]

@bot.event
async def on_ready():
    logger.info(f'Bot is ready. Logged in as {bot.user.name} ({bot.user.id})')
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.event
async def on_command_error(ctx, error):
    logger.error(f'Error in command {ctx.command}: {type(error).__name__} - {error}')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Bad argument.')
    else:
        await ctx.send('An error occurred while executing the command.')

async def main():
    # Memuat extensions
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f'Loaded extension: {extension}')
            print(f'Loaded extension: {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}: {type(e).__name__} - {e}')
            print(f'Failed to load extension {extension}: {type(e).__name__} - {e}')

    # Menjalankan bot
    try:
        await bot.start(config['DISCORD_TOKEN'])
    except Exception as e:
        logger.error(f'Failed to start bot: {type(e).__name__} - {e}')
        print(f'Failed to start bot: {type(e).__name__} - {e}')

if __name__ == '__main__':
    asyncio.run(main())