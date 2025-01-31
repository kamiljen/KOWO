import sqlite3
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

if __name__ == "__main__":
    search_engine_main()  # Po prostu uruchamiamy funkcję i skrypt kończy działanie
