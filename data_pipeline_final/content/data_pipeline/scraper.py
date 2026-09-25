
import requests
import pandas as pd

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


BASE_URL = "https://books.toscrape.com/"
GBP_TO_INR = 105.50

OUTPUT_DIR = Path("/content/data_pipeline")
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_PATH = OUTPUT_DIR / "books.csv"

CATEGORIES = {
    "Travel": "catalogue/category/books/travel_2/index.html",
    "Mystery": "catalogue/category/books/mystery_3/index.html",
    "Historical Fiction": "catalogue/category/books/historical-fiction_4/index.html",
}

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def fetch_page(url):

    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


def get_next_page_url(soup, current_url):

    next_link = soup.select_one("li.next a")

    if next_link and next_link.get("href"):

        return urljoin(
            current_url,
            next_link["href"]
        )

    return None


def parse_book(book_card):

    # ---------------------------
    # TITLE
    # ---------------------------

    title_tag = book_card.select_one("h3 a")

    title = ""

    if title_tag:
        title = title_tag.get(
            "title",
            ""
        ).strip()

    # ---------------------------
    # PRICE
    # ---------------------------

    price_tag = book_card.select_one(
        "p.price_color"
    )

    price = ""

    if price_tag:
        price = price_tag.get_text(
            strip=True
        )

    # ---------------------------
    # RATING
    # ---------------------------

    rating_tag = book_card.select_one(
        "p.star-rating"
    )

    star_rating = ""

    if rating_tag:

        classes = rating_tag.get(
            "class",
            []
        )

        for rating_name in RATING_MAP:

            if rating_name in classes:

                star_rating = rating_name

                break

    # ---------------------------
    # AVAILABILITY
    # ---------------------------

    availability_tag = book_card.select_one(
        "p.instock.availability"
    )

    availability = ""

    if availability_tag:

        availability = availability_tag.get_text(
            " ",
            strip=True
        )

    return {
        "title": title,
        "price": price,
        "star_rating": star_rating,
        "availability": availability
    }


def scrape_category(
    category_name,
    category_path
):

    books = []

    current_url = urljoin(
        BASE_URL,
        category_path
    )

    page_number = 1

    while current_url:

        print(
            f"Scraping {category_name} "
            f"- page {page_number}"
        )

        soup = fetch_page(
            current_url
        )

        book_cards = soup.select(
            "article.product_pod"
        )

        print(
            "Books found:",
            len(book_cards)
        )

        for book_card in book_cards:

            book = parse_book(
                book_card
            )

            book["category"] = category_name

            books.append(book)

        current_url = get_next_page_url(
            soup,
            current_url
        )

        page_number += 1

    return books


def clean_data(raw_books):

    df = pd.DataFrame(
        raw_books
    )

    # ---------------------------
    # PRICE
    # ---------------------------

    df["price_gbp"] = (
        df["price"]
        .astype(str)
        .str.replace(
            "£",
            "",
            regex=False
        )
        .str.strip()
    )

    df["price_gbp"] = pd.to_numeric(
        df["price_gbp"],
        errors="coerce"
    )

    # ---------------------------
    # RATING
    # ---------------------------

    df["rating"] = df[
        "star_rating"
    ].map(RATING_MAP)

    # ---------------------------
    # AVAILABILITY
    # ---------------------------

    df["in_stock"] = (
        df["availability"]
        .astype(str)
        .str.contains(
            "In stock",
            case=False,
            na=False
        )
    )

    # ---------------------------
    # MEDIAN IMPUTATION
    # ---------------------------

    if df["price_gbp"].isna().any():

        median_price = df[
            "price_gbp"
        ].median()

        df["price_gbp"] = df[
            "price_gbp"
        ].fillna(
            median_price
        )

    if df["rating"].isna().any():

        median_rating = df[
            "rating"
        ].median()

        df["rating"] = df[
            "rating"
        ].fillna(
            median_rating
        )

    df["rating"] = (
        df["rating"]
        .round()
        .astype(int)
    )

    # ---------------------------
    # REMOVE INVALID ESSENTIAL ROWS
    # ---------------------------

    df = df[
        (df["title"].astype(str).str.strip() != "")
        &
        (df["category"].astype(str).str.strip() != "")
    ].copy()

    # ---------------------------
    # GBP → INR
    # ---------------------------

    df["price_inr"] = (
        df["price_gbp"]
        * GBP_TO_INR
    ).round(2)

    # ---------------------------
    # BOOLEAN
    # ---------------------------

    df["in_stock"] = df[
        "in_stock"
    ].astype(bool)

    # ---------------------------
    # FINAL COLUMNS
    # ---------------------------

    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]

    return df


def main():

    all_books = []

    # ---------------------------
    # SCRAPE
    # ---------------------------

    for category_name, category_path in CATEGORIES.items():

        category_books = scrape_category(
            category_name,
            category_path
        )

        print(
            category_name,
            ":",
            len(category_books),
            "books"
        )

        all_books.extend(
            category_books
        )

    print(
        "\nTotal raw books:",
        len(all_books)
    )

    if len(all_books) < 60:

        raise ValueError(
            "Less than 60 books were scraped."
        )

    # ---------------------------
    # CLEAN
    # ---------------------------

    df = clean_data(
        all_books
    )

    print(
        "Clean books:",
        len(df)
    )

    # ---------------------------
    # VALIDATION
    # ---------------------------

    print(
        "\nMissing values:"
    )

    print(
        df.isnull().sum()
    )

    print(
        "\nData types:"
    )

    print(
        df.dtypes
    )

    print(
        "\nCategories:"
    )

    print(
        df["category"].value_counts()
    )

    # ---------------------------
    # SAVE
    # ---------------------------

    df.to_csv(
        CSV_PATH,
        index=False
    )

    print(
        "\nSaved:",
        CSV_PATH
    )


if __name__ == "__main__":

    main()
