import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re

def remove_ref_from_link(link):
    return link.split('ref=')[0]  # Split the link by 'ref=' and keep only the part before it

def is_link_in_file(link, file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row and row[0] == link:
                return True
    return False

# Handles missing possible missing data in each row so the final csv remains estructured
def handle_missing_book_data(row: list):
    reviews_exist = any('Avaliações' in field for field in row)
    publisher_exist =  any('Editora' in field for field in row)
    if not publisher_exist:
        publisher_index = 2
        row.insert(publisher_index, '')
    if not reviews_exist:
        review_score_index =  7
        num_of_reviews_index = 8
        row.insert(review_score_index,'')
        row.insert(num_of_reviews_index,'')

link_file = "link-livros.csv"
output_file = "livros.csv"

# Configure Chrome options for headless mode and logging level
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--log-level=3')
driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)

# Define regular expressions for filtering lines
regex_patterns = [
    r'.*páginas$',
    r'^Editora :',
    r'^ISBN-10 :',
    r'^ISBN-13 :',
    r'^Ranking dos mais vendidos:',
    r'^Avaliações dos clientes:',
    r'.* avaliações de clientes'
]

with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)   
    headers = ['url',
                'title',
                'description',
                'publisher',
                'cover type/page num.',
                'ISBN-10',
                'ISBN-13',
                'best bellers rank',
                'review score',
                'num. of reviews',
                'frequently bought togheter']
    csv_writer.writerow(headers)

with open(link_file, 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)

    for index, row in enumerate(csv_reader):
        url = row[0]
        while True:
            driver.get(url)
            # Check if the "Request was throttled" message is present
            if "Request was throttled. Please wait a moment and refresh the page" in driver.page_source:
                print("Throttling detected. Refreshing the page...")
                time.sleep(2)  # Wait for a moment before refreshing
                continue  # Reload the page
            else:
                break  # Exit the loop if the message is not present

        time.sleep(1)
        book = False

        if "Clientes que compraram este item também compraram" in driver.page_source:
            try:
                if ("Livros" in driver.find_element(By.ID, "wayfinding-breadcrumbs_feature_div").text) or ("Capa" in driver.find_element(By.ID, "tmmSwatches").text):
                    book = True
            except:
                book = False
                pass

            if book:
                # Click the "Leia mais" element if it exists
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    leia_mais_element = driver.find_element(By.PARTIAL_LINK_TEXT, "Leia mais")
                    leia_mais_element.click()
                except:
                    pass
                
                # Retry finding the elements in case of failure
                fail = 1
                while fail:
                    try:
                        book_title = driver.find_element(By.ID, "productTitle").text
                        book_description = driver.find_element(By.ID, "bookDescription_feature_div")
                        expander_content = book_description.find_element(By.CLASS_NAME, "a-expander-content")
                        book_description_content = expander_content.text.replace('\n', '').replace('"', '')
                        faceout_box = driver.find_element(By.CLASS_NAME, "p13n-sc-shoveler")
                        link_elements = faceout_box.find_elements(By.CLASS_NAME, "p13n-sc-uncoverable-faceout")
                        fail = 0
                        print(index+2, " - ", book_title)
                        break  # Elements found successfully, exit retry loop
                    except Exception as e:
                        print(f"Failed to find elements: {str(e)}")
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)  # Wait for a moment before retrying

                link_list = []
                link_titles = []
                for i in range(0, len(link_elements)):
                    link = link_elements[i].find_element(By.TAG_NAME, "a").get_attribute('href')
                    cleaned_link = remove_ref_from_link(link)  # Remove everything after "ref="
                    link_titles.append(link_elements[i].find_element(By.CLASS_NAME, "p13n-sc-truncate-desktop-type2").text)
                    
                    if not is_link_in_file(cleaned_link, link_file):  # Check if the link is not already in the file
                        link_list.append(cleaned_link)
                        # Append the cleaned link to the end of the link_file
                        with open(link_file, 'a', newline='', encoding='utf-8') as link_file_append:
                            link_file_writer = csv.writer(link_file_append)
                            link_file_writer.writerow([cleaned_link])
                    
                # Find the element with the ID "detailBullets_feature_div"
                detail_bullets = driver.find_element(By.ID, "detailBullets_feature_div")
                
                # Extract the content of the element and split it into lines
                detail_bullets_content = detail_bullets.text.split('\n')
                
                # Filter lines using regular expressions
                filtered_lines = [line for line in detail_bullets_content if any(re.match(pattern, line) for pattern in regex_patterns)]
                
                # Write the filtered content to the output CSV file
                with open(output_file, 'a', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    row = [url, book_title, book_description_content, *filtered_lines, link_titles]
                    handle_missing_book_data(row)
                    csv_writer.writerow(row)
            else:
                print("Not a book.")
        else:
            print("Text 'Frequentemente comprados juntos' not found on the page.")

driver.quit()