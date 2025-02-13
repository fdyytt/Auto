import discord
from discord.ext import commands
from live import db, BuyButton, Database  # Pastikan Database diimpor dari live.py
from discord.ui import View

class AdminCommands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def is_admin(self, ctx):
        return ctx.author.id in self.db.get_admin_ids()

    @commands.command(name='addProduct')
    async def add_product(self, ctx, name_product: str, price: float):
        if self.is_admin(ctx):
            try:
                product = {"name": name_product, "price": price, "stock": 0, "description": ""}
                self.db.insert("products", product)
                await ctx.send(f'Product {name_product} added with price {price}!')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='addStock')
    async def add_stock(self, ctx, name_product: str, stock: int):
        if self.is_admin(ctx):
            product = self.db.find_product("products", {"name": name_product, "admin_id": ctx.author.id})
            if product:
                new_stock = product[3] + stock
                self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"stock": new_stock})
                await ctx.send(f'Stock for {name_product} updated to {new_stock}!')
            else:
                await ctx.send(f'Product {name_product} not found!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='deleteProduct')
    async def delete_product(self, ctx, name_product: str):
        if self.is_admin(ctx):
            self.db.delete("products", {"name": name_product, "admin_id": ctx.author.id})
            await ctx.send(f'Product {name_product} deleted!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='changePrice')
    async def change_price(self, ctx, name_product: str, new_price: float):
        if self.is_admin(ctx):
            self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"price": new_price})
            await ctx.send(f'Price for {name_product} changed to {new_price}!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='setDescription')
    async def set_description(self, ctx, name_product: str, description: str):
        if self.is_admin(ctx):
            self.db.update("products", {"name": name_product, "admin_id": ctx.author.id}, {"description": description})
            await ctx.send(f'Description for {name_product} set to {description}!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot, db))