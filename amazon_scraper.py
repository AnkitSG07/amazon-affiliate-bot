import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

AFFILIATE_TAG = "ankit007"

# URL Definitions
URLS = {
    "Bestseller": "https://www.amazon.in/gp/bestsellers",
    "TopDeals": "https://www.amazon.in/deals?ref_=nav_cs_gb",
    "PriceDrops": "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb&rh=p_n_pct-off-with"
}

def setup_selenium():
    """Set up Selenium Chrome Driver for headless browsing."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_bestsellers():
    """Scrape bestsellers using BeautifulSoup."""
    response = requests.get(URLS["Bestseller"], headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select(".p13n-sc-uncoverable-faceout")
    products = []
    for item in items:
        title = item.select_one(".p13n-sc-truncate-desktop-type2, .p13n-sc-truncated, ._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price, span.a-price > span.a-offscreen")

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price.get_text(strip=True) if price else "N/A",
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}",
                'category': "Bestseller",
                'type': "Bestseller"
            }
            products.append(product)

    return products

def scrape_deals(driver, category, url, discount_threshold):
    """Scrape dynamically loaded deals using Selenium."""
    driver.get(url)
    time.sleep(5)  # Allow time for JS to load

    products = []
    items = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
    for item in items:
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, 'h2 a span')
            link_elem = item.find_element(By.CSS_SELECTOR, 'h2 a')
            image_elem = item.find_element(By.CSS_SELECTOR, 'img')
            price_elem = item.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen')

            title = title_elem.text
            link = f"https://www.amazon.in{link_elem.get_attribute('href')}&tag={AFFILIATE_TAG}"
            image = image_elem.get_attribute('src')
            price_text = price_elem.text.replace('₹', '').replace(',', '')

            if price_text.isdigit():
                price = int(price_text)
                old_price = price * 2
                discount = int(((old_price - price) / old_price) * 100)

                product_type = "N/A"
                if discount >= discount_threshold:
                    product_type = category

                product = {
                    'title': title,
                    'image': image,
                    'price': f"₹{price}",
                    'old_price': f"₹{old_price}",
                    'category': category,
                    'type': product_type,
                    'link': link,
                }
                products.append(product)

        except Exception as e:
            continue

    return products

def save_to_js(products):
    """Save scraped products to products.js."""
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

    # Setup Selenium
    driver = setup_selenium()

    # Scrape Bestsellers
    all_products = scrape_bestsellers()

    # Scrape Top Deals (Above 50% Discount)
    all_products.extend(scrape_deals(driver, "Top Deals", URLS["TopDeals"], 50))

    # Scrape Price Drops (Above 80% Discount)
    all_products.extend(scrape_deals(driver, "Price Drops", URLS["PriceDrops"], 80))

    # Close Selenium Driver
    driver.quit()

    # Save to products.js
    save_to_js(all_products)
    print("🎉 Scraping and saving completed successfully.")
