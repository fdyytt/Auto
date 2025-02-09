import discord
from discord.ext import commands
from database import Database, load_config

# Membaca konfigurasi dari file config.txt dengan validasi
config = load_config('config.txt')

class AdminCommands(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db

    @commands.command(name='addProduct')
    async def add_product(self, ctx, name: str, price: float):
        product = {"name": name, "price": price, "stock": 0, "description": "", "admin_id": ctx.author.id}
        self.db.insert_product("products", product)
        await ctx.send(f'Product {name} added with price {price}!')

    @commands.command(name='addStock')
    async def add_stock(self, ctx, name: str, stock: int):
        product = self.db.find_product("products", {"name": name, "admin_id": ctx.author.id})
        if product:
            new_stock = product["stock"] + stock
            self.db.update_product("products", {"name": name, "admin_id": ctx.author.id}, {"stock": new_stock})
            await ctx.send(f'Stock for {name} updated to {new_stock}!')
        else:
            await ctx.send(f'Product {name} not found!')

    @commands.command(name='deleteProduct')
    async def delete_product(self, ctx, name: str):
        self.db.delete_product("products", {"name": name, "admin_id": ctx.author.id})
        await ctx.send(f'Product {name} deleted!')

    @commands.command(name='changePrice')
    async def change_price(self, ctx, name: str, new_price: float):
        self.db.update_product("products", {"name": name, "admin_id": ctx.author.id}, {"price": new_price})
        await ctx.send(f'Price for {name} changed to {new_price}!')

    @commands.command(name='setDescription')
    async def set_description(self, ctx, name: str, description: str):
        self.db.update_product("products", {"name": name, "admin_id": ctx.author.id}, {"description": description})
        await ctx.send(f'Description for {name} updated!')

    @commands.command(name='setWorld')
    async def set_world(self, ctx, world: str, owner: str, bot: str):
        world_info = {"world": world, "owner": owner, "bot": bot, "admin_id": ctx.author.id}
        self.db.update_world_info("world_info", world_info)
        await ctx.send(f'World information updated!')

    @commands.command(name='send')
    async def send_product(self, ctx, user: str, product: str, count: int):
        product_info = self.db.find_product("products", {"name": product, "admin_id": ctx.author.id})
        if product_info and product_info["stock"] >= count:
            self.db.update_product("products", {"name": product, "admin_id": ctx.author.id}, {"stock": product_info["stock"] - count})
            await ctx.send(f'Sent {count} {product} to {user}!')
        else:
            await ctx.send(f'Not enough stock for {product}!')

    @commands.command(name='addBal')
    async def add_balance(self, ctx, user: str, balance: float):
        user_info = self.db.find_user("users", {"name": user, "admin_id": ctx.author.id})
        if user_info:
            new_balance = user_info["balance"] + balance
            self.db.update_user("users", {"name": user, "admin_id": ctx.author.id}, {"balance": new_balance})
            await ctx.send(f'Balance for {user} updated to {new_balance}!')

    @commands.command(name='reduceBal')
    async def reduce_balance(self, ctx, user: str, balance: float):
        user_info = self.db.find_user("users", {"name": user, "admin_id": ctx.author.id})
        if user_info:
            new_balance = user_info["balance"] - balance
            self.db.update_user("users", {"name": user, "admin_id": ctx.author.id}, {"balance": new_balance})
            await ctx.send(f'Balance for {user} updated to {new_balance}!')

async def setup(bot):
    db = Database(config['LINK_DATABASE'], 'discord_bot')
    await bot.add_cog(AdminCommands(bot, db))