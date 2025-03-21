import openai
import os
import json
from datetime import datetime

# CONFIGURATION
BLOG_FOLDER = "blogs"
BLOG_JSON = "blogs.json"

# OpenAI API Keys List (from GitHub Secrets)
OPENAI_API_KEYS = [
    os.getenv("OPENAI_KEY_1"),
    os.getenv("OPENAI_KEY_2"),
    os.getenv("OPENAI_KEY_3"),
    os.getenv("OPENAI_KEY_4"),
    os.getenv("OPENAI_KEY_5")
]

# Ensure blog folder exists
os.makedirs(BLOG_FOLDER, exist_ok=True)

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
                filename = f"{BLOG_FOLDER}/blog-{today}.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Amazon Trends {today}</title>
</head>
<body>
  <h1>Amazon Trends - {today}</h1>
  <p>{blog_content}</p>
</body>
</html>
""")
                print(f"Blog saved: {filename}")
                return {"title": f"Amazon Trends {today}", "link": f"./{filename}"}
            except Exception as e:
                print(f"Key failed, trying next... ({e})")
    print("All keys exhausted or invalid!")
    return None

def update_blogs_json(new_blog):
    if os.path.exists(BLOG_JSON):
        with open(BLOG_JSON, "r", encoding="utf-8") as f:
            blogs = json.load(f)
    else:
        blogs = []

    blogs.insert(0, new_blog)  # Add latest blog at top
    with open(BLOG_JSON, "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=4)
    print("blogs.json updated.")

if __name__ == "__main__":
    print("Generating blog...")
    new_blog = generate_blog()
    if new_blog:
        update_blogs_json(new_blog)
        print("Done!")
