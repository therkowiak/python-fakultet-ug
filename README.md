# Prediction Market - Projekt I

---

## 1. Opis Projektu
Aplikacja to giełda predykcyjna umożliwiająca obstawianie wyników wydarzeń. System wykorzystuje algorytm kursów dynamicznych oraz wbudowanego asystenta AI.

## 2. Zrealizowane Wymagania (Checklista)
* **5+ Podstron:** Home, Event Detail, Dashboard, Login, Register.
* **5+ Modeli:** `User`, `UserProfile`, `Event`, `Option`, `Bet`.
* **Pełny CRUD:** Tworzenie zakładów, Odczyt historii, Aktualizacja salda, Usuwanie (anulowanie) zakładów.
* **3 Autorskie komendy:** `reset_market`, `add_dummy_data`, `close_events`.
* **8 Testów:** Sprawdzających logikę zakładów i dostępność widoków.
* **Obsługa błędów:** Własne szablony 404.html i 500.html.

## 3. Wykorzystane technologie
* **Framework:** Django 6.x
* **Frontend:** Bootstrap 5
* **AI Tool:** Gemini 2.5 Flash (Google).

## 4. Instrukcja
1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py runserver`
