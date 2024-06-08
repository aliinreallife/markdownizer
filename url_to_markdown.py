import os
from typing import Dict, Union
import requests
from bs4 import BeautifulSoup
import html2text
import logging
from urllib.parse import urlparse
from bs4.element import Tag

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

UNWANTED_SELECTORS = {
    "div": [
        ".content-list",
        ".helpful",
        ".card",
        ".posts",
        ".share",
        ".satisfaction",
        ".report",
        ".cta-content",
        ".in-person-consultation-cta",
        ".call-cta",
    ],
    "button": [".share"],
    "p": [".breadcrumbs", ".views"],
    "a": [".call"],
}


def url_to_markdown(url: str) -> str:
    """
    Converts the content of a URL to markdown format.

    Args:
        url (str): The URL to convert.

    Returns:
        str: The markdown content as a string or an error message.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info("Successfully fetched URL content.")
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return f"An error occurred: {err}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <img> tags and remove them
    for img in soup.find_all("img"):
        img.decompose()

    soup = remove_breadcrumbs(soup)
    article_content = soup.find("article")

    if article_content:
        logging.info("Found article content.")
        article_content = remove_unwanted_elements(article_content)
        article_content = remove_last_element(
            article_content, "div", {"class": "container px-sm-0"}
        )
        html_converter = html2text.HTML2Text()
        html_converter.ignore_links = False
        html_converter.body_width = 0  # Prevents line wrapping
        markdown_content = html_converter.handle(str(article_content))
        return markdown_content
    else:
        logging.warning("No article tag found in the HTML content.")
        return "No article tag found in the HTML content."


def remove_unwanted_elements(article_content: Tag) -> Tag:
    """
    Removes unwanted elements from the article content.

    Args:
        article_content (Tag): The BeautifulSoup object containing the article content.

    Returns:
        Tag: The modified BeautifulSoup object with unwanted elements removed.
    """
    for tag, selectors in UNWANTED_SELECTORS.items():
        for selector in selectors:
            for element in article_content.select(f"{tag}{selector}"):
                element.decompose()
                logging.info(f"Removed unwanted element: {selector}")

    return article_content


def remove_last_element(soup: Tag, tag: str, attrs: Dict[str, str]) -> Tag:
    """
    Removes the last element of a specific tag and attributes from the soup.

    Args:
        soup (Tag): The BeautifulSoup object.
        tag (str): The tag name to remove.
        attrs (Dict[str, str]): The attributes to match.

    Returns:
        Tag: The modified BeautifulSoup object with the last specified element removed.
    """
    elements = soup.find_all(tag, attrs=attrs)
    if elements:
        elements[-1].decompose()
        logging.info(f"Removed the last {tag} element with attributes {attrs}")

    return soup


def remove_breadcrumbs(soup: Tag) -> Tag:
    """
    Removes the 'p' tag with id 'breadcrumbs' from the soup.

    Args:
        soup (Tag): The BeautifulSoup object.

    Returns:
        Tag: The modified BeautifulSoup object with breadcrumbs removed.
    """
    breadcrumbs = soup.find("p", id="breadcrumbs")
    if breadcrumbs:
        breadcrumbs.decompose()
        logging.info("Removed breadcrumbs.")

    return soup


def dump_to_file(
    md_content: str, filename: str, directory: str = "", base_dir: str = "output"
) -> None:
    """Dumps markdown content to a file in a specific directory.

    Args:
        md_content (str): The markdown content to save.
        filename (str): The name of the file.
        directory (str, optional): The directory to save the file in. Defaults to "".
        base_dir (str, optional): The base directory to save the file in. Defaults to "output".
    """

    full_dir = os.path.join(base_dir, directory)
    os.makedirs(full_dir, exist_ok=True)  # Ensure the directory exists

    # Ensure the file has a .md extension
    if not filename.endswith(".md"):
        filename += ".md"

    save_path = os.path.join(full_dir, filename)
    with open(save_path, "w") as f:
        f.write(md_content)
    logging.info(f"Markdown content saved to {save_path}")


def get_url_path(url: str) -> str:
    """Extracts the path of the URL after the base."""
    path = urlparse(url).path
    return path.strip("/")  # Remove leading and trailing slashes


# Usage:
url = "https://visaland.org/australian-tourist-visa"
md_content = url_to_markdown(url)
file_name = get_url_path(url)
dump_to_file(md_content=md_content, filename=f"{file_name}.md")
