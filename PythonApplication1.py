import os
import requests 
from bs4 import BeautifulSoup
import re
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urljoin, quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import pyautogui
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from difflib import get_close_matches
import subprocess
import tempfile
import re
import urllib.parse
import unicodedata
from difflib import get_close_matches
import time
import requests
from datetime import datetime
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select  # Ensure this is imported
import time
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pyppeteer
import requests
import concurrent.futures
from tqdm import tqdm


# Base directory for manga storage

base_dir =  r"F:\Z Mangas 4 Battwo"
seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"  # Ensure path uses raw string or double backslashes


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Referer": "",
}

def init_selenium():
    # Initialize Chrome options
    chrome_options = Options()
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass Selenium automation detection
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for better compatibility
    chrome_options.add_argument("--incognito")  # Use incognito mode to prevent tracking
    chrome_options.add_argument("--start-maximized")  # Simulate a maximized window
    chrome_options.add_argument("--enable-unsafe-swiftshader")

    chrome_options.add_experimental_option("useAutomationExtension", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Avoid sandboxing issues in some environments
    # Set the path to chromedriver.exe
    chromedriver_path = r"C:\chromedriver\chromedriver.exe"  # Modify this path if needed
    service = Service(chromedriver_path)  # Use Service to handle the executable path

    # Initialize the Chrome driver with the specified options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.execute_cdp_cmd("Network.enable", {})  # Ensure Network domain is enabled
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Referer": "",
        })
    except Exception as e:
        print(f"CDP Command Error: {e}")

    return driver

def human_like_interaction(driver):
    time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
    
    # Simulate scrolling
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1, 3))
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(2, 5))

def close_chrome_like_human():
    """
    Simulates human-like behavior to close Chrome by sending the Ctrl+W (or Command+W on macOS) keyboard shortcut.
    """
    print("Simulating human-like Chrome closure...")
    
    # Adding a delay to mimic human pause before action
    time.sleep(2)

    # Simulate pressing Ctrl+W to close the active Chrome tab (Command+W for macOS)
    pyautogui.hotkey('ctrl', 'w')

    print("Chrome tab closed like a human!")

#clean titles  
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def clean_title_for_search(title):
    # Step 1: Remove content along with brackets: [], (), {}
    title = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", "", title)
    # Step 2: Replace non-alphanumeric characters (except spaces, dashes, and apostrophes) with spaces
    title = re.sub(r"[^\w\s\'-]", " ", title)
    # Step 3: Replace dashes with spaces to avoid word merging (e.g., "Sss-Class" -> "Sss Class")
    title = title.replace("-", " ")
    # Step 4: Normalize spaces and convert to lowercase
    title = re.sub(r"\s+", " ", title).strip().lower()
    # Step 5: Use urllib.parse.quote to encode the title for URL
    return urllib.parse.quote(title)

def normalize_text(text):
    """Normalize text by removing accents and converting to lowercase."""
    return unicodedata.normalize('NFKC', text).strip().lower()

def save_url(manga_dir, url):
    url_file_path = os.path.join(manga_dir, "url.txt")
    with open(url_file_path, "w", encoding="utf-8") as url_file:
        url_file.write(url)
    print(f"URL saved to {url_file_path}")

def update_combined_log():
    combined_log_path = os.path.join(base_dir, "combined_download_log.txt")

    with open(combined_log_path, "w", encoding="utf-8") as combined_log:
        combined_log.write(f"{'Manga Title':<30} {'Total Chapters':<15} {'Last Updated':<25}\n")
        combined_log.write("="*70 + "\n")
        
        for manga_folder in os.listdir(base_dir):
            manga_path = os.path.join(base_dir, manga_folder)
            if os.path.isdir(manga_path):
                log_file = os.path.join(manga_path, "download_log.txt")
                
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8") as individual_log:
                        chapters = individual_log.readlines()
                        if chapters:
                            last_updated = chapters[-1].strip().split("\t")[-1]
                            combined_log.write(f"{manga_folder:<30} {len(chapters):<15} {last_updated:<25}\n")

