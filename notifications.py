import sqlite3
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku env_variables.env
load_dotenv('env_variables.env')

DATABASE_PATH = 'bookstore.db'
EMAIL_ADDRESS = 'kowo.ksiazkowyoutlet@gmail.com'
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Pobierz hasło ze zmiennej środowiskowej
RECIPIENT_EMAIL = 'kamiljen@gmail.com'

# Konfiguracja dla Gmail
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587  # Gmail używa portu 587 dla TLS


def fetch_recent_books() -> tuple:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Pobierz dwa ostatnie timestampy
    cursor.execute('''
        SELECT DISTINCT date_found 
        FROM search_history 
        ORDER BY date_found DESC 
        LIMIT 2
    ''')

    timestamps = cursor.fetchall()

    if len(timestamps) < 2:
        # Jeśli mamy tylko jedno lub zero wyszukiwań, zwróć wszystkie książki z ostatniego wyszukiwania
        cursor.execute('''
            SELECT author, title, price, date_found, link, series, IMAGE_LINK, salable_qty
            FROM search_history 
            WHERE date_found = ?
        ''', (latest_timestamp,))

        new_books = cursor.fetchall()
        conn.close()
        return new_books

    latest_timestamp, previous_timestamp = timestamps[0][0], timestamps[1][0]

    # Pobierz wszystkie książki z poprzedniego wyszukiwania
    cursor.execute('''
        SELECT author, title, price, date_found, link, series, IMAGE_LINK, salable_qty
        FROM search_history 
        WHERE date_found = ?
    ''', (previous_timestamp,))
    previous_books = set(
        (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        for row in cursor.fetchall()
    )

    # Pobierz książki z ostatniego wyszukiwania
    cursor.execute('''
        SELECT author, title, price, date_found, link, series, IMAGE_LINK, salable_qty
        FROM search_history 
        WHERE date_found = ?
    ''', (latest_timestamp,))
    latest_books = cursor.fetchall()

    # Znajdź nowe książki, które nie istniały w poprzednim wyszukiwaniu
    new_books = [
        book for book in latest_books
        if (book[0], book[1], book[2], book[4], book[5], book[6], book[7]) not in previous_books
    ]

    conn.close()
    return new_books

def load_email_template(template_path: str) -> str:
    """Ładuje szablon HTML z pliku."""
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def send_email_notification(books: list):
    """Wysyła powiadomienie mailowe z listą nowych książek, korzystając z szablonu HTML."""
    if not books:
        print("Brak nowych książek do wysłania.")
        return

    try:
        # Wczytaj szablon HTML
        template = load_email_template('email_template.html')

        # Stwórz dynamiczną zawartość dla książek
        books_content = "".join(f"""
            <div class="product-info">
                <img class="product-image" src="{book[6]}" alt="Okładka książki">
                <div class="product-details">
                    <h3>{book[1]}</h3>
                    <p>Autor: {book[0]}</p>
                    <p>Cena: {book[2]} PLN</p>
                    <p>Dostępnych: {book[7]} szt.</p>
                    <a href="{book[4]}" class="card-link" target="_blank">Sprawdź książkę</a>
                </div>
            </div>
        """ for book in books)

        # Podmień {{books_content}} w szablonie
        html_body = template.replace('{{books_content}}', books_content)

        # Składanie wiadomości
        message = MIMEMultipart()
        message['From'] = EMAIL_ADDRESS
        message['To'] = RECIPIENT_EMAIL
        message['Subject'] = f'Znaleziono {len(books)} nowych książek w outlecie!'

        # Dodaj zawartość HTML do wiadomości
        message.attach(MIMEText(html_body, "html"))

        # Połączenie z serwerem SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)

        print("Powiadomienie email wysłane pomyślnie!")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def check_and_notify():
    """Sprawdza, czy są nowe książki i wysyła powiadomienie tylko jeśli pojawiły się nowe pozycje."""
    new_books = fetch_recent_books()

    # Dodaj dodatkowe logowanie lub sprawdzenie
    print(f"Liczba książek w ostatnim wyszukiwaniu: {len(new_books)}")

    if new_books:
        print(f"Znaleziono {len(new_books)} nowych książek! Wysyłam powiadomienie...")
        send_email_notification(new_books)
    else:
        print("Brak nowych książek w porównaniu z poprzednim wyszukiwaniem.")