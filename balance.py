from MultipleFiles.database import Database

class Balance:
    def __init__(self, db):
        self.db = db
        self.collection = db.get_collection("balance")

    def get_balance(self, grow_id):
        return self.collection.find_one({"grow_id": grow_id})

    def update_balance(self, grow_id, jumlah_donasi, mata_uang_donasi):
        konversi = {
            'WL': 1,
            'DL': 100,
            'BGL': 10000
        }
        jumlah_donasi_wl = jumlah_donasi * konversi.get(mata_uang_donasi, 0)
        self.collection.update_one({"grow_id": grow_id}, {"$inc": {"balance": jumlah_donasi_wl}}, upsert=True)

    def add_balance(self, grow_id, balance):
        self.collection.insert_one({"grow_id": grow_id, "balance": balance})