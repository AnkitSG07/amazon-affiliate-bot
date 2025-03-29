import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import time

# URLs for different categories
URLS = {
    "Bestseller": "https://www.amazon.in/gp/bestsellers",
    "Top Deal": "https://www.amazon.in/deals?ref_=nav_cs_gb",
    "Price Drop": "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb&rh=p_n_pct-off-with-tax%3A80-"
}

# Amazon Affiliate Tag
AFFILIATE_TAG = "ankit007"

# Setup Selenium with automatic ChromeDriver installation
def setup_selenium():
    """Set up Selenium with ChromeDriver and headless mode."""
    # Automatically install the correct version of ChromeDriver
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Create WebDriver instance
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

# Scrape Bestsellers using BeautifulSoup
def scrape_bestsellers():
    """Scrapes Amazon Bestsellers and returns a list of product dictionaries."""
    response = requests.get(URLS["Bestseller"], headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print(f"❌ Failed to fetch Bestsellers. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

    if not items:
        print("❗ No Bestseller products found.")
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
        link_href = f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}" if link else "#"

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price_text,
                'old_price': "N/A",
                'category': "Bestsellers",
                'type': "Bestseller",
                'link': link_href
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} Bestseller products.")
    return products

# Scrape Top Deals and Price Drops using Selenium (Open Product Page)
def scrape_deals(url, category_name, discount_range):
    """Scrapes Top Deals and Price Drops dynamically from deal pages."""
    driver = setup_selenium()
    driver.get(url)
    time.sleep(5)  # Give page time to load

    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".DesktopDiscountAsinGrid-module__grid_pi4xEmM7RAHNMG9sGVBJ > div")

    for item in items:
        try:
            # Extract link and open product page
            link = item.find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")
            if not link:
                continue

            driver.get(link)  # Open product page
            time.sleep(3)

            # Extract title, price, old price, and discount percentage
            try:
                title = driver.find_element(By.ID, "productTitle").text.strip()
            except:
                title = "N/A"

            try:
                price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price > span.a-offscreen")
                price_text = price_element.text.strip()
            except:
                price_text = "N/A"

            try:
                old_price_element = driver.find_element(By.CSS_SELECTOR, "span.priceBlockStrikePriceString")
                old_price = old_price_element.text.strip()
            except:
                old_price = "N/A"

            # Calculate discount percentage
            if price_text != "N/A" and old_price != "N/A":
                try:
                    price_number = float(price_text.replace('₹', '').replace(',', '').strip())
                    old_price_number = float(old_price.replace('₹', '').replace(',', '').strip())
                    discount_percentage = round(((old_price_number - price_number) / old_price_number) * 100)
                except ValueError:
                    discount_percentage = 0
            else:
                discount_percentage = 0

            # Categorize based on discount percentage
            if discount_range[0] <= discount_percentage <= discount_range[1]:
                product_type = category_name
                product = {
                    'title': title,
                    'image': driver.find_element(By.CSS_SELECTOR, "img#landingImage").get_attribute("src"),
                    'price': price_text,
                    'old_price': old_price,
                    'category': category_name,
                    'type': product_type,
                    'link': f"{link}&tag={AFFILIATE_TAG}"
                }
                products.append(product)

        except Exception as e:
            continue

    driver.quit()
    print(f"✅ Scraped {len(products)} {category_name} products.")
    return products

# Save products to JavaScript file
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

    all_products = []
    all_products.extend(scrape_bestsellers())
    all_products.extend(scrape_deals(URLS["Top Deal"], "Top Deals", (50, 60)))  # 50-60% for Top Deals
    all_products.extend(scrape_deals(URLS["Price Drop"], "Price Drops", (80, 90)))  # 80-90% for Price Drops

    if all_products:
        save_to_js(all_products)
        print("🎉 Scraping and saving completed successfully.")
    else:
        print("⚠️ No products were saved. Check scraper or Amazon layout.")
