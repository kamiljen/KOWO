import requests
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from typing import List


@dataclass
class Book:
    author: str
    title: str
    price: float
    date_found: datetime
    link: str
    series: str
    image_link: str
    salable_qty: int

    @staticmethod
    def get_search_keywords() -> List[str]:
        """Pobiera słowa kluczowe z bazy danych i konwertuje je na lowercase"""
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT keywords FROM currently_searching')
            keywords = [keyword[0].lower() for keyword in cursor.fetchall()]
            return keywords
        except sqlite3.Error as e:
            print(f"Błąd podczas pobierania słów kluczowych: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def fetch_books_from_swiat_ksiazki(cls, keyword: str) -> List['Book']:
        """Pobiera książki dla danego słowa kluczowego"""
        url = f"https://www.swiatksiazki.pl/graphql?hash=2086150927&sort_1={{%22position%22:%22ASC%22}}&filter_1={{%22price%22:{{}},%22customer_group_id%22:{{%22eq%22:%220%22}}}}&search_1=%22outlet%20{keyword}%22&pageSize_1=1000&currentPage_1=1&_currency=%22PLN%22"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            books = []

            for item in data['data']['products']['items']:
                try:
                    authors = item['dictionary'].get('authors', [])
                    author_names = ', '.join([a.get('name', '') for a in authors]) if authors else 'Nieznany autor'

                    series_list = item['dictionary'].get('series', [])
                    series_name = series_list[0].get('name', 'Brak serii') if series_list else 'Brak serii'

                    book = cls(
                        author=author_names,
                        title=item['name'].replace('[OUTLET] ', ''),
                        price=float(item['price_range']['minimum_price']['final_price']['value']),
                        date_found=datetime.now(),
                        link=f"https://www.swiatksiazki.pl/{item['url_rewrites'][0]['url']}",
                        series=series_name,
                        image_link=item['small_image']['url'],
                        salable_qty=item['salable_qty']
                    )
                    books.append(book)
                except (KeyError, IndexError, ValueError) as e:
                    print(f"Błąd podczas przetwarzania książki: {e}")

            return books

        except requests.RequestException as e:
            print(f"Błąd podczas pobierania danych: {e}")
            return []

    def save_to_db(self, conn: sqlite3.Connection):
        """Zapisuje wyniki wyszukiwania w tabeli search_history."""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_history 
            (author, title, price, date_found, link, series, IMAGE_LINK, salable_qty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.author,
            self.title,
            self.price,
            self.date_found.strftime('%Y-%m-%d %H:%M:%S'),
            self.link,
            self.series,
            self.image_link,
            int(self.salable_qty) if self.salable_qty is not None else 0
        ))