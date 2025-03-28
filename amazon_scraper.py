import requests
from bs4 import BeautifulSoup
import random
import time

# Amazon URLs for different sections
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AMAZON_DEALS_URL = "https://www.amazon.in/deals"
AMAZON_DISCOUNT_URL = "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb"

AFFILIATE_TAG = "ankit007"

# User-Agent List to Rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Proxy List to Rotate (optional - add working proxies)
PROXIES = [
    "http://proxy1.com",
    "http://proxy2.com"
]

HEADERS = {"User-Agent": random.choice(USER_AGENTS)}


def scrape_products(url, category):
    """Scrapes products from a given Amazon URL."""
    proxy = random.choice(PROXIES) if PROXIES else None
    proxies = {"http": proxy, "https": proxy} if proxy else None

    response = requests.get(url, headers=HEADERS, proxies=proxies)
    if response.status_code != 200:
        print(f"❌ Failed to fetch data from {url}. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Selectors for bestsellers and deals
    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

    products = []
    for item in items:
        title = (item.select_one(".p13n-sc-truncate-desktop-type2") or
                 item.select_one(".p13n-sc-truncated") or
                 item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y"))

        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = (item.select_one(".p13n-sc-price") or
                 item.select_one("span.a-price > span.a-offscreen"))

        # Correcting image URL
        image_url = image.get('src') or image.get('data-src') if image else None

        # Extracting Price & Discount
        price_text = price.get_text(strip=True) if price else "N/A"
        discount_span = item.select_one("span.a-letter-space + span")
        discount_text = discount_span.get_text(strip=True) if discount_span else "0%"

        old_price = "N/A"
        discount_percentage = 0
        if price and price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"  # Assuming 50% as fallback
                discount_percentage = 50
            except ValueError:
                pass

        # Check if all required fields exist
        if title and link and image_url:
            product = {
                'title': title.get_text(strip=True),
                'image': image_url,
                'price': price_text,
                'old_price': old_price,
                'category': category,
                'discount': f"{discount_percentage}%" if discount_percentage else "N/A",
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} products from {category}.")
    return products


def save_to_js(products):
    """Saves the scraped product data to products.js."""
    js_content = "const products = [\n"
    for p in products:
        js_content += f"""    {{
        title: "{p['title']}",
        image: "{p['image']}",
        price: "{p['price']}",
        old_price: "{p['old_price']}",
        category: "{p['category']}",
        discount: "{p['discount']}",
        link: "{p['link']}"
    }},
"""
    js_content += "];\n"

    with open("products.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ products.js updated successfully!")


def main():
    """Main function to scrape and save products."""
    print("🚀 Starting Amazon Scraper...")
    
    # Scraping Bestsellers
    bestsellers = scrape_products(AMAZON_BESTSELLER_URL, "Bestsellers")
    time.sleep(3)  # Add delay to avoid detection

    # Scraping Best Deals
    best_deals = scrape_products(AMAZON_DEALS_URL, "Best Deals")
    time.sleep(3)

    # Scraping Discounted Products
    discounted_items = scrape_products(AMAZON_DISCOUNT_URL, "Drastically Reduced")

    # Merging all results
    all_products = bestsellers + best_deals + discounted_items

    # Save to JS file
    save_to_js(all_products)

    print("🎉 Scraping and saving completed successfully!")


if __name__ == "__main__":
    main()
