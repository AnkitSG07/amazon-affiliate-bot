import requests
from bs4 import BeautifulSoup
import random

# Amazon Bestsellers URL
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AFFILIATE_TAG = "ankit007"

# User-Agent List to Rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

HEADERS = {"User-Agent": random.choice(USER_AGENTS)}


def scrape_bestsellers():
    """Scrapes Amazon Bestsellers and returns a list of product dictionaries."""
    response = requests.get(AMAZON_BESTSELLER_URL, headers=HEADERS)
    
    # Check for successful response
    if response.status_code != 200:
        print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Multiple selectors to account for Amazon's layout changes
    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

    # Check if items were found
    if not items:
        print("❗ No products found. Amazon may have changed the layout.")
        return []

    products = []
    for item in items:
        # Extract title
        title = (item.select_one(".p13n-sc-truncate-desktop-type2") or
                 item.select_one(".p13n-sc-truncated") or
                 item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y"))

        # Extract product link
        link = item.select_one("a.a-link-normal")

        # Extract image (handle lazy loading with fallback)
        image = item.select_one("img")
        image_url = image.get('src') or image.get('data-src') if image else None

        # Extract price and handle multiple formats
        price = (item.select_one(".p13n-sc-price") or
                 item.select_one("span.a-price > span.a-offscreen"))
        price_text = price.get_text(strip=True) if price else "N/A"

        # Determine category (from heading or fallback to 'Miscellaneous')
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"

        # Calculate old price for display (50% as fallback)
        old_price = "N/A"
        if price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"  # Assumed old price as double
            except ValueError:
                old_price = "N/A"

        # Add valid products to list
        if title and link and image_url:
            product = {
                'title': title.get_text(strip=True),
                'image': image_url,
                'price': price_text,
                'old_price': old_price,
                'category': category_text,
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} products successfully.")
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
        link: "{p['link']}"
    }},
"""
    js_content += "];\n"

    with open("products.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ products.js updated successfully.")


if __name__ == "__main__":
    print("🚀 Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()

    if products:
        save_to_js(products)
        print("🎉 Scraping and saving completed successfully.")
    else:
        print("⚠️ No products were saved. Check scraper or Amazon layout.")
