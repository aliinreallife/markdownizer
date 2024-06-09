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
