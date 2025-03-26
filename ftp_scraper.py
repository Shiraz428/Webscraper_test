from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def get_directory_contents(url):
    """
    Retrieves and prints the names of directories and files within those directories
    from the given URL.

    Args:
        url: The URL of the FTP-like directory listing.

    Returns:
        None.  Prints the directory and file structure.
    """

    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service

    # use context manager for the WebDriver to close properly.
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  #run Chrome in headless mode (no gui)
        options.add_argument("--no-sandbox")  #bypass OS security
        options.add_argument("--disable-dev-shm-usage")  #overcome limited resource problems
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        #wait
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//pre"))  #wait for tag
        )

        #get all links within <pre> tag - drs and files
        links = driver.find_elements(By.TAG_NAME, "a")
        
        #extract href attributes and filter out parent directory link ("../")
        hrefs = [link.get_attribute('href') for link in links if link.get_attribute('href') and "../" not in link.get_attribute('href')]


        for href in hrefs:
            if href.endswith('/'):
                print(f"\nDirectory: {href.split('/')[-2]}")  # Extract directory name

                try:
                    #navigate to subdirectory
                    driver.get(href)

                    #wait
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//pre"))
                    )

                    #find file links within subdirectory.
                    sub_links = driver.find_elements(By.TAG_NAME, "a")
                    
                    #extract href & text, filter out parent directory
                    for sub_link in sub_links:
                        sub_href = sub_link.get_attribute('href')
                        if sub_href and "../" not in sub_href:
                            file_name = sub_link.text
                            print(f"  File: {file_name}")

                except TimeoutException:
                    print(f"  Timed out waiting for directory: {href}")
                except NoSuchElementException:
                    print(f"  Could not find elements in directory: {href}")
                except Exception as e:
                    print(f"  An unexpected error occurred while processing {href}: {e}")

            #The website doesn't list files in top directory, only subdirectories
            #else:
                #print(f"File: {href.split('/')[-1]}") #extract the file name


    except TimeoutException:
        print(f"Timed out waiting for the initial page to load: {url}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'driver' in locals():  #check if driver was initialized
            driver.quit()


#Main
if __name__ == "__main__":
    base_url = ""
    get_directory_contents(base_url)

print("\nDirectory and file listing complete.")
