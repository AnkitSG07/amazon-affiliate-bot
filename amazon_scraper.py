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


def save_to_json(products):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved product data to JSON.")


def generate_index_page(products):
    categories = sorted(set([product['category'] for product in products]))

    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Amazon Bestsellers</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; font-family: Arial, sans-serif; }
            .sidebar { float: left; width: 20%; padding: 20px; background: #fff; border-radius: 10px; margin-right: 5%; }
            .product-container { float: left; width: 75%; }
            .product-card { border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; }
            .product-card img { border-radius: 10px 10px 0 0; max-height: 200px; object-fit: contain; }
            .discount-badge { background: red; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
            .old-price { text-decoration: line-through; color: gray; }
            .buy-btn { background: #28a745; color: white; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h1 class="mb-4 text-center">Amazon Bestsellers</h1>
            <div class="sidebar">
                <h4>Categories</h4>
                <ul class="list-unstyled">
                    <li><a href="#" onclick="filterCategory('All')">All</a></li>
    """

    for category in categories:
        index_html += f"<li><a href='#' onclick=\"filterCategory('{category}')\">{category}</a></li>"

    index_html += """
                </ul>
            </div>
            <div class="product-container row" id="product-container">
    """

    for product in products:
        index_html += f"""
        <div class='col-md-4 product-item' data-category='{product['category']}'>
            <div class='product-card'>
                <img src="{product['image']}" class="card-img-top" alt="{product['title']}">
                <div class="p-3">
                    <h5>{product['title']}</h5>
                    <p><span class="fw-bold">Price:</span> {product['price']} <span class="old-price">₹{int(product['price'].replace('₹','').replace(',',''))*2}</span> <span class="discount-badge">50% OFF</span></p>
                    <p><strong>Category:</strong> {product['category']}</p>
                    <a href="{product['link']}" class="btn buy-btn" target="_blank">Buy Now <i class="fas fa-arrow-right"></i></a>
                </div>
            </div>
        </div>
        """

    index_html += """
            </div>
        </div>
        <script>
            function filterCategory(category) {
                const products = document.querySelectorAll('.product-item');
                products.forEach(product => {
                    if (product.getAttribute('data-category') === category || category === 'All') {
                        product.style.display = 'block';
                    } else {
                        product.style.display = 'none';
                    }
                });
            }
        </script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Homepage updated to Blurb-style design.")


if __name__ == "__main__":
    print("Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()
    print(f"Found {len(products)} products.")
    print("Generating content and homepage...")
    save_to_markdown(products)
    save_to_json(products)
    generate_index_page(products)
    print("All done! Ready for deployment.")
