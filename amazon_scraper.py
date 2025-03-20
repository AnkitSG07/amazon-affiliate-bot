import requests
from bs4 import BeautifulSoup
import openai
import os
import json
from datetime import datetime

# CONFIGURATION
AMAZON_BESTSELLER_URL = "https://www.amazon.in/gp/bestsellers"
AFFILIATE_TAG = "ankit007"
GITHUB_REPO_PATH = "./content/"  # Local path to save files
JSON_PATH = "products.json"  # JSON output file
BLOGS_PATH = "./blogs/"  # Folder to save blogs

# OpenAI API Key from GitHub Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure folders exist
for folder in [GITHUB_REPO_PATH, BLOGS_PATH]:
    if not os.path.exists(folder):
        os.makedirs(folder)


def scrape_bestsellers():
    response = requests.get(AMAZON_BESTSELLER_URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []

    for item in soup.select(".p13n-sc-uncoverable-faceout"):
        title = item.select_one(".p13n-sc-truncate-desktop-type2")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price")

        # Try to get category from parent section or fallback to 'Miscellaneous'
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"

        price_text = price.get_text(strip=True) if price else "N/A"
        old_price = "N/A"
        if price and price_text != "N/A":
            try:
                price_number = int(price_text.replace('₹', '').replace(',', '').strip())
                old_price = f"₹{price_number * 2}"  # Just doubling for demonstration
            except ValueError:
                price_number = "N/A"
                old_price = "N/A"

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'link': "https://www.amazon.in" + link['href'] + f"&tag={AFFILIATE_TAG}",
                'image': image['src'],
                'price': price_text,
                'old_price': old_price,
                'category': category_text
            }
            products.append(product)
    return products


def generate_review(product_title):
    prompt = f"Write a short, engaging review for the product '{product_title}' in 100 words."

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        review = response.choices[0].message.content.strip()
        return review
    except Exception as e:
        print(f"Error generating review: {e}")
        return ""


def save_to_markdown(products):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{GITHUB_REPO_PATH}bestsellers-{today}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Amazon Bestsellers - {today}\n\n")
        for product in products:
            review = generate_review(product['title'])
            f.write(f"## {product['title']}\n")
            f.write(f"![Product Image]({product['image']})\n\n")
            f.write(f"**Current Price:** {product['price']}\n\n")
            f.write(f"**Previous Price:** {product['old_price']}\n\n")
            f.write(f"**Category:** {product['category']}\n\n")
            f.write(f"**[Buy Now]({product['link']})**\n\n")
            f.write(f"{review}\n\n---\n\n")

    print(f"Saved: {filename}")


def save_to_json(products):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved product data to JSON.")


def generate_blog():
    today = datetime.now().strftime("%Y-%m-%d")
    blog_title = f"Top Shopping Tips {today}"
    prompt = f"Write a 300-word engaging blog post about online shopping tips for {today}."

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        blog_content = response.choices[0].message.content.strip()

        image_url = f"https://source.unsplash.com/600x400/?shopping,technology"

        filename = f"{BLOGS_PATH}blog-{today}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {blog_title}\n\n")
            f.write(f"![Blog Image]({image_url})\n\n")
            f.write(blog_content)

        print(f"Blog generated: {filename}")
    except Exception as e:
        print(f"Error generating blog: {e}")


def generate_index_page(products):
    # Basic placeholder homepage
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Amazon Bestsellers - Auto Updated</h1></body></html>")
    print("Homepage updated.")


if __name__ == "__main__":
    print("Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()
    print(f"Found {len(products)} products.")
    print("Generating content and homepage...")
    save_to_markdown(products)
    save_to_json(products)
    generate_blog()
    generate_index_page(products)
    print("All done! Homepage updated and ready.")
