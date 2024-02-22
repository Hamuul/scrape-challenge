from xmltodict import parse
import aiofiles


async def convert_xmls_to_iterable(filenames):
    xml_content = []
    for i, file in enumerate(filenames):
        async with aiofiles.open(file, "r") as f:
            xml_content.append(parse(await f.read()))
    product_link_gen = [
        subpart["loc"] for part in xml_content for subpart in part["urlset"]["url"]
    ]
    return product_link_gen
