class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(config['LINK_DATABASE'])

    @commands.command(name='setAdmin')
    @commands.has_guild_permissions(administrator=True)
    async def set_admin(self, ctx, admin_id: str, guild_id: str, id_history_deposit: str, id_history_buy: str, id_live_stock: str, id_log_purch: str, id_donation_log: str):
        admin_data = {
            'discord_id': admin_id,
            'guild_id': guild_id,
            'id_history_deposit': id_history_deposit,
            'id_history_buy': id_history_buy,
            'id_live_stock': id_live_stock,
            'id_log_purch': id_log_purch,
            'id_donation_log': id_donation_log
        }
        self.db.insert('admins', admin_data)
        await ctx.send(f"Admin {admin_id} telah ditambahkan untuk guild {guild_id}.")

    @commands.command(name='delAdmin')
    @commands.has_guild_permissions(administrator=True)
    async def del_admin(self, ctx, admin_id: str):
        self.db.delete('admins', {'discord_id': admin_id})
        await ctx.send(f"Akses admin {admin_id} telah dihapus.")

    @commands.command(name='showAdmin')
    @commands.has_guild_permissions(administrator=True)
    async def show_admin(self, ctx, admin_id: str):
        admin_data = self.db.find('admins', {'discord_id': admin_id})
        if admin_data:
            await ctx.send(f"Admin {admin_id} memiliki akses hingga {admin_data[0]['rental_time']}.")
        else:
            await ctx.send(f"Admin {admin_id} tidak ditemukan.")

    @commands.command(name='addTime')
    @commands.has_guild_permissions(administrator=True)
    async def add_time(self, ctx, admin_id: str, time: int):
        admin_data = self.db.find('admins', {'discord_id': admin_id})
        if admin_data:
            new_rental_time = admin_data[0]['rental_time'] + time
            self.db.update('admins', {'discord_id': admin_id}, {'rental_time': new_rental_time})
            await ctx.send(f"Waktu sewa untuk admin {admin_id} telah ditambah {time}.")

    # Tambahan validasi waktu sewa admin
    async def cog_check(self, ctx):
        admin_data = self.db.find('admins', {'discord_id': ctx.author.id})
        if not admin_data:
            await ctx.send("Anda tidak memiliki akses admin.")
            return False
        if 'rental_time' in admin_data[0] and admin_data[0]['rental_time'] <= 0:
            await ctx.send("Waktu sewa Anda telah habis.")
            return False
        return True

async def setup(bot):
    db = Database(config['LINK_DATABASE'])
    await bot.add_cog(OwnerCommands(bot))