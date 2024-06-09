from logger import logger
from get_urls import categorize_urls, extract_urls_from_sitemap
from url_to_markdown import url_to_markdown, dump_to_file, get_url_path


def main(sitemap_url):
    try:
        urls_from_sitemap = extract_urls_from_sitemap(sitemap_url)
    except Exception as e:
        logger.error(f"Failed to extract URLs from sitemap: {e}")
        return

    categorized_urls, special_categories = categorize_urls(urls_from_sitemap)

    for category, urls in categorized_urls.items():
        for url in urls:
            try:
                file_name = get_url_path(url)
                markdown = url_to_markdown(url)
                dump_to_file(
                    md_content=markdown, filename=file_name, directory=category
                )
            except Exception as e:
                logger.error(f"Failed to convert URL to markdown and save it: {e}")


if __name__ == "__main__":

    # Sitemap URL
    sitemap_url = "https://visaland.org/post-sitemap.xml"

    main(sitemap_url)
