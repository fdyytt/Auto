import os
import json
import discord
from discord.ext import commands
import asyncio
import time
import datetime
import random
import string
import re

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_file_path(file_name):
    return os.path.join(os.getcwd(), file_name)

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def is_valid_url(url):
    return re.match(r'https?://[^\s]+', url) is not None

def is_valid_email(email):
    return re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email) is not None

def get_discord_user(bot, user_id):
    return bot.get_user(user_id)

def get_discord_member(guild, member_id):
    return guild.get_member(member_id)

def get_discord_channel(bot, channel_id):
    return bot.get_channel(channel_id)

def get_discord_role(guild, role_id):
    return guild.get_role(role_id)

def send_embed(ctx, title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    return ctx.send(embed=embed)

def send_message(ctx, message):
    return ctx.send(message)

def send_file(ctx, file_path, file_name):
    return ctx.send(file=discord.File(file_path, file_name))

def delete_message(message):
    return message.delete()

def add_reaction(message, reaction):
    return message.add_reaction(reaction)

def remove_reaction(message, reaction):
    return message.remove_reaction(reaction)

def clear_reactions(message):
    return message.clear_reactions()