from typing import List
import requests
from bs4 import BeautifulSoup
import json


def extract_urls_from_sitemap(sitemap_url: str) -> List[str]:
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, "xml")
    loc_tags = soup.find_all("loc")

    # Extract the text from each <loc> tag and store it in a list
    urls = [tag.text for tag in loc_tags]

    # Filter out URLs containing 'wp-content'
    urls = [url for url in urls if "wp-content" not in url]

    # Return the extracted URLs
    return urls


def categorize_urls(urls):
    # Initialize the categories with their variations
    with open("categorizer.json", "r") as f:
        categorizer = json.load(f)

    # Initialize the dictionary for the categorized URLs and the lists for uncategorized URLs and URLs in multiple categories
    categorized_urls = {category: [] for category in categorizer}
    uncategorized_urls = []
    multiple_categories_urls = []

    # Categorize the URLs
    for url in urls:
        url_categories = []

        for category, variations in categorizer.items():
            if any(variation in url for variation in variations):
                url_categories.append(category)
                categorized_urls[category].append(url)

        if len(url_categories) == 0:
            uncategorized_urls.append(url)
        elif len(url_categories) > 1:
            multiple_categories_urls.append(url)

    # Return a tuple with the categorized URLs and the special lists
    return categorized_urls, {
        "uncategorized": uncategorized_urls,
        "multiple_categories": multiple_categories_urls,
    }


# # Usage
# sitemap_url = "https://visaland.org/post-sitemap.xml"
# urls_from_sitemap = extract_urls_from_sitemap(sitemap_url)
# categories, special_categories = categorize_urls(urls_from_sitemap)

# # Print the categorized URLs
# for category, urls in categories.items():
#     print(f"{category} URLs:")
#     for url in urls:
#         print(url)
#     print()

# # Print the uncategorized URLs
# print("Uncategorized URLs:")
# for url in special_categories["uncategorized"]:
#     print(url)
# print()

# # Print the URLs in multiple categories
# print("URLs in multiple categories:")
# for url in special_categories["multiple_categories"]:
#     print(url)
# print()

# print("total:", len(urls_from_sitemap))
# print(
#     "uncategorized:",
#     len(special_categories["uncategorized"]),
#     "| multiple categories:",
#     len(special_categories["multiple_categories"]),
# )
