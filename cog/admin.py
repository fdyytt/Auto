import discord
from discord.ext import commands
from main import db

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db

    def is_admin(self, ctx):
        # Mengambil daftar admin_ids dari database
        admin_ids = [admin[0] for admin in self.db.cursor.execute("SELECT discord_id FROM admins").fetchall()]
        return ctx.author.id in admin_ids or ctx.author.id == self.bot.owner_id

    @commands.command(name='addProduct')
    async def add_product(self, ctx, name_product: str, id_product: str, price: float):
        if self.is_admin(ctx):
            try:
                self.db.cursor.execute("INSERT INTO products (id, name, price, stock, description, admin_id) VALUES (?, ?, ?, 0, '', ?)", (id_product, name_product, price, ctx.author.id))
                self.db.conn.commit()
                await ctx.send(f'Product {name_product} dengan id {id_product} added with price {price}!')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='addStock')
    async def add_stock(self, ctx, id_product: str):
        if self.is_admin(ctx):
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
                if attachment.filename.endswith('.txt'):
                    await attachment.save("stock.txt")
                    with open("stock.txt", "r") as file:
                        stock = int(file.read())
                    product = self.db.cursor.execute("SELECT * FROM products WHERE id = ? AND admin_id = ?", (id_product, ctx.author.id)).fetchone()
                    if product:
                        new_stock = product[3] + stock
                        self.db.cursor.execute("UPDATE products SET stock = ? WHERE id = ? AND admin_id = ?", (new_stock, id_product, ctx.author.id))
                        self.db.conn.commit()
                        await ctx.send(f'Stock for product {id_product} updated to {new_stock}!')
                    else:
                        await ctx.send(f'Product {id_product} not found!')
                else:
                    await ctx.send("File attachment harus berupa file .txt!")
            else:
                await ctx.send("File attachment diperlukan untuk menambah stock!")
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='deleteProduct')
    async def delete_product(self, ctx, name_product: str):
        if self.is_admin(ctx):
            self.db.cursor.execute("DELETE FROM products WHERE name = ? AND admin_id = ?", (name_product, ctx.author.id))
            self.db.conn.commit()
            await ctx.send(f'Product {name_product} deleted!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='changePrice')
    async def change_price(self, ctx, name_product: str, new_price: float):
        if self.is_admin(ctx):
            self.db.cursor.execute("UPDATE products SET price = ? WHERE name = ? AND admin_id = ?", (new_price, name_product, ctx.author.id))
            self.db.conn.commit()
            await ctx.send(f'Price for {name_product} changed to {new_price}!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='setDescription')
    async def set_description(self, ctx, name_product: str, description: str):
        if self.is_admin(ctx):
            self.db.cursor.execute("UPDATE products SET description = ? WHERE name = ? AND admin_id = ?", (description, name_product, ctx.author.id))
            self.db.conn.commit()
            await ctx.send(f'Description for {name_product} updated!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

    @commands.command(name='setWorld')
    async def set_world(self, ctx, world: str, owner: str, bot: str):
        if self.is_admin(ctx):
            self.db.cursor.execute("UPDATE world_info SET world = ?, owner = ?, bot = ? WHERE admin_id = ?", (world, owner, bot, ctx.author.id))
            self.db.conn.commit()
            await ctx.send(f'World information updated!')
        else:
            await ctx.send("Anda tidak memiliki akses admin.")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
