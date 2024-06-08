from typing import Dict
import requests
from bs4 import BeautifulSoup
import html2text

UNWANTED_ELEMENTS = {
    "div": [
        "content-list",
        "helpful",
        "card",
        "posts",
        "share",
        "satisfaction",
        "report",
        "cta-content",
    ],
    "button": ["share"],
    "p": ["breadcrumbs", "views"],
}


def url_to_markdown(url: str) -> str:
    """Converts the content of a URL to markdown format."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

    soup = BeautifulSoup(response.text, "html.parser")
    article_content = soup.find("article")

    if article_content:
        article_content = remove_unwanted_elements(article_content)
        article_content = remove_last_element(
            article_content, "div", {"class": "container px-sm-0"}
        )
        html_converter = html2text.HTML2Text()
        html_converter.ignore_links = False
        markdown_content = html_converter.handle(str(article_content))
        return markdown_content
    else:
        return "No article tag found in the HTML content."


def remove_unwanted_elements(article_content) -> BeautifulSoup:
    """Removes unwanted elements from the article content."""
    for tag, classes in UNWANTED_ELEMENTS.items():
        for class_name in classes:
            for element in article_content.find_all(tag, class_=class_name):
                element.decompose()
    return article_content


def remove_last_element(soup, tag, attrs):
    """Removes the last element of a specific tag and attributes from the soup."""
    elements = soup.find_all(tag, attrs=attrs)
    if elements:
        elements[-1].decompose()
    return soup


url = "https://visaland.org/business-visa/"
print(url_to_markdown(url))
