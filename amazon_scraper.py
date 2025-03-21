import requests
from bs4 import BeautifulSoup
import os

# CONFIGURATION
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AFFILIATE_TAG = "ankit007"

def scrape_bestsellers():
    response = requests.get(AMAZON_BESTSELLER_URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    for item in soup.select(".p13n-sc-uncoverable-faceout"):
        title = item.select_one(".p13n-sc-truncate-desktop-type2")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price")
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"

        price_text = price.get_text(strip=True) if price else "N/A"
        old_price = "N/A"
        if price and price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"
            except ValueError:
                price_number = "N/A"
                old_price = "N/A"

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price_text,
                'old_price': old_price,
                'category': category_text,
                'link': "https://www.amazon.in" + link['href'] + f"&tag={AFFILIATE_TAG}"
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
        link: "{p['link']}"
    }},
"""
    js_content += "];\n"

    with open("products.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("products.js updated successfully.")

if __name__ == "__main__":
    print("Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()
    print(f"Found {len(products)} products.")
    save_to_js(products)
    print("All done!")
