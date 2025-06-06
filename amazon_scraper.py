import time
import random
import requests
from bs4 import BeautifulSoup
from seleniumwire import webdriver
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

# User-Agent List to Rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
]


def setup_selenium():
    """Sets up headless Chrome driver with rotating user-agent."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Rotate User-Agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)
    return driver


def scroll_and_load_more(driver, scroll_pause_time=3, max_scrolls=10):
    """Scroll down to load more products dynamically."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_bestsellers():
    """Scrapes Amazon Bestsellers using BeautifulSoup."""
    response = requests.get(URLS["Bestseller"], headers={"User-Agent": random.choice(USER_AGENTS)})
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(".p13n-sc-uncoverable-faceout, li.zg-item-immersion, div.zg-grid-general-faceout")

    products = []
    for item in items:
        title = item.select_one(".p13n-sc-truncate-desktop-type2, .p13n-sc-truncated, ._cDEzb_p13n-sc-css-line-clamp-3_1Fn1y")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price, span.a-price > span.a-offscreen")

        price_text = price.get_text(strip=True) if price else "N/A"
        old_price = f"₹{int(price_text.replace('₹', '').replace(',', '').strip()) * 2}" if price_text != "N/A" else "N/A"

        if title and link and image:
            product = {
                "title": title.get_text(strip=True),
                "image": image["src"],
                "price": price_text,
                "old_price": old_price,
                "category": "Bestseller",
                "type": "Bestseller",
                "link": f"https://www.amazon.in{link['href']}&tag={AFFILIATE_TAG}",
            }
            products.append(product)

    print(f"✅ Scraped {len(products)} Bestseller products.")
    return products


def scrape_deals(url, category_name, max_items=10):
    """Scrapes Top Deals and Price Drops with Selenium."""
    driver = setup_selenium()
    driver.get(url)
    time.sleep(5)

    # Scroll to load more content dynamically
    scroll_and_load_more(driver, scroll_pause_time=3, max_scrolls=5)

    try:
        items = driver.find_elements(By.CSS_SELECTOR, ".DesktopDiscountAsinGrid-module__grid_pi4xEmM7RAHNMG9sGVBJ > div")

        if not items:
            print(f"❗ No products found for {category_name}.")
            driver.quit()
            return []

        print(f"✅ Found {len(items)} items for {category_name}.")
        products = []

        for item in items[:max_items]:
            try:
                link_element = item.find_element(By.TAG_NAME, "a")
                product_link = link_element.get_attribute("href")

                driver.get(product_link)
                time.sleep(3)

                title = driver.find_element(By.ID, "productTitle").text.strip()
                image = driver.find_element(By.ID, "landingImage").get_attribute("src")

                try:
                    price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
                    price_text = f"₹{price}"
                except:
                    price_text = "N/A"

                try:
                    old_price = driver.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price span.a-offscreen").text.strip()
                except:
                    old_price = "N/A"

                product_data = {
                    "title": title,
                    "image": image,
                    "price": price_text,
                    "old_price": old_price,
                    "category": category_name,
                    "type": category_name,
                    "link": f"{product_link}&tag={AFFILIATE_TAG}",
                }
                products.append(product_data)

                # Go back to the deals page
                driver.back()
                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Error scraping item: {e}")
                continue

        driver.quit()
        print(f"✅ Scraped {len(products)} {category_name} products.")
        return products

    except Exception as e:
        print(f"❗ Error loading {category_name}: {e}")
        driver.quit()
        return []


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
    all_products.extend(scrape_deals(URLS["Top Deals"], "Top Deals", max_items=5))
    all_products.extend(scrape_deals(URLS["Price Drops"], "Price Drops", max_items=5))

    save_to_js(all_products)
    print("🎉 Scraping and saving completed successfully.")
