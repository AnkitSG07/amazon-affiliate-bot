import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Amazon URLs
URLS = {
    "Bestseller": "https://www.amazon.in/gp/bestsellers",
    "Top Deals": "https://www.amazon.in/deals?ref_=nav_cs_gb",
    "Price Drops": "https://www.amazon.in/gp/goldbox?ref_=nav_cs_gb&rh=p_n_pct-off-with-tax%3A80-"
}

# Affiliate tag for adding affiliate links
AFFILIATE_TAG = "ankit007"

# Setup Selenium for scraping
def setup_selenium():
    """Sets up headless Chrome driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

# Scroll and load more products for infinite scroll pages
def scroll_and_load_more(driver, scroll_pause_time=2, max_scrolls=10):
    """Scroll down to load more products dynamically."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Scrape Bestsellers using BeautifulSoup
def scrape_bestsellers():
    """Scrapes Amazon Bestsellers using BeautifulSoup."""
    response = requests.get(URLS["Bestseller"], headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select(".p13n-sc-uncoverable-faceout") or \
            soup.select("li.zg-item-immersion") or \
            soup.select("div.zg-grid-general-faceout")

    products = []
    for item in items:
        title = item.select_one(".p13n-sc-truncate-desktop-type2") or \
                item.select_one(".p13n-sc-truncated") or \
                item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y")

        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price") or item.select_one("span.a-price > span.a-offscreen")

        price_text = price.get_text(strip=True) if price else "N/A"
        old_price = "₹" + str(int(price_text.replace('₹', '').replace(',', '').strip()) * 2) if price_text != "N/A" else "N/A"

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'image': image['src'],
                'price': price_text,
                'old_price': old_price,
                'category': "Bestseller",
                'type': "Bestseller",
                'link': f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}"
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} Bestseller products.")
    return products

# Scrape Top Deals and Price Drops using Selenium
def scrape_deals(url, category_name, max_items=50):
    """Scrapes Top Deals and Price Drops with Selenium."""
    driver = setup_selenium()
    driver.get(url)
    time.sleep(5)

    # Scroll to load more content dynamically
    scroll_and_load_more(driver, scroll_pause_time=3, max_scrolls=15)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".DesktopDiscountAsinGrid-module__grid_pi4xEmM7RAHNMG9sGVBJ > div"))
        )
    except:
        print(f"❗ No products found for {category_name}.")
        driver.quit()
        return []

    products = []
    items = driver.find_elements(By.CSS_SELECTOR,
                                 ".DesktopDiscountAsinGrid-module__grid_pi4xEmM7RAHNMG9sGVBJ > div")

    print(f"✅ Found {len(items)} items for {category_name}.")

    for item in items[:max_items]:  # Limit to max_items to avoid timeouts
        try:
            link_element = item.find_element(By.CSS_SELECTOR, "a.a-link-normal")
            product_link = link_element.get_attribute("href")

            # Open product page to fetch price and details
            driver.get(product_link)
            time.sleep(random.uniform(3, 6))  # Random delay to prevent blocking

            title = driver.find_element(By.ID, "productTitle").text.strip()
            image = driver.find_element(By.CSS_SELECTOR, "#landingImage").get_attribute("src")

            try:
                price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
                price_text = f"₹{price}"
            except:
                price_text = "N/A"

            try:
                old_price = driver.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price span.a-offscreen").text.strip()
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
        except Exception as e:
            print(f"⚠️ Error scraping item: {e}")
            continue

    driver.quit()
    print(f"✅ Scraped {len(products)} {category_name} products.")
    return products

# Save products to JS file
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


# Main Execution
if __name__ == "__main__":
    print("🚀 Scraping Amazon Bestsellers, Top Deals, and Price Drops...")

    all_products = []
    all_products.extend(scrape_bestsellers())
    all_products.extend(scrape_deals(URLS["Top Deals"], "Top Deals", max_items=30))
    all_products.extend(scrape_deals(URLS["Price Drops"], "Price Drops", max_items=30))

    save_to_js(all_products)
    print("🎉 Scraping and saving completed successfully.")
