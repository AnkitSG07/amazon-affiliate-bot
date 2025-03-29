import requests
from bs4 import BeautifulSoup

# Amazon Bestsellers URL
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AFFILIATE_TAG = "ankit007"

# Map Amazon categories to fixed category names
CATEGORY_MAPPING = {
    "Bestsellers in Sports, Fitness & Outdoors": "Bestsellers",
    "Bestsellers in Computers & Accessories": "Bestsellers",
    "Bestsellers in Car & Motorbike": "Bestsellers",
    "Bestsellers in Home & Kitchen": "Bestsellers",
    "Bestsellers in Musical Instruments": "Bestsellers",
    "Bestsellers in Beauty": "Bestsellers",
    "Bestsellers in Shoes & Handbags": "Bestsellers",
    "Discounted Products": "Price Drop",
    "Best Deals Products": "Best Deal"
}

def scrape_bestsellers():
    """Scrapes Amazon Bestsellers and returns a list of product dictionaries."""
    response = requests.get(AMAZON_BESTSELLER_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    # Check for successful response
    if response.status_code != 200:
        print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Multiple selectors to account for Amazon's layout changes
    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

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

        # Extract image with fallback
        image = item.select_one("img")
        image_url = image.get('src') or image.get('data-src') if image else None

        # Extract price with fallback
        price = (item.select_one(".p13n-sc-price") or
                 item.select_one("span.a-price > span.a-offscreen"))
        price_text = price.get_text(strip=True) if price else "N/A"

        # Determine category and assign mapped name
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"
        category_mapped = CATEGORY_MAPPING.get(category_text, category_text)

        # Calculate old price and discount
        old_price, discount_percentage, product_type = "N/A", 0, "Bestseller"
        if price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price_number = price_number * 2  # Assume old price as double of current price
                discount_percentage = round(((old_price_number - price_number) / old_price_number) * 100)

                # Assign product type based on discount
                if 80 <= discount_percentage <= 90:
                    product_type = "Price Drop"
                elif 45 <= discount_percentage <= 55:  # Best Deal around 50%
                    product_type = "Best Deal"
                else:
                    product_type = "Bestseller"
                
                old_price = f"₹{old_price_number}"
            except ValueError:
                price_number, discount_percentage, product_type = "N/A", 0, "Bestseller"

        # Add valid products
        if title and link and image_url:
            product = {
                'title': title.get_text(strip=True),
                'image': image_url,
                'price': price_text,
                'old_price': old_price,
                'category': category_mapped,
                'type': product_type,
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
        type: "{p['type']}",
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
