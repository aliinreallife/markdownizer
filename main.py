from get_urls import categorize_urls, extract_urls_from_sitemap
from url_to_markdown import url_to_markdown, dump_to_file, get_url_path

sitemap_url = "https://visaland.org/post-sitemap.xml"
urls_from_sitemap = extract_urls_from_sitemap(sitemap_url)

categorized_urls, special_categories = categorize_urls(urls_from_sitemap)

for category, urls in categorized_urls.items():
    for url in urls:
        file_name = get_url_path(url)
        markdown = url_to_markdown(url)

        dump_to_file(md_content=markdown, filename=file_name, directory=category)
