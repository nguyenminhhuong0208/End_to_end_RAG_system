import scrapy
from scrapy.spiders import Spider
from urllib.parse import urlparse
import os
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import datetime
import pytz

class UETSpider(Spider):
    name = 'uet_spider'
    start_urls = ['https://uet.vnu.edu.vn/']
    allowed_domains = ['vnu.edu.vn', 'www.vnu.edu.vn', 'uet.vnu.edu.vn', 'repository.vnu.edu.vn']
    restricted_terms = ['login', 'signin', 'auth', 'facebook', 'youtube', 'vieclam.uet', 'twitter', 'tiktok', 'instagram', 'linkedin']
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = 'data_RAG/data'
        self.processed_urls_file = 'processed_urls.txt'
        self.pending_urls_file = 'pending_urls.txt'
        self.error_urls_file = 'error_urls.txt'
        self.processed_urls = set()
        self.pending_urls = set()
        self.content_threshold = 100  # Minimum content length in characters

        # Create output directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Load previously processed URLs
        if os.path.exists(self.processed_urls_file):
            with open(self.processed_urls_file, 'r', encoding='utf-8') as f:
                self.processed_urls = set(line.strip() for line in f if line.strip())

        # Load pending URLs
        if os.path.exists(self.pending_urls_file):
            with open(self.pending_urls_file, 'r', encoding='utf-8') as f:
                self.pending_urls = set(line.strip() for line in f if line.strip())

    def start_requests(self):
        # Prioritize crawling pending URLs
        for url in self.pending_urls:
            if not (url.startswith('http://') or url.startswith('https://')):
                self.processed_urls.add(url)
                continue
            if url not in self.processed_urls and not any(term in url.lower() for term in self.restricted_terms):
                yield scrapy.Request(url, callback=self.process_page)

        # If no pending URLs, start with initial URLs
        if not self.pending_urls:
            for url in self.start_urls:
                if url not in self.processed_urls:
                    yield scrapy.Request(url, callback=self.extract_links)

    def extract_links(self, response):
        # Parse page to extract links
        soup = BeautifulSoup(response.text, 'html.parser')
        anchors = soup.find_all('a', href=True)
        for anchor in anchors:
            link = anchor['href']
            if not (link.startswith('http://') or link.startswith('https://')):
                continue
            if 'uet' not in link:
                continue
            if not any(term in link.lower() for term in self.restricted_terms) and link not in self.processed_urls and link not in self.pending_urls:
                self.pending_urls.add(link)
                with open(self.pending_urls_file, 'a', encoding='utf-8') as f:
                    f.write(link + '\n')
                yield scrapy.Request(link, callback=self.process_page)

    def process_page(self, response):
        # Skip if URL was already processed
        url = response.url
        if url in self.processed_urls:
            return

        # Generate file path from URL
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        file_name = path.replace('/', '_') or 'home'
        file_path = os.path.join(self.data_dir, file_name)

        # Get crawl timestamp
        crawl_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S %z')

        # Extract page title
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title') or soup.find('h1')
        page_title = title_tag.get_text(strip=True) if title_tag else 'Untitled'

        if url.endswith('.pdf'):
            file_path += '.pdf'
            if not os.path.exists(file_path):
                try:
                    # Save PDF content
                    with open(file_path, 'wb') as f:
                        f.write(response.body)
                    self.processed_urls.add(url)
                    with open(self.processed_urls_file, 'a', encoding='utf-8') as f:
                        f.write(url + '\n')
                    if url in self.pending_urls:
                        self.pending_urls.remove(url)
                        self._update_pending_urls()

                    # Save PDF metadata
                    metadata = (
                        f"--- Page Metadata ---\n"
                        f"Source URL: {url}\n"
                        f"Crawl Time: {crawl_time}\n"
                        f"Page Title: {page_title}\n"
                        f"Content Type: PDF\n"
                        f"Stored Path: {file_path}\n"
                        f"--- End Metadata ---\n"
                    )
                    metadata_path = file_path + '.txt'
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        f.write(metadata)
                except Exception as e:
                    with open(self.error_urls_file, 'a', encoding='utf-8') as f:
                        f.write(f"{url}: Failed to save PDF - {str(e)}\n")
        else:
            file_path += '.txt'
            if not os.path.exists(file_path):
                try:
                    # Remove non-content elements
                    for tag in soup(['header', 'footer', 'nav', 'script', 'style']):
                        tag.decompose()
                    content_area = soup.find('main') or soup.find('article') or soup
                    extracted_content = []

                    # Handle tables if present
                    if soup.find('table'):
                        try:
                            tables = pd.read_html(StringIO(response.text), flavor='bs4')
                            for idx, table in enumerate(tables, 1):
                                if not table.empty:
                                    markdown_table = table.to_markdown(index=False)
                                    extracted_content.append(f"\nTable {idx}:\n{markdown_table}\n")
                                else:
                                    html_tables = soup.find_all('table')
                                    if idx <= len(html_tables):
                                        extracted_content.append(f"\nTable {idx} (Complex):\n{str(html_tables[idx-1])}\n")
                        except ValueError as e:
                            if "No tables found" not in str(e):
                                extracted_content.append(f"\nTable Processing Error: {str(e)}\n")

                    # Handle images with alt text
                    for img in soup.find_all('img'):
                        alt = img.get('alt', '').strip()
                        if alt:
                            extracted_content.append(f"Image Description: {alt}\n")

                    # Extract main text content while preserving structure
                    for element in content_area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                        text = element.get_text(strip=True)
                        if text:
                            prefix = '- ' if element.name == 'li' else ''
                            extracted_content.append(f"{prefix}{text}\n")

                    # Combine extracted content
                    final_text = ''.join(extracted_content)

                    # Check for minimal content
                    if len(final_text.strip()) < self.content_threshold:
                        with open(self.error_urls_file, 'a', encoding='utf-8') as f:
                            f.write(f"{url}: Content too short (length: {len(final_text)})\n")
                    else:
                        # Add metadata to output
                        metadata = (
                            f"--- Page Metadata ---\n"
                            f"Source URL: {url}\n"
                            f"Crawl Time: {crawl_time}\n"
                            f"Page Title: {page_title}\n"
                            f"Content Type: HTML\n"
                            f"Stored Path: {file_path}\n"
                            f"--- End Metadata ---\n\n"
                        )
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(metadata + final_text)
                        self.processed_urls.add(url)
                        with open(self.processed_urls_file, 'a', encoding='utf-8') as f:
                            f.write(url + '\n')
                        if url in self.pending_urls:
                            self.pending_urls.remove(url)
                            self._update_pending_urls()
                except Exception as e:
                    with open(self.error_urls_file, 'a', encoding='utf-8') as f:
                        f.write(f"{url}: Page processing failed - {str(e)}\n")

        # Extract further links for crawling
        anchors = soup.find_all('a', href=True)
        for anchor in anchors:
            link = anchor['href']
            if not (link.startswith('http://') or link.startswith('https://')):
                continue
            if 'uet' not in link:
                continue
            if not any(term in link.lower() for term in self.restricted_terms) and link not in self.processed_urls and link not in self.pending_urls:
                self.pending_urls.add(link)
                with open(self.pending_urls_file, 'a', encoding='utf-8') as f:
                    f.write(link + '\n')
                yield scrapy.Request(link, callback=self.process_page)

    def _update_pending_urls(self):
        # Update pending URLs file
        with open(self.pending_urls_file, 'w', encoding='utf-8') as f:
            for url in self.pending_urls:
                f.write(url + '\n')

    def closed(self, reason):
        # Save pending URLs when spider closes
        self._update_pending_urls()