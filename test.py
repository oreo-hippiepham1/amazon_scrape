import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re



driver = webdriver.Chrome()
driver.get("http://www.amazon.com/")
#driver.maximize_window()
input("Press ENTER after filling CAPTCHA")

def search_item(item_name):
    # Search bar
    search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    search_box.clear()
    search_box.send_keys(item_name)
    # Search button CLICKED
    driver.find_element(By.ID, 'nav-search-submit-button').click()

def scrape_items():
    item_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
    print(f'----- TOTAL: {len(item_elements)}-----')
    
    count = 0

    items_dict = {}

    for item_element in item_elements:
        try:
            count += 1
            link_element = item_element.find_element(By.CSS_SELECTOR, '.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
            link = link_element.get_attribute('href')

            name_element = item_element.find_element(By.CSS_SELECTOR, 'span.a-size-base-plus')

            # Retry mechanism to wait for price element to be visible
            price_element = None
            retries = 3
            while retries > 0:
                try:
                    price_element = WebDriverWait(item_element, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.a-price'))
                    )
                    break
                except selenium.common.exceptions.TimeoutException:
                    print("Retrying to locate price element...")
                    retries -= 1

            if price_element is None:
                print("Skipping item due to timeout")
                continue

            price = price_element.text

            print("Name:", name_element.text)
            print("Price:", price)
            print("Link:", link)

            # extract product ASIN code
            try:
                product_code = re.search(r"/dp/([A-Z0-9]+)", link).group(1)
                print(product_code)
                items_dict[name_element.text] = product_code
            except AttributeError:
                try:
                    product_code = item_element.find_element(By.XPATH, '//*[@id="detailBullets_feature_div"]/ul/li[5]/span/span[2]')
                except NoSuchElementException:
                    pass
            
            print(f'---COUNT: {count}---')
            print("------------------------")

        except NoSuchElementException:
            print("Skipping item due to missing element")
            continue

    return items_dict
        

search_item('foundation')
di = scrape_items()

driver.quit()

print('\n\n\n___________________')

# for n, c in di.items():
#     print(f'{n} - {c}')

print('CLOSING')