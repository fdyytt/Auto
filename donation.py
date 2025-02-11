from balance import Balance
from MultipleFiles.database import Database

class Donation:
    def __init__(self, db):
        self.balance_manager = Balance(db)

    def donate(self, grow_id, jumlah_donasi, mata_uang_donasi):
        self.balance_manager.update_balance(grow_id, jumlah_donasi, mata_uang_donasi)
        return self.balance_manager.get_balance(grow_id)

if __name__ == "__main__":
    db_uri = "mongodb+srv://cluster0.mongodb.net/"
    db_name = "nama_database"
    db = Database(db_uri, db_name)
    
    donation_manager = Donation(db)
    
    # Example usage
    grow_id = "user123"
    jumlah_donasi = 10
    mata_uang_donasi = "DL"

    updated_balance = donation_manager.donate(grow_id, jumlah_donasi, mata_uang_donasi)
    print(f"Updated balance for {grow_id}: {updated_balance['balance']}")