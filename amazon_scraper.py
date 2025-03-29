import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# URLs for different categories
URLS = {
    "Bestseller": "https://www.amazon.in/gp/bestsellers",
    "Top Deal": "https://www.amazon.in/deals?ref_=nav_cs_gb",
    "Price Drop": "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb&rh=p_n_pct-off-with-tax%3A80-"
}

# Amazon Affiliate Tag
AFFILIATE_TAG = "ankit007"

# Maximum retries for failed page loads
MAX_RETRIES = 3

# Set delay between product page requests (to prevent blocking)
MIN_DELAY = 3
MAX_DELAY = 7

# Setup Selenium with automatic ChromeDriver installation
def setup_selenium():
    """Set up Selenium with ChromeDriver and headless mode."""
    chromedriver_autoinstaller.install()  # Automatically install the right version
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Create WebDriver instance
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)  # Increased page load timeout
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

# Scrape Top Deals and Price Drops with complete details
def scrape_deals(url, category_name, max_items=20):
    """Scrapes Top Deals and Price Drops with full price info."""
    driver = setup_selenium()
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load

    products = []
    items = driver.find_elements(By.CSS_SELECTOR,
                                  ".DesktopDiscountAsinGrid-module__grid_pi4xEmM7RAHNMG9sGVBJ > div")

    for item in items[:max_items]:  # Fetch up to max_items items (can be increased)
        try:
            link_element = item.find_element(By.CSS_SELECTOR, "a.a-link-normal")
            product_link = link_element.get_attribute("href")

            # Visit product page to get complete info with retries
            for attempt in range(MAX_RETRIES):
                try:
                    driver.get(product_link)
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))  # Random delay

                    # Scrape product info from the opened product page
                    title = driver.find_element(By.ID, "productTitle").text.strip()
                    image = driver.find_element(By.CSS_SELECTOR, "#landingImage").get_attribute("src")

                    try:
                        price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
                        price_text = f"₹{price}"
                    except:
                        price_text = "N/A"

                    try:
                        old_price = driver.find_element(By.CSS_SELECTOR,
                                                        "span.a-price.a-text-price span.a-offscreen").text.strip()
                    except:
                        old_price = "N/A"

                    if title and product_link and image:
                        product = {
                            'title': title,
                            'image': image,
                            'price': price_text,
                            'old_price': old_price,
                            'category': category_name,
                            'type': category_name,
                            'link': f"{product_link}&tag={AFFILIATE_TAG}"
                        }
                        products.append(product)

                    break  # Break loop if successful
                except TimeoutException:
                    print(f"⚠️ Timeout for {product_link}. Retrying ({attempt + 1}/{MAX_RETRIES})...")
                    if attempt == MAX_RETRIES - 1:
                        print(f"❌ Failed to load {product_link} after {MAX_RETRIES} attempts.")
                        continue

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
    all_products.extend(scrape_deals(URLS["Top Deal"], "Top Deals"))
    all_products.extend(scrape_deals(URLS["Price Drop"], "Price Drops"))

    if all_products:
        save_to_js(all_products)
        print("🎉 Scraping and saving completed successfully.")
    else:
        print("⚠️ No products were saved. Check scraper or Amazon layout.")
