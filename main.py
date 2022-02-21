#! /usr/bin/python3.10
# utf-8
"""Scrapes Vinilo record store outputs .csv or json (default .csv)"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

page_urls = [f"https://vinilo.co.uk/collections/all?page={i}" for i in range(1, 130)]

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}


def get_soup(urls) -> BeautifulSoup:
    """Returns BeautifulSoup object from url"""
    r = requests.get(urls, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    return soup


def get_prod_url(urls: list) -> list:
    """Returns list of tuples (product url, json url) product pages (also deals with pagination)"""
    product_urls = []

    for page in urls:
        soup = get_soup(page)
        for count, link in enumerate(
            soup.find_all("a", class_="grid-view-item__link grid-view-item__image-container full-width-link")
        ):
            product_urls.append((f"https://vinilo.co.uk{link['href']}", f"https://vinilo.co.uk/{link['href']}.json"))
            print(f"Saving: {link['href']}")
            # time.sleep(1)
    return product_urls


def get_meta(url: tuple) -> dict:
    r = requests.get(url[1], headers=headers).text
    product_meta = json.loads(r)

    album = product_meta["product"]["title"]
    artist = product_meta["product"]["title"].replace("/", "-").split("-")[0].strip()
    vendor = product_meta["product"]["vendor"]
    tags = product_meta["product"]["tags"]
    price = float(product_meta["product"]["variants"][0]["price"])
    price_created = product_meta["product"]["variants"][0]["created_at"]
    price_updated = product_meta["product"]["variants"][0]["updated_at"]

    try:
        image = product_meta["product"]["images"][0]["src"]
    except IndexError:
        image = "No Image Url"

    product = {
        "album": album,
        "artist": artist,
        "vendor": vendor,
        "tags": tags,
        "price": price,
        "price_created": price_created,
        "price_updated": price_updated,
        "image": image,
    }
    print(f"Saving: {product['artist'], product['album']}")
    return dict(product)


def export(stack: list, filetype="csv") -> None:
    """Exports .csv by default, optional json, saves to /home/ryan/Data/vinilo/csv"""

    def filename(ext) -> str:
        """Creates filename, saves to path /home/ryan/Data/vinilo/csv"""

        file_timestamp = str(datetime.now().date()) + "_" + str(datetime.now().time()).replace(":", ".")[:8]
        file_name = f"vinilo_stock_{file_timestamp}.{ext}"

        if ext == "csv":

            path = Path("/home/ryan/Data/vinilo/csv", file_name)
            print(path)
        elif ext == "json":
            path = Path("/home/ryan/Data/vinilo/json", file_name)
        else:
            raise ValueError("Only csv or json are valid arguments")

        return str(path)

    def export_csv(lst):
        df = pd.DataFrame(lst)

        df.to_csv(filename("csv"), index=False)
        print(f"csv exported")

    def export_json(lst):
        with open(filename("json"), "w") as f:
            f.write(json.dumps(lst, indent=2))

    if filetype == "csv":
        export_csv(stack)
    elif filetype == "json":
        export_json(stack)
    else:
        raise ValueError("Invalid argument")

    return None


def main():
    product_stack = []
    urls = get_prod_url(page_urls)
    for item in urls:
        product_stack.append(get_meta(item))
    export(product_stack)


if __name__ == "__main__":
    main()
