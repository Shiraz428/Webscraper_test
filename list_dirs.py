import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# Define request headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_directory_contents(url, retries=3):
    """
    Retrieves and prints the names of directories and files within those directories
    from the given URL. Handles connection errors and retries.

    Args:
        url: The URL of the FTP-like directory listing.
        retries: Number of retry attempts if the request fails.
    """
    for attempt in range(retries):
        try:
            # Use a session to reuse the connection
            with requests.Session() as session:
                response = session.get(url, headers=HEADERS, timeout=30)
                response.raise_for_status()  # Raise an error for bad status codes

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links in the page
                links = soup.find_all('a')

                for link in links:
                    href = link.get('href')
                    if href and not href.startswith('../'):  # Skip parent directory links
                        # Skip query parameters (e.g., ?C=N;O=D)
                        if '?' in href:
                            continue

                        # Construct the full URL using urljoin to handle relative paths
                        full_url = urljoin(url, href)

                        if href.endswith('/'):
                            # It's a directory, recursively process it
                            #print(f"\nDirectory: {href.rstrip('/')}")
                            get_directory_contents(full_url)
                        else:
                            # It's a file, print its name
                            print(f"  File: {href}")

                return  # Exit the function on success

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:  # Wait before retrying
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                print(f"Failed to access {url} after {retries} attempts.")


# Main execution
if __name__ == "__main__":
    base_url = "https://gml.noaa.gov/aftp/data/greenhouse_gases/"

    # Define the directories to process
    directories = {
        "n2o": "n2o/flask/surface/",
        "sf6": "sf6/flask/surface/",
    }

    for dir_name, dir_path in directories.items():
        print(f"Processing directory: {dir_name}")
        dir_url = urljoin(base_url, dir_path)
        get_directory_contents(dir_url)

    print("\nDirectory and file listing complete.")
