from database import Database

class Balance:
    def __init__(self, db):
        self.db = db
        self.collection = "balances"

    def get_balance(self, grow_id, admin_id):
        balance_data = self.db.find(self.collection, {"grow_id": grow_id, "admin_id": admin_id})
        if balance_data:
            return balance_data[0]
        else:
            return {"grow_id": grow_id, "balance": 0, "admin_id": admin_id}

    def update_balance(self, grow_id, admin_id, jumlah_donasi, mata_uang_donasi):
        konversi = {
            'WL': 1,
            'DL': 100,
            'BGL': 10000
        }
        jumlah_donasi_wl = jumlah_donasi * konversi.get(mata_uang_donasi, 0)
        current_balance = self.get_balance(grow_id, admin_id)["balance"]
        new_balance = current_balance + jumlah_donasi_wl
        self.db.update(self.collection, {"grow_id": grow_id, "admin_id": admin_id}, {"balance": new_balance})

    def add_balance(self, grow_id, admin_id, balance):
        self.db.insert(self.collection, {"grow_id": grow_id, "balance": balance, "admin_id": admin_id})