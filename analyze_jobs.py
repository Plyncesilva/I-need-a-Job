#!.venv/bin/python

import argparse
import logging
import os

import httpx
from urllib.parse import urlparse
import cloudscraper

def create_data_directory():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logging.info(f"Created data directory at {data_dir}")
    return data_dir

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_input(file_path: str) -> list[str]:
    """
    Read lines from a file and return them as a list of strings.

    Args:
        file_path (str): Path to the input file.

    Returns:
        list[str]: List of strings, with each string representing a line from the file.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def fetch_job_description_cloud(uri):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(uri)
    return response.text

from bs4 import BeautifulSoup

def extract_job_description(html_content):
    """
    Extract text from the job description's main content area.
    
    Args:
        html_content (str): Full HTML page content
    
    Returns:
        str: Extracted text from the job description
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find main content div
    main_content = soup.find('main', id='job-ad-detail-content')
    
    if not main_content:
        return ""
    
    # Extract all text, removing extra whitespace
    job_text = " ".join(main_content.get_text(strip=True, separator=' ').split())
    
    return job_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Job Description Analyzer Bot",
        epilog="Example usage:\n"
               "  python analyze_jobs.py -f [file path] \n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-f', '--file', type=str, required=True, help='Input file')
    args = parser.parse_args()

    setup_logging(args.debug)
    logging.info("Logging setup complete")

    create_data_directory()
    logging.info("Data directory created")

     # Main processing loop
    job_listings = load_input(args.file)
    for uri in job_listings:
        job_description = fetch_job_description_cloud(uri)
        print("="*50)
        print(extract_job_description(job_description))