import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Initialize the Chrome driver with options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--log-level=3')
driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)

url = "https://www.amazon.com.br/gp/bestsellers/books/7873971011/ref=zg_bs_pg_1_books?ie=UTF8&pg=1"
data = []
link_list = []

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
            # Set the field "num. of reviews" as an empty string if there are no reviews
            len_without_reviews = 5
            reviews_position = 3
            if len(lines) == len_without_reviews:
                lines.insert(reviews_position, '')
            
            # Find the a-link-normal element inside the div
            link_element = element.find_element(By.CLASS_NAME, 'a-link-normal')
            
            # Get the href attribute value
            href = link_element.get_attribute('href')
            
            # Remove everything after "ref=" in href
            link = href.split('ref=')[0]
            
            # 
            data.append(lines)
            
            # Write the details to the informations CSV file
            link_list.append(href)
        
        # Check if there is a "Próxima página" button
        try:
            next_page_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Próxima página")
            if next_page_button.is_enabled():
                next_page_button.click()
            else:
                break  # Exit the loop if the "Próxima página" button is not available
        except NoSuchElementException: # NoSuchElementException is lauched if the element is not foud i.e. if  there's no next page
            break

# Create Pandas DataFrames from the collected data
df = pd.DataFrame(data)
df.columns = ['position', 'name', 'publisher/author', 'num. of reviews', 'cover type', 'price']
href_df = pd.DataFrame(link_list, columns=['url'])

# Write the DataFrames to CSV files
df.to_csv('mais-vendidos.csv', index=False, encoding='utf-8')
href_df.to_csv('link-livros.csv', index=False, encoding='utf-8')

driver.quit()
