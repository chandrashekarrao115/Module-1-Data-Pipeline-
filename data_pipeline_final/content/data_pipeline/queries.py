
import sqlite3
import pandas as pd

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "books.db"

OUTPUT_DIR = BASE_DIR / "query_outputs"

OUTPUT_DIR.mkdir(
    exist_ok=True
)


def main():

    connection = sqlite3.connect(
        DB_PATH
    )

    # --------------------------------
    # Query 1: SELECT + WHERE
    # --------------------------------

    query_1 = """
    SELECT
        title,
        price_gbp,
        rating,
        in_stock
    FROM books
    WHERE rating >= 4
    """

    result_1 = pd.read_sql(
        query_1,
        connection
    )

    print("\nQUERY 1")
    print(query_1)
    print(result_1.head(10))

    result_1.to_csv(
        OUTPUT_DIR /
        "query_01_select_where.csv",
        index=False
    )

    # --------------------------------
    # Query 2: ORDER BY + LIMIT
    # --------------------------------

    query_2 = """
    SELECT
        title,
        price_gbp,
        rating
    FROM books
    ORDER BY price_gbp DESC
    LIMIT 10
    """

    result_2 = pd.read_sql(
        query_2,
        connection
    )

    print("\nQUERY 2")
    print(query_2)
    print(result_2)

    result_2.to_csv(
        OUTPUT_DIR /
        "query_02_order_by_limit.csv",
        index=False
    )

    # --------------------------------
    # Query 3: DISTINCT
    # --------------------------------

    query_3 = """
    SELECT DISTINCT
        rating
    FROM books
    ORDER BY rating
    """

    result_3 = pd.read_sql(
        query_3,
        connection
    )

    print("\nQUERY 3")
    print(query_3)
    print(result_3)

    result_3.to_csv(
        OUTPUT_DIR /
        "query_03_distinct.csv",
        index=False
    )

    # --------------------------------
    # Query 4: BETWEEN
    # --------------------------------

    query_4 = """
    SELECT
        title,
        price_gbp,
        price_inr
    FROM books
    WHERE price_gbp BETWEEN 20 AND 40
    ORDER BY price_gbp
    """

    result_4 = pd.read_sql(
        query_4,
        connection
    )

    print("\nQUERY 4")
    print(query_4)
    print(result_4.head(10))

    result_4.to_csv(
        OUTPUT_DIR /
        "query_04_between.csv",
        index=False
    )

    # --------------------------------
    # Query 5: IN
    # --------------------------------

    query_5 = """
    SELECT
        title,
        rating,
        in_stock
    FROM books
    WHERE rating IN (4, 5)
    ORDER BY rating DESC
    """

    result_5 = pd.read_sql(
        query_5,
        connection
    )

    print("\nQUERY 5")
    print(query_5)
    print(result_5.head(10))

    result_5.to_csv(
        OUTPUT_DIR /
        "query_05_in.csv",
        index=False
    )

    # --------------------------------
    # JOIN
    # --------------------------------

    join_query = """
    SELECT
        c.category_name,
        b.title,
        b.price_gbp,
        b.price_inr,
        b.rating,
        b.in_stock
    FROM books AS b
    JOIN categories AS c
        ON b.category_id = c.category_id
    ORDER BY
        c.category_name,
        b.rating DESC,
        b.title
    """

    sql_join_result = pd.read_sql(
        join_query,
        connection
    )

    print("\nJOIN QUERY")
    print(join_query)
    print(sql_join_result.head(20))

    sql_join_result.to_csv(
        OUTPUT_DIR /
        "join_sql.csv",
        index=False
    )

    # --------------------------------
    # Pandas merge
    # --------------------------------

    books_df = pd.read_sql(
        """
        SELECT
            book_id,
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        FROM books
        """,
        connection
    )

    categories_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        """,
        connection
    )

    merged_df = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    pandas_join_result = (
        merged_df[
            [
                "category_name",
                "title",
                "price_gbp",
                "price_inr",
                "rating",
                "in_stock"
            ]
        ]
        .sort_values(
            [
                "category_name",
                "rating",
                "title"
            ],
            ascending=[
                True,
                False,
                True
            ]
        )
        .reset_index(drop=True)
    )

    pandas_join_result.to_csv(
        OUTPUT_DIR /
        "join_pandas.csv",
        index=False
    )

    # --------------------------------
    # Compare
    # --------------------------------

    sql_join_result = (
        sql_join_result
        .reset_index(drop=True)
    )

    print("\nSQL/PANDAS EQUIVALENCE:")

    print(
        sql_join_result.equals(
            pandas_join_result
        )
    )

    connection.close()


if __name__ == "__main__":
    main()
