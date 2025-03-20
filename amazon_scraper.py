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

# OpenAI API Key from GitHub Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure content folder exists
if not os.path.exists(GITHUB_REPO_PATH):
    os.makedirs(GITHUB_REPO_PATH)


def scrape_bestsellers():
    response = requests.get(AMAZON_BESTSELLER_URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []

    # UPDATED SELECTORS BASED ON CURRENT AMAZON STRUCTURE
    for item in soup.select(".p13n-sc-uncoverable-faceout"):
        title = item.select_one(".p13n-sc-truncate-desktop-type2")
        link = item.select_one("a.a-link-normal")
        image = item.select_one("img")
        price = item.select_one(".p13n-sc-price")
        category = item.select_one(".a-badge-text")

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'link': "https://www.amazon.in" + link['href'] + f"&tag={AFFILIATE_TAG}",
                'image': image['src'],
                'price': price.get_text(strip=True) if price else "N/A",
                'category': category.get_text(strip=True) if category else "General"
            }
            products.append(product)
    return products


def generate_review(product_title):
    prompt = f"Write a short, engaging review for the product '{product_title}' in 100 words."

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        review = response.choices[0].text.strip()
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
            f.write(f"**Price:** {product['price']}\n\n")
            f.write(f"**Category:** {product['category']}\n\n")
            f.write(f"**[Buy Now]({product['link']})**\n\n")
            f.write(f"{review}\n\n---\n\n")

    print(f"Saved: {filename}")


# Save JSON data
def save_to_json(products):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved product data to JSON.")


# Website Index Page Generator
def generate_index_page(products):
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Amazon Bestsellers</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
            .product { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
            img { max-width: 200px; display: block; margin-bottom: 10px; }
            a { text-decoration: none; color: #2d89ef; }
        </style>
    </head>
    <body>
        <h1>Amazon Bestsellers - Auto Updated</h1>
    """

    for product in products:
        index_html += f"""
        <div class='product'>
            <h2>{product['title']}</h2>
            <img src="{product['image']}" alt="{product['title']}">
            <p>Price: {product['price']}</p>
            <p>Category: {product['category']}</p>
            <p><a href="{product['link']}" target="_blank">Buy Now on Amazon</a></p>
        </div>
        """

    index_html += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Homepage updated.")


if __name__ == "__main__":
    print("Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()
    print(f"Found {len(products)} products.")
    print("Generating content and homepage...")
    save_to_markdown(products)
    save_to_json(products)
    generate_index_page(products)
    print("All done! Ready for deployment.")
