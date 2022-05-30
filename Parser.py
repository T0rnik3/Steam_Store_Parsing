import csv
import sqlite3
import time
from random import randint

import requests
from bs4 import BeautifulSoup


def containsNumber(value):
    return any(char.isdigit() for char in value)


def scraping_steam():
    page = int(input("From How Many pages do you want to get a Data:\nINPUT:"))
    with open("Top_Sellers.csv", "w", encoding="utf-8_sig", newline="\n") as file:
        file_obj = csv.writer(file)
        file_obj.writerow(
            [
                "Id",
                "Title",
                "Release Date",
                "Old Price",
                "Discount",
                "New Price",
                "Platforms",
                "Positive Ratings",
                "Reviews Count",
                "IMAGE",
            ]
        )

        index = 1
        for ind in range(1, page + 1):
            url = f"https://store.steampowered.com/search/?category1=998&filter=topsellers&page={ind}"

            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            games = soup.find_all("a", class_="search_result_row")

            for game in games:
                title = game.find("span", class_="title").text
                price = game.find("div", class_="search_price").text.strip().split("$")
                img = game.img.attrs.get("src")
                release_date = game.find("div", class_="search_released").text
                platforms_soup = game.find_all("span", class_="platform_img")

                try:
                    ratings = game.find(
                        "span", class_="search_review_summary"
                    ).attrs.get("data-tooltip-html")
                    ratings = ratings.replace("<br>", " ").split()
                    positive_rating, users = tuple(
                        el for el in ratings if containsNumber(el)
                    )
                    positive_rating = positive_rating[:-1]
                    users = users.replace(",", "")
                except AttributeError:
                    positive_rating, users = "None", "None"

                platforms = [
                    platform.attrs.get("class")[1] for platform in platforms_soup
                ]

                if len(price) > 2:
                    old_price, new_price = float(price[1]), float(price[-1])
                    discount = round((1 - new_price / old_price) * 100)
                else:
                    old_price, new_price = price[-1], price[-1]
                    discount = 0

                file_obj.writerow(
                    [
                        index,
                        title,
                        release_date,
                        old_price,
                        discount,
                        new_price,
                        platforms,
                        positive_rating,
                        users,
                        img,
                    ]
                )
                index += 1

            print(f"Page {ind} Scraped Successfully...")
            time.sleep(randint(15, 20))

        print("Done!")


def csv_to_sqlite():
    conn = sqlite3.connect("Top_Sellers.sqlite")
    cur = conn.cursor()

    # Dropping a Table
    cur.execute(
        """--sql
        DROP TABLE if exists data;
        """
    )

    create_table = """--sql
                    CREATE TABLE IF NOT EXISTS data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Release_Date INTEGER NOT NULL,
                    Old_Price TEXT,
                    Discount INTEGER,
                    New_Price TEXT,
                    Platforms TEXT,
                    Positive_Ratings INTEGER,
                    Reviews_Count INTEGER,
                    Images BLOB);
                    """

    cur.execute(create_table)

    file = open("Top_Sellers.csv")

    contents = csv.reader(file)
    headings = next(contents)

    insert_records = """INSERT INTO data (id, Title, Release_Date, Old_Price, Discount, New_Price, Platforms, Positive_ratings, Reviews_Count, Images) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    cur.executemany(insert_records, contents)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    scraping_steam()
    csv_to_sqlite()
