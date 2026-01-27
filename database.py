import sqlite3 
import datetime 

def init_db():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT, 
            price Real,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )     
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized: 'prices.db' created successfully."  )

def save_to_db(name, price, url):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"  -> Saving to DB: {name} | ₹{price} | {timestamp}")

    cursor.execute('''
        INSERT INTO prices (product_name, price, url)
        VALUES (?, ?, ?)
    ''', (name, price, url))

    conn.commit()
    conn.close()

def delete_product_by_name(name):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    print(f" --> Deleting all records for: {name}")

    cursor.execute("DELETE FROM prices WHERE product_name = ?", (name,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()