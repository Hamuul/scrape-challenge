import asyncio
import json
from itertools import cycle

from fake_useragent import UserAgent
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from assemble_product_urls import convert_xmls_to_prodlink_generator as convert

fopt = FirefoxOptions()
ua = UserAgent()

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", ua.random)
profile.set_preference("permissions.default.stylesheet", 2)
profile.set_preference("permissions.default.image", 2)
profile.set_preference("javascript.enabled", False)
profile.set_preference("layers.acceleration.disabled", True)
profile.set_preference("network.http.pipelining", True)
profile.set_preference("network.prefetch-next", False)
fopt.profile = profile
fopt.page_load_strategy = 'eager'
fopt.add_argument("--headless")



NUM_DRIVERS = 4
drivers = [webdriver.Firefox(options=fopt) for _ in range(NUM_DRIVERS)]


def extract_desired_fields(url, driver):
    driver.get(url)
    try:
        tree = html.fromstring(
            driver.find_element(By.CSS_SELECTOR, "#pdpr-ProductInformation").get_attribute("innerHTML"))
        price_element = tree.xpath('//meso-data[@data-context="product-detail"]')[0]
        price = price_element.get('data-price')

        json_string = driver.find_element(By.CSS_SELECTOR, '[id^="pdpr-propstore"]').get_attribute('textContent')
        json_dict = json.loads(json_string)
        json_dict = json_dict["productData"]
    except NoSuchElementException:
        return
    try:
        print(
            f'{json_dict["productName"]}\n{json_dict["brandKey"]}\n{price}eur\n'
            f'{json_dict["gtin"]}\n')
    except KeyError:  # sometimes brandKey is missing (when product is only in xml)
        idx = json_dict["slug"].find("-")
        print(
            f'{json_dict["productName"]}\n{json_dict["slug"][:idx]}\n{price}eur\n'
            f'{json_dict["gtin"]}\n')


async def main():
    for link, driver in zip(await convert(["extracted0.xml", "extracted1.xml"]), cycle(drivers)):
        extract_desired_fields(link, driver)


asyncio.run(main())
