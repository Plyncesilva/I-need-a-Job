import cloudscraper
from bs4 import BeautifulSoup
from .batch_request import BatchRequest, RequestBody, Message
import uuid
from abc import abstractmethod
from requests import Response

    
class DTUJobPosting:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.job_description = ""
    
    def __cloud_scrape(self, uri: str) -> Response:
        scraper = cloudscraper.create_scraper()
        return scraper.get(uri)

    def to_message(self) -> Message:
        message = f"{self.uri}" \
                    f"{self.job_description}" \
                    + "\n" + "=" * 50 + "\n" \
        
        return Message("user", message)

    def extract_job_description(self) -> str:
        retries = 3
        html_content = None
        
        for _ in range(retries):
            response = self.__cloud_scrape(self.uri)
            if response.status_code == 200:
                html_content = response.text
                break
            
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find main content div
        main_content = soup.find('main', id='job-ad-detail-content')
        
        if not main_content:
            return ""
        
        # Extract all text, removing extra whitespace
        job_text = " ".join(main_content.get_text(strip=True, separator=' ').split())
        self.job_description = job_text