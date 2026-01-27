import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for
import steam_price  # Your scraper module
from database import save_to_db, init_db, delete_product_by_name

app = Flask(__name__)


def get_dashboard_data():
    """
    Fetches history, converts UTC to IST, and calculates Best/Current prices.
    Uses 'sqlite3.Row' to access columns by name (prevents index errors).
    """
    conn = sqlite3.connect('prices.db')
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT * FROM prices ORDER BY scraped_at DESC")
    all_rows = cursor.fetchall()
    conn.close()

    summary = {}

    for row in all_rows:
        name = row['product_name']
        price = row['price']
        
       
        db_time_str = row['scraped_at'] # Time from DB (UTC)
        try:
           
            utc_time = datetime.datetime.strptime(db_time_str, "%Y-%m-%d %H:%M:%S")
           
            ist_time = utc_time + datetime.timedelta(hours=5, minutes=30)
           
            timestamp = ist_time.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            timestamp = db_time_str # Fallback if parsing fails

      
        url = row['url'] if 'url' in row.keys() else None 

        if name not in summary:
            
            summary[name] = {
                'name': name,
                'url': url,
                'current_price': price,
                'best_price': price, 
                'last_checked': timestamp, 
                'history_count': 1
            }
        else:
            
            if price < summary[name]['best_price']:
                summary[name]['best_price'] = price
            summary[name]['history_count'] += 1
            
           
            if url:
                summary[name]['url'] = url

    return list(summary.values())

def refresh_stale_prices(items):
    """
    Checks if prices are older than 4 hours. 
    If yes, re-scrapes the URL to update the database.
    """
    print("Checking for stale prices...")
    
    for item in items:
       
        if not item['last_checked']:
            continue

        try:
         
            last_checked = datetime.datetime.strptime(item['last_checked'], "%d-%m-%Y %H:%M:%S")
            time_diff = datetime.datetime.now() - last_checked
            
           
            if time_diff.total_seconds() > 14400: 
                print(f"Refreshing outdated item: {item['name']}")
                
               
                if item['url'] and "store.steampowered.com" in item['url']:
                    new_results = steam_price.scrape_steam(item['url'])
                    
                    
                    for res in new_results:
                        if res['name'] == item['name']:
                            save_to_db(res['name'], res['price'], item['url'])
                            print(f" -> Updated {item['name']} to ₹{res['price']}")
                            break
        except Exception as e:
            print(f"Skipping auto-refresh for {item['name']}: {e}")


@app.route('/')
def home():
    
    items = get_dashboard_data()
    
    
    refresh_stale_prices(items)
    
    
    items = get_dashboard_data() 
    
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def find_products():
    """Step 1: Scrape URL and show 'Select Edition' screen"""
    url = request.form.get('url')
    
    print(f"Web Request: Scraping {url}")
    
    if "store.steampowered.com" in url:
        results = steam_price.scrape_steam(url)
        
  
        if results:
            return render_template('select.html', items=results, url=url)
            
  
    return redirect(url_for('home'))

@app.route('/save', methods=['POST'])
def save_product():
    """Step 2: User selected an edition, now save it"""
    name = request.form.get('name')
    price = request.form.get('price')
    url = request.form.get('url') 
    
    if name and price:
     
        save_to_db(name, float(price), url)
        
    return redirect(url_for('home'))

@app.route('/delete', methods=['POST'])
def remove_product():
    name = request.form.get('name')
    
    if name:
        delete_product_by_name(name)
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    
    init_db()
    app.run(debug=True)