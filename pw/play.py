import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Pool, Process

import ujson
import uvloop

from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from lxml import html


from assemble_product_urls import convert_xmls_to_prodlink_generator as convert


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
async def extract_desired_field(url, page):
    """Retrieves and returns the HTML source of the given URL asynchronously.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML source of the page.
    """
    try:
        await page.goto(url)
        html_source = await page.content()
        tree = html.fromstring(html_source)
        # price_element = tree.xpath('//meso-data[@data-context="product-detail"]')[0]
        # price = price_element.get('data-price')
        element = tree.cssselect("[id^='pdpr-propstore']")
        if not element:
           return
        json_dict = ujson.loads(element[0].text_content().strip())["productData"]
        price_str = str(json_dict["pricing"]["price"])
        numlen = len(price_str)
        price2 = f'{price_str[0:numlen - 2]}.{price_str[-2:]}'
        # print(ujson.dumps(json_dict["productData"], indent=4))
        try:
            print(
                f'{json_dict["productName"]}\n{json_dict["brandKey"]}\n{price2}eur\n'
                f'{json_dict["gtin"]}\n')
        except KeyError:
            idx = json_dict["slug"].find("-")
            print(
                f'{json_dict["productName"]}\n{json_dict["slug"][:idx]}\n{price2}eur\n'
                f'{json_dict["gtin"]}\n')
           # print(html_source)
    except Exception as e:
        print(f"Error: {e}")
        return None



async def task(context, link_gen):
    page = await context.new_page()
    for link in link_gen:
        try:
            await page.route("**/*.{png,jpg,jpeg,svg}", lambda route: route.abort())
            await extract_desired_field(link, page)  # Pass the page to the function
        except Exception as e:
            print(f"Error processing {link}: {e}")
            await page.close()
            page = await context.new_page()
async def main():
    link_gen = await convert(["extracted0.xml", "extracted1.xml"])
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, ignore_default_args=
        ["--no-sandbox",
         "--log-level=0",
         "--in-process-gpu",
         "--enable-automation",
         "--enable-gpu",
         "--use-angle=vulkan"])
        context = await browser.new_context(java_script_enabled=False,
                                            user_agent=UserAgent().random)

        chunked_list = list()
        l = len(link_gen)
        chunk_size =  22000

        for i in range(0, l, chunk_size):
            chunked_list.append(link_gen[i:i + chunk_size])
            #print(i)


        await asyncio.gather(
             *[task(context, chunked_list[i]) for i in range(len(chunked_list))]
         )





asyncio.run(main())
    # Run asynchronously to leverage parallelism
