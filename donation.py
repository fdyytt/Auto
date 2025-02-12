import discord
from discord.ext import commands
from balance import Balance
from database import Database

class Donation(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.balance_manager = Balance(db)

    def parse_webhook_message(self, message):
        lines = message.content.split('\n')
        grow_id = lines[0].split(': ')[1]
        amount, currency = lines[1].split(': ')[1].split(' ')
        return grow_id, float(amount), currency

    def get_donation_log_channel_id(self, admin_id):
        admin_data = self.db.get_admin_data(admin_id)
        return admin_data.get('id_donation_log')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.webhook_id:
            admin_id = str(message.author.id)
            donation_log_channel_id = self.get_donation_log_channel_id(admin_id)
            if donation_log_channel_id and message.channel.id == int(donation_log_channel_id):
                grow_id, amount, currency = self.parse_webhook_message(message)
                self.balance_manager.update_balance(grow_id, admin_id, amount, currency)
                updated_balance = self.balance_manager.get_balance(grow_id, admin_id)
                await message.channel.send(f"Deposit berhasil! Saldo {grow_id} telah diperbarui dengan {updated_balance['balance']} WL.")

async def setup(bot):
    db = Database(config['LINK_DATABASE'])
    await bot.add_cog(Donation(bot, db))