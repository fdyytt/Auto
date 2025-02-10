import json
import os
import logging
import sqlite3

def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            config_lines = f.readlines()
            if len(config_lines) < 2:
                raise ValueError("Config file must contain at least two lines")
            config = [line.strip() for line in config_lines]
            return {
                'DISCORD_TOKEN': config[0].split('=')[1].strip('\"'),
                'LINK_DATABASE': config[1].split('=')[1].strip('\"'),
            }
    except IndexError as e:
        logging.error(f"Failed to load config: {type(e).__name__} - {e}. Please check the format of the config file.")
        raise
    except Exception as e:
        logging.error(f"Failed to load config: {type(e).__name__} - {e}")
        raise

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE,
                world_name TEXT,
                owner TEXT,
                bot_name TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                nama TEXT,
                harga INTEGER,
                stock INTEGER,
                deskripsi TEXT,
                FOREIGN KEY (admin_id) REFERENCES admins(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                user_id TEXT PRIMARY KEY,
                balance INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                guild_id TEXT PRIMARY KEY,
                channel_id TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                product_id INTEGER,
                jumlah INTEGER,
                total_harga INTEGER,
                tanggal DATETIME,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        self.conn.commit()

    def insert(self, collection, data):
        if collection == "admins":
            self.cursor.execute('''
                INSERT INTO admins (discord_id, world_name, owner, bot_name) VALUES (?, ?, ?, ?)
            ''', (data['discord_id'], data['world_name'], data['owner'], data['bot_name']))
        elif collection == "products":
            self.cursor.execute('''
                INSERT INTO products (admin_id, nama, harga, stock, deskripsi) VALUES (?, ?, ?, ?, ?)
            ''', (data['admin_id'], data['nama'], data['harga'], data['stock'], data['deskripsi']))
        elif collection == "balances":
            self.cursor.execute('''
                INSERT INTO balances (user_id, balance) VALUES (?, ?)
            ''', (data['user_id'], data['balance']))
        elif collection == "channels":
            self.cursor.execute('''
                INSERT INTO channels (guild_id, channel_id) VALUES (?, ?)
            ''', (data['guild_id'], data['channel_id']))
        elif collection == "transactions":
            self.cursor.execute('''
                INSERT INTO transactions (user_id, product_id, jumlah, total_harga, tanggal) VALUES (?, ?, ?, ?, ?)
            ''', (data['user_id'], data['product_id'], data['jumlah'], data['total_harga'], data['tanggal']))
        self.conn.commit()

    def find(self, collection, query):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        self.cursor.execute(f'SELECT * FROM {collection} WHERE {query_string}', tuple(query.values()))
        return self.cursor.fetchall()

    def update(self, collection, query, new_data):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        update_string = ', '.join(f"{k}=?" for k in new_data.keys())
        self.cursor.execute(f'UPDATE {collection} SET {update_string} WHERE {query_string}', tuple(new_data.values()) + tuple(query.values()))
        self.conn.commit()

    def delete(self, collection, query):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        self.cursor.execute(f'DELETE FROM {collection} WHERE {query_string}', tuple(query.values()))
        self.conn.commit()

    def get_all_products(self, collection, admin_id):
        return self.find(collection, {"admin_id": admin_id})

    def get_user_balance(self, user_id):
        balances = self.find("balances", {"user_id": user_id})
        return balances[0][1] if balances else 0

    def update_user_balance(self, user_id, amount):
        balances = self.find("balances", {"user_id": user_id})
        if balances:
            new_balance = balances[0][1] + amount
            self.update("balances", {"user_id": user_id}, {"balance": new_balance})

    def update_product_stock(self, product_id, amount):
        products = self.find("products", {"id": product_id})
        if products:
            new_stock = products[0][4] + amount
            self.update("products", {"id": product_id}, {"stock": new_stock})

    def get_channel_id(self, guild_id):
        channels = self.find("channels", {"guild_id": guild_id})
        return channels[0][1] if channels else None

    def get_admin_data(self, admin_id):
        admins = self.find("admins", {"discord_id": admin_id})
        return admins[0] if admins else None

    def find_product(self, collection, query):
        results = self.find(collection, query)
        return results[0] if results else None
