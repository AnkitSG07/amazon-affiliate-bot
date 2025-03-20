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

        # Try to get category from parent section or fallback to 'Miscellaneous'
        category_tag = item.find_previous("h2")
        category_text = category_tag.get_text(strip=True) if category_tag else "Miscellaneous"

        if title and link and image:
            product = {
                'title': title.get_text(strip=True),
                'link': "https://www.amazon.in" + link['href'] + f"&tag={AFFILIATE_TAG}",
                'image': image['src'],
                'price': price.get_text(strip=True) if price else "N/A",
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
    # Blurb-style header and layout
    header_html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Amazon Bestsellers</title>
        <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
        <style>
            body { background-color: #f8f9fa; font-family: Arial, sans-serif; }
            .navbar { background: #fff; padding: 1rem; }
            .navbar-brand { font-weight: bold; color: #ff6600; }
            .search-bar { width: 400px; }
            .category-section { margin: 2rem 0; }
            .product-card { border: 1px solid #e0e0e0; border-radius: 10px; padding: 1rem; margin: 1rem; background: #fff; }
            .product-card img { max-height: 150px; object-fit: contain; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <nav class=\"navbar navbar-expand-lg\">
            <div class=\"container-fluid\">
                <a class=\"navbar-brand\" href=\"#\">Blurb</a>
                <form class=\"d-flex\">
                    <input class=\"form-control me-2 search-bar\" type=\"search\" placeholder=\"Search...\">
                    <button class=\"btn btn-outline-success\" type=\"submit\">Search</button>
                </form>
            </div>
        </nav>
        <div class=\"container\">
            <h2 class=\"my-4\">Amazon Top Deals</h2>
            <div class=\"row\">
    """

    product_html = ""
    for product in products:
        product_html += f"""
        <div class='col-md-3'>
            <div class='product-card text-center'>
                <img src='{product['image']}' class='img-fluid' alt='{product['title']}'>
                <h5>{product['title']}</h5>
                <p>{product['price']}</p>
                <p><strong>Category:</strong> {product['category']}</p>
                <a href='{product['link']}' class='btn btn-primary' target='_blank'>Buy Now</a>
            </div>
        </div>
        """

    footer_html = """
            </div>
        </div>
        <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>
    </body>
    </html>
    """

    full_html = header_html + product_html + footer_html

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    print("Homepage generated in Blurb style.")


if __name__ == "__main__":
    print("Scraping Amazon Bestsellers...")
    products = scrape_bestsellers()
    print(f"Found {len(products)} products.")
    print("Generating content and homepage...")
    save_to_markdown(products)
    save_to_json(products)
    generate_index_page(products)
    print("All done! Ready for deployment.")
