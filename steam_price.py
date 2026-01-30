import requests 
from bs4 import BeautifulSoup 

def extract_number(price_str):
    if not price_str: return 0.0 
    clean = "".join(filter(lambda x:x.isdigit() or x == '.', price_str))

    try:
        return float(clean)
    except ValueError:
        return 0.0
    
def scrape_steam(url):
    cookies = {
        'lastagecheckage': '1-0-1988', 
        'birthtime': '568022401',       
        'wants_mature_content': '1',   
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5" 
    }

    print(f"Debug: Requesting {url} with age-gate cookies...")
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code != 200:
        print(f"Failed to load page: {response.status_code}") 
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    found_items = []

    page_title = soup.title.string.strip() if soup.title else "No Title"
    if "Age Check" in page_title:
        print("CRITICAL ERROR: Still stuck at Age Gate!")
        return []
    
    purchase_blocks = soup.find_all("div", class_="game_area_purchase_game")

    for block in purchase_blocks:
        title_tag = block.find("h1")
        if not title_tag:
            title_tag = block.find("h2")

        if not title_tag:
            continue 

        name = title_tag.text.strip().replace("Buy ", "")

        price_tag = block.find("div", class_="discount_final_price")

        if not price_tag:
            price_tag = block.find("div", class_="game_purchase_price")

        if price_tag:
            price_val = extract_number(price_tag.text)
            item_type = "bundle" if "bundle" in name.lower() or "edition" in name.lower() else "base_game"

            found_items.append({
                "name": name, 
                "price": price_val,
                "type": item_type 
            })

    dlc_rows = soup.find_all("div", class_="game_area_dlc_row")
    for row in dlc_rows:
        name_tag = row.find("span", class_="color_overlay")
        price_tag = row.find("div", class_="discount_final_price")
        if not price_tag:
            price_tag = row.find("div", class_="game_purchase_price")

        if name_tag and price_tag:
            found_items.append({
                "name": name_tag.text.strip(),
                "price": extract_number(price_tag.text),
                "type": "dlc"
            })

    return found_items