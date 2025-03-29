import requests
from bs4 import BeautifulSoup

# URLs for different sections
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AMAZON_DEALS_URL = "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb"
AMAZON_LIGHTNING_DEALS_URL = "https://www.amazon.in/gp/goldbox/ref=gbps_ftr_s-1_1f2b_page_1"

# Affiliate tag
AFFILIATE_TAG = "ankit007"

def scrape_amazon(url, category_type):
    """Scrapes Amazon URL and returns a list of product dictionaries."""
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print(f"❌ Failed to fetch data from {url}. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

    if not items:
        print(f"❗ No products found on {url}.")
        return []

    products = []
    for item in items:
        title = (item.select_one(".p13n-sc-truncate-desktop-type2") or
                 item.select_one(".p13n-sc-truncated") or
                 item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y"))

        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = (item.select_one(".p13n-sc-price") or
                 item.select_one("span.a-price > span.a-offscreen"))

        price_text = price.get_text(strip=True) if price else "N/A"
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"

        # Calculate discount percentage and old price
        old_price, discount_percentage = "N/A", 0
        if price and price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"
                discount_percentage = round(((price_number * 2 - price_number) / (price_number * 2)) * 100)
            except ValueError:
                price_number, old_price, discount_percentage = "N/A", "N/A", 0

        # Assign type based on source and discount
        if category_type == "Bestseller":
            product_type = "Bestseller"
        elif category_type == "Price Drop" and 80 <= discount_percentage <= 90:
            product_type = "Price Drop"
        elif category_type == "Best Deal" and 45 <= discount_percentage <= 55:
            product_type = "Best Deal"
        else:
            continue  # Skip products that don't match the discount criteria

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price_text,
                'old_price': old_price,
                'category': category_text,
                'type': product_type,
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} products from {url}.")
    return products

def save_to_js(products):
    """Saves the scraped products to a JavaScript file."""
    js_content = "const products = [\n"
    for p in products:
        js_content += f"""    {{
        title: "{p['title']}",
        image: "{p['image']}",
        price: "{p['price']}",
        old_price: "{p['old_price']}",
        category: "{p['category']}",
        type: "{p['type']}",
        link: "{p['link']}"
    }},
"""
    js_content += "];\n"

    with open("products.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ products.js updated successfully.")

# Scrape from multiple sources
products_bestsellers = scrape_amazon(AMAZON_BESTSELLER_URL, "Bestseller")
products_price_drops = scrape_amazon(AMAZON_DEALS_URL, "Price Drop")
products_best_deals = scrape_amazon(AMAZON_LIGHTNING_DEALS_URL, "Best Deal")

# Combine all products
all_products = products_bestsellers + products_price_drops + products_best_deals
save_to_js(all_products)
print("🎉 Scraping and saving completed successfully.")
