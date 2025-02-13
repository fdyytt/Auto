import discord
from discord.ext import commands
from main import db

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db

    def is_owner(self, ctx):
        return ctx.author.id == self.bot.owner_id

    @commands.command(name='setAdmin')
    async def set_admin(self, ctx, admin_id: int, guild_id: int, id_history_buy: int, id_live_stock: int, id_log_purch: int, id_donation_log: int):
        if self.is_owner(ctx):
            try:
                self.db.cursor.execute('''
                INSERT INTO admins (discord_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log, rental_time_days)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(discord_id) DO UPDATE SET
                guild_id=excluded.guild_id,
                id_history_buy=excluded.id_history_buy,
                id_live_stock=excluded.id_live_stock,
                id_log_purch=excluded.id_log_purch,
                id_donation_log=excluded.id_donation_log
                ''', (admin_id, guild_id, id_history_buy, id_live_stock, id_log_purch, id_donation_log))
                self.db.conn.commit()
                await ctx.send(f'Admin {admin_id} has been set for guild {guild_id}.')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='delAdmin')
    async def del_admin(self, ctx, admin_id: int):
        if self.is_owner(ctx):
            try:
                self.db.cursor.execute("DELETE FROM admins WHERE discord_id = ?", (admin_id,))
                self.db.conn.commit()
                await ctx.send(f'Admin {admin_id} has been removed.')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='showAdmin')
    async def show_admin(self, ctx, admin_id: int):
        if self.is_owner(ctx):
            try:
                admin_data = self.db.cursor.execute("SELECT * FROM admins WHERE discord_id = ?", (admin_id,)).fetchone()
                if admin_data:
                    await ctx.send(f'Admin ID: {admin_data[0]}\nGuild ID: {admin_data[1]}\nHistory Buy ID: {admin_data[2]}\nLive Stock ID: {admin_data[3]}\nLog Purchase ID: {admin_data[4]}\nDonation Log ID: {admin_data[5]}\nRental Time (days): {admin_data[6]}')
                else:
                    await ctx.send(f'Admin {admin_id} not found.')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name='addTime')
    async def add_time(self, ctx, admin_id: int, days: int):
        if self.is_owner(ctx):
            try:
                self.db.cursor.execute("UPDATE admins SET rental_time_days = rental_time_days + ? WHERE discord_id = ?", (days, admin_id))
                self.db.conn.commit()
                await ctx.send(f'Rental time for admin {admin_id} has been increased by {days} days.')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("You do not have permission to use this command.")

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))