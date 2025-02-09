import discord
from discord.ext import commands
from discord.ui import View, Button
import sqlite3
from .config import load_config
# Inisialisasi intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Inisialisasi bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Membaca konfigurasi dari file config.txt
config = load_config('../../config.txt')

# Inisialisasi database dengan konfigurasi
db_path = config['LINK_DATABASE']
conn = sqlite3.connect(db_path)

class Database:
    def __init__(self, conn):
        self.conn = conn

    def get_admin_data(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE user_id=?", (user_id,))
        return cursor.fetchone()

    def get_all_products(self, table, admin_id):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE admin_id=?", (admin_id,))
        return cursor.fetchall()

    def get_user_balance(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_user_balance(self, user_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        self.conn.commit()

    def update_product_stock(self, product_id, quantity):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
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

db = Database(conn)

# World command
@bot.command(name='world')
async def world(ctx):
    admin_data = db.get_admin_data(ctx.author.id)
    if admin_data:
        world_name = admin_data[1]  # Assuming world_name is the second column
        owner = admin_data[2]  # Assuming owner is the third column
        bot_name = admin_data[3]  # Assuming bot_name is the fourth column
        await ctx.send(f'World: {world_name}\nOwner: {owner}\nBot: {bot_name}')
    else:
        await ctx.send('Data world tidak ditemukan.')

# Stock command
@bot.command(name='stock')
async def stock(ctx):
    if ctx.author.guild_permissions.administrator:
        produk_data = db.get_all_products("products", ctx.guild.owner_id)
        user_balance = db.get_user_balance(ctx.author.id)
        embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
        for produk in produk_data:
            embed.add_field(name=produk[1], value=f'Harga: {produk[2]}\nStock: {produk[3]}', inline=False)
        view = View()
        for produk in produk_data:
            button = Button(label=produk[1], style=discord.ButtonStyle.green)
            button.custom_id = f'beli_{produk[0]}'
            view.add_item(button)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send('Anda tidak memiliki akses untuk menjalankan command ini!')

# Event on interaction
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.custom_id.startswith('beli_'):
            produk_id = interaction.data.custom_id.split('_')[1]
            produk_data = db.find_product("products", {"_id": produk_id, "admin_id": interaction.guild.owner_id})
            if produk_data is None:
                await interaction.response.send_message('Produk tidak ditemukan!', ephemeral=True)
                return
            produk_data = produk_data
            harga = produk_data[2]
            
            await interaction.response.send_message(f'Anda ingin membeli {produk_data[1]} dengan harga {harga} per unit. Berapa jumlah yang ingin Anda beli?', ephemeral=True)

            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel

            msg = await bot.wait_for('message', check=check)
            try:
                jumlah = int(msg.content)
                if jumlah <= 0:
                    raise ValueError("Jumlah harus lebih dari 0")
            except ValueError:
                await interaction.followup.send('Jumlah yang Anda masukkan tidak valid. Silakan coba lagi.', ephemeral=True)
                return

            total_harga = harga * jumlah
            user_balance = db.get_user_balance(interaction.user.id)
            if user_balance < total_harga:
                await interaction.followup.send('Saldo tidak cukup!', ephemeral=True)
                return
            
            if produk_data[3] < jumlah:
                await interaction.followup.send('Stok tidak mencukupi!', ephemeral=True)
                return

            db.update_user_balance(interaction.user.id, -total_harga)
            db.update_product_stock(produk_id, -jumlah)
            await interaction.followup.send(f'Anda telah membeli {jumlah} {produk_data[1]} dengan total harga {total_harga}!', ephemeral=True)

            # Kirimkan barang ke buyer
            buyer = interaction.user
            with open(f"results_{buyer.name}.txt", "w") as f:
                f.write(produk_data[4])  # Assuming deskripsi is the fifth column
            await buyer.send(file=discord.File(f"results_{buyer.name}.txt"))

            # Update stock embed
            produk_data = db.get_all_products("products", interaction.guild.owner_id)
            user_balance = db.get_user_balance(interaction.user.id)
            embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
            for produk in produk_data:
                embed.add_field(name=produk[1], value=f'Harga: {produk[2]}\nStock: {produk[3]}', inline=False)
            view = View()
            for produk in produk_data:
                button = Button(label=produk[1], style=discord.ButtonStyle.green)
                button.custom_id = f'beli_{produk[0]}'
                view.add_item(button)
            channel_id = db.get_channel_id(interaction.guild.id)
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed, view=view)

async def update_live_stock():
    for guild in bot.guilds:
        # Logika untuk memperbarui stok secara live
        pass

# Menjalankan bot
bot.run(config['DISCORD_TOKEN'])