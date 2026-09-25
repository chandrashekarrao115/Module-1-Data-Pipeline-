
import sqlite3
import pandas as pd

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "books.csv"
DB_PATH = BASE_DIR / "books.db"


def main():

    df = pd.read_csv(CSV_PATH)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS books"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS categories"
    )

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,

            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    for category in sorted(
        df["category"].unique()
    ):

        cursor.execute(
            """
            INSERT INTO categories
            (category_name)
            VALUES (?)
            """,
            (category,)
        )

    category_lookup = dict(
        cursor.execute(
            """
            SELECT category_name, category_id
            FROM categories
            """
        ).fetchall()
    )

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO books (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(row["in_stock"]),
                category_lookup[row["category"]]
            )
        )

    connection.commit()

    book_count = cursor.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    category_count = cursor.execute(
        "SELECT COUNT(*) FROM categories"
    ).fetchone()[0]

    print(
        f"Books inserted: {book_count}"
    )

    print(
        f"Categories inserted: {category_count}"
    )

    print(
        f"Database created: {DB_PATH}"
    )

    connection.close()


if __name__ == "__main__":
    main()
