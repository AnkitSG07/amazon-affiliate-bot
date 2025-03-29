import requests
from bs4 import BeautifulSoup
import random
import time

# Amazon URLs
URLS = {
    "Bestseller": "https://www.amazon.in/gp/bestsellers",
    "Top Deals": "https://www.amazon.in/deals",
    "Price Drops": "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb"
}

AFFILIATE_TAG = "ankit007"
PAGES_TO_SCRAPE = 5  # Number of pages to scrape for Top Deals & Price Drops

# List of User Agents to rotate between
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604",
]

def get_random_headers():
    """Get random headers with rotating User-Agent."""
    return {"User-Agent": random.choice(USER_AGENTS)}

def scrape_category(url, category_name, max_pages=1):
    """Scrape Amazon category products."""
    products = []

    for page in range(1, max_pages + 1):
        page_url = f"{url}?pg={page}"
        response = requests.get(page_url, headers=get_random_headers())

        # Handle errors and skip invalid pages
        if response.status_code != 200:
            print(f"❌ Failed to fetch data from {url}, page {page}. Status Code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Selectors for products
        items = soup.select(".p13n-sc-uncoverable-faceout") or \
                soup.select("li.zg-item-immersion") or \
                soup.select("div.zg-grid-general-faceout")

        if not items:
            print(f"❗ No products found for {category_name} on page {page}.")
            continue

        # Scrape all products from the page
        for item in items:
            title = item.select_one(".p13n-sc-truncate-desktop-type2") or \
                    item.select_one(".p13n-sc-truncated") or \
                    item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y")

            link = item.select_one("a.a-link-normal")
            image = item.select_one("img")
            price = item.select_one(".p13n-sc-price") or item.select_one("span.a-price > span.a-offscreen")
            price_text = price.get_text(strip=True) if price else "N/A"

            # Skip invalid products
            if not title or not link or not image:
                continue

            # Calculate old price and discount
            old_price, discount_percentage = "N/A", "0%"
            try:
                if price_text != "N/A":
                    price_number = int(price_text.replace("₹", "").replace(",", "").strip())
                    old_price = f"₹{price_number * 2}"  # Double the price for old price
                    discount_percentage = round(((price_number * 2 - price_number) / (price_number * 2)) * 100)
            except ValueError:
                pass

            # Determine product type
            product_type = "Bestseller"
            if discount_percentage >= 80 and discount_percentage <= 90:
                product_type = "Price Drop"
            elif discount_percentage >= 50 and discount_percentage < 80:
                product_type = "Top Deals"

            # Create product dictionary
            product = {
                "title": title.get_text(strip=True),
                "image": image["src"],
                "price": price_text,
                "old_price": old_price,
                "category": category_name,
                "type": product_type,
                "link": f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

        # Add delay between requests to avoid 503 errors
        time.sleep(random.uniform(3, 7))

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


if __name__ == "__main__":
    print("🚀 Scraping Amazon Bestsellers, Top Deals, and Price Drops...")

    # Scrape products from all categories
    all_products = []
    all_products.extend(scrape_category(URLS["Bestseller"], "Bestseller", 3))  # Scrape 3 pages for Bestsellers
    all_products.extend(scrape_category(URLS["Top Deals"], "Top Deals", PAGES_TO_SCRAPE))  # Scrape Top Deals
    all_products.extend(scrape_category(URLS["Price Drops"], "Price Drops", PAGES_TO_SCRAPE))  # Scrape Price Drops

    # Save products to JS
    if all_products:
        save_to_js(all_products)
        print("🎉 Scraping and saving completed successfully.")
    else:
        print("⚠️ No products were saved. Check scraper or Amazon layout.")
