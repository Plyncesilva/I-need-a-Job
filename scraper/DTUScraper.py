from requests import Response
import cloudscraper
from bs4 import BeautifulSoup
import brotli
from typing import List
import argparse

def fetch_page_html(page_number: int, url: str) -> str:
    # Headers
    headers = {
        'Host': 'dtu.jobteaser.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
        "Accept": "text/html, text/plain",  # Only accept HTML or plain text
        "Accept-Encoding": "identity",  # No compression (no br, gzip, deflate)
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://dtu.jobteaser.com/da/onboarding/search-tools',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        'Te': 'trailers',
        'Cookie': ''
    }
    
    url = url +  f"&page={page_number}"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    return response.text

def fetch_dtu_job_offers(url: str) -> Response:
    try:
        # figure out number of pages
        html = fetch_page_html(1, url)

        last_page_num = 1

        soup = BeautifulSoup(html, 'html.parser')
        nav = soup.find('nav', class_=lambda x: x and x.startswith('Pagination_main__'))
        if nav:
            last_link = nav.find('a', class_=lambda x: x and 'Pagination_item___last__' in x)
            if last_link:
                last_page_text = last_link.get_text()

                last_page_num = int(last_page_text) if last_page_text else 1
        print(f"Total search pages are: {last_page_num}")

        urls = []
        for page_number in range(1, last_page_num + 1):
            html = fetch_page_html(page_number, url)
            new_urls = fetch_job_posting_urls(html)
            print(f"Found {len(new_urls)} job offers on page {page_number}")
            urls.extend(new_urls)
            print("Current size of urls list:", len(urls))

        return urls
    except Exception as e:
        print(f"Error fetching job offers: {e}")
        return None

def fetch_job_posting_urls(html: str) -> List[str]:
    base_url = "https://dtu.jobteaser.com"

    soup = BeautifulSoup(html, 'html.parser')
    # Find ul element with class that starts with PageContent_results
    results_ul = soup.find('ul', class_=lambda x: x and x.startswith('PageContent_results'))
    if not results_ul:
        print("No results <ul> element found")

    # Extract all href values from the results
    links = []
    if results_ul:
        for a_tag in results_ul.find_all('a'):
            href = a_tag.get('href')
            if href:
                links.append(base_url + href)

    return links

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape job postings from DTU Career Hub')
    parser.add_argument('--url', help='Full URL of the search from DTU Career Hub', required=True)
    parser.add_argument('--out', help='Output file to store URLs', required=True)
    args = parser.parse_args()

    urls = fetch_dtu_job_offers(args.url)

    with open(args.out, 'w') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"Job URLs written to {args.out}")
    