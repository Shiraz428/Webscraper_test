import os
import requests
from bs4 import BeautifulSoup

def download_file(url, save_path):
    """
    Downloads a file from the given URL and saves it to the specified path.

    Args:
        url: The URL of the file to download.
        save_path: The path where the file should be saved.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        # Save the file
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")


def get_directory_contents(url, save_folder):
    """
    Retrieves and downloads files from the given URL and saves them to the specified folder.

    Args:
        url: The URL of the FTP-like directory listing.
        save_folder: The folder where files should be saved.
    """
    try:
        # Create the save folder if it doesn't exist
        os.makedirs(save_folder, exist_ok=True)

        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the page
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href and not href.startswith('../'):  # Skip parent directory links
                if href.endswith('/'):
                    # It's a directory, recursively process it
                    subdir_url = url + href
                    subdir_save_folder = os.path.join(save_folder, href.rstrip('/'))
                    get_directory_contents(subdir_url, subdir_save_folder)
                else:
                    # It's a file, download it
                    file_url = url + href
                    save_path = os.path.join(save_folder, href)
                    download_file(file_url, save_path)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing {url}: {e}")


# Main execution
if __name__ == "__main__":
    base_url = "https://gml.noaa.gov/aftp/data/greenhouse_gases/"

    # Define the directories to process and their corresponding save folders
    directories = {
        "n2o": "n2o_files",  # Save folder for n2o files
        "sf6": "sf6_files",  # Save folder for sf6 files
    }

    for dir_name, save_folder in directories.items():
        print(f"Processing directory: {dir_name}")
        dir_url = base_url + dir_name + "/"
        get_directory_contents(dir_url, save_folder)

    print("\nFile download complete.")
