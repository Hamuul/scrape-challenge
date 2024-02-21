from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By

from fake_useragent import UserAgent

fopt = FirefoxOptions()
ua = UserAgent()


profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", ua.random)
fopt.profile = profile
fopt.add_argument("--headless")

driver = webdriver.Firefox(options=fopt)
# driver.get('https://shop.rewe.de/sitemaps/sitemap-shop-produkte.xml')
# product_links = driver.find_elements(By.TAG_NAME, 'loc')


# gen = (link.text for link in product_links[:1])

# for url in gen:
driver.get("https://shop.rewe.de/p/all-e-bleue-cool-hills-weisswein-sauvignon-blanc-trocken-0-75l/1454443")
sleep(2)
full_json = driver.find_element(By.CSS_SELECTOR, '[id^="pdpr-propstore"]').get_attribute('textContent')
print(full_json)
driver.quit()

