import requests
from bs4 import BeautifulSoup
import time
import random

# Amazon URLs for different categories
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AMAZON_TOP_DEALS_URL = "https://www.amazon.in/deals"
AMAZON_PRICE_DROPS_URL = "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb"

AFFILIATE_TAG = "ankit007"
PAGES_TO_SCRAPE = 5  # Scrape multiple pages to get more products

# User agents to rotate (avoid getting blocked)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
]


def scrape_amazon_products(url, category_name, max_pages=5):
    """Scrapes multiple pages of Amazon products and returns a list of product dictionaries."""
    products = []

    for page in range(1, max_pages + 1):
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(f"{url}?pg={page}", headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to fetch data from {url}, page {page}. Status Code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Selectors to handle layout changes
        items = soup.select(".p13n-sc-uncoverable-faceout") or \
                soup.select("li.zg-item-immersion") or \
                soup.select("div.zg-grid-general-faceout")

        for item in items:
            title = (item.select_one(".p13n-sc-truncate-desktop-type2") or
                     item.select_one(".p13n-sc-truncated") or
                     item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y"))

            link = item.select_one("a.a-link-normal")
            image = item.select_one("img")
            price = (item.select_one(".p13n-sc-price") or
                     item.select_one("span.a-price > span.a-offscreen"))

            category_tag = item.find_previous("h2")
            category_text = category_tag.get_text(strip=True) if category_tag else category_name

            price_text = price.get_text(strip=True) if price else "N/A"
            old_price, discount_percentage = "N/A", 0
            if price and price_text != "N/A":
                try:
                    price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                    old_price = f"₹{price_number * 2}"
                    discount_percentage = round(((price_number * 2 - price_number) / (price_number * 2)) * 100)
                except ValueError:
                    price_number, old_price = "N/A", "N/A"

            # Define product type based on URL and discount
            product_type = "Bestseller"
            if url == AMAZON_PRICE_DROPS_URL and 80 <= discount_percentage <= 90:
                product_type = "Price Drop"
            elif url == AMAZON_TOP_DEALS_URL and 45 <= discount_percentage <= 55:
                product_type = "Best Deal"

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

        # Delay to avoid being blocked by Amazon
        time.sleep(random.uniform(2, 5))

    print(f"✅ Scraped {len(products)} products successfully from {url}.")
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


# Scrape from all sources and combine results
bestseller_products = scrape_amazon_products(AMAZON_BESTSELLER_URL, "Bestsellers", PAGES_TO_SCRAPE)
top_deals_products = scrape_amazon_products(AMAZON_TOP_DEALS_URL, "Top Deals", PAGES_TO_SCRAPE)
price_drop_products = scrape_amazon_products(AMAZON_PRICE_DROPS_URL, "Price Drops", PAGES_TO_SCRAPE)

# Merge all products
all_products = bestseller_products + top_deals_products + price_drop_products

# Save products to products.js
save_to_js(all_products)
