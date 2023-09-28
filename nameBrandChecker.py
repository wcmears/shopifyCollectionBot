from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import openai
import json

openai.api_key = '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'

try:
    with open('seenBrands.json', 'r') as f:
        seenTitles = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    seenTitles = []

try:
    with open('Brand.json', 'r') as f:
        brands = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    brands = []

# Define chrome options
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir=/Users/willmears/Library/Application Support/Google/Chrome/User Data")
chrome_options.add_argument("/Users/willmears/Library/Application Support/Google/Chrome/Default")
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
chrome_options.add_argument("/Users/willmears/Library/Application Support/Google/Chrome/Default")
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
chrome_options.add_experimental_option("useAutomationExtension", False) 

service = Service('/Users/willmears/Desktop/newdriver/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

driver.get('https://admin.shopify.com/store/f472ca/products?selectedView=all')

wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continue with unsupported browser')]")))
button.click()


def process_table():

    num_rows = len(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Polaris-IndexTable__TableRow_1a85o'))))

    for i in range(num_rows):

        rows = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Polaris-IndexTable__TableRow_1a85o')))
        row = rows[i]

        title_element = row.find_element("xpath", './/span[@class="Polaris-Text--root_yj4ah Polaris-Text--bodyMd_jaf4s"]')
        title_text = title_element.text

        if title_text not in seenTitles:   

          response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                  {"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": "Is there a famous brand that you recognize in this title, like Disney, Lenovo, etc.: " + title_text + "? If not, just respond simply by saying \" No \", if yes respond by saying \" Yes \" and the brand name."},
              ]
          )

          brands.append(response['choices'][0]['message']['content'])

          with open('Brand.json', 'w') as f:
              json.dump(brands, f)       

          seenTitles.append(title_text)

          with open('seenBrands.json', 'w') as f:
              json.dump(seenTitles, f)           

while True:

    time.sleep(5)
    process_table()

    try:
        next_button = wait.until(EC.presence_of_element_located((By.ID, 'nextURL')))
        next_button.click()
    except TimeoutException:

        break
