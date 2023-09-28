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
    with open('seenTitles.json', 'r') as f:
        seenTitles = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    seenTitles = []

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

        word_count = len(title_text.split())

        if word_count > 10:

            link = row.find_element(By.CSS_SELECTOR, 'a[data-polaris-unstyled="true"][data-primary-link="true"]')
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-polaris-unstyled="true"][data-primary-link="true"]')))
            link.click()

            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'product-description_ifr')))

            driver.execute_script('document.body.innerHTML = "";')

            driver.switch_to.default_content()

            title_input_css = 'input[name="title"]'
            title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_input_css)))

            if title_input.get_attribute('value') not in seenTitles:
                response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Rename the following product name to be less confusing and more straight forward, only respond with the new product name and nothing else, aim for 4-8 words: " + title_input.get_attribute('value')},
                    ]
                )

                newProductNameString = response['choices'][0]['message']['content']
                seenTitles.append(newProductNameString)

                with open('seenTitles.json', 'w') as f:
                    json.dump(seenTitles, f)

                driver.execute_script("arguments[0].select();", title_input)

                title_input.send_keys(Keys.BACK_SPACE)

                title_input.send_keys(newProductNameString)


            try:
                save_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Polaris-Button_r99lw.Polaris-Button--sizeLarge_61dxo.Polaris-Button--primary_7k9zs.Polaris-Button--success_z03ht')))
                save_button.click()
            except TimeoutException:
                pass

            back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.Polaris-Button_r99lw.Polaris-Button--iconOnly_viazp')))
            back_button.click()

while True:

    time.sleep(5)
    process_table()

    try:
        next_button = wait.until(EC.presence_of_element_located((By.ID, 'nextURL')))
        next_button.click()
    except TimeoutException:

        break
