from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from fake_useragent import UserAgent

urls = ["https://shop.rewe.de/sitemaps/sitemap-shop-produkte.xml",
        "https://shop.rewe.de/sitemaps/sitemap-shop-produkte_1.xml"]
def write_xmls_to_disk(urls:list[str]):
    fopt = FirefoxOptions()
    ua = UserAgent()

    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", ua.random)
    profile.set_preference("permissions.default.stylesheet", 2);
    profile.set_preference("permissions.default.image", 2);
    profile.set_preference("javascript.enabled", False);
    fopt.profile = profile
    fopt.add_argument("--headless")

    drivers =  (webdriver.Firefox(options=fopt) for _ in urls)
    for (i, url) , driver in zip(enumerate(urls), drivers):
        driver.get(url)
        with open(f"extracted{i}.xml", "w+") as f:
            f.write(driver.page_source)
        driver.quit()


write_xmls_to_disk(urls)
