import sqlite3

def upgrade_database():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE prices ADD COLUMN url TEXT")
        print("Success: Added 'url column to database.")
    except sqlite3.OperationalError:
        print("Notices: 'url' column already exists.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    upgrade_database()