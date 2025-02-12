import discord
from discord.ext import commands
from database import Database
from main import config
import datetime
import asyncio

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(config['LINK_DATABASE'])
        self.check_rental_time_task = None

    async def setup_hook(self):
        self.check_rental_time_task = self.bot.loop.create_task(self.check_rental_time())

    async def cog_unload(self):
        if self.check_rental_time_task:
            self.check_rental_time_task.cancel()
    @commands.command(name='setAdmin')
    @commands.is_owner()
    async def set_admin(self, ctx, admin_id: str, guild_id: str, id_history_deposit: str, id_history_buy: str, id_live_stock: str, id_log_purch: str, id_donation_log: str):
        admin_data = {
            'discord_id': admin_id,
            'guild_id': guild_id,
            'id_history_deposit': id_history_deposit,
            'id_history_buy': id_history_buy,
            'id_live_stock': id_live_stock,
            'id_log_purch': id_log_purch,
            'id_donation_log': id_donation_log,
            'rental_time': 0,
            'can_use_commands': True
        }
        self.db.insert('admins', admin_data)
        await ctx.send(f"Admin {admin_id} telah ditambahkan untuk guild {guild_id}.")

    @commands.command(name='delAdmin')
    @commands.is_owner()
    async def del_admin(self, ctx, admin_id: str):
        self.db.delete('admins', {'discord_id': admin_id})
        await ctx.send(f"Akses admin {admin_id} telah dihapus.")

    @commands.command(name='showAdmin')
    @commands.is_owner()
    async def show_admin(self, ctx, admin_id: str):
        admin_data = self.db.find('admins', {'discord_id': admin_id})
        if admin_data:
            await ctx.send(f"Admin {admin_id} memiliki akses hingga {admin_data[0]['rental_time']}.")
        else:
            await ctx.send(f"Admin {admin_id} tidak ditemukan.")

    @commands.command(name='addTime')
    @commands.is_owner()
    async def add_time(self, ctx, admin_id: str, time: int):
        admin_data = self.db.find('admins', {'discord_id': admin_id})
        if admin_data:
            new_rental_time = admin_data[0]['rental_time'] + time
            self.db.update('admins', {'discord_id': admin_id}, {'rental_time': new_rental_time})
            await ctx.send(f"Waktu sewa untuk admin {admin_id} telah ditambah {time}.")
        else:
            await ctx.send(f"Admin {admin_id} tidak ditemukan.")

    async def cog_check(self, ctx):
        return ctx.author.id == config['OWNER_ID']

    async def check_rental_time(self):
        try:
            while True:
                admins = self.db.find('admins', {})
                for admin in admins:
                    rental_time = admin['rental_time']
                    current_time = datetime.datetime.now().timestamp()
                    if rental_time - current_time <= 3 * 24 * 60 * 60:
                        admin_user = self.bot.get_user(admin['discord_id'])
                        if admin_user:
                            await admin_user.send("Waktu sewa Anda akan habis dalam waktu 3 hari. Silakan perpanjang sewa Anda.")
                    if rental_time - current_time <= 0:
                        self.db.update('admins', {'discord_id': admin['discord_id']}, {'can_use_commands': False})
                await asyncio.sleep(60 * 60)  # Jalankan setiap 1 jam
        except Exception as e:
            print(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))