def log_error(manga_dir, error_message):
    error_log_path = os.path.join(manga_dir, "error_log.txt")
    with open(error_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {error_message}\n")
    print(f"Error logged to {error_log_path}")


#Pay attention
#manganelo txt file and extarct title names
def save_html_as_txt(manga_dir, html_content):
    html_file_path = os.path.join(manga_dir, "page_content.txt")
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    return html_file_path

def extract_alternative_titles_from_file(manga_dir):
    """Extract alternative manga titles from the page_content.txt file."""
    page_content_path = os.path.join(manga_dir, "page_content.txt")
    
    if not os.path.exists(page_content_path):
        print(f"page_content.txt not found in {manga_dir}")
        return []

    # Read the content of the page_content.txt file
    with open(page_content_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML to extract alternative titles 
    soup = BeautifulSoup(html_content, 'html.parser')
    alternative_titles_tag = soup.find('div', class_='pb-2 alias-set line-b-f')

    if alternative_titles_tag:
    
        # Extract the text after the <span> (excluding the label itself)
        titles_text = alternative_titles_tag.text.strip()

        # Split using known delimiters: colon (:) and semicolon (;)
        alternative_titles = [title.strip() for title in re.split(r'\s*[,/]\s*', titles_text) if title.strip()]
        if alternative_titles:
            print("Alternative Titles:", alternative_titles)
            return alternative_titles
        else:
            print("No alternative titles found.")
            return []
    else:
        return []

def extract_alternative_titles(html_content):
    """Extract alternative manga titles from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    alternative_titles_tag = soup.find('div', class_='pb-2 alias-set line-b-f')

    if alternative_titles_tag:
    
        # Extract the text after the <span> (excluding the label itself)
        titles_text = alternative_titles_tag.text.strip()

        # Split using known delimiters: colon (:) and semicolon (;)
        alternative_titles = [title.strip() for title in re.split(r'\s*[,/]\s*', titles_text) if title.strip()]
        if alternative_titles:
            print("Alternative Titles:", alternative_titles)
            return alternative_titles
        else:
            print("No alternative titles found.")
            return []
    else:
        return []

def extract_and_download_cover(manga_dir, html_file_path, base_url, manga_title, alt_site_url):
    success = search_mangadex_and_download_cover_selenium(manga_title, manga_dir, alt_site_url)  # Use Selenium-based search
    if success:
        return

    print("Falling back to original method to download cover image.")
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Select the <img> inside <div class="media-left cover-detail">
    cover_img_tag = soup.select_one('div', class_='col-24 col-sm-8 col-md-6 attr-cover')

    if not cover_img_tag or not cover_img_tag.get('src'):
        log_error(manga_dir, "Cover image tag not found or missing 'src' attribute.")
        return

    # Get the full cover image URL
    cover_img_url = cover_img_tag['src']

    # Download the image
    download_image(cover_img_url, manga_dir, "cover.jpg")

def download_image(img_url, save_dir, save_name, max_retries=3):
    """Download image with retry mechanism."""
    save_path = os.path.join(save_dir, save_name)
    retries = 0

    while retries < max_retries:
        try:
            session = requests.Session()
            # Set default headers, customize as needed
            session.headers.update(headers)
            
            with session.get(img_url, stream=True, timeout=10) as img_response:
                img_response.raise_for_status()

                with open(save_path, 'wb') as img_file:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            img_file.write(chunk)
            
            print(f"Image successfully downloaded and saved at: {save_path}")
            return True
        
        except requests.exceptions.RequestException as e:
            retries += 1
            print(f"Attempt {retries} failed: {e}. Retrying...")
            time.sleep(2)
    
    print(f"Failed to download image after {max_retries} attempts.")
    return False

def search_mangadex_and_download_cover_selenium(manga_title, manga_dir, alt_site_url):

    if os.path.exists(os.path.join(manga_dir, "cover.jpg")):
        print(f"Cover already exists for {manga_title}. Skipping download.")
        return True
    else:
        driver = None  # Initialize driver to None for better exception handling
        try:
            driver = init_selenium()  # Initialize Selenium driver
            cleaned_title = clean_title_for_search(manga_title)
            search_url = f"https://mangadex.org/search?q={cleaned_title}"
            print(f"Searching for {manga_title} on MangaDex using Selenium: {search_url}")
        
            driver.get(search_url)
            human_like_interaction(driver)  # Simulate human behavior on the page

            # Try to find the first manga card that has an image
            first_manga_card = driver.find_element(By.CSS_SELECTOR, 'div.grid.gap-2 img.rounded.shadow-md')
            if not first_manga_card:
                print(f"No results found on MangaDex for {manga_title}. Falling back to alternative titles...")
                return search_using_alternative_titles_from_file(manga_title, manga_dir)

            # Get the cover image URL
            cover_img_url = first_manga_card.get_attribute('src').rsplit('.', 2)[0]
            print(f"Found cover image via Selenium: {cover_img_url}")

            # Download and save the image using Selenium
            driver.get(cover_img_url)
            time.sleep(2)  # Wait for the image to fully load
            save_path = os.path.join(manga_dir, "cover.jpg")

            # Save the image as a screenshot
            with open(save_path, "wb") as file:
                file.write(driver.find_element(By.TAG_NAME, "img").screenshot_as_png)

            print(f"Image downloaded and saved at: {save_path}")
            return True

        except Exception as e:
            log_error(manga_dir, f"Error searching or downloading cover using Selenium: {e}")
            # Fall back to alternative titles if there was an error
            return search_using_alternative_titles_from_file(manga_title, manga_dir)

        finally:
            if driver:
                driver.quit()  

def search_using_alternative_titles_from_file(manga_title, manga_dir):
    global save_title_for_later
    alternative_titles = extract_alternative_titles_from_file(manga_dir)

    if alternative_titles:
        print(f"Alternative titles found in page_content.txt: {alternative_titles}")
        for alt_title in alternative_titles:
            if download_cover_from_mangadex(alt_title, manga_dir):
                print(f"CCC Cover image downloaded using alternative title: {alt_title}")
                save_title_for_later = alt_title
                return True

    print("Failed to download cover image using alternative titles.")
    return False

def download_cover_from_mangadex(manga_title, manga_dir):
    """Attempt to download the cover image from MangaDex using Selenium."""
    driver = init_selenium()
    try:
        manga_title=clean_title_for_search(manga_title)
        search_url = f"https://mangadex.org/search?q={manga_title.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(3)  # Allow time for page load

        first_manga_card = driver.find_element(By.CSS_SELECTOR, 'div.grid.gap-2 img.rounded.shadow-md')
        if first_manga_card:
            cover_img_url = first_manga_card.get_attribute('src').rsplit('.', 2)[0]

            # Download and save the image using Selenium
            driver.get(cover_img_url)
            time.sleep(2)  # Wait for the image to fully load
            save_path = os.path.join(manga_dir, "cover.jpg")

            # Save the image as a screenshot
            with open(save_path, "wb") as file:
                file.write(driver.find_element(By.TAG_NAME, "img").screenshot_as_png)

            return True

        else:
            print(f"No cover image found for {manga_title} on MangaDex.")
            return False

    except Exception as e:
        print(f"Error downloading cover from MangaDex: {e}")
        return False

    finally:
        driver.quit()












def add_cover_to_cbz(manga_title, chapter_title, cbz_name, manga_dir):

    match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
    if match:
        chapter_number = match.group(1)
        if '.' in chapter_number:
            chapter_number = chapter_number.replace('.', 'p')
        else:
            chapter_number = f"{int(chapter_number):02}"

    cbz_name = f"{manga_title} Chapter {chapter_number}.cbz"
    cbz_path = os.path.join(manga_dir, cbz_name)

    cover_image_path = os.path.join(manga_dir, "cover.jpg")

    # Check if the CBZ file exists
    if not os.path.exists(cbz_path):
        print(f"CBZ file for '{manga_title}' not found.")
        return

    # Append the cover image to the CBZ file as '000.jpg'
    print("Adding cover image to the CBZ file as '000.jpg'.")
    
    with ZipFile(cbz_path, 'a', ZIP_DEFLATED) as cbz_file:
        cbz_file.write(cover_image_path, '000.jpg')
    
    print(f"Cover image added to '{cbz_name}' as '000.jpg'.")

#MangaUpdates Help searching close titles
def find_closest_match2(search_title, manga_titles):
    """
    Find the closest match for a given title.
    First, look for an exact match; if none, use difflib.get_close_matches to find the closest title.
    """
    # Normalize the search title
    search_title = normalize_text(search_title)
    # Normalize and clean the manga titles
    manga_titles_clean = [normalize_text(title) for title in manga_titles]
    
    # Debugging output
    print(f"Normalized search title: {search_title}")
    print(f"Normalized manga titles: {manga_titles_clean}")

    # First, check for an exact match
    if search_title in manga_titles_clean:
        exact_index = manga_titles_clean.index(search_title)
        print(f"Exact match found: {manga_titles[exact_index]}")
        return manga_titles[exact_index]  # Return the original title (unmodified)
    
    # If no exact match, find the closest match using difflib
    closest_matches = get_close_matches(search_title, manga_titles_clean, n=1, cutoff=0.6)
    if closest_matches:
        closest_index = manga_titles_clean.index(closest_matches[0])
        print(f"Closest match found: {manga_titles[closest_index]}")
        return manga_titles[closest_index]  # Return the original title

    print("No match found.")
    return None

def find_and_extract_closest_match(txt_file_path, manga_title):
    """Search the text file for the closest title match and extract the corresponding link."""
    if not os.path.exists(txt_file_path):
        print(f"File {txt_file_path} not found.")  # Debugging
        return None, None
    
    with open(txt_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Extract titles and links using the updated regex-based functions
    titles = extract_titles_from_content(content)
    links = extract_links_from_content(content)
    
    print(f"Extracted {len(titles)} titles and {len(links)} links")  # Debugging
    
    # Check if the number of titles matches the number of links
    if len(titles) != len(links):
        print(f"Mismatch between number of titles and links: {len(titles)} titles, {len(links)} links.")
        return None, None

    if titles:
        # Find the closest matching title (using the cleaned title list for matching)
        closest_title = find_closest_match2(manga_title, titles)
        if closest_title:
            # Normalize titles to find the index of the closest match
            normalized_titles = [title.strip().lower() for title in titles]
            match_index = normalized_titles.index(closest_title.strip().lower())  # Use normalized title for lookup
            print(f"Closest title found: {titles[match_index]}, at index: {match_index}")  # Return the original title and index
            return titles[match_index], links[match_index]  # Return the original title and the link

    # Return None if no match was found
    print("No match found.")  # Debugging
    return None, None

def extract_titles_from_content(content):
    """Extract all manga titles from the downloaded content."""
    # Adjusted regex to match <a title="Click for Series Info" and extract the title inside <span>
    return re.findall(r'<a[^>]*title="Click for Series Info"[^>]*><span[^>]*>(.*?)</span></a>', content)

def extract_links_from_content(content):
    """Extract all manga info links from the downloaded content."""
    # Adjusted regex to extract the href attribute from <a title="Click for Series Info">
    return re.findall(r'<a\s+title="Click for Series Info"\s+href="(.*?)"', content)

manga_title3 = None
manga_title4 = None
#MangaUpdates
def search_manga_and_download_html_mangaupdates(manga_title, manga_dir):
    """Search for a manga on MangaUpdates and download the HTML of the Series Info page."""
    txt_file_path = os.path.join(manga_dir, "Mangaupdates_SearchResults.txt")
    global save_title_for_later  # Fallback title
    global manga_title3

    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangaupdates_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file


    # Construct the search URL 

    cleaned_title = re.sub(r"[!$@#%&*\(\)\-+=\[\]{}|;:'\"<>\?/.,]", "", manga_title)
    search_title = cleaned_title.replace(" ", "+")
    encoded_title = urllib.parse.quote(search_title)
    search_url = f"https://www.mangaupdates.com/site/search/result?search={encoded_title}"
    
    try:
        # Fetch the static content from the URL
        response = requests.get(search_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get content type
        content_type = response.headers.get('Content-Type')

        # Ensure directory exists
        if not os.path.exists(manga_dir):
            os.makedirs(manga_dir)

        # Determine file extension based on content type
        mode = 'w' if 'text' in content_type else 'wb'  # Text or binary mode
        content = response.text if mode == 'w' else response.content

        # Save the content into the appropriate file
        with open(txt_file_path, mode, encoding='utf-8' if mode == 'w' else None) as file:
            file.write(content)

        print(f"Content successfully saved to {txt_file_path}")

        # Find the closest match in the downloaded file
        closest_title, manga_link = find_and_extract_closest_match(txt_file_path, manga_title)

        if closest_title:
            print(f"Found closest match: {closest_title}")

            # Use Selenium to load the manga info page
            driver = init_selenium()
            try:
                driver.get(manga_link)
                time.sleep(3)  # Wait for the page to load


                manga_title3 = driver.find_element(By.CLASS_NAME, 'releasestitle').text
                manga_title3 = sanitize_filename(manga_title3)
                if manga_title3.endswith("."):
                    manga_title3 = manga_title3[:-1]
                html_file_path = os.path.join(manga_dir, f"Mangaupdates_Metadata_{manga_title3}.txt")

                # Save the HTML content of the manga info page
                html_content = driver.page_source
                with open(html_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)
                print(f"HTML content saved to {html_file_path}")

                return html_file_path
            finally:
                # Clean up the search results file after successful match
                if os.path.exists(txt_file_path):
                    os.remove(txt_file_path)
                driver.quit()
        else:
            print(f"No close match found for '{manga_title}'. Deleting {txt_file_path}.")
            if os.path.exists(txt_file_path):
                os.remove(txt_file_path)

            # Retry with alternative title if available
            if save_title_for_later:
                print(f"Trying alternative title: {save_title_for_later}")
                return search_manga_and_download_html_mangaupdates2(save_title_for_later, manga_dir)
            else:
                print("No alternative title available to fall back on.")
                return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the content: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        # Retry with alternative title if available
        try:
            if save_title_for_later:
                print(f"Trying alternative title: {save_title_for_later}")
                return search_manga_and_download_html_mangaupdates2(save_title_for_later, manga_dir)
            else:
                print("No alternative title available to fall back on.")
                return None
        except Exception as e:
            print(f"Failed with alternative title: {e}. Trying alternative title search V2...")
            return search_manga_and_download_html_mangaupdates3(manga_dir)

def search_manga_and_download_html_mangaupdates2(manga_title, manga_dir):
    """Search for a manga on MangaUpdates and download the HTML of the Series Info page."""
    txt_file_path = os.path.join(manga_dir, "Mangaupdates_SearchResults.txt")

    global manga_title3

    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangaupdates_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file

    # Construct the search URL 
    cleaned_title = re.sub(r"[!$@#%&*\(\)\-+=\[\]{}|;:'\"<>\?/.,]", "", manga_title)
    search_title = cleaned_title.replace(" ", "+")
    encoded_title = urllib.parse.quote(search_title)
    search_url = f"https://www.mangaupdates.com/site/search/result?search={encoded_title}"



    try:
        # Fetch the static content from the URL
        response = requests.get(search_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get content type
        content_type = response.headers.get('Content-Type')

        # Ensure directory exists
        if not os.path.exists(manga_dir):
            os.makedirs(manga_dir)

        # Save the content based on type (text or binary)
        mode = 'w' if 'text' in content_type else 'wb'
        content = response.text if mode == 'w' else response.content

        # Save the search results into the appropriate file
        with open(txt_file_path, mode, encoding='utf-8' if mode == 'w' else None) as file:
            file.write(content)

        print(f"Content successfully saved to {txt_file_path}")

        # Find the closest match in the downloaded file
        closest_title, manga_link = find_and_extract_closest_match(txt_file_path, manga_title)

        if closest_title:
            print(f"Found closest match: {closest_title}")

            # Use Selenium to load the manga info page
            driver = init_selenium()
            try:
                driver.get(manga_link)
                time.sleep(3)  # Wait for the page to load

                manga_title3 = driver.find_element(By.CLASS_NAME, 'releasestitle').text
                manga_title3 = sanitize_filename(manga_title3)
                if manga_title3.endswith("."):
                    manga_title3 = manga_title3[:-1]
                html_file_path = os.path.join(manga_dir, f"Mangaupdates_Metadata_{manga_title3}.txt")



                # Save the HTML content of the manga info page
                html_content = driver.page_source
                with open(html_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

                print(f"HTML content saved to {html_file_path}")
                return html_file_path
            finally:
                # Ensure the driver quits and clean up the text file
                driver.quit()
                if os.path.exists(txt_file_path):
                    os.remove(txt_file_path)
        else:
            print(f"No close match found for '{manga_title}'. Deleting {txt_file_path}.")
            if os.path.exists(txt_file_path):
                os.remove(txt_file_path)
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the content: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def search_manga_and_download_html_mangaupdates3(manga_dir):
    """Search for a manga on MangaUpdates using alternative titles and download the HTML of the Series Info page."""
    global manga_title3
    # Extract multiple alternative titles from the file
    alternative_titles = extract_alternative_titles_from_file2(manga_dir)
    txt_file_path = os.path.join(manga_dir, "Mangaupdates_SearchResults.txt")
    
    if not alternative_titles:
        print("No valid alternative titles found.")
        return None

    

    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangaupdates_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file

    try:
        # Iterate through the alternative titles to find the closest match
        for manga_title in alternative_titles:
            # Construct the search URL 

            cleaned_title = re.sub(r"[!$@#%&*\(\)\-+=\[\]{}|;:'\"<>\?/.,]", "", manga_title)
            search_title = cleaned_title.replace(" ", "+")
            encoded_title = urllib.parse.quote(search_title)
            search_url = f"https://www.mangaupdates.com/site/search/result?search={encoded_title}"

            
            print(f"Searching for: {manga_title}")

            try:
                # Fetch the static content from the URL
                response = requests.get(search_url, stream=True)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Get content type
                content_type = response.headers.get('Content-Type')

                # Ensure directory exists
                if not os.path.exists(manga_dir):
                    os.makedirs(manga_dir)

                # Determine file extension based on content type
                mode = 'w' if 'text' in content_type else 'wb'
                content = response.text if mode == 'w' else response.content

                # Save the content into the appropriate file
                with open(txt_file_path, mode, encoding='utf-8' if mode == 'w' else None) as file:
                    file.write(content)

                print(f"Content successfully saved to {txt_file_path}")

                # Find the closest match in the downloaded file
                closest_title, manga_link = find_and_extract_closest_match(txt_file_path, manga_title)

                if closest_title:
                    print(f"Found closest match: {closest_title}")

                    # Use Selenium to load the manga info page
                    driver = init_selenium()  # Initialize the driver only when needed
                    try:
                        driver.get(manga_link)
                        time.sleep(3)  # Wait for the page to load

                        manga_title3 = driver.find_element(By.CLASS_NAME, 'releasestitle').text
                        manga_title3 = sanitize_filename(manga_title3)
                        if manga_title3.endswith("."):
                           manga_title3 = manga_title3[:-1]
                        html_file_path = os.path.join(manga_dir, f"Mangaupdates_Metadata_{manga_title3}.txt")



                        # Save the HTML content of the manga info page
                        html_content = driver.page_source
                        with open(html_file_path, "w", encoding="utf-8") as html_file:
                            html_file.write(html_content)
                        print(f"HTML content saved to {html_file_path}")
                        
                        return html_file_path  # Return after successful save
                    finally:
                        driver.quit()  # Ensure driver quits properly
                        if os.path.exists(txt_file_path):
                            os.remove(txt_file_path)  # Clean up text file after successful search
                else:
                    print(f"No close match found for '{manga_title}'. Deleting {txt_file_path}.")
                    if os.path.exists(txt_file_path):
                        os.remove(txt_file_path)  # Clean up if no match
                    continue  # Try the next title

            except requests.exceptions.RequestException as e:
                print(f"An error occurred while downloading the content: {e}")
                continue  # Continue to the next alternative title if there's a network issue

            except TimeoutException as e:
                print(f"Timeout while searching for '{manga_title}': {e}")
                continue  # Continue to the next alternative title if there's a timeout

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Exhausted all alternative titles without finding a match.")
    return None

# Mangadex
def search_manga_and_download_html(manga_title, manga_dir):
    """
    Search for a manga on MangaDex and download the HTML if it doesn't exist already.
    If this fails, try searching via the alternative title stored in `save_title_for_later`.
    """
    global save_title_for_later
    global manga_title4

    
    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangadex_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file


    driver = init_selenium()  # Assumes you have an init_selenium() function
    cleaned_title = clean_title_for_search(manga_title)
    search_url = f"https://mangadex.org/search?q={cleaned_title}"
    driver.get(search_url)

    try:
        # Wait for the manga card to load, with retries in case of failures
        first_manga_card = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.grid.gap-2 a.manga-card-dense'))
        )
        first_manga_card.click()
        time.sleep(3)


        manga_title4 = driver.find_element(By.CLASS_NAME, 'title').find_element(By.TAG_NAME, 'p').text
        manga_title4 = sanitize_filename(manga_title4)
        if manga_title4.endswith("."):
            manga_title4 = manga_title4[:-1]
        html_file_path = os.path.join(manga_dir, f"Mangadex_Metadata_{manga_title4}.txt")

        # Save the current page's HTML as a .txt file
        html_content = driver.page_source
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"HTML content saved to {html_file_path}")
        return html_file_path
    except Exception as e:
        print(f"Error searching manga with title '{manga_title}': {e}")

        # Retry with alternative title if available
        try:
            if save_title_for_later:
                print(f"Trying alternative title: {save_title_for_later}")
                return search_manga_and_download_html2(save_title_for_later, manga_dir)
            else:
                print("No alternative title available to fall back on.")
                return None
        except Exception as e:
            print(f"Failed with alternative title: {e}. Trying alternative title search V2...")
            return search_manga_and_download_html3(manga_dir)
        finally:
            driver.quit()
    finally:
        driver.quit()

def search_manga_and_download_html2(manga_title, manga_dir):
    """
    Search for a manga on MangaDex and download the HTML if it doesn't exist already.
    If this fails, retry by using alternative titles from `page_content.txt` one at a time.
    """
    global manga_title4

    
    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangadex_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file


    driver = init_selenium()
    search_url = f"https://mangadex.org/search?q={manga_title.replace(' ', '+')}"
    driver.get(search_url)

    try:
        # Wait for the first manga card to load
        first_manga_card = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.grid.gap-2 a.manga-card-dense'))
        )
        first_manga_card.click()
        time.sleep(3)  # Allow the page to load

        manga_title4 = driver.find_element(By.CLASS_NAME, 'title').find_element(By.TAG_NAME, 'p').text
        manga_title4 = sanitize_filename(manga_title4)
        if manga_title4.endswith("."):
           manga_title4 = manga_title4[:-1]
        
        html_file_path = os.path.join(manga_dir, f"Mangadex_Metadata_{manga_title4}.txt")

        # Save the page's HTML as a .txt file
        html_content = driver.page_source
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"HTML content saved to {html_file_path}")
        return html_file_path

    except Exception as e:
        print(f"Error searching manga with title '{manga_title}': {e}")

        # Retry with alternative titles from the file
        alternative_titles = extract_alternative_titles_from_file2(manga_dir)
        if not alternative_titles:
            print("No alternative titles available.")
            return None

        for alt_title in alternative_titles:
            print(f"Trying alternative title: {alt_title}")
            html_file_path = search_manga_and_download_html3(alt_title, manga_dir)
            if html_file_path:
                return html_file_path  # Stop if a match is found

        print("No matching titles found, even with alternative titles.")
        return None

    finally:
        driver.quit()

def search_manga_and_download_html3(manga_dir):
    """
    Search for a manga on MangaDex and download the HTML if it doesn't exist already.
    This is the final fallback method with no further retries.
    """
    global manga_title4

    
    # Check if file exists without including the manga title yet
    existing_file = [f for f in os.listdir(manga_dir) if f.startswith("Mangadex_Metadata")]
    if existing_file:
        print(f"File {existing_file} already exists. Skipping download.")
        return existing_file

    # Extract multiple alternative titles from the file
    alternative_titles = extract_alternative_titles_from_file2(manga_dir)
    
    if not alternative_titles:
        print("No valid alternative titles found.")
        return None

    driver = init_selenium()

    try:
        # Loop through each alternative title to find a match
        for manga_title in alternative_titles:
            search_url = f"https://mangadex.org/search?q={quote_plus(manga_title)}"
            print(f"Searching for: {manga_title}")
            driver.get(search_url)

            try:
                # Wait for the first manga card to appear
                first_manga_card = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.grid.gap-2 a.manga-card-dense'))
                )
                first_manga_card.click()

                time.sleep(3)  # Allow the page to load

                manga_title4 = driver.find_element(By.CLASS_NAME, 'title').find_element(By.TAG_NAME, 'p').text
                manga_title4 = sanitize_filename(manga_title4)
                if manga_title4.endswith("."):
                   manga_title4 = manga_title4[:-1]

                html_file_path = os.path.join(manga_dir, f"Mangadex_Metadata_{manga_title4}.txt")

                # Save the HTML content of the page
                html_content = driver.page_source
                with open(html_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)
                print(f"HTML content saved to {html_file_path}")
                return html_file_path

            except TimeoutException as e:
                print(f"Timeout while searching for '{manga_title}': {e}")
                continue  # Try the next title in the list

        print("Exhausted all alternative titles without finding a match.")
        return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    finally:
        driver.quit()


#Comicinfo.xml
def extract_metadata_from_txt_mangaupdates(manga_dir):

    if manga_title3 is None:
        metadata_files = [os.path.join(manga_dir, f) for f in os.listdir(manga_dir) if f.startswith("Mangaupdates_Metadata")]
        if not metadata_files:
            print(f"Error: No Mangaupdates_Metadata.txt found in {manga_dir}")
            return {}
        page_content_path = metadata_files[0]  # Select the first file
    elif manga_title3 is not None:
        page_content_path = os.path.join(manga_dir, f"Mangaupdates_Metadata_{manga_title3}.txt")
        if not os.path.exists(page_content_path):
            print(f"Error: {page_content_path} not found.")
            return {}

    # Read the content of the .txt file (HTML)
    with open(page_content_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize empty metadata dictionary
    metadata = {
        'Authors': [],
        'Artists': [],
        'Publishers': [],
        'Genres': [],
        'Year': [],
        'Alternative Titles': [],
        'Summary': []
    }
    
    # Extract Authors
    authors_section = soup.find('div', {'data-cy': 'info-box-authors'})
    if authors_section:
        metadata['Authors'] = [span.text.strip() for span in authors_section.find_all('span', class_='linked-name_name_underline__QgZKK')]
    else:
        metadata['Authors'] = None

    # Extract Artists
    artists_section = soup.find('div', {'data-cy': 'info-box-artists'})
    if artists_section:
        metadata['Artists'] = [span.text.strip() for span in artists_section.find_all('span', class_='linked-name_name_underline__QgZKK')]
    else:
        metadata['Artists'] = None

    # Extract Genres
    genres_section = soup.find('div', {'data-cy': 'info-box-genres'})

    if genres_section:
        genre_links = genres_section.find_all('a', href=True)
        # Filter out unwanted "Search for series of same genre(s)" links
        metadata['Genres'] = [
            link.text.strip() 
            for link in genre_links 
            if not 'Search for series of same genre(s)' in link.text
        ]
    else:
        metadata['Genres'] = None

    # Extract Publishers
    publishers_section = soup.find('div', {'data-cy': 'info-box-original_publisher'})
    if publishers_section:
        publisher_names = publishers_section.find_all('span', class_='linked-name_name_underline__QgZKK')
        metadata['Publishers'] = [pub.text.strip() for pub in publisher_names]
    else:
        metadata['Publishers'] = None

    # Extract Year
    year_section = soup.find('div', {'data-cy': 'info-box-year'})
    if year_section:
        year_text = year_section.text.strip()
        if re.match(r'\d{4}', year_text):
            metadata['Year'] = year_text
        else:
            metadata['Year'] = None
    else:
            metadata['Year'] = None
    

    # Extract Alternative Titles
    alt_titles_section = soup.find('div', {'data-cy': 'info-box-associated'})
    if alt_titles_section:
        alt_titles = [div.text.strip() for div in alt_titles_section.find_all('div')]
        metadata['Alternative Titles'] = alt_titles
    else:
            metadata['Alternative Titles'] = None

    print(f"Extracted Mangaupdates Metadata: {metadata}")


    # Find the specific class containing the summary
    summary_section = soup.find('div', {'class': 'mu-markdown_mu_markdown__pqmRi'})

    # Extract the text from the summary section, excluding unwanted parts
    if summary_section:
        # Remove specific parts like "Original Webtoon"
        for p in summary_section.find_all('p'):
            if 'Original Webtoon' in p.get_text():
                p.decompose()
    
        # Join the remaining text as the summary
        summary = ' '.join(p.get_text(strip=True) for p in summary_section.find_all('p'))
    else:
        summary = None

    # Output metadata
    metadata['Summary'] = summary
    

    return metadata

def extract_metadata_from_txt(manga_dir):
    """Extract metadata from Mangadex_Metadata.txt."""

    if manga_title4 is None:
        metadata_files = [os.path.join(manga_dir, f) for f in os.listdir(manga_dir) if f.startswith("Mangadex_Metadata")]
        if not metadata_files:
            print(f"Error: No Mangadex_Metadata.txt found in {manga_dir}")
            return {}
        page_content_path = metadata_files[0]  # Select the first file
    elif manga_title4 is not None:
         page_content_path = os.path.join(manga_dir, f"Mangadex_Metadata_{manga_title4}.txt")
    if not os.path.exists(page_content_path):
        print(f"Error: {page_content_path} not found.")
        return {}

    # Read the content of the .txt file (HTML)
    with open(page_content_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    
    # Find the container holding the authors.
    authors_container = soup.find('div', class_='flex gap-2 flex-wrap')
    if authors_container:
        # Extract all <span> tags within the <a> tags for authors.
        extracted_authors = [
            span.get_text(strip=True)
            for span in authors_container.find_all('span')
        ]
    
        # Join the author names with commas if any are found.
        if extracted_authors:
            writer = ', '.join(extracted_authors)
        else:
            writer = None
    else:
            writer = None 



    # Find the container holding the artist names
    artists_container = soup.find('div', class_='flex gap-2 flex-wrap')
    if artists_container:
        # Extract all <span> tags within the <a> tags for artists
        extracted_artists = [
            span.get_text(strip=True)
            for span in artists_container.find_all('span')
        ]
    
        # Join the artist names with commas if any are found
        if extracted_artists:
            Artist = ', '.join(extracted_artists)
        else:
            Artist = None
    else:
            Artist = None

    # Extract Genres
    genre_tags = soup.find_all('a', class_='tag bg-accent')
    genres = [genre_tag.text for genre_tag in genre_tags] if genre_tags else None

    # Extract Tags
    tag_elements = soup.find_all('span', class_='tag text-white bg-status-yellow')
    tags = [tag_element.text for tag_element in tag_elements] if tag_elements else None


    # Find the container holding the content
    summary_tag = soup.find('div', class_='md-md-container')
    if not summary_tag:
        return 'No summary available.'
    
    # Initialize an empty list to store paragraphs
    paragraphs = []
    
    # Traverse the elements inside the container
    for element in summary_tag.contents:
        if element.name == 'hr':
            # Stop processing if <hr> is encountered (links section starts here)
            break
        if element.name == 'p':
            # Add only text content from <p> tags
            paragraphs.append(element.get_text(strip=True))
    
    # Join paragraphs with line breaks and return the cleaned summary
    summary = "\n\n".join(paragraphs)
    if not summary:
        summary = None

    alt_titles_elements = soup.find_all('div', class_='alt-title')
    alt_titles = [alt_title.find('span').text.strip() for alt_title in alt_titles_elements] if alt_titles_elements else None
    # If the list is empty after extraction, assign None
    alt_titles = alt_titles if alt_titles else None


    # Find the span that contains the publication year
    publication_span = soup.find('span', text=lambda t: t and 'Publication:' in t)

    # Extract the year
    if publication_span:
        # Split the text to isolate the year
        publication_text = publication_span.text
        year = publication_text.split('Publication: ')[1].split(',')[0].strip()
        Year = year if year else None


    metadata = {
        'Writer': writer,
        'Artist': Artist,
        'Genres': genres,
        'Tags': tags,
        'Summary': summary,
        'Alternative Titles': alt_titles,
        'Year': Year
    }

    print(f"Extracted MangaDex Metadata: {metadata}")
    return metadata

def extract_alternative_titles_from_file2(manga_dir):

    page_content_path = os.path.join(manga_dir, "page_content.txt")
    
    if not os.path.exists(page_content_path):
        print(f"Error: page_content.txt not found in {manga_dir}")
        return []

    # Read the content of the page_content.txt file
    with open(page_content_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    alternative_titles_tag = soup.find('td', class_='table-label')
    
    if alternative_titles_tag and 'Alternative' in alternative_titles_tag.text:
        # Find the sibling <td class="table-value">
        alternative_titles_value = alternative_titles_tag.find_next_sibling('td', class_='table-value')
        
        if alternative_titles_value:
            # Target the <h2> tag within the table-value
            h2_tag = alternative_titles_value.find('h2')
            if h2_tag:
                titles_text = h2_tag.text.strip()

                # Handle multiple delimiters robustly
                delimiters = [';', ',']
                for delimiter in delimiters:
                    if delimiter in titles_text:
                        alternative_titles = [title.strip() for title in titles_text.split(delimiter)]
                        return alternative_titles

                # Return the text as a single title if no delimiter is found
                return [titles_text]

    print("No alternative titles found or malformed HTML in page_content.txt.")
    return []

def merge_metadata(metadata1, metadata2, manga_dir):
    """Merge two metadata dictionaries into one."""
    merged_metadata = {}

    # Merge Genres lists from metadata1 and metadata2, handling None values
    genres1 = metadata1.get('Genres') or []  # Default to empty list if None
    genres2 = metadata2.get('Genres') or []  # Default to empty list if None
    merged_metadata['Genres'] = list(set(genres1 + genres2))

    # Allowed genres list
    allowed_genres = {
        "Action", "Adult", "Adventure", "Comedy", "Cooking", "Doujinshi", "Drama",
        "Ecchi", "Erotica", "Fantasy", "Gender Bender", "Harem", "Historical", 
        "Horror", "Isekai", "Josei", "Martial arts", "Mature", "Mecha", "Medical", 
        "Mystery", "Pornographic", "Psychological", "Romance", "School life", 
        "Sci fi", "Sci-fi", "Shoujo ai", "Shounen ai", "Slice of life", "Smut", "Sports", 
        "Supernatural", "Tragedy", "Yaoi", "Yuri"
    }

    # Filter and de-duplicate genres to include only allowed genres
    genres_from_metadata = merged_metadata['Genres']
    filtered_genres = [genre for genre in genres_from_metadata if genre in allowed_genres]
    merged_metadata['Genres'] = list(dict.fromkeys(filtered_genres))

    # Move any genre not in allowed genres to 'Tags'
    extra_tags = [genre for genre in genres_from_metadata if genre not in allowed_genres]
    tags = (metadata2.get('Tags') or []) + extra_tags  # Handle None in Tags with or []
    merged_metadata['Tags'] = list(dict.fromkeys(tags))

    # Authors list from metadata1
    authors1 = metadata1.get('Authors', [])

    # Writer from metadata2, always treated as a list for consistency
    writer2 = metadata2.get('Writer')
    authors2 = [writer2] if writer2 and writer2 != 'Unknown' else []

    def normalize_name(name):
        return re.sub(r'\s+|\(.*?\)', '', name)

    normalized_authors = {normalize_name(author): author for author in authors1}
    normalized_writer = {normalize_name(writer): writer for writer in authors2}

    merged_authors = []
    merged_authors.extend(normalized_authors.values())

    for norm_writer, original_writer in normalized_writer.items():
        if norm_writer not in normalized_authors:
            merged_authors.append(original_writer)
        else:
            existing_author = normalized_authors[norm_writer]
            if len(original_writer) > len(existing_author):
                merged_authors = [original_writer if author == existing_author else author for author in merged_authors]

    def remove_shorter_versions(authors):
        detailed_authors = {}
        for author in authors:
            normalized = normalize_name(author)
            if normalized not in detailed_authors or len(author) > len(detailed_authors[normalized]):
                detailed_authors[normalized] = author
        return list(detailed_authors.values())

    merged_authors = remove_shorter_versions(merged_authors)

    flattened_authors = []
    for item in merged_authors:
        if isinstance(item, list):
            flattened_authors.extend(str(sub_item) for sub_item in item)
        else:
            flattened_authors.append(str(item))

    merged_metadata['Authors'] = flattened_authors if flattened_authors else []

    artists1 = metadata1.get('Artists', [])
    artist2 = metadata2.get('Artist')
    artists2 = [artist2] if artist2 and artist2 != 'Unknown' else []

    normalized_artists1 = {normalize_name(artist): artist for artist in artists1}
    normalized_artists2 = {normalize_name(artist): artist for artist in artists2}

    merged_artists = []
    merged_artists.extend(normalized_artists1.values())

    for norm_artist, original_artist in normalized_artists2.items():
        if norm_artist not in normalized_artists1:
            merged_artists.append(original_artist)
        else:
            existing_artist = normalized_artists1[norm_artist]
            if len(original_artist) > len(existing_artist):
                merged_artists = [original_artist if artist == existing_artist else artist for artist in merged_artists]

    merged_artists = remove_shorter_versions(merged_artists)

    flattened_artists = []
    for item in merged_artists:
        if isinstance(item, list):
            flattened_artists.extend(str(sub_item) for sub_item in item)
        else:
            flattened_artists.append(str(item))

    merged_metadata['Artists'] = flattened_artists if flattened_artists else []

    merged_metadata['Publishers'] = list(set(metadata1.get('Publishers') or []))

    # Ensure metadata1 and metadata2 have a properly merged 'Summary'
    summary2 = metadata2.get('Summary', None)
    if summary2 is None:
        summary2 = metadata1.get('Summary', None)
    if isinstance(summary2, list):
        summary2 = "\n".join(summary2)
    elif not isinstance(summary2, str):
        summary2 = str(summary2)

    merged_metadata['Summary'] = "\n" + summary2

    merged_metadata['Year'] = metadata1.get('Year') or metadata2.get('Year') or []

    try:
        file_alternative_titles = extract_alternative_titles_from_file2(manga_dir)
        file_alternative_titles = file_alternative_titles or []
        merged_titles = (file_alternative_titles + 
                         metadata1.get('Alternative Titles', []) + 
                         metadata2.get('Alternative Titles', []))
        merged_titles = [str(title) if isinstance(title, list) else title for title in merged_titles]
        merged_metadata['Alternative Titles'] = list(set(merged_titles)) or []
    except Exception:
        merged_metadata['Alternative Titles'] = []

    merged_metadata['Alternative Titles'] = clean_alternative_titles(merged_metadata['Alternative Titles'])
    
    return merged_metadata

def extract_chapter_number_from_cbz(cbz_name):
    # Use regex to extract numbers from the CBZ file name (e.g., "One Piece Chapter 123.cbz")
    match = re.search(r'\bChapter (\d+)', cbz_name, re.IGNORECASE)
    return match.group(1) if match else "Unknown"

def count_images_in_cbz(cbz_file_path):
    try:
        with zipfile.ZipFile(cbz_file_path, 'r') as cbz_file:
            # List only image files inside the archive
            image_files = [file for file in cbz_file.namelist() if file.endswith(('.jpg', '.png', '.jpeg'))]
            return len(image_files)
    except Exception as e:
        print(f"Error counting images in {cbz_file_path}: {e}")
        return "Unknown"   

def clean_alternative_titles(alternative_titles):
    """
    Clean alternative titles by removing unwanted <br/> tags, trimming spaces,
    and removing duplicates while preserving order.
    """
    cleaned_titles = []
    for title in alternative_titles:
        # Remove <br/> tags and trim spaces
        clean_title = title.replace('<br/>', '').strip()
        # Add to cleaned list if not already present
        if clean_title and clean_title not in cleaned_titles:
            cleaned_titles.append(clean_title)

    return cleaned_titles

def create_comicinfo_xml(manga_dir, metadata, manga_title, chapter_url, cbz_name, image_tags=None):
    """Create a ComicInfo.xml file using the merged metadata and save it in the specified manga directory."""
    
    # Extract chapter number from the cbz file name
    chapter_number = extract_chapter_number_from_cbz(cbz_name)

    # Full path to the cbz file
    cbz_file_path = os.path.join(manga_dir, cbz_name)

    # Determine page count based on image_tags or fallback to counting images in the cbz
    if image_tags and len(image_tags):  
        page_count = len(image_tags) + 1  # Add 1 for the cover image
    else:
        page_count = count_images_in_cbz(cbz_file_path)



    # Create the root of the XML structure
    root = ET.Element("ComicInfo")
    ET.SubElement(root, "Series").text = f"{manga_title};"
    ET.SubElement(root, "LocalizedSeries").text = ", ".join(metadata.get('Alternative Titles', [])) if metadata.get('Alternative Titles') else ''
    ET.SubElement(root, "Number").text = chapter_number  # Ensure chapter_number is a string
    ET.SubElement(root, "Writer").text = ", ".join(metadata.get('Authors', [])) if metadata.get('Authors') else 'Unknown'
    ET.SubElement(root, "Artists").text = ", ".join(metadata.get('Artists', [])) if metadata.get('Artists') else 'Unknown'
    ET.SubElement(root, "Publisher").text = ", ".join(metadata.get('Publishers', [])) if metadata.get('Publishers') else 'Unknown'
    ET.SubElement(root, "Year").text = metadata.get('Year', []) if metadata.get('Year') else 'Unknown'
    ET.SubElement(root, "Genre").text = ", ".join(metadata.get('Genres', [])) if metadata.get('Genres') else 'Not Available'
    ET.SubElement(root, "Tags").text = ", ".join(metadata.get('Tags', [])) if metadata.get('Tags') else 'Not Available'
    ET.SubElement(root, "Summary").text = metadata.get('Summary', 'No summary available')
    ET.SubElement(root, "Web").text = chapter_url
    ET.SubElement(root, "LanguageISO").text = "en"
    ET.SubElement(root, "PageCount").text = str(page_count)
    ET.SubElement(root, "Format").text = "CBZ"

    # Save the ComicInfo.xml file
    xml_file_path = os.path.join(manga_dir, "ComicInfo.xml")
    tree = ET.ElementTree(root)
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
    print(f"ComicInfo.xml created at {xml_file_path}")

    return xml_file_path

def insert_comicinfo_into_cbz(manga_dir, cbz_name, xml_file_path):
    """Insert ComicInfo.xml into CBZ file."""
    cbz_file_path = os.path.join(manga_dir, cbz_name)

    if not os.path.exists(cbz_file_path):
        print(f"Error: {cbz_file_path} does not exist.")
        return False

    with zipfile.ZipFile(cbz_file_path, 'a') as cbz_file:
        cbz_file.write(xml_file_path, "ComicInfo.xml")
        print(f"ComicInfo.xml inserted into {cbz_name}")

    return True
















def get_binary_data_size(img_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }
    response = requests.get(img_url, headers=headers, stream=True, timeout=10)
    response.raise_for_status()  # Ensure the request was successful
    return len(response.content)  # Get the size in bytes
    
#Pay attention
total_download_size_multiple = 0
def download_manga(url, manga_title = None):
    global total_download_size_multiple
    global seven_zip_path
    global Check_idx
    """
    Main function to download manga chapters. If image download fails, switches to download_manga2 to handle the failed chapter.
    """
    headers['Referer'] = url
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the manga page. Error: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract manga title if not provided
    if not manga_title:
        title_tag = soup.find("h3", class_="item-title")
        manga_title = title_tag.text.strip()

    if manga_title.endswith("[Official]"):
        manga_title = manga_title[:-10]

    manga_title = sanitize_filename(manga_title)

    if manga_title.endswith("."):
        manga_title = manga_title[:-1]
    if manga_title.endswith("Manga"):
        manga_title = manga_title[:-6]

    print(f"Processing Manga: {manga_title}")
    
    # Create directory for the manga
    manga_dir = os.path.join(base_dir, manga_title)
    os.makedirs(manga_dir, exist_ok=True)

    # Save URL and HTML content if not already saved
    save_url(manga_dir, url)
    html_file_path = save_html_as_txt(manga_dir, html_content)
    print(f"HTML content saved to {html_file_path}")

    # Extract and download cover with alternative titles
    alt_site_url = "https://www.mangapanda.in/manga/return-of-the-sword-god-rank-civil-servant"
    extract_and_download_cover(manga_dir, html_file_path, url, manga_title, alt_site_url)


    # Find all chapter lists (not just the first one)
    chapter_list = soup.find("div", class_="main")

    ##fix later again
    chapter_links =  chapter_list.find_all("div", class_=["p-2 d-flex flex-column flex-md-row item is-new", "p-2 d-flex flex-column flex-md-row item"])



    print(f"Number of chapters found: {len(chapter_links)}")

    log_file_path = os.path.join(manga_dir, "download_log.txt")

    # Load existing download log to avoid re-downloading
    existing_log = {}
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            for line in log_file:
                chapter_url, chapter_title, last_updated = line.strip().split("\t")
                existing_log[chapter_url] = (chapter_title, last_updated)

    total_download_size = 0


    for chapter_item in chapter_links:

        chapter_link2 = chapter_item.find("a", class_="visited chapt")  # Find the right <a> tag
        if chapter_link2 and chapter_link2.has_attr("href"):  # Ensure href exists
            chapter_url = urljoin("https://battwo.com", chapter_link2["href"])

        chapter_title = chapter_link2.find("b").get_text(strip=True)
      
        # Skip chapters that are already logged as downloaded
        if chapter_url in existing_log:
            print(f"Chapter {chapter_title} already downloaded. Skipping...")
            continue

        print(f"Processing Chapter: {chapter_title} | URL: {chapter_url}")

        match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
        if match:
            chapter_number = match.group(1)
            if '.' in chapter_number:
                chapter_number = chapter_number.replace('.', 'p')
            else:
                chapter_number = f"{int(chapter_number):02}"
            # Generate the CBZ filename and save the file
            cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
            cbz_path = os.path.join(manga_dir, cbz_filename)
        else:
            # Check if the .cbz file for this chapter already exists and skip if so
            cbz_filename = f"{manga_title} {sanitize_filename(chapter_title)}.cbz"
            cbz_path = os.path.join(manga_dir, cbz_filename)

        if os.path.exists(cbz_path) and os.path.getsize(cbz_path) > 0:
            print(f"Chapter {chapter_title} already exists as {cbz_filename}. Skipping...")
            continue

        if chapter_url:
            driver = init_selenium()  # Use the correct driver (e.g., Chrome, Firefox)
            driver.get(chapter_url)

            # Wait for the viewer div to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "d-flex"))
            )

            # Get page source after it fully loads
            page_source = driver.page_source
            driver.quit()  # Close the browser

        chapter_soup = BeautifulSoup(page_source, "html.parser")

        # Find the chapter viewer
        viewer_element = chapter_soup.find("div", class_="d-flex flex-column align-items-center align-content-center")


        if viewer_element:              
            print(viewer_element)

            image_tags=[img.get("src") for img in viewer_element.find_all("img") if img.get("src")]

            if not image_tags:
                print("No valid images found.")
            else:
                print(f"Found {len(image_tags)} images.")

            Check_idx = len(image_tags)



            chapter_size = 0

            def get_size(img_url):
                """Retrieve binary data size of the image."""
                return get_binary_data_size(img_url)

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                sizes = list(executor.map(get_size, image_tags))

            chapter_size = sum(sizes)  # Aggregate results
        

            def download_image(img_data):
                """Download image and return (image index, name, content)."""
                i, img_url = img_data
                img_response = requests.get(img_url, stream=True)

                if img_response.status_code == 200:
                    return (i, f"{i+1:03}.jpg", img_response.content, get_binary_data_size(img_url))
                return (i, None, None, 0)  # Return 0 size for progress if download fails

            total_download_size += chapter_size

            print(f"Estimated size for {chapter_title}: {chapter_size / (1024 * 1024):.2f} MB")

                        # Start downloading images and create CBZ
            with BytesIO() as img_data:
                with ZipFile(img_data, 'a') as cbz_file:
                    progress = tqdm(total=chapter_size, desc=f"Downloading {chapter_title}", unit="B", unit_scale=True)

                    # Step 1: Download images concurrently
                    downloaded_images = []
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        futures = {executor.submit(download_image, (i, img_url)): i for i, img_url in enumerate(image_tags)}

                        for future in concurrent.futures.as_completed(futures):
                            i, img_name, img_content, size2 = future.result()
                            if img_name and img_content:
                                downloaded_images.append((i, img_name, img_content, size2))
                            progress.update(size2)

                    # Step 2: Write images sequentially to ZIP (thread-safe)
                    for i, img_name, img_content, _ in sorted(downloaded_images):
                        cbz_file.writestr(img_name, img_content)

                    progress.close()  # Ensure progress bar is closed


                    # Extract chapter number using regex
                    match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
                    if match:
                        chapter_number = match.group(1)
                        if '.' in chapter_number:
                            chapter_number = chapter_number.replace('.', 'p')
                        else:
                            chapter_number = f"{int(chapter_number):02}"

                        # Generate the CBZ filename and save the file
                        cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
                        cbz_path = os.path.join(manga_dir, cbz_filename)

                        with open(cbz_path, 'wb') as file:
                            file.write(img_data.getvalue())

                        # Add cover, metadata, and update logs
                        cbz_name = f"{manga_title} Chapter {chapter_number}.cbz"
                        add_cover_to_cbz(manga_title, chapter_title, cbz_name, manga_dir)

                                                   
                        # Download and extract metadata from MangaUpdates
                        html_file_path_mangaupdates = search_manga_and_download_html_mangaupdates(manga_title, manga_dir)
                        if html_file_path_mangaupdates is None:
                            print("Failed to download MangaUpdates metadata.")
                        metadata_mangaupdates = extract_metadata_from_txt_mangaupdates(manga_dir)

                        # Download and extract metadata from MangaDex
                        html_file_path_mangadex = search_manga_and_download_html(manga_title, manga_dir)
                        if html_file_path_mangadex is None:
                            print("Failed to download MangaDex metadata.")
                        metadata_mangadex = extract_metadata_from_txt(manga_dir)

                        # Merge metadata from both sources
                        merged_metadata = merge_metadata(metadata_mangaupdates, metadata_mangadex, manga_dir)

                        # Create ComicInfo.xml using the merged metadata
                        xml_file_path = create_comicinfo_xml(manga_dir, merged_metadata, manga_title, chapter_url, cbz_name, image_tags)

                        # Insert ComicInfo.xml into the CBZ file
                        insert_comicinfo_into_cbz(manga_dir, cbz_name, xml_file_path)

                        cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
                        cbz_path = os.path.join(manga_dir, cbz_filename)
                
                        # Step 1: Create a temporary directory for extraction
                        with tempfile.TemporaryDirectory() as temp_extract_dir:
                            # Step 2: Use 7z to extract the CBZ file
                            subprocess.run([seven_zip_path, 'x', cbz_path, f'-o{temp_extract_dir}'], check=True)

                            # Step 3: Delete the original CBZ file
                            os.remove(cbz_path)

                            # Step 4: Use 7z to re-compress files into a new CBZ file with the original structure
                            new_cbz_path = os.path.join(manga_dir, cbz_filename)
                            subprocess.run([seven_zip_path, 'a', '-tzip', new_cbz_path, f'{temp_extract_dir}/*'], check=True)

                        # Log the successful download
                        with open(log_file_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"{chapter_url}\t{chapter_title}\t{datetime.now().isoformat()}\n")
                    else:
                        print(f"Failed to extract chapter number from title '{chapter_title}'. Skipping...")


    # No return needed, continue to the next chapter
    # Final summary of download size

    total_download_size_multiple += total_download_size
    total_download_size_in_mb = total_download_size / (1024 * 1024)

    print(f"Total estimated download size: {total_download_size_in_mb:.2f} MB")
    update_combined_log()

total_update_size = 0



def update_manga(url, manga_title = None):
    global total_update_size
    global seven_zip_path
    global Check_idx
    """
    Main function to download manga chapters. If the first image download fails,
    it switches to update_manga2 to handle the specific chapter.
    """
    headers['Referer'] = url
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the manga page. Error: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract manga title if not provided
    if not manga_title:
        title_tag = soup.find("h3", class_="item-title")
        manga_title = title_tag.text.strip()

    if manga_title.endswith("[Official]"):
        manga_title = manga_title[:-10]

    manga_title = sanitize_filename(manga_title)

    if manga_title.endswith("."):
        manga_title = manga_title[:-1]
    if manga_title.endswith("Manga"):
        manga_title = manga_title[:-6]



    print(f"Updating Manga: {manga_title}")
        
    manga_dir = os.path.join(base_dir, manga_title)

    # Create directory if it doesn't exist
    os.makedirs(manga_dir, exist_ok=True)


    chapter_list = soup.find("div", class_="main")
    chapter_links =  chapter_list.find_all("div", class_=["p-2 d-flex flex-column flex-md-row item is-new", "p-2 d-flex flex-column flex-md-row item"])

    print("Chapter links found.")
        
                        
    print(f"Number of chapters found: {len(chapter_links)}")

    log_file_path = os.path.join(manga_dir, "download_log.txt")

    # Load existing download log to avoid re-downloading
    existing_log = {}
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            for line in log_file:
                parts = line.strip().split("\t")
                if len(parts) == 3:
                    chapter_url, chapter_title, last_updated = parts
                    existing_log[chapter_url] = (chapter_title, last_updated)
                else:
                    print(f"Skipping invalid log entry: {line.strip()}")

    total_download_size = 0

    for chapter_item in chapter_links:

        chapter_link2 = chapter_item.find("a", class_="visited chapt")  # Find the right <a> tag
        if chapter_link2 and chapter_link2.has_attr("href"):  # Ensure href exists
            chapter_url = urljoin("https://battwo.com", chapter_link2["href"])

        chapter_title = chapter_link2.find("b").get_text(strip=True)
      
        # Skip chapters that are already logged as downloaded
        if chapter_url in existing_log:
            print(f"Chapter {chapter_title} already downloaded. Skipping...")
            continue

        print(f"Processing Chapter: {chapter_title} | URL: {chapter_url}")

        match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
        if match:
            chapter_number = match.group(1)
            if '.' in chapter_number:
                chapter_number = chapter_number.replace('.', 'p')
            else:
                chapter_number = f"{int(chapter_number):02}"
            # Generate the CBZ filename and save the file
            cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
            cbz_path = os.path.join(manga_dir, cbz_filename)
        else:
            # Check if the .cbz file for this chapter already exists and skip if so
            cbz_filename = f"{manga_title} {sanitize_filename(chapter_title)}.cbz"
            cbz_path = os.path.join(manga_dir, cbz_filename)

        if os.path.exists(cbz_path) and os.path.getsize(cbz_path) > 0:
            print(f"Chapter {chapter_title} already exists as {cbz_filename}. Skipping...")
            continue

        if chapter_url:
            driver = init_selenium()  # Use the correct driver (e.g., Chrome, Firefox)
            driver.get(chapter_url)

            # Wait for the viewer div to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "d-flex"))
            )

            # Get page source after it fully loads
            page_source = driver.page_source
            driver.quit()  # Close the browser

        chapter_soup = BeautifulSoup(page_source, "html.parser")

        # Find the chapter viewer
        viewer_element = chapter_soup.find("div", class_="d-flex flex-column align-items-center align-content-center")


        if viewer_element:              
            print(viewer_element)

            image_tags=[img.get("src") for img in viewer_element.find_all("img") if img.get("src")]

            if not image_tags:
                print("No valid images found.")
            else:
                print(f"Found {len(image_tags)} images.")

            Check_idx = len(image_tags)

            chapter_size = 0

            def get_size(img_url):
                """Retrieve binary data size of the image."""
                return get_binary_data_size(img_url)

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                sizes = list(executor.map(get_size, image_tags))

            chapter_size = sum(sizes)  # Aggregate results
        

            def download_image(img_data):
                """Download image and return (image index, name, content)."""
                i, img_url = img_data
                img_response = requests.get(img_url, stream=True)

                if img_response.status_code == 200:
                    return (i, f"{i+1:03}.jpg", img_response.content, get_binary_data_size(img_url))
                return (i, None, None, 0)  # Return 0 size for progress if download fails

            total_download_size += chapter_size

            print(f"Estimated size for {chapter_title}: {chapter_size / (1024 * 1024):.2f} MB")

                        # Start downloading images and create CBZ
            with BytesIO() as img_data:
                with ZipFile(img_data, 'a') as cbz_file:
                    progress = tqdm(total=chapter_size, desc=f"Downloading {chapter_title}", unit="B", unit_scale=True)

                    # Step 1: Download images concurrently
                    downloaded_images = []
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        futures = {executor.submit(download_image, (i, img_url)): i for i, img_url in enumerate(image_tags)}

                        for future in concurrent.futures.as_completed(futures):
                            i, img_name, img_content, size2 = future.result()
                            if img_name and img_content:
                                downloaded_images.append((i, img_name, img_content, size2))
                            progress.update(size2)

                    # Step 2: Write images sequentially to ZIP (thread-safe)
                    for i, img_name, img_content, _ in sorted(downloaded_images):
                        cbz_file.writestr(img_name, img_content)

                    progress.close()  # Ensure progress bar is closed
              
                   # Extract chapter number using regex
                    match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
                    if match:
                        chapter_number = match.group(1)
                        if '.' in chapter_number:
                            chapter_number = chapter_number.replace('.', 'p')
                        else:
                            chapter_number = f"{int(chapter_number):02}"

                        # Generate the CBZ filename and save the file
                        cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
                        cbz_path = os.path.join(manga_dir, cbz_filename)

                        with open(cbz_path, 'wb') as file:
                            file.write(img_data.getvalue())

                        # Add cover, metadata, and update logs
                        cbz_name = f"{manga_title} Chapter {chapter_number}.cbz"
                        add_cover_to_cbz(manga_title, chapter_title, cbz_name, manga_dir)

                                                   
                        # Download and extract metadata from MangaUpdates
                        html_file_path_mangaupdates = search_manga_and_download_html_mangaupdates(manga_title, manga_dir)
                        if html_file_path_mangaupdates is None:
                            print("Failed to download MangaUpdates metadata.")
                        metadata_mangaupdates = extract_metadata_from_txt_mangaupdates(manga_dir)

                        # Download and extract metadata from MangaDex
                        html_file_path_mangadex = search_manga_and_download_html(manga_title, manga_dir)
                        if html_file_path_mangadex is None:
                            print("Failed to download MangaDex metadata.")
                        metadata_mangadex = extract_metadata_from_txt(manga_dir)

                        # Merge metadata from both sources
                        merged_metadata = merge_metadata(metadata_mangaupdates, metadata_mangadex, manga_dir)

                        # Create ComicInfo.xml using the merged metadata
                        xml_file_path = create_comicinfo_xml(manga_dir, merged_metadata, manga_title, chapter_url, cbz_name, image_tags)

                        # Insert ComicInfo.xml into the CBZ file
                        insert_comicinfo_into_cbz(manga_dir, cbz_name, xml_file_path)

                        cbz_filename = f"{manga_title} Chapter {chapter_number}.cbz"
                        cbz_path = os.path.join(manga_dir, cbz_filename)
                
                        # Step 1: Create a temporary directory for extraction
                        with tempfile.TemporaryDirectory() as temp_extract_dir:
                            # Step 2: Use 7z to extract the CBZ file
                            subprocess.run([seven_zip_path, 'x', cbz_path, f'-o{temp_extract_dir}'], check=True)

                            # Step 3: Delete the original CBZ file
                            os.remove(cbz_path)

                            # Step 4: Use 7z to re-compress files into a new CBZ file with the original structure
                            new_cbz_path = os.path.join(manga_dir, cbz_filename)
                            subprocess.run([seven_zip_path, 'a', '-tzip', new_cbz_path, f'{temp_extract_dir}/*'], check=True)

                        # Log the successful download
                        with open(log_file_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"{chapter_url}\t{chapter_title}\t{datetime.now().isoformat()}\n")
                    else:
                        print(f"Failed to extract chapter number from title '{chapter_title}'. Skipping...")


    # Update total download size
    total_update_size += total_download_size
    total_download_size_in_mb = total_update_size / (1024 * 1024)
    print(f"Total estimated download size: {total_download_size_in_mb:.2f} MB")
    update_combined_log()    

























def  txturldownlaod(txt_filepath):
    with open(txt_filepath, 'r', encoding='utf-8') as file:
        all_titles = [line.strip() for line in file if line.strip()]  
    total_titles = len(all_titles)
 
    try:
        # Open the text file for reading
        with open(txt_filepath, 'r', encoding='utf-8') as file:
            
            line_count = 0  # Initialize a line counter
            processed_count = 0  # Counter for processed lines

            for line in file:
                line_count += 1  # Increment line count 
                parts = line.strip().split("\t")  # Split by tab

                if len(parts) > 1 and parts[0].startswith("http"):  # Ensure there's a URL
                    url_title = unicodedata.normalize("NFKC", parts[0]).strip()  # Extract URL
                    manga_title = unicodedata.normalize("NFKC", parts[1]).strip() if len(parts) > 1 else None
                elif line.strip().startswith("http"):
                    url_title = line.strip()
                    manga_title = None
                
                if manga_title == None:
                    try:
                        response = requests.get(url_title, headers=headers)
                        response.raise_for_status()
                        html_content = response.text
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        title_tag = soup.find("h3", class_="item-title with-flag")
                        manga_title = title_tag.text.strip()
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to fetch the manga page. Error: {e}")
                        return

                log_file_path = os.path.join(base_dir, "Download_Progress_url.txt")

                # Normalize text to ensure consistent spacing
                manga_title = unicodedata.normalize("NFKC", manga_title).strip()
                url_title = unicodedata.normalize("NFKC", url_title).strip()

                
                # Fixed width for manga titles
                max_title_length = 50  

                # Determine longest URL dynamically (starting with current URL length)
                max_url_length = len(url_title)
    
                # Read existing log file to find longest URL length
                if os.path.exists(log_file_path):
                    with open(log_file_path, "r", encoding="utf-8") as log_file:
                        for line in log_file:
                            parts = line.split("\t")
                            if len(parts) > 1:  # Ensure URL exists in the line
                                max_url_length = max(max_url_length, len(parts[0].strip()))

                # Ensure a minimum width of 40 for URL column
                max_url_length = max(max_url_length, 0)

                # Apply consistent padding for alignment
                formatted_url = url_title.ljust(max_url_length)  # Dynamically sized URL
                formatted_title = manga_title[:max_title_length].ljust(max_title_length)  # Fixed-sized manga title

                # Create log entry
                log_entry = f"{formatted_url}\t{formatted_title}\n"

                # Append to log file
                with open(log_file_path, "a", encoding="utf-8") as log_file:
                    log_file.write(log_entry)

                if url_title:
                   processed_count += 1  # Increment processed lines count
                   print(f"Processing line {line_count}, Remaining Titles {total_titles - processed_count}:")
                   download_manga(url_title)

    except FileNotFoundError:
        print(f"Error: File not found at {txt_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

def list_manga_folders():
    manga_folders = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]
    print("Available Manga Titles:")
    for index, folder in enumerate(manga_folders, 1):
        print(f"{index}. {folder}")
    return manga_folders

def select_and_update_folders():
    manga_folders = list_manga_folders()
    print("Enter 'all' to update all folders.")
    selected_numbers = input("Enter the numbers of the manga folders to update (comma-separated): ").split(',')
    
    if 'all' in selected_numbers:
        selected_numbers = range(1, len(manga_folders) + 1)
    else:
        selected_numbers = [int(num.strip()) for num in selected_numbers]

    for num in selected_numbers:
        if 1 <= num <= len(manga_folders):
            manga_folder = manga_folders[num-1]
            manga_folder_path = os.path.join(base_dir, manga_folder)
            url_file_path = os.path.join(manga_folder_path, "url.txt")

            if os.path.exists(url_file_path):
                with open(url_file_path, "r", encoding="utf-8") as url_file:
                    manga_page_url = url_file.read().strip()
                print(f"Updating folder: {manga_folder}")
                update_manga(manga_page_url, manga_title=manga_folder)
            else:
                try:
                    manga_title=manga_folder
                    driver = init_selenium() 

                    try:
                        # Attempt to encode and decode to UTF-8, replacing unreadable characters
                        manga_title = manga_title.encode('utf-8', 'replace').decode('utf-8')
                    except UnicodeDecodeError:
                        # Fallback for non-UTF-8 characters
                        manga_title = manga_title.encode('ascii', 'replace').decode('ascii')

                    # Remove all non-ASCII characters (including special replacement characters like �)
                    manga_title = re.sub(r'[^\x00-\x7F]', '', manga_title)

                    # Remove unwanted special characters
                    cleaned_title = re.sub(r'[!$@#%&*\(\)\-+=\[\]{}|;:\'"<>\?/.,~]', '', manga_title, flags=re.UNICODE)

                    # Convert to lowercase and strip leading/trailing spaces
                    cleaned_title = cleaned_title.lower().strip()

                    # Replace spaces with `+` for URL compatibility
                    search_title = re.sub(r"\s+", "+", cleaned_title)

                    # URL encode while keeping `+` safe
                    search_title = urllib.parse.quote(search_title, safe='+')

                    # Construct the search URL
                    search_url = f"https://www.mangapanda.in/search?q={search_title}"


                    driver.get(search_url)

                    # Wait for the page to load
                    time.sleep(5)  # Adjust as needed for slow connections

                    # Locate search results
                    search_items = driver.find_elements(By.CSS_SELECTOR, '.cate-manga .media-body')

                    if not search_items:
                        print("No search results found.")
                    else:
                        # Extract and print manga links
                        for item in search_items:
                            link_tag = item.find_element(By.TAG_NAME, 'a')  # Find the first <a> tag
                            manga_link = link_tag.get_attribute('href')
                            print(manga_link)

                    # Quit the driver
                    driver.quit()
                        

                    print(f"URL saved successfully in {manga_folder_path}")
                    print(f"Updating manga '{manga_folder}' with URL: {manga_link}")

                    save_url(manga_folder_path, manga_link)
                    update_manga(manga_link, manga_title=manga_folder)

        
                    if not manga_link:
                        raise Exception("No valid manga link found in search results.")
        
       
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"URL file missing for folder '{manga_folder}'. Please enter the URL.")
                    new_url = input(f"Enter the URL for '{manga_folder}': ").strip()
        
                    if new_url.startswith("http://") or new_url.startswith("https://"):                          
   
                        save_url(manga_folder_path, new_url)
                        update_manga(new_url, manga_title=manga_folder)
            
                        print(f"URL saved successfully in {manga_folder_path}")
                        print(f"Updating manga '{manga_folder}' with URL: {new_url}")
                    else:
                        print("Invalid URL. Please try again.")

        else:
            print(f"Invalid selection: {num}. Skipping...")

def check_links(base_dir):

    manga_folders =  [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]
    invalid_manga = []

    print(f"Found {len(manga_folders)} manga folders.")

    for index, folder in enumerate(manga_folders, 1):
        if index == len(manga_folders) or index % 100 == 0:
            print(f"Checking {index} out of {len(manga_folders)}")
        else:
            print(f"Checking {index} out of {len(manga_folders)}",  end="\r")

        manga_folder_path = os.path.join(base_dir, folder)
        url_file = os.path.join(manga_folder_path, "url.txt")
    
        with open(url_file, "r", encoding="utf-8") as file:
           url = file.readline().strip()

        try:
            response = requests.get(url, timeout=5, headers=headers)
            if response.status_code >= 400 or response.status_code == 404 or "<title>404" in response.text or "Page Not Found" in response.text:
                print(f"Error occured while Checking for {index} {folder}")
                invalid_manga.append(f'{index} {folder}')
                continue  # No need to check further links for this manga
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Error while Checking {index} {folder}")
            print(f"Error occured for {url}: {e}")
            invalid_manga.append(f'{index} {folder}')
            continue


    return invalid_manga

def handle_user_input():
    # Ask for initial input: '1', 'many', or 'update'
    user_input = input("Type '1' to download one manga title, 'many' for multiple manga titles, 'txt' from via text file format,  'check' for check if links work  or 'update' to select folders for update: ").strip().lower()

    if user_input == 'update':
        # Handle the update case
        select_and_update_folders()
        total_update_size_in_mb = total_update_size / (1024 * 1024)
        print(f"Total estimated update size: {total_update_size_in_mb:.2f} MB")

    elif user_input == 'many':
        # Interactive mode for entering multiple URLs
        print("Enter as many URLs as you wish. Type 'done' when finished.")
        url_list = []
        url_count = 1

        while True:
            user_input = input(f"Count {url_count}. Enter URL or 'done' to finish: ").strip()

            if user_input.lower() == 'done':
                break
    
            url_count += 1

            # Handle potential entry of multiple URLs in a single line
            urls = [url.strip() for url in user_input.split(',') if url.strip()]
            url_list.extend(urls)

        if not url_list:
            print("No valid URLs were provided.")
            return

        total_titles = len(url_list)
        for i, url in enumerate(url_list, start=1):
            remaining = total_titles - i
            print(f"Downloading {i} out of {total_titles} manga titles. Remaining files: {remaining}")
            download_manga(url)

        total_download_size_multiple_in_mb = total_download_size_multiple / (1024 * 1024)

        # Check if the size exceeds 1024 MB (1 GB)
        if total_download_size_multiple_in_mb >= 1024:
            # Convert to GB and print
            total_download_size_multiple_in_gb = total_download_size_multiple_in_mb / 1024
            print(f"Total estimated Download size: {total_download_size_multiple_in_gb:.2f} GB")
        else:
            # Print in MB
            print(f"Total estimated Download size: {total_download_size_multiple_in_mb:.2f} MB")

    elif user_input == '1':
        # Single URL download
        url = input("Enter the URL for the manga title: ").strip()

        if url:
            download_manga(url)
        else:
            print("No valid URL provided.")




    elif user_input == 'txt':
        name = input("Do you wish to downlaod via 'url'?: ").strip().lower()
        if name=="url":
            txt_filepath = input("Enter the path to the text file which has only urls of mangas: ")
            txturldownlaod(txt_filepath)



    elif user_input == 'check':
        invalid_titles = check_links(base_dir)
        if invalid_titles:
            print("Manga folders with invalid links:")
            for title in invalid_titles:
                print(title)
        else:
             print("No manga folders found with invalid links:")

    else:
        print("Invalid input. Please enter '1', 'many', or 'update' 'Check' or 'txt'")
        return

    if user_input in ['update', 'many', '1', 'txt']:
    # Final messages after download or update
        print("All selected chapters downloaded and saved in their respective directories.")
        print(f"Combined log file updated and saved at {os.path.join(base_dir, 'combined_download_log.txt')}")

    # Wait for user input to exit
    input("Press Enter to exit...")

handle_user_input()
