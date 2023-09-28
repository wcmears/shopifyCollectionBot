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
    with open('seenTitlesCollection.json', 'r') as f:
        seenTitles = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    seenTitles = []

category_names = [
    "Auto Parts and Accessories",
    "Baby",
    "Bath",
    "Beauty and Makeup",
    "Electronics",
    "Garden",
    "Home Improvement",
    "Household Appliances",
    "Jewelry and Accessories",
    "Kitchen",
    "Lights",
    "Luggage and Bags",
    "Men's Clothing",
    "Pets",
    "Pool",
    "School and Office Supplies",
    "Shoes",
    "Sports and Fitness",
    "Tools",
    "Toys",
    "Watches",
    "Women's Clothing"
]

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

          link = row.find_element(By.CSS_SELECTOR, 'a[data-polaris-unstyled="true"][data-primary-link="true"]')
          WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-polaris-unstyled="true"][data-primary-link="true"]')))
          link.click()

          response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                  {"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": "If you HAD to choose one of the following, which would you categorize \""  + title_text + "\" into? : 1. Auto Parts and Accessories, 2. Baby, 3. Bath, 4. Beauty and Makeup, 5. Electronics, 6. Garden, 7. Home Improvement, 8. Household Appliances, 9. Jewelry and Accessories, 10. Kitchen, 11. Lights, 12. Luggage and Bags, 13. Men's Clothing, 14. Pets, 15. Pool, 16. School and Office Supplies, 17. Shoes, 18. Sports and Fitness, 19. Tools, 20. Toys, 21. Watches, 22. Women's Clothing. Respond with your selection exactly as it appears in the list that I just gave you."},
              ]
          )

          category = response['choices'][0]['message']['content']

          check = False
          for categoryCheck in category_names:
              if categoryCheck in category or category in categoryCheck:
                  cat = categoryCheck
                  check = True
                  break
          if check == False:
            print("GPT SUCKS")
          
          input_box = wait.until(EC.element_to_be_clickable((By.ID, 'CollectionsAutocompleteField1')))
          input_box.click()
          time.sleep(1)

          collection_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//label//span[text()="' + cat + '"]/../../..//input[@type="checkbox"]')))
          driver.execute_script("arguments[0].click();", collection_checkbox)
          time.sleep(1)

          try:
              save_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Polaris-Button_r99lw.Polaris-Button--sizeLarge_61dxo.Polaris-Button--primary_7k9zs.Polaris-Button--success_z03ht')))
              save_button.click()
              time.sleep(9)
          except TimeoutException:
              pass

          back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.Polaris-Button_r99lw.Polaris-Button--iconOnly_viazp')))
          back_button.click()

          seenTitles.append(title_text)

          with open('seenTitlesCollection.json', 'w') as f:
              json.dump(seenTitles, f)           

while True:

    time.sleep(5)
    process_table()

    try:
        next_button = wait.until(EC.presence_of_element_located((By.ID, 'nextURL')))
        next_button.click()
    except TimeoutException:

        break
