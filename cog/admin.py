import discord
from discord.ext import commands
from database import Database
from config import load_config

# Membaca konfigurasi dari file config.txt dengan validasi
config = load_config('config.txt')

class AdminCommands(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db

    @commands.command(name='addProduct')
    async def add_product(self, ctx, name_product: str, price: float):
        product = {"name": name_product, "price": price, "stock": 0, "description": "", "admin_id": ctx.author.id}
        self.db.insert("products", product)
        await ctx.send(f'Product {name_product} added with price {price}!')

    @commands.command(name='addStock')
    async def add_stock(self, ctx, name_product: str, stock: int):
        product = self.db.find_product("products", {"name": name_product, "admin_id": ctx.author.id})
        if product:
            new_stock = product[3] + stock  # Assuming stock is the 4th column
            self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"stock": new_stock})
            await ctx.send(f'Stock for {name_product} updated to {new_stock}!')
        else:
            await ctx.send(f'Product {name_product} not found!')

    @commands.command(name='deleteProduct')
    async def delete_product(self, ctx, name_product: str):
        self.db.delete("products", {"name": name_product, "admin_id": ctx.author.id})
        await ctx.send(f'Product {name_product} deleted!')

    @commands.command(name='changePrice')
    async def change_price(self, ctx, name_product: str, new_price: float):
        self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"price": new_price})
        await ctx.send(f'Price for {name_product} changed to {new_price}!')

    @commands.command(name='setDescription')
    async def set_description(self, ctx, name_product: str, description: str):
        self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"description": description})
        await ctx.send(f'Description for {name_product} updated!')

    @commands.command(name='setWorld')
    async def set_world(self, ctx, world: str, owner: str, bot: str):
        world_info = {"world": world, "owner": owner, "bot": bot, "admin_id": ctx.author.id}
        self.db.update("world_info", {"world": world, "admin_id": ctx.author.id}, world_info)
        await ctx.send(f'World information updated!')

    @commands.command(name='send')
    async def send_product(self, ctx, grow_id: str, product: str, count: int):
        product_info = self.db.find_product("products", {"name": product, "admin_id": ctx.author.id})
        if product_info and product_info[3] >= count:  # Assuming stock is the 4th column
            new_stock = product_info[3] - count
            self.db.update("products", {"name": product, "admin_id": ctx.author.id}, {"stock": new_stock})
            await ctx.send(f'Sent {count} {product} to {grow_id}!')
        else:
            await ctx.send(f'Not enough stock for {product}!')

    @commands.command(name='addBal')
    async def add_balance(self, ctx, grow_id: str, balance: float):
        user_info = self.db.find("balances", {"grow_id": grow_id, "admin_id": ctx.author.id})
        if user_info:
            new_balance = user_info[0][1] + balance  # Assuming balance is the 2nd column
            self.db.update("balances", {"grow_id": grow_id, "admin_id": ctx.author.id}, {"balance": new_balance})
            await ctx.send(f'Balance for {grow_id} updated to {new_balance}!')

    @commands.command(name='reduceBal')
    async def reduce_balance(self, ctx, grow_id: str, balance: float):
        user_info = self.db.find("balances", {"grow_id": grow_id, "admin_id": ctx.author.id})
        if user_info:
            new_balance = user_info[0][1] - balance  # Assuming balance is the 2nd column
            self.db.update("balances", {"grow_id": grow_id, "admin_id": ctx.author.id}, {"balance": new_balance})
            await ctx.send(f'Balance for {grow_id} updated to {new_balance}!')

async def setup(bot):
    db = Database(config['LINK_DATABASE'])
    await bot.add_cog(AdminCommands(bot, db))