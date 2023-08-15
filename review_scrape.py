import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd


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


def get_links(limit=1):
    item_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
    print(f'----- TOTAL: {len(item_elements)}-----')

    product_links = []

    count = 0
    for item_element in item_elements:
        if count <= limit:
            try:
                link_element = item_element.find_element(By.CSS_SELECTOR,
                                                         '.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
                link = link_element.get_attribute('href')
                product_links.append(link)
                count += 1
            except NoSuchElementException:
                print("Skipping item due to missing element")
                continue
        else:
            break

    return product_links


def scrape_reviews(main_type, link, df):
    driver.get(link)

    name = ""
    try:
        t = driver.find_element(By.CSS_SELECTOR, '#productTitle')
        name = t.text
    except NoSuchElementException:
        name = "None"

    review_elements = driver.find_elements(By.CSS_SELECTOR, '[id^="customer_review-"] > div:nth-child(5)')
    reviews = []

    for review_element in review_elements:
        review_text = review_element.text
        #reviews.append(review_text)
        df = pd.concat([df, pd.DataFrame({'main_type': [main_type],'name': [name], 'link': [link], 'reviews': [review_text]})])

    #df.loc[len(df)] = [main_type, name, link, reviews]
    return df



df = pd.DataFrame(columns=['main_type', 'name', 'link', 'reviews'])

item_store = [ "Waterproof Mascara",
    "Glitter Eyeshadow",
    "Cream Blush",
    "Stick Foundation",
    "Setting Powder Brush",
    "Makeup Setting Mist"]

for i in item_store:
    search_item(i)
    links = get_links(limit=40)  # Scrape reviews for 2 products

    for link in links:
        df = scrape_reviews(i, link, df)


print(df)
df.to_csv('review_test_final.csv')
