import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--log-level=3')

driver = webdriver.Chrome(service=Service('chromedriver.exe'))
url = "https://www.amazon.com.br/gp/bestsellers/books/7873971011/ref=zg_bs_pg_1_books?ie=UTF8&pg=1"

while True:
    driver.get(url)
    
    # Check if the "Request was throttled" message is present
    if "Request was throttled. Please wait a moment and refresh the page" in driver.page_source:
        print("Throttling detected. Refreshing the page...")
        time.sleep(2)  # Wait for a moment before refreshing
        continue  # Reload the page
    else:
        break  # Exit the loop if the message is not present

# Create and open a CSV file for writing information
with open('mais-vendidos.csv', 'w', newline='', encoding='utf-8') as csvfile:
    details_csv_writer = csv.writer(csvfile)
    
    # Create and open a CSV file for writing href values
    with open('link-livros.csv', 'w', newline='', encoding='utf-8') as href_csvfile:
        href_csv_writer = csv.writer(href_csvfile)
    
        while True:
            # Scroll to the bottom of the page using JavaScript
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Sleep for 2 seconds after scrolling
            
            # Find all elements with ids matching the pattern p13n-asin-index-*
            elements = driver.find_elements(By.CSS_SELECTOR, '[id^="p13n-asin-index-"]')
            
            # Loop through the elements
            for element in elements:
                # Split element.text into lines
                lines = element.text.split('\n')
                
                # Find the a-link-normal element inside the div
                link_element = element.find_element(By.CLASS_NAME, 'a-link-normal')
                
                # Get the href attribute value
                href = link_element.get_attribute('href')
                
                # Remove everything after "ref=" in href
                href = href.split('ref=')[0]
                
                # Write the href to the href CSV file
                href_csv_writer.writerow([href])
                
                # Write the details to the informations CSV file
                details_csv_writer.writerow(lines)
            
            # Check if there is a "Próxima página" button
            next_page_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Próxima página")
            
            if next_page_button.is_enabled():
                next_page_button.click()
            else:
                break  # Exit the loop if the "Próxima página" button is not available

driver.quit()
