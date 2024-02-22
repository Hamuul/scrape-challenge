### Initial mapping/analysis of problem:

- After some digging we find that ```http://shop.rewe.de```
exposes sitemaps at ```/sitemaps``` .  We notice that
there are 2 xml files which contain most/all products.
However, upon trying to use ```cURL``` with various 
user-agents and headers to spoof our scraper, we are faced with 403 Forbidden status codes.

- Although they would greatly improve perforamnce, 403 is what
```aiottp, requests``` and other popular python packages also return
when trying to fetch the HTML source. Furthermore, if the site
suspects programmatic access of any kind, it requests a captcha
which is a significant hindrance to scraping.

### Scraping product details
- We use LXML package because it generally offers the best parsing performance
in python.
- In the page source of each product there is a field matched by a css selector 
like ```id=pdpr-propstore*```
which contains most/all product info we wanted in a nice JSON (actually, much more than that, like
nutritional info, price per liter/kg, allergens etc)
- If we're fine with prices like `````'980'````` or `````'1199'````` which represent 9.80€ and 11.99€
and know we must post-process them in code, that is actually all we need to 
scrape.
- We can also scrape the already formatted price with a CSS selector ```#pdpr-ProductIinformation``` + Xpath
expression ```//meso-data[@data-context="product-detail"]```
but this may hurt performance
- 
### Selenium solution 

- Tryin selenium, the headless webdriver can thankfully
access any page of the marketplace, and avoids 403 and captcha.
- Fetch the xml files which contain all product urls with selenium
 and parse them into a collection (list/generator), stripping whatever
is not inside <loc> tags.
- We end up with a list of about 70k product urls. We spawn
NUM_DRIVERS (tests suggest 4 and 8 work decently) headless webdrivers 
which fetch their html source successively and writes to 
a .txt file with shell redirection.

- Selenium webdrivers are pretty slow to boot up and pretty slow 
to fetch the html. Also, they are not compatible with async. Overall
this leads to a slow process. It took more than 4 hours to 
extract the product data with this approach.

### Playwright
- After research we find out playwright supports ```async```
and suspect it might offer better performance.
- We port most of the logic from the selenium scraper 
but try to optimize file I/O and leverage concurrency to improve 
performance.
- Switch from writing to .txt to writing to .csv

#### Miscellanous
- Fine-tuning of parameters like ```timeout, chunk_size,
NUM_DRIVERS``` may net better performance but they require 
very thorough and broad profiling which is time-consuming 
in itself.
- The scraper would probably benefit from being ported
to a faster language like Java / C#. It felt really hard 
to go above an average ~5 products details extracted and
written to disk per second.
- Though some products are not currently in stock, their details
are still available in the HTML source, though not rendered. I 
have chosen to keep track of them too.