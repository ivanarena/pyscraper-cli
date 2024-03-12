import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse

def crawl(start_url, directory, pdf=False):
    if not os.path.exists(directory):
        os.makedirs(directory)

    visited = set()
    links_to_visit = [start_url]

    while links_to_visit:
        url = links_to_visit.pop(0)
        if url not in visited:
            visited.add(url)
            print(f"Visiting: {url}.")
            if url.endswith('.pdf') and pdf:
                download_pdf(url, directory)
            else:
                download_html(url, directory)
            links = extract_links(url=url, start_url=start_url)
            links_to_visit.extend(links - visited) # Exclude already visited links
        print(f"{len(links_to_visit)} to visit.")

def extract_links(url, start_url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and (href.startswith(start_url) or href.startswith('/')):
            # Join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            links.add(href)
    return links

def download_pdf(url, directory):
    response = requests.get(url)
    filename = url.split('/')
    filepath = os.path.join(directory, filename)
    print(f"Downloaded {filepath}.")
    with open(filepath, 'wb') as f:
        f.write(response.content)

def sanitize_url(url):
    """
        Sanitizes url for html file saving
    """
    if url.startswith('https://'):
        url = url[8:]
    url = url[:-1].replace('/', '_') + '.html'
    return url

def download_html(url, directory):
    """
        Downloads HTML page as a file in output directory
    """
    response = requests.get(url)
    filename = sanitize_url(url)
    filepath = os.path.join(directory, filename)
    print(f"Downloaded {filepath}.")
    with open(filepath, 'wb') as f:
        soup = BeautifulSoup(response.content, features='lxml')
        f.write(soup.prettify().encode('utf-8'))


def cleandir(directory):
    """
    Delete all files and directories in a directory.
    """
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return
    for element in os.listdir(directory):
        element_path = os.path.join(directory, element)
        
        if os.path.isfile(element_path):
            os.remove(element_path)
            print(f"Deleted file: {element_path}")
        elif os.path.isdir(element_path):
            cleandir(element_path)
            os.rmdir(element_path)
            print(f"Deleted directory: {element_path}")
    
    print(f"All elements in {directory} have been deleted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pyscraper CLI")
    parser.add_argument("BASE_URL", help="Base URL to crawl")
    parser.add_argument("-o", "--output-dir", dest="OUTPUT_DIR", default="output", help="Output directory (default: 'output')")
    parser.add_argument("-pdf", "--pdf", dest="PDF", default=True, help="PDF download (default: False)")
    args = parser.parse_args()

    crawl(args.BASE_URL, args.OUTPUT_DIR, args.PDF)