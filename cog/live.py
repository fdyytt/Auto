import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import sqlite3
from main import config
import asyncio

# Inisialisasi database dengan konfigurasi
db_path = config['DEFAULT']['LINK_DATABASE']
conn = sqlite3.connect(db_path)

class Database:
    def __init__(self, conn):
        self.conn = conn

    def get_admin_data(self, admin_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE discord_id=?", (admin_id,))
        return cursor.fetchone()

    def get_all_products(self, table, admin_id, guild_id):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE admin_id=? AND guild_id=?", (admin_id, guild_id))
        return cursor.fetchall()

    def get_user_balance(self, grow_id, admin_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM balances WHERE grow_id=? AND admin_id=?", (grow_id, admin_id))
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_user_balance(self, grow_id, admin_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE balances SET balance = balance + ? WHERE grow_id = ? AND admin_id = ?", (amount, grow_id, admin_id))
        self.conn.commit()

    def update_product_stock(self, product_id, admin_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ? AND admin_id = ?", (amount, product_id, admin_id))
        self.conn.commit()

    def find_product(self, table, query):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ? AND admin_id = ?", (query["_id"], query["admin_id"]))
        return cursor.fetchone()

    def get_channel_id(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT channel_id FROM guilds WHERE guild_id=?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def log_purchase(self, grow_id, product_id, jumlah, total_harga, admin_id):
        sql = '''INSERT INTO transactions (grow_id, product_id, jumlah, total_harga, tanggal, admin_id)
                 VALUES (?, ?, ?, ?, datetime('now'), ?)'''
        cursor = self.conn.cursor()
        cursor.execute(sql, (grow_id, product_id, jumlah, total_harga, admin_id))
        self.conn.commit()

    def set_grow_id(self, grow_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM grow_ids WHERE grow_id=?", (grow_id,))
        if cursor.fetchone():
            return False
        cursor.execute("INSERT INTO grow_ids (grow_id, user_id) VALUES (?, ?)", (grow_id, user_id))
        self.conn.commit()
        return True

    def get_world_info(self, admin_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT world, owner, bot FROM world_info WHERE admin_id=?", (admin_id,))
        return cursor.fetchone()

    def get_grow_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT grow_id FROM grow_ids WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

db = Database(conn)

class BuyButton(Button):
    def __init__(self, label, product_id, style=discord.ButtonStyle.green):
        super().__init__(label=label, style=style)
        self.product_id = product_id

    async def callback(self, interaction: discord.Interaction):
        produk_data = db.find_product("products", {"_id": self.product_id, "admin_id": interaction.guild.owner_id})
        if produk_data is None:
            await interaction.response.send_message('Produk tidak ditemukan!', ephemeral=True)
            return
        produk_data = produk_data
        harga = produk_data[2]

        await interaction.response.send_message(f'Anda ingin membeli {produk_data[1]} dengan harga {harga} per unit. Berapa jumlah yang ingin Anda beli?', ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        msg = await self.view.bot.wait_for('message', check=check)
        try:
            jumlah = int(msg.content)
            if jumlah <= 0:
                raise ValueError("Jumlah harus lebih dari 0")
        except ValueError:
            await interaction.followup.send('Jumlah yang Anda masukkan tidak valid. Silakan coba lagi.', ephemeral=True)
            return

        total_harga = harga * jumlah
        grow_id = db.get_grow_id(interaction.user.id)
        if not grow_id:
            await interaction.followup.send('Anda belum mengatur Grow ID Anda. Gunakan tombol "Set Grow ID" untuk mengaturnya.', ephemeral=True)
            return

        user_balance = db.get_user_balance(grow_id, interaction.guild.owner_id)
        if user_balance < total_harga:
            await interaction.followup.send('Saldo tidak cukup!', ephemeral=True)
            return

        if produk_data[3] < jumlah:
            await interaction.followup.send('Stok tidak mencukupi!', ephemeral=True)
            return

        db.update_user_balance(grow_id, interaction.guild.owner_id, -total_harga)
        db.update_product_stock(self.product_id, interaction.guild.owner_id, -jumlah)
        db.log_purchase(grow_id, self.product_id, jumlah, total_harga, interaction.guild.owner_id)
        await interaction.followup.send(f'Anda telah membeli {jumlah} {produk_data[1]} dengan total harga {total_harga}!', ephemeral=True)

        # Kirimkan barang ke buyer
        buyer = interaction.user
        with open(f"results_{buyer.name}.txt", "w") as f:
            f.write(produk_data[4])  # Assuming deskripsi is the fifth column
        await buyer.send(file=discord.File(f"results_{buyer.name}.txt"))

        # Update stock embed
        produk_data = db.get_all_products("products", interaction.guild.owner_id, interaction.guild.id)
        user_balance = db.get_user_balance(grow_id, interaction.guild.owner_id)
        embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
        for produk in produk_data:
            embed.add_field(name=produk[1], value=f'Harga: {produk[2]}\nStock: {produk[3]}', inline=False)
        view = View()
        for produk in produk_data:
            button = BuyButton(label=produk[1], product_id=produk[0])
            view.add_item(button)
        view.add_item(SetGrowIDButton())
        view.add_item(WorldButton())
        view.add_item(BalanceButton())
        channel_id = db.get_channel_id(interaction.guild.id)
        channel = self.view.bot.get_channel(channel_id)
        await channel.send(embed=embed, view=view)

class SetGrowIDButton(Button):
    def __init__(self, label='Set Grow ID', style=discord.ButtonStyle.blurple):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('Masukkan Grow ID yang ingin Anda atur:', ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        msg = await self.view.bot.wait_for('message', check=check)
        grow_id = msg.content

        if db.set_grow_id(grow_id, interaction.user.id):
            await interaction.followup.send(f'Grow ID {grow_id} berhasil diatur!', ephemeral=True)
        else:
            await interaction.followup.send(f'Grow ID {grow_id} sudah ada di database dan tidak dapat digunakan.', ephemeral=True)

class WorldButton(Button):
    def __init__(self, label='World', style=discord.ButtonStyle.gray):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        world_info = db.get_world_info(interaction.guild.owner_id)
        if world_info:
            world_name, owner, bot = world_info
            await interaction.response.send_message(f'World: {world_name}\nOwner: {owner}\nBot: {bot}', ephemeral=True)
        else:
            await interaction.response.send_message('Data world tidak ditemukan.', ephemeral=True)

class BalanceButton(Button):
    def __init__(self, label='Balance', style=discord.ButtonStyle.green):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        grow_id = db.get_grow_id(interaction.user.id)
        if not grow_id:
            await interaction.response.send_message('Anda belum mengatur Grow ID Anda. Gunakan tombol "Set Grow ID" untuk mengaturnya.', ephemeral=True)
            return
        balance = db.get_user_balance(grow_id, interaction.guild.owner_id)
        await interaction.response.send_message(f'Saldo Anda: :WL: {balance}', ephemeral=True)

class LiveCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, ctx):
        admin_data = db.get_admin_data(ctx.author.id)
        return admin_data is not None

    @commands.command(name='world')
    async def world(self, ctx):
        if not self.is_admin(ctx):
            return
        admin_data = db.get_admin_data(ctx.author.id)
        if admin_data:
            world_name = admin_data[1]  # Assuming world_name is the second column
            owner = admin_data[2]  # Assuming owner is the third column
            bot_name = admin_data[3]  # Assuming bot_name is the fourth column
            await ctx.send(f'World: {world_name}\nOwner: {owner}\nBot: {bot_name}')
        else:
            await ctx.send('Data world tidak ditemukan.')

    @commands.command(name='stock')
    async def stock(self, ctx):
        if not self.is_admin(ctx):
            return
        produk_data = db.get_all_products("products", ctx.author.id, ctx.guild.id)
        grow_id = db.get_grow_id(ctx.author.id)
        user_balance = db.get_user_balance(grow_id, ctx.author.id) if grow_id else 0
        embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
        if produk_data:
            for produk in produk_data:
                embed.add_field(name=produk[1], value=f'Harga: {produk[2]}\nStock: {produk[3]}', inline=False)
        else:
            embed.add_field(name="No products available", value="Silakan tambahkan produk terlebih dahulu.", inline=False)
        view = View()
        for produk in produk_data:
            button = BuyButton(label=produk[1], product_id=produk[0])
            view.add_item(button)
        view.add_item(SetGrowIDButton())
        view.add_item(WorldButton())
        view.add_item(BalanceButton())
        await ctx.send(embed=embed, view=view)
        self.update_stock.start(ctx, embed, view)

    @tasks.loop(seconds=20)
    async def update_stock(self, ctx, embed, view):
        produk_data = db.get_all_products("products", ctx.author.id, ctx.guild.id)
        grow_id = db.get_grow_id(ctx.author.id)
        user_balance = db.get_user_balance(grow_id, ctx.author.id) if grow_id else 0
        embed.clear_fields()
        embed.description = f'Saldo Anda: :WL: {user_balance}'
        if produk_data:
            for produk in produk_data:
                embed.add_field(name=produk[1], value=f'Harga: {produk[2]}\nStock: {produk[3]}', inline=False)
        else:
            embed.add_field(name="No products available", value="Silakan tambahkan produk terlebih dahulu.", inline=False)
        await ctx.send(embed=embed, view=view)

    @update_stock.before_loop
    async def before_update_stock(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(LiveCommands(bot))
