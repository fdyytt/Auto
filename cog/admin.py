import discord
from discord.ext import commands
from main import config
import sqlite3

# Inisialisasi database dengan konfigurasi
db_path = config['DEFAULT']['LINK_DATABASE']
conn = sqlite3.connect(db_path)

class Database:
    def __init__(self, conn):
        self.conn = conn

    def set_admin(self, admin_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO admins (discord_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log, rental_time_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (admin_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log, 0))
        self.conn.commit()

    def del_admin(self, admin_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM admins WHERE discord_id=?", (admin_id,))
        self.conn.commit()

    def show_admin(self, admin_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE discord_id=?", (admin_id,))
        return cursor.fetchone()

    def add_time(self, admin_id, days):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE admins SET rental_time_days = rental_time_days + ? WHERE discord_id=?", (days, admin_id))
        self.conn.commit()

db = Database(conn)

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == self.bot.owner_id

    @commands.command(name='setAdmin')
    async def set_admin(self, ctx, admin_id: int, guild_id: int, id_history_buy: int, id_live_stock: int, id_log_purch: int, id_donation_log: int):
        if self.is_owner(ctx):
            db.set_admin(admin_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log)
            await ctx.send(f'Admin {admin_id} has been set for guild {guild_id}.')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='delAdmin')
    async def del_admin(self, ctx, admin_id: int):
        if self.is_owner(ctx):
            db.del_admin(admin_id)
            await ctx.send(f'Admin {admin_id} has been removed.')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='showAdmin')
    async def show_admin(self, ctx, admin_id: int):
        if self.is_owner(ctx):
            admin_data = db.show_admin(admin_id)
            if admin_data:
                await ctx.send(f'Admin ID: {admin_data[0]}\nGuild ID: {admin_data[1]}\nHistory Buy ID: {admin_data[2]}\nLive Stock ID: {admin_data[3]}\nLog Purchase ID: {admin_data[4]}\nDonation Log ID: {admin_data[5]}\nRental Time (days): {admin_data[6]}')
            else:
                await ctx.send(f'Admin {admin_id} not found.')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='addTime')
    async def add_time(self, ctx, admin_id: int, days: int):
        if self.is_owner(ctx):
            db.add_time(admin_id, days)
            await ctx.send(f'Rental time for admin {admin_id} has been increased by {days} days.')
        else:
            await ctx.send("You do not have permission to use this command.")

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))