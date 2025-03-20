(Full updated code with Blog Section added visually to homepage and styled separately)

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
BLOG_PATH = "./blogs/"  # Path to save blogs

# OpenAI API Keys List (Set via GitHub Secrets)
OPENAI_API_KEYS = [
    os.getenv("OPENAI_KEY_1"),
    os.getenv("OPENAI_KEY_2"),
    os.getenv("OPENAI_KEY_3"),
    os.getenv("OPENAI_KEY_4"),
    os.getenv("OPENAI_KEY_5")
]

# Ensure folders exist
os.makedirs(GITHUB_REPO_PATH, exist_ok=True)
os.makedirs(BLOG_PATH, exist_ok=True)


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
            f.write(f"{review}\n\n")
            f.write(f"---\n\n")

    print(f"Saved: {filename}")


def save_to_json(products):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved product data to JSON.")


def generate_review(title):
    prompt = f"Write a short, engaging review for the product: {title}"
    for key in OPENAI_API_KEYS:
        if key:
            try:
                openai.api_key = key
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=100
                )
                return response.choices[0].text.strip()
            except Exception as e:
                print(f"Key failed, trying next... ({e})")
    print("All keys exhausted or invalid.")
    return ""


def generate_blog():
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"Write a 300-word blog post about trending products on Amazon India for {today}."

    for key in OPENAI_API_KEYS:
        if key:
            try:
                openai.api_key = key
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=500
                )
                blog_content = response.choices[0].text.strip()
                filename = f"{BLOG_PATH}blog-{today}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# Blog - {today}\n\n{blog_content}\n")
                print(f"Blog saved: {filename}")
                return
            except Exception as e:
                print(f"Blog key failed, trying next... ({e})")
    print("All keys exhausted or invalid for blog.")


def generate_index_page(products):
    categories = sorted(set([p['category'] for p in products]))

    index_html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Amazon Bestsellers</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
            .filter, .sort { margin-bottom: 20px; }
            .product { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; display: inline-block; width: 300px; vertical-align: top; margin-right: 20px; }
            img { max-width: 100%; height: auto; display: block; margin-bottom: 10px; }
            a { text-decoration: none; color: #2d89ef; }
            .blog-section { margin-top: 50px; padding: 20px; background: white; border-radius: 8px; }
        </style>
        <script>
            function filterCategory(category) {
                const products = document.querySelectorAll('.product');
                products.forEach(p => {
                    if(category === 'All' || p.dataset.category === category){
                        p.style.display = 'inline-block';
                    } else {
                        p.style.display = 'none';
                    }
                });
            }
            function sortProducts(option) {
                let container = document.getElementById('product-container');
                let items = Array.from(container.getElementsByClassName('product'));
                if(option === 'low'){ items.sort((a,b)=>parseFloat(a.dataset.price)-parseFloat(b.dataset.price)); }
                if(option === 'high'){ items.sort((a,b)=>parseFloat(b.dataset.price)-parseFloat(a.dataset.price)); }
                container.innerHTML = '';
                items.forEach(item => container.appendChild(item));
            }
        </script>
    </head>
    <body>
        <h1>Amazon Bestsellers - Auto Updated</h1>
        <div class=\"filter\">
            <label for=\"categories\">Filter by Category: </label>
            <select id=\"categories\" onchange=\"filterCategory(this.value)\">
                <option value=\"All\">All</option>
    """
    for category in categories:
        index_html += f"<option value='{category}'>{category}</option>"

    index_html += """
            </select>
        </div>
        <div class=\"sort\">
            <label for=\"sort\">Sort by Price: </label>
            <select id=\"sort\" onchange=\"sortProducts(this.value)\">
                <option value=\"none\">None</option>
                <option value=\"low\">Lowest First</option>
                <option value=\"high\">Highest First</option>
            </select>
        </div>
        <div id=\"product-container\">
    """

    for product in products:
        price_numeric = product['price'].replace('₹','').replace(',','').strip()
        try:
            price_float = float(price_numeric)
        except:
            price_float = 0
        index_html += f"""
        <div class='product' data-category='{product['category']}' data-price='{price_float}'>
            <h2>{product['title']}</h2>
            <img src="{product['image']}" alt="{product['title']}">
            <p><strong>Price:</strong> {product['price']} <span style='text-decoration: line-through; color: grey;'>{product['old_price']}</span></p>
            <p><strong>Category:</strong> {product['category']}</p>
            <p><a href="{product['link']}" target="_blank">Buy Now on Amazon</a></p>
        </div>
        """

    index_html += "</div>"

    # Blog Section
    index_html += """
    <div class="blog-section">
        <h2>Latest Blogs</h2>
        <ul>
    """

    # List all blog files
    blog_files = sorted(os.listdir(BLOG_PATH), reverse=True)
    for blog in blog_files:
        index_html += f"<li><a href='./blogs/{blog}' target='_blank'>{blog.replace('-', ' ').replace('.md', '')}</a></li>"

    index_html += """
        </ul>
    </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Homepage updated with Blog section.")

