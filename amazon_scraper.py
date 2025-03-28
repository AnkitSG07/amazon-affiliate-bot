import requests
from bs4 import BeautifulSoup

# Amazon URLs for different sections
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AMAZON_DEALS_URL = "https://www.amazon.in/deals"
AMAZON_DISCOUNT_URL = "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb"

AFFILIATE_TAG = "ankit007"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_products(url, category):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Multiple selectors to ensure robustness
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

        discount_span = item.select_one("span.a-letter-space + span")
        discount_text = discount_span.get_text(strip=True) if discount_span else "0%"

        price_text = price.get_text(strip=True) if price else "N/A"
        old_price = "N/A"
        discount_percentage = 0

        if price and price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"
                discount_percentage = 50
            except ValueError:
                price_number = "N/A"
                old_price = "N/A"
                discount_percentage = 0

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price_text,
                'old_price': old_price,
                'category': category,
                'discount': f"{discount_percentage}%" if discount_percentage else "N/A",
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

    return products


def save_to_js(products):
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
    print("🚀 Scraping Amazon Data...")

    bestsellers = scrape_products(AMAZON_BESTSELLER_URL, "Bestsellers")
    print(f"✅ Scraped {len(bestsellers)} bestsellers.")

    best_deals = scrape_products(AMAZON_DEALS_URL, "Best Deals")
    print(f"✅ Scraped {len(best_deals)} best deals.")

    discounted_items = scrape_products(AMAZON_DISCOUNT_URL, "Drastically Reduced")
    print(f"✅ Scraped {len(discounted_items)} discounted items.")

    # Combine all products
    all_products = bestsellers + best_deals + discounted_items

    # Save to products.js
    save_to_js(all_products)

    print("🎉 Scraping and saving completed successfully!")


if __name__ == "__main__":
    main()
