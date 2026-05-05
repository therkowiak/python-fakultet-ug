# Dokumentacja Projektu: Binturong Signals

## 1. Informacje ogólne
- **Tytuł projektu:** Binturong Signals  
- **Autor:** Tymoteusz Herkowiak 
- **Data oddania:**  
  - Prezentacja: 22.04.2025  
  - Wersja ostateczna: 29.04.2025  
- **Technologia:** Python, Flask  

---

## 2. Opis Projektu
**Binturong Signals** to aplikacja webowa służąca do śledzenia cen akcji giełdowych w czasie rzeczywistym.  

Główną funkcjonalnością systemu jest możliwość ustawiania personalizowanych alertów cenowych.  
Gdy cena wybranej akcji spadnie poniżej zdefiniowanego przez użytkownika poziomu, system automatycznie wysyła powiadomienie e-mail.

---

## 3. Realizacja wymagań technicznych

### Elementy niezbędne

- **Komunikacja z bazą danych**  
  Wykorzystano SQLAlchemy do obsługi relacyjnej bazy danych SQLite (modele `User` i `Stock`).  
  Zaimplementowano operacje CRUD:
  - dodawanie akcji  
  - pobieranie danych użytkownika  
  - aktualizacja/usuwanie alertów  

- **Wykorzystanie Blueprintów**  
  Kod został podzielony na moduły:
  - `auth_bp` (autoryzacja)  
  - `main_bp` (główne funkcjonalności)  

- **Obsługa błędów**  
  Zaimplementowano niestandardowe szablony dla błędów:
  - 404 – nie znaleziono strony  
  - 500 – błąd serwera  

- **Testy**  
  Plik `test_app.py` zawiera testy jednostkowe sprawdzające:
  - poprawność ładowania stron  
  - obsługę błędów  
  - wymagania dotyczące logowania  

---

### Wybrane opcje dodatkowe

- **Możliwość wysyłania maili**  
  Integracja z Flask-Mail do wysyłania powiadomień o osiągnięciu ceny docelowej  

- **System logowania**  
  Użytkownicy mogą tworzyć konta i logować się, co pozwala na personalizację śledzonych akcji  

- **Wyszukiwanie / API**  
  Wykorzystanie biblioteki `yfinance` do pobierania aktualnych danych giełdowych z zewnętrznego API  

---

## 4. Instrukcja uruchomienia

1. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```

2. Uruchom aplikację:
   ```bash
   python app.py
   ```

3. System automatycznie zainicjalizuje bazę danych `gielda.db` przy pierwszym uruchomieniu.

4. Domyślny adres aplikacji:
   ```
   http://127.0.0.1:5000
   ```

---

## 5. Struktura plików

- `app.py` – główny plik aplikacji, konfiguracja serwera, maila i harmonogramu zadań (APScheduler)  
- `models.py` – definicje modeli bazodanowych (`User`, `Stock`)  
- `routes/` – katalog zawierający blueprinty (logika tras)  
- `templates/` – katalog z szablonami Jinja2
- `test_app.py` – zautomatyzowane testy jednostkowe  
- `mailAlertTest.py` – skrypt do manualnego testowania systemu powiadomień  
- `requirements.txt` – lista zależności projektowych  

---
## 6. 
Aplikacja wykorzystuje szablony Jinja2 oparte na wspólnym szablonie bazowym base.html. Wszystkie widoki utrzymane są w spójnym, ciemnym, technicznym stylu (IBM Plex Mono + niebieska kolorystyka cyber/inwestycyjna).
**Szablon bazowy**
 - base.html – wspólny layout całej aplikacji (navbar, style CSS, logo).

**Główne widoki**
 -`index.html` - / - Strona główna (landing page) z powitaniem i przyciskami do logowania/rejestracji.
 -`register.html` - /register - Formularz rejestracji nowego użytkownika (username, email, hasło).
 -`login.html` - /login - Formularz logowania (email + hasło).
 -`dashboard.html` - /dashboard - Główny panel użytkownika. Wyświetla karty obserwowanych akcji z aktualną ceną, poziomem alarmowym, widgetem TradingView oraz opcją usunięcia.
 -`search.html` - /search - Wyszukiwarka tickerów (np. AAPL). Po wyszukaniu pokazuje aktualną cenę, widget TradingView oraz formularz dodania akcji z opcjonalnym progiem alertu.
 -`profile.html` - /profile - Edycja profilu – zmiana nazwy użytkownika i adresu e-mail (używanego do alertów).

**Strony błędów**
- `404.html` - 404 - Niestandardowa strona błędu 404 z humorystycznym komunikatem.
- `500.html` - 500 - Strona błędu wewnętrznego serwera.
---

## 6. Bibliografia i źródła

### Wykorzystane biblioteki

- Flask (v3.0.3) – framework webowy  
- Flask-SQLAlchemy (v3.1.1) – obsługa bazy danych  
- Flask-Login (v0.6.3) – zarządzanie sesjami użytkowników  
- yfinance (v0.2.40) – pobieranie danych giełdowych z Yahoo Finance  
- APScheduler (v3.10.4) – planowanie zadań w tle (sprawdzanie cen co 1 minutę)  
- Flask-Mail – wysyłanie powiadomień e-mail

---

### Wykorzystanie AI

- **Model:** Gemini 3 Flash (Google)  
- **Data dostępu:** 20.04.2026

**Zakres pomocy:**
- optymalizacja struktury bazy danych w `models.py`  
- sformułowanie treści powiadomień e-mail w funkcji `check_price_alerts`  
- pomoc w tworzeniu 'szkieletu' widoków html zgodnych z pomysłem autora.
- stworzenie loga strony .png
