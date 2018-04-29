import requests
import shutil
import xmltodict
import sys


def load_products(fp):
    """
    Loads product names from scihub downloaded cart.

    :param fp: (String) Filepath to products.meta4
    :return: (List) Esa formatted product names
    """
    with open(fp) as fh:
        xml_doc = xmltodict.parse(fh.read())
    return [obj['@name'] for obj in xml_doc['metalink']['file']]


def gen_swea_name(esa_name):
    """
    Reformats esa style product name using swea naming conventions.

    :param esa_name: (String) Esa formatted product name
    :return: (String) Swea formatted product name
    """
    p = list(filter(None, esa_name.split('_')))
    return "{mission}{time}_{type}SAR{mode}_%".format(mission=p[0], time=p[4][2:].replace('T', ''), type=p[2],
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


def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv)
