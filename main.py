import steam_price
from database import save_to_db, init_db

def start_tracker():
    url = input("Enter the product URL to track: ").strip()

    print("\nAnalyzing URL...")
    scraped_data = []

    if "store.steampowered.com" in url:
        print("Detected: Steam Store")
        scraped_data = steam_price.scrape_steam(url)
    else:
        print("Error: This website is currently Unsupported!")
        return 
    
    if not scraped_data:
        print("No prices found on this page:")
        print("-" * 50)

    for i, item in enumerate(scraped_data):
        print(f"[{i+1}] {item['type'].upper()}: {item['name']} - ₹{item['price']}")

    print("-" * 50)

    choice = input("\nWhich item number do you want to track? (or type 'all'): ")
    
    if choice.lower() == 'all':
        print("Saving ALL items to database...") 
        for item in scraped_data:
            save_to_db(item['name'], item['price'])
       
    else:
        try:
            idx = int(choice) - 1
            selected = scraped_data[idx]
            print(f"Saving '{selected['name']}' to database...")
            save_to_db(item['name'], item['price'])
        
        except (ValueError, IndexError):
            print("Invalid selection.")

if __name__ == "__main__":
    init_db()
    start_tracker()