import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Caminho para o ChromeDriver baixado
chromedriver_path = r'C:\Users\lucas\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

# Inicializa as opções do Chrome
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--log-level=3')

# Inicializa o driver do Chrome
driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

url = "https://www.amazon.com.br/gp/bestsellers/books/ref=zg_bs_pg_1_books?ie=UTF8&pg=1"
data = []
link_list = []

while True:
    driver.get(url)
    
    # Verifica se há mensagem de "Request was throttled"
    if "Request was throttled. Please wait a moment and refresh the page" in driver.page_source:
        print("Throttling detected. Refreshing the page...")
        time.sleep(2)  # Espera antes de atualizar a página
        continue  # Recarrega a página
    else:
        break  # Sai do loop se a mensagem não estiver presente

# Cria e abre um arquivo CSV para escrever as informações
with open('mais-vendidos.csv', 'w', newline='', encoding='utf-8') as csvfile:
    details_csv_writer = csv.writer(csvfile)
    
# Cria e abre um arquivo CSV para escrever os valores de href
    while True:
        # Faz scroll até o final da página usando JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Espera 2 segundos após o scroll
        
        # Encontra todos os elementos com ids correspondendo ao padrão p13n-asin-index-*
        elements = driver.find_elements(By.CSS_SELECTOR, '[id^="p13n-asin-index-"]')
        
        # Itera sobre os elementos
        for element in elements:
            # Divide o texto do elemento em linhas
            lines = element.text.split('\n')
            # Define o campo "num. of reviews" como uma string vazia se não houver avaliações
            len_without_reviews = 5
            reviews_position = 3
            if len(lines) == len_without_reviews:
                lines.insert(reviews_position, '')
            
            # Encontra o elemento a-link-normal dentro do div
            link_element = element.find_element(By.CLASS_NAME, 'a-link-normal')
            
            # Obtém o valor do atributo href
            href = link_element.get_attribute('href')
            
            # Remove tudo após "ref=" em href
            link = href.split('ref=')[0]
            
            # Adiciona os dados à lista data
            data.append(lines)
            
            # Adiciona o link à lista link_list
            link_list.append(link)
        
        # Verifica se há um botão "Próxima página"
        try:
            next_page_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Próxima página")
            if next_page_button.is_enabled():
                next_page_button.click()
            else:
                break  # Sai do loop se o botão "Próxima página" não estiver disponível
        except NoSuchElementException:
            break  # Sai do loop se não houver próxima página

# Cria DataFrames do Pandas com os dados coletados
df = pd.DataFrame(data)
df.columns = ['position', 'name', 'publisher/author', 'num. of reviews', 'cover type', 'price']
href_df = pd.DataFrame(link_list, columns=['url'])

# Escreve os DataFrames em arquivos CSV
df.to_csv('mais-vendidos.csv', index=False, encoding='utf-8')
href_df.to_csv('link-livros.csv', index=False, encoding='utf-8')

# Fecha o navegador
driver.quit()
