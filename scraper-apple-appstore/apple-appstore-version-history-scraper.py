import os
import pandas as pd
from tqdm import tqdm
from time import sleep
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
options.add_argument("--no-sandbox"); # bypass OS security model

INDEX_RANGE = [6000, 10000]
PATH = os.path.join(os.getcwd(), "data")
DATASET = pd.read_csv(os.path.join(PATH, "apps_of_interest.csv"))[INDEX_RANGE[0]:INDEX_RANGE[1]]

def scrape_version_history():
    links = DATASET["appstore_link"].tolist()
    num_major_updates = []
    num_minor_updates = []

    for i in tqdm(range(len(DATASET))):
        
        # access Apple App Store link
        driver = webdriver.Chrome("C:/bin/chromedriver.exe", options = options)
        url = links[i]

        try:
            driver.get(url)
        except TimeoutException as ex:
            driver.close()
            num_major_updates.append(-1)
            num_minor_updates.append(-1)
            continue
        except WebDriverException as ex:
            driver.close()
            num_major_updates.append(-4)
            num_minor_updates.append(-4)

        # click on Version History button
        try:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/main/div[2]/section[4]/div[1]/div/button")))
            button = driver.find_element_by_xpath("/html/body/div[4]/div/main/div[2]/section[4]/div[1]/div/button")
            button.click()
        except TimeoutException as ex:
            driver.close()
            num_major_updates.append(-2)
            num_minor_updates.append(-2)
            continue
        
        # get versions into an array
        try:
            modal = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]")))
            version_items = modal.find_elements_by_tag_name("h4")
        except TimeoutException as ex:
            print("TimeoutException thrown at locating modal and its elements.")
            driver.close()
            num_major_updates.append(-3)
            num_minor_updates.append(-3)
            continue
            
        versions = list(map(lambda v: v.text, version_items))
        driver.close()
        
        # count and save the number of major and minor updates
        major = int(len(set([v[0] for v in versions])) - 1)
        minor = int(len(versions) - 1 - major)
        num_major_updates.append(major)
        num_minor_updates.append(minor)

    return num_major_updates, num_minor_updates

def write_to_csv():
    #now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = "".join([str(INDEX_RANGE[0]), "_", str(INDEX_RANGE[1]-1), "_appdata.csv"])
    DATASET.to_csv(fname, index = False)

if __name__ == '__main__':
    num_major_updates, num_minor_updates = scrape_version_history()
    DATASET["num_major_updates"] = num_major_updates
    DATASET["num_minor_updates"] = num_minor_updates
    write_to_csv()