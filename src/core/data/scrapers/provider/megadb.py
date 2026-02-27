import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


options = uc.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = uc.Chrome(options=options, version_main=145)
driver.get("https://megadb.net/qp0yi1v1p6nl")

WebDriverWait(driver, 20).until(
     EC.frame_to_be_available_and_switch_to_it(
        (By.XPATH, "//iframe[@title='reCAPTCHA']")
    )
)

checkboxui = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
)

checkboxelement = driver.find_element(By.ID, "recaptcha-anchor")

while checkboxelement.get_attribute("aria-checked") == "false":
    time.sleep(1)



print("captcha is solved")

driver.quit()
