import sqlite3
from typing import List


class SearchCriteria:
    def __init__(self):
        self.conn = sqlite3.connect('bookstore.db')
        self.cursor = self.conn.cursor()

    def add_keyword(self, keyword: str) -> None:
        """Dodaje nowe słowo kluczowe do tabeli currently_searching"""
        try:
            self.cursor.execute('INSERT INTO currently_searching (keywords) VALUES (?)', (keyword,))
            self.conn.commit()
            print(f"Dodano słowo kluczowe: {keyword}")
        except sqlite3.Error as e:
            print(f"Błąd podczas dodawania słowa kluczowego: {e}")
            self.conn.rollback()

    def get_all_keywords(self) -> List[tuple]:
        """Zwraca listę wszystkich słów kluczowych z tabeli currently_searching"""
        try:
            self.cursor.execute('SELECT id, keywords FROM currently_searching')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Błąd podczas pobierania słów kluczowych: {e}")
            return []

    def delete_keyword(self, keyword_id: int) -> bool:
        """Usuwa słowo kluczowe o podanym ID"""
        try:
            self.cursor.execute('DELETE FROM currently_searching WHERE id = ?', (keyword_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Usunięto słowo kluczowe o ID: {keyword_id}")
                return True
            else:
                print(f"Nie znaleziono słowa kluczowego o ID: {keyword_id}")
                return False
        except sqlite3.Error as e:
            print(f"Błąd podczas usuwania słowa kluczowego: {e}")
            self.conn.rollback()
            return False

    def close_connection(self):
        """Zamyka połączenie z bazą danych"""
        self.conn.close()


def display_keywords(keywords: List[tuple]) -> None:
    """Wyświetla listę słów kluczowych"""
    if not keywords:
        print("Brak zapisanych słów kluczowych.")
        return

    print("\nLista zapisanych słów kluczowych:")
    print("ID  | Słowo kluczowe")
    print("-" * 30)
    for keyword_id, keyword in keywords:
        print(f"{keyword_id:3} | {keyword}")
