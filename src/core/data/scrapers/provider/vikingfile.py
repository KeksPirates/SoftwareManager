import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

import requests

def scrape_vikingfile(url):

    options = uc.ChromeOptions()

    driver = uc.Chrome(options=options, version_main=145)
    driver.get(url)

    while driver.find_element(By.ID, "download-link").get_attribute("href") is None:
        continue

    link = driver.find_element(By.ID, "download-link").get_attribute("href")

    driver.quit()

    return link

if __name__ == "__main__":
    example = "https://vik1ngfile.site/f/4txMf0RghN"
    downloadlink = scrape_vikingfile(example)
    print(downloadlink)