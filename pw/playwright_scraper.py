# Author: Luca Pana | Year: 2024
import os
import asyncio
from functools import partial


import uvloop
import pypeln as pl
import ujson
import aiofiles


from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from lxml import html
from aiocsv import AsyncWriter


from assemble_product_urls import convert_xmls_to_iterable as convert


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # may improve perforamnce


async def extract_desired_field(url, page):
    """Asynchronously retrieves HTML source, parses it for price,
        brand and GTIN and writes them to a csv file on disk.
    Args:
        url (str): The URL to fetch.
        page : Playwright page object.
    Returns:
        None. Appends to a csv file as a side effect.
    """
    try:
        await page.goto(url)
        html_source = await page.content()
        tree = html.fromstring(html_source)
        element = tree.cssselect("[id^='pdpr-propstore']")
        if not element:
            return
        json_dict = ujson.loads(element[0].text_content().strip())["productData"]
        price_str = str(json_dict["pricing"]["price"])
        digit_count = len(price_str)
        price = f"{price_str[0:digit_count - 2]}.{price_str[-2:]}"
        if price.startswith("."):
            price = f"0{price}"

        async with aiofiles.open("products.csv", mode="a", encoding="utf-8", newline="") as afp:
            writer = AsyncWriter(afp, dialect="unix")
            try:
                await writer.writerows(
                    [
                        [
                            json_dict["productName"],
                            json_dict["brandKey"],
                            price,
                            json_dict["gtin"],
                        ]
                    ]
                )
            except KeyError:
                idx = json_dict["slug"].find("-")
                await writer.writerows(
                    [
                        [
                            json_dict["productName"],
                            json_dict["slug"][:idx],
                            price,
                            json_dict["gtin"],
                        ]
                    ]
                )
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
    if not os.path.exists("products.csv"):
        open("products.csv", "w").write("productName,brand,price,GTIN\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            ignore_default_args=[
                "--no-sandbox",
                "--log-level=0",
                "--in-process-gpu",
                "--enable-automation",
                "--enable-gpu",
                "--use-angle=vulkan",
            ],
        )
        context = await browser.new_context(
            java_script_enabled=False, user_agent=UserAgent().random
        )

        chunked_list = list()
        num_links = len(link_gen)
        chunk_size = 8096

        for i in range(0, num_links, chunk_size):
            chunked_list.append(link_gen[i : i + chunk_size])
        await asyncio.gather(
            *[task(context, chunked_list[i]) for i in range(len(chunked_list))]
        )
        # stage = pl.task.map(partial(task, context), chunked_list, workers=12)
        # await stage


asyncio.run(main())
