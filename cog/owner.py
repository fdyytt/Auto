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
            config_dict = {}
            for line in config:
                key, value = line.split('=', 1)
                config_dict[key.strip()] = value.strip().strip('"')
            return config_dict
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
                guild_id TEXT,
                id_history_deposit TEXT,
                id_history_buy TEXT,
                id_live_stock TEXT,
                id_log_purch TEXT,
                id_donation_log TEXT,
                rental_time INTEGER DEFAULT 0,
                rental_time_days INTEGER DEFAULT 0
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
                grow_id TEXT PRIMARY KEY,
                balance INTEGER,
                admin_id INTEGER,
                FOREIGN KEY (admin_id) REFERENCES admins(id)
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
                grow_id TEXT,
                product_id INTEGER,
                jumlah INTEGER,
                total_harga INTEGER,
                tanggal DATETIME,
                admin_id INTEGER,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (admin_id) REFERENCES admins(id)
            )
        ''')
        self.conn.commit()

    def insert(self, collection, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f'INSERT INTO {collection} ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, tuple(data.values()))
        self.conn.commit()

    def find(self, collection, query):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        sql = f'SELECT * FROM {collection} WHERE {query_string}'
        self.cursor.execute(sql, tuple(query.values()))
        return self.cursor.fetchall()

    def update(self, collection, query, new_data):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        update_string = ', '.join(f"{k}=?" for k in new_data.keys())
        sql = f'UPDATE {collection} SET {update_string} WHERE {query_string}'
        self.cursor.execute(sql, tuple(new_data.values()) + tuple(query.values()))
        self.conn.commit()

    def delete(self, collection, query):
        query_string = ' AND '.join(f"{k}=?" for k in query.keys())
        sql = f'DELETE FROM {collection} WHERE {query_string}'
        self.cursor.execute(sql, tuple(query.values()))
        self.conn.commit()

    def get_all_products(self, collection, admin_id):
        return self.find(collection, {"admin_id": admin_id})

    def get_user_balance(self, grow_id, admin_id):
        balances = self.find("balances", {"grow_id": grow_id, "admin_id": admin_id})
        return balances[0][1] if balances else 0

    def update_user_balance(self, grow_id, admin_id, amount):
        balances = self.find("balances", {"grow_id": grow_id, "admin_id": admin_id})
        if balances:
            new_balance = balances[0][1] + amount
            self.update("balances", {"grow_id": grow_id, "admin_id": admin_id}, {"balance": new_balance})
        else:
            self.insert("balances", {"grow_id": grow_id, "balance": amount, "admin_id": admin_id})

    def update_product_stock(self, product_id, admin_id, amount):
        products = self.find("products", {"id": product_id, "admin_id": admin_id})
        if products:
            new_stock = products[0][4] + amount
            self.update("products", {"id": product_id, "admin_id": admin_id}, {"stock": new_stock})

    def get_channel_id(self, guild_id):
        channels = self.find("channels", {"guild_id": guild_id})
        return channels[0][1] if channels else None

    def get_admin_data(self, admin_id):
        admins = self.find("admins", {"discord_id": admin_id})
        return admins[0] if admins else None

    def find_product(self, collection, query):
        results = self.find(collection, query)
        return results[0] if results else None

    def log_purchase(self, grow_id, product_id, jumlah, total_harga, admin_id):
        sql = '''INSERT INTO transactions (grow_id, product_id, jumlah, total_harga, tanggal, admin_id)
                 VALUES (?, ?, ?, ?, datetime('now'), ?)'''
        self.cursor.execute(sql, (grow_id, product_id, jumlah, total_harga, admin_id))
        self.conn.commit()