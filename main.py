from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
import os

####################### NOTE FOR PROJECT ##################################

#Google does not allow you to login via selenium webdriver. The code scrapes and submits all the data to the google
#form automatically, however I have to login manually to my personal account to view the spreadsheet and responses.

###########################################################################

chrome_driver_path = os.environ.get("chrome_driver_path")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

service = ChromeService(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

ACCEPT = os.environ.get("ACCEPT")
USER_AGENT = os.environ.get("USER_AGENT")
GOOGLE_FORM_LINK = os.environ.get("GOOGLE_FORM_LINK")
ZILLOW_LINK = os.environ.get("ZILLOW_LINK")

headers = {
    "User-Agent": USER_AGENT,
    "ACCEPT": ACCEPT,
}

response = requests.get(ZILLOW_LINK, headers=headers)
html = response.text
soup = BeautifulSoup(html, "html.parser")

data = json.loads(
    soup.select_one("script[data-zrr-shared-data-key]").contents[0].strip("!<>-")
)

house_links = [
    result["detailUrl"]
    for result in data["cat1"]["searchResults"]["listResults"]
]

house_links = [
    link.replace(link, "https://www.zillow.com" + link)
    if not link.startswith("http")
    else link
    for link in house_links
]

house_address = [
    result["address"]
    for result in data["cat1"]["searchResults"]["listResults"]
]

house_rent = [
    int(result["units"][0]["price"].strip("$").replace(",", "").strip("+"))
    if "units" in result
    else result["unformattedPrice"]
    for result in data["cat1"]["searchResults"]["listResults"]
]

for n in range(len(house_links)):
    driver.get(GOOGLE_FORM_LINK)
    time.sleep(1)

    address = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[0]
    address.send_keys(house_address[n])

    price = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[1]
    price.send_keys(house_rent[n])

    link = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[2]
    link.send_keys(house_links[n])

    submit_button = driver.find_element(By.CSS_SELECTOR, "div.lRwqcd div")
    submit_button.click()