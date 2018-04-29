import requests
import shutil
import xmltodict
import asyncio
import argparse
import concurrent.futures


def load_products(fp):
    """
    Loads product names from scihub downloaded cart.

    :param fp: (String) Filepath to products.meta4
    :return: (List) Esa formatted product names
    """
    with open(fp) as fh:
        xml_doc = xmltodict.parse(fh.read())
    try:
        return [obj['@name'] for obj in xml_doc['metalink']['file']]
    except TypeError:
        # If products.meta4 has only one file, the returned xmltodict is not iterable
        return [xml_doc['metalink']['file']['@name']]


def gen_swea_name(esa_name):
    """
    Reformats esa style product name using swea naming conventions.

    :param esa_name: (String) Esa formatted product name
    :return: (String) Swea formatted product name
    """
    p = list(filter(None, esa_name.split('_')))
    return "{mission}{time}_{type}SAR{mode}_%".format(mission=p[0], time=p[4][2:].replace('T', ''), type=p[2][:3],
                                                      mode=p[1])


def gen_swea_id(swea_name):
    """
    Fetches swea product id from swea Rest API.

    :param swea_name: (String) Swea formatted product name
    :return: (String) Swea product id
    """
    request_url = "https://swea.rymdstyrelsen.se/rest/v1/images"
    req_payload = {
        'limit': 1,
        'imageNames': swea_name}
    request_obj = requests.get(request_url, params=req_payload)
    request_json = request_obj.json()
    return request_json['images'][0]['id']


def get_swea_prod(swea_id):
    """
    Downloads swea product.

    :param swea_id: (String) Swea product id
    :return: None
    """
    request_url = "https://swea.rymdstyrelsen.se/servlets/itembutton1"
    req_payload = {
        'NODE': "swea-keystone",
        'ID': swea_id}

    request_obj = requests.get(request_url, params=req_payload, stream=True)
    object_name = request_obj.headers['content-disposition'].split('\"')[1]

    with open(object_name, 'wb') as fh:
        shutil.copyfileobj(request_obj.raw, fh)


async def main(args):
    if args.products.endswith(".meta4"):
        esa_products = load_products(args.products)
    else:
        esa_products = [args.products]

    swea_products = [gen_swea_name(esa_name) for esa_name in esa_products]
    swea_product_ids = [gen_swea_id(swea_name) for swea_name in swea_products]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, get_swea_prod, swea_id) for swea_id in swea_product_ids]
        await asyncio.gather(*futures)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terminal client for downloading images for Swea Portal.")
    parser.add_argument('products',
                        help="ESA Product name, or filepath to downloaded cart. e.g. S1A_IW_GRDH_1SDV_20180224T162111_20180224T162136_020751_0238FE_48D1 or products.meta4")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
