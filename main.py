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
                link_element = item_element.find_element(By.CSS_SELECTOR, '.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
                link = link_element.get_attribute('href')
                product_links.append(link)
                count += 1
            except NoSuchElementException:
                print("Skipping item due to missing element")
                continue
        else:
            break

    return product_links


def scrape_metadata(selector):
    try:
        t = driver.find_element(By.CSS_SELECTOR, selector)
        return t.text
    except NoSuchElementException:
        return "None"


# Function to scrape product data and add it to the DataFrame
def scrape_product_data(main_type, link, df):
    driver.get(link)
    #print(f'LINK: {link}')

    # NAME
    name = scrape_metadata('#productTitle')

    # IMG
    try:
        img_element = driver.find_element(By.CSS_SELECTOR, '#landingImage')
        img = img_element.get_attribute('src')
    except NoSuchElementException:
        img = "None"

    # PRICE
    price = scrape_metadata('#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center > span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay > span:nth-child(2)')

    # ITEM CODE (KEY)
    try:
        item_code = re.search(r"/dp/([A-Z0-9]+)", link).group(1)
    except AttributeError:
        item_code = scrape_metadata('#detailBullets_feature_div > ul > li:nth-child(6) > span > span:nth-child(2)')

    # BRAND 
    brand = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-brand > td.a-span9')

    # ITEM FORM
    item_form = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-item_form > td.a-span9')

    # COLOR
    color = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-color > td.a-span9')

    # SKIN TYPE
    skin_type = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-skin_type > td.a-span9')

    # FINISH TYPE
    finish_type = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-finish_type > td.a-span9')

    # PRODUCT BENEFITS
    product_benefits = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-product_benefit > td.a-span9')

    # COVERAGE
    coverage = scrape_metadata('#productOverview_feature_div > div > table > tbody > tr.a-spacing-small.po-coverage > td.a-span9')

    # ABOUT THIS ITEM
    about_item = scrape_metadata('#feature-bullets > ul')

    # Append the scraped data as a new row to the DataFrame
    df.loc[len(df)] = [main_type ,link, name, img, price, item_code, brand, item_form, color, skin_type, finish_type, product_benefits, coverage, about_item]
    


data = pd.DataFrame(columns=['main_type','Link', 'Name', 'Image', 'Price', 'Item Code', 'Brand', 'Item Form', 'Color', 'Skin Type', 'Finish Type', 'Product Benefits', 'Coverage', 'About This Item'])

item_store = ['foundation', 'lipstick', 'eyeliner', 'blush', 'primer', 'mascara', 'bronzer']
item_store = [ "Cuticle Oil",
    "Gel Eyeliner",
    "Liquid Lipstick",
    "Matte Lipstick",
    "Lip Cream",
    "Lip Tint",
    "Lip Oil",
    "Shimmer Eyeliner",]

# for main_type in item_store:
#     search_item(main_type)
#     links = get_links(limit=1)
#     for link in links:
#         scrape_product_data(main_type, link, data)
for main_type in item_store:
    search_item(main_type)
    links = get_links(limit=60)
    for l in links:
        scrape_product_data(main_type, l, data)

print(data)
data.to_csv('up_8_2nd.csv')
driver.quit()

print('DONE')