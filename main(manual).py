"""
To do:
1. Dodać samoczynne uruchamianie skryptu 'w chmurze'.
2. Polepszyć design wiadomości mailowych - dodaj odstęp w przycisku.
3. Wystawić API.
4. Zrobić stronę webową.
5. Zintegrować ją z API.
6. Spróbować zrobić APK.
"""


import sqlite3
from search_engine import Book
from search_criteria import SearchCriteria, display_keywords
from notifications import check_and_notify  # Import nowego modułu


def search_engine_main():
    """Główna funkcja wyszukiwania książek"""
    conn = sqlite3.connect('bookstore.db')

    try:
        # Pobranie słów kluczowych
        keywords = Book.get_search_keywords()

        if not keywords:
            print("Brak słów kluczowych do wyszukiwania.")
            return

        total_books = 0

        # Wyszukiwanie książek dla każdego słowa kluczowego
        for keyword in keywords:
            print(f"\nWyszukiwanie książek dla słowa kluczowego: {keyword}")
            books = Book.fetch_books_from_swiat_ksiazki(keyword)

            print(f"Znaleziono {len(books)} książek:")

            # Zapisanie każdej książki do bazy danych
            for book in books:
                book.save_to_db(conn)
                print(f"{book.title} - {book.author} - {book.price} PLN - ilość: {book.salable_qty}")

            total_books += len(books)

        # Zatwierdzenie zmian w bazie danych
        conn.commit()
        print(f"\nŁącznie zapisano {total_books} książek w bazie danych.")

        # Wywołanie funkcji do wysyłania powiadomień
        check_and_notify()

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        conn.rollback()

    finally:
        conn.close()

def search_criteria_main():
    """Główna funkcja zarządzania słowami kluczowymi"""
    search = SearchCriteria()

    while True:
        print("\n=== MENU ===")
        print("1. Dodaj nowe słowo kluczowe")
        print("2. Wyświetl wszystkie słowa kluczowe")
        print("3. Usuń słowo kluczowe")
        print("4. Wyszukaj książki")
        print("5. Wyjście")

        choice = input("\nWybierz opcję (1-5): ")

        if choice == '1':
            keyword = input("Podaj słowo kluczowe do wyszukiwania: ")
            if keyword.strip():
                search.add_keyword(keyword)
            else:
                print("Słowo kluczowe nie może być puste!")

        elif choice == '2':
            keywords = search.get_all_keywords()
            display_keywords(keywords)

        elif choice == '3':
            keywords = search.get_all_keywords()
            display_keywords(keywords)
            if keywords:
                try:
                    keyword_id = int(input("\nPodaj ID słowa kluczowego do usunięcia: "))
                    search.delete_keyword(keyword_id)
                except ValueError:
                    print("Nieprawidłowe ID. Podaj liczbę.")

        elif choice == '4':
            search_engine_main()

        elif choice == '5':
            search.close_connection()
            print("Do widzenia!")
            break

        else:
            print("Nieprawidłowa opcja. Wybierz 1-5.")


if __name__ == "__main__":
    search_criteria_main()
