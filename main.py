import time
import sqlite3
from datetime import datetime
from search_engine import Book
from notifications import check_and_notify  # Import modułu

def search_engine_main():
    """Główna funkcja wyszukiwania książek"""
    conn = sqlite3.connect('bookstore.db')

    try:
        keywords = Book.get_search_keywords()

        if not keywords:
            print("Brak słów kluczowych do wyszukiwania.")
            return

        total_books = 0

        for keyword in keywords:
            print(f"\nWyszukiwanie książek dla słowa kluczowego: {keyword}")
            books = Book.fetch_books_from_swiat_ksiazki(keyword)

            print(f"Znaleziono {len(books)} książek:")

            for book in books:
                book.save_to_db(conn)
                print(f"{book.title} - {book.author} - {book.price} PLN - ilość: {book.salable_qty}")

            total_books += len(books)

        conn.commit()
        print(f"\nŁącznie zapisano {total_books} książek w bazie danych.")
        check_and_notify()

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        conn.rollback()

    finally:
        conn.close()

def main():
    target_hours = {10, 13, 17, 22}  # Godziny uruchamiania skryptu
    while True:
        now = datetime.now()
        if now.hour in target_hours and now.minute == 0:  # Uruchamiaj tylko na początku godziny
            try:
                search_engine_main()
            except Exception as e:
                print(f"Błąd: {e}")
        time.sleep(60)  # Sprawdzaj co minutę

if __name__ == "__main__":
    main()
