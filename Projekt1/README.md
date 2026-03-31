# Prediction Market - Projekt I

**Przedmiot:** Programowanie w języku Python (2025/26)

**Autor:** Tymoteusz Herkowiak

## 1. Opis Projektu
Prediction Market to aplikacja internetowa pełniąca rolę giełdy predykcyjnej. Pozwala użytkownikom na obstawianie wyników przyszłych wydarzeń (np. politycznych, sportowych, pogodowych). System dynamicznie przelicza kursy i szanse procentowe w oparciu o wpłaconą przez użytkowników płynność finansową.

## 2. Autorzy i podział prac
* **Tymoteusz Herkowiak** - 100% wkładu w logikę biznesową, architekturę bazy danych, implementację widoków, testy automatyczne, autorskie komendy oraz integrację z API. Projekt realizowany samodzielnie.

## 3. Zrealizowane Wymagania Techniczne
Projekt spełnia wszystkie wytyczne ze specyfikacji:
* **Przynajmniej 5 podstron:** Strona główna (`/`), Rejestracja (`/register/`), Logowanie (`/login/`), Szczegóły wydarzenia (`/event/<id>/`), Panel użytkownika (`/dashboard/`).
* **Komunikacja z bazą (Pełny CRUD):** * **C**reate: Tworzenie nowych zakładów.
  * **R**ead: Wyświetlanie historii zakładów i wydarzeń.
  * **U**pdate: Doładowanie wirtualnego portfela użytkownika.
  * **D**elete: Anulowanie aktywnych zakładów i zwrot środków.
* **5 Modeli danych z relacjami:** `UserProfile`, `Category`, `Event`, `Option`, `Bet` (wykorzystano relacje `ForeignKey` oraz `OneToOneField`).
* **Formularze:** Obsługa rejestracji (`UserCreationForm`), logowania oraz formularze doładowania konta i obstawiania zakładów.
* **Obsługa błędów:** Autorskie szablony graficzne dla błędów `404.html` i `500.html`.
* **Autorskie polecenia manage.py:**
  1. `add_dummy_data` - zasila bazę przykładowymi danymi i kategoriami.
  2. `close_events` - zamyka wydarzenia, których czas dobiegł końca.
  3. `reset_market` - usuwa zakłady i przywraca salda użytkowników do 1000 euro.
* **Testy:** Napisano 8 testów jednostkowych (`bets/tests.py`) pokrywających najważniejsze funkcjonalności (walidacja salda, dynamiczne wyliczanie kursów, dostępność widoków).

### Wybrane 3 opcje dodatkowe:
1. **Stylizacja frameworkiem:** Wykorzystano framework **Bootstrap 5**.
2. **Konta użytkowników:** Zaimplementowano system rejestracji i logowania oraz weryfikację dostępu (`@login_required`). Użytkownik `admin` posiada uprawnienia superusera.
3. **Chat AI:** Zintegrowano "Asystenta AI" opartego na modelu Gemini, pomagającego w analizie ryzyka na giełdzie.

## 4. Wykorzystanie Sztucznej Inteligencji i Wkład Własny
Zgodnie z zasadami projektu, deklaruję następujący podział prac:

* **Oryginalny, wkład własny:** Architektura relacyjnej bazy danych (w tym system powiązań między kategoriami, wydarzeniami a zakładami), mechanizm walidacji uniemożliwiającej ujemne saldo (`full_clean` zaimplementowany w metodzie `save` w klasach `UserProfile` i `Bet`), autorskie komendy do zarządzania bazą danych (w katalogu `management/commands`) oraz ogólna struktura i logika plików szablonów.
* **Wsparcie modelu AI (Gemini):** Sztuczna inteligencja została wykorzystana jako wsparcie przy debugowaniu problemów z migracjami, do optymalizacji formularza `POST` asynchronicznego zapytania (Fetch API) dla wbudowanego czatu oraz do pomocy w wygenerowaniu stylizacji CSS do wyskakującego widżetu asystenta AI.
* **Gotowe fragmenty z samouczków (Dokumentacja Django):**
  Zaimplementowanie standardowych widoków logowania i wylogowania (`LoginView`, `LogoutView`) pochodzi wprost z oficjalnej dokumentacji frameworka.

## 5. Bibliografia i Źródła
* **Sztuczna Inteligencja:** Model **Gemini 2.5 Flash**, stworzony przez firmę **Google**. Data dostępu: 24.03.2026 - 31.03.2026.
* **Framework Backendowy:** **Django (wersja 6.0.3)**. Dokumentacja: https://docs.djangoproject.com/.
* **Framework Frontendowy:** **Bootstrap (wersja 5.3.0)**. Dokumentacja: https://getbootstrap.com/.
* **Biblioteka AI:** **google-generativeai**. Użyta do komunikacji z API Gemini.

## 6. Instrukcja uruchomienia lokalnego
1. Uruchom wirtualne środowisko.
2. Zainstaluj wymagane pakiety:
   `pip install django google-generativeai`
3. Przeprowadź migracje bazy danych:
   `python manage.py migrate`
4. Wgraj przykładowe dane na rynek:
   `python manage.py add_dummy_data`
5. Uruchom serwer testowy:
   `python manage.py runserver`

---

## 7. Szczegółowy Opis Funkcjonalności

### 7.1 Ogólne Założenia Aplikacji

**Prediction Market** to **giełda predykcyjna** działająca na zasadzie **rynku finansowego w miniaturze**. Użytkownicy mogą obstawiać wyniki przyszłych zdarzeń (polityka, sport, pogoda, itp.), a system dynamicznie przelicza kursy w oparciu o rzeczywiste decyzje graczy. Aplikacja symuluje rzeczywisty rynek, gdzie ceny (kursy) zmieniają się w zależności od rozkładu inwestycji.

**Kluczowe cechy:**
- Rejestracja i autoryzacja użytkowników
- System wirtualnego portfela (każdy użytkownik startuje z 1000 euro)
- Dynamiczne obliczanie kursów w czasie rzeczywistym
- Możliwość obstawiania przed konkretną datą
- Automatyczne rozliczanie zakładów i generowanie komunikatów
- Asystent AI do analizy ryzyka

---

### 7.2 Architektura Modelu Danych

#### **Model 1: UserProfile** (Profil Użytkownika)
```
UserProfile
├── user (OneToOneField) → User (Django)
├── balance (DecimalField) → Saldo w euro (domyślnie 1000.00)
└── Walidacja: Saldo nigdy nie może być ujemne
```

**Rola:** Każdy zarejestrowany użytkownik ma przywiązany profil zawierający jego wirtualne saldo. To saldo jest głównym zasobem w grze.

**Bezpieczeństwo:** Metoda `save()` automatycznie uruchamia `full_clean()`, co zapobiega zapisaniu profilu z ujemnym saldem.

---

#### **Model 2: Category** (Kategoria Wydarzenia)
```
Category
├── name (CharField) → Unikalna nazwa kategorii (max 100 znaków)
└── description (TextField) → Opis (opcjonalny)
```

**Przykłady kategorii:**
- Polityka (wybory, decyzje rządowe)
- Sport (wyniki meczów, igrzyska)
- Pogoda (opady, temperatury)
- Gospodarka (kursy walut, inflacja)

**Rola:** Organizacja wydarzeń w logiczne grupy dla lepszej nawigacji.

---

#### **Model 3: Event** (Wydarzenie do Obstawienia)
```
Event
├── title (CharField) → Nazwa wydarzenia (max 200 znaków)
├── category (ForeignKey) → Relacja do Category
├── description (TextField) → Szczegółowy opis
├── is_active (BooleanField) → Czy można jeszcze obstawiać? (domyślnie True)
├── created_at (DateTimeField) → Data utworzenia (auto)
├── end_date (DateTimeField) → Koniec okresu obstawiania
└── winning_option (ForeignKey) → [NOWE] Wskazana wygrana opcja po rozsądzeniu
```

**Rola:** Event to centralna jednostka - konkretne zdarzenie, które użytkownicy obstawiają.

**Lifecycle Eventu:**
1. **Utworzenie** - Administrator tworzy event z opisem, kategorią i datą końca
2. **Obstawianie (is_active=True)** - Użytkownicy mogą obstawiać do daty koniec
3. **Zamknięcie (is_active=False)** - Po upłynięciu czasu automatycznie zamyka się
4. **Rozliczenie** - Admin ustawia `winning_option` i komenda rozlicza wszystkie zakłady

**Przykład Eventu:**
```
Tytuł: "Jaki będzie wynik wyborów 2026?"
Kategoria: Polityka
Opis: Przewidź, który kandydat wygra wybory prezydenckie.
Koniec: 2026-06-30 17:00
Opcje: Kandydat A, Kandydat B, Kandydat C
```

---

#### **Model 4: Option** (Opcja Zakładu)
```
Option
├── event (ForeignKey) → Relacja do Event
├── name (CharField) → Nazwa opcji (np. "TAK", "NIE", "Kandydat A")
└── initial_liquidity (DecimalField) → Początkowa płynność wirtualna (domyślnie 100.00)
```

**Rola:** Option to możliwy wynik danego eventu. Event ma zawsze minimum 2 opcje.

**Dynamiczne Właściwości (Properties):**

1. **option_pool** - Całkowita płynność na daną opcję
   ```
   option_pool = initial_liquidity + suma_wszystkich_zakładów_na_tę_opcję
   
   Przykład:
   - Początkowa płynność: 100 €
   - Użytkownik A obstaw: 50 €
   - Użytkownik B obstaw: 30 €
   - option_pool = 100 + 50 + 30 = 180 €
   ```

2. **odds** - Kurs (szansa na zwrot)
   ```
   odds = całkowita_pula_wszystkich_opcji / option_pool
   
   Przykład (Event z 2 opcjami):
   - Pula "TAK": 200 € (100 initial + 100€ od uczestników )
   - Pula "NIE": 150 € (100 initial + 50€ od uczestników) 
   - Całkowita pula: 350 €
   - odds dla "TAK": 350 / 200 = 1.75
   - odds dla "NIE": 350 / 150 = 2.33
   ```
   
   **Interpretacja:** Jeśli obstawisz 100 € na "TAK" z kursem 1.75, możliwe wygrane to: 100 × 1.75 = 175 €

3. **percentage** - Procent rozkładu
   ```
   percentage = (option_pool / całkowita_pula) × 100
   
   Przykład:
   - "TAK": (200 / 350) × 100 = 57.1%
   - "NIE": (150 / 350) × 100 = 42.9%
   ```
   Wyświetla się na stronie eventu w progress barze, pokazując opinię rynku.

---

#### **Model 5: Bet** (Konkretny Zakład)
```
Bet
├── user (ForeignKey) → Użytkownik, który postawił zakład
├── option (ForeignKey) → Na którą opcję obstawiamy
├── amount (DecimalField) → Wysokość stawki (przynajmniej 0.01 €)
├── created_at (DateTimeField) → Kiedy został wystawiony (auto)
├── is_resolved (BooleanField) → Czy został już rozliczony? (domyślnie False)
└── is_won (BooleanField) → Czy wygrał? (domyślnie False)
```

**Rola:** Reprezentuje pojedynczy zakład gracza.

**Constraints i Walidacja:**
- Nie można obstawiać nieaktywnego eventu
- Nie można obstawiać po terminie końca eventu
- Użytkownik musi mieć wystarczające saldo

**Logika Obstawiania:**
```
1. Użytkownik wybiera event i opcję
2. Kwota jest natychmiast odejmowana z portfela (is_resolved=False, is_won=False)
3. Po upłynięciu czasu admin rozlicza event
4. Komenda sprawdza czy hazardista wygrał czy przegrał
5. Jeśli wygrana: kwota jest zwracana (is_resolved=True, is_won=True)
   Jeśli przegrana: kwota zostaje stracona (is_resolved=True, is_won=False)
```

---

#### **Model 6: Message** (Komunikaty dla Użytkowników)
```
Message
├── user (ForeignKey) → Adresat wiadomości
├── bet (ForeignKey) → Powiązany zakład (opcjonalny)
├── message_type (CharField) → Typ: 'win', 'loss', 'info'
├── title (CharField) → Nagłówek wiadomości
├── content (TextField) → Pełna treść z szczegółami
├── amount (DecimalField) → Kwota (do wypłaty, straty)
├── created_at (DateTimeField) → Data/czas (auto)
└── is_read (BooleanField) → Czy przeczytana? (domyślnie False)
```

**Rola:** System powiadomień dla użytkowników o wynikach rozliczonych zakładów.

**Typy wiadomości:**
- **'win'** - Zakład wygrał, zawiera informację o zysku
- **'loss'** - Zakład przegrał, zawiera informację o stracie
- **'info'**  - Inne informacje (np. systemy, oferty)

---

### 7.3 Strony i Widoki Użytkownika

#### **Strona 1: Strona Główna (`/`)**

**Funkcjonalność:**
- Wyświetla wszystkie aktywne eventy
- Klikając "ZOBACZ I OBSTAW" przechodzimy do strony szczegółów
- Asystent AI dostępny w rogu (ikona okrągła)

---

#### **Strona 2: Rejestracja (`/register/`)**
```
Formularz:
- Username (unikalny)
- Hasło
- Potwierdzenie hasła

Po rejestracji:
- Konto utworzone
- UserProfile automatycznie stworzony z saldem 1000.00 €
- Użytkownik zalogowany
- Przekierowanie na stronę główną
```

---

#### **Strona 3: Logowanie (`/login/`)**
```
Formularz:
- Username
- Hasło

Po zalogowaniu:
- Sesja ustalona
- Przekierowanie na stronę główną
```

---

#### **Strona 4: Szczegóły Eventu (`/event/<id>/`)**

**Mechanika:**
1. System pokazuje rozkład (progress bar) - pomaga ocenić opinię rynku
2. Kursy się zmieniają na żywo w zależności od przepływu pieniędzy
3. Po wysłaniu formularza:
   - Walidacja: czy user ma wystarczające saldo
   - Walidacja: czy event jeszcze aktywny
   - Walidacja: czy kwota min. 0.01 €
   - Utworzenie Bet (is_resolved=False)
   - Odjęcie kwoty z portfela
   - Przekierowanie na dashboard z potwierdzeniem

---

#### **Strona 5: Panel Użytkownika (`/dashboard/`)**

**Sekcja 1: Profil**

**Sekcja 2: Ostatnie Wiadomości**

**Sekcja 3: Aktywne Zakłady**

**Funkcjonalności:**
- Doładuj portfel dowolną kwotę
- Przeglądaj ostatnie wiadomości o rozliczeniach
- Widzisz wszystkie swoje zakłady
- Możliwość anulowania aktywnych zakładów (dostaje zwrot)
- Widok statusu każdego zakładu

---

### 7.4 Logika Dynamicznego Obliczania Kursów

**Problem:** Jak uniknąć sytuacji, gdzie kurs jest stały i nie reaguje na rynek?

**Rozwiązanie:** System **Liquidity Pool** (pula płynności)

**Algorytm:**
```
1. Każda opcja ma initial_liquidity (np. 100 €)
2. Gdy użytkownik obstaw X €, dodaje się to do puli tej opcji
3. Kurs = całkowita_pula_wszystkich_opcji / pula_tej_opcji

Przykład:
┌─ Event: "Czy będzie deszcz?"
├─ Opcja 1: "TAK"
│  ├─ initial_liquidity: 100 €
│  ├─ Zakłady graczy: 200 €
│  └─ option_pool: 300 €
│
├─ Opcja 2: "NIE"
│  ├─ initial_liquidity: 100 €
│  ├─ Zakłady graczy: 50 €
│  └─ option_pool: 150 €
│
└─ Całkowita pula: 450 €

Kursy:
- "TAK": 450 / 300 = 1.5
- "NIE": 450 / 150 = 3.0

### 7.5 System Rozliczania Zakładów i Komunikatów

#### **Faza 1: Zamknięcie Eventu**
```
Czasowo (auto na stronie):
- Event.end_date mija
- Event.is_active zmienia się na False (zapobiega nowym zakładom)
```

#### **Faza 2: Admin Rozsądza Wynik**
```
W panelu /admin/:
1. Admin przechodzi do Event
2. Ustawia pole "winning_option" na prawidłową opcję
3. Klika Save

Przykład:
Event: "Czy będzie deszcz?"
winning_option = "TAK" 
```

#### **Faza 3: Uruchomienie Komendy Rozliczającej**
```bash
python manage.py close_events
```

**Co się dzieje:**
```
1. Komenda szuka wszystkich nierozliczonych (is_resolved=False) 
   eventów z ustawioną winning_option

2. Dla każdego takiego eventu:
   - Pobiera wszystkie Bety
   - Dzieli je na wygrane i przegrane
   
3. Dla BET WYGRANEJ (option == winning_option):
   - is_resolved = True
   - is_won = True
   - Oblicza: winnings = amount × option.odds
   - Oblicza: total_payout = amount + winnings
   - Dodaje total_payout do UserProfile.balance
   - Tworzy Message z typem 'win'

4. Dla BET PRZEGRANY (option != winning_option):
   - is_resolved = True
   - is_won = False
   - Brak zmian w balansie (już odjęto przy obstawianiu)
   - Tworzy Message z typem 'loss'


### 7.6 Asystent AI (Gemini)

**Dostęp:** Okno w rogu każdej strony ("Asystent AI")

**Funkcjonalność:**
- Użytkownik zadaje pytanie w chacie
- Prompt wysłany do API Gemini
- AI odpowiada radami dotyczącymi analizy ryzyka, strategii obstawiania, itp.
- Odpowiedź wyświetla się w oknie chatu

**Przykładowe Pytania:**
```
"Jakie opcje mają najlepszą szansę?"
- AI analizuje kursy i podaje rekomendacje

"Czy powinienem obstawiać gdy kurs robi się niski?"
- AI wyjaśnia ryzyko vs. ewentualną nagrodę

"Ile średnio wygrywa się na takiej giełdzie?"
- AI dyskutuje o statystykach i strategiach
```

---

### 7.7 Autorskie Komendy Django

#### **Komenda 1: `add_dummy_data`**
```bash
python manage.py add_dummy_data
```
- Tworzy kategorie przykładowe
- Tworzy przyklad Events z Opcjami
- Przydatna do szybkiego testowania

#### **Komenda 2: `close_events`** 
```bash
python manage.py close_events
```
- Rozlicza wszystkie eventy z ustawioną winning_option
- Generuje Messages dla użytkowników
- Operacja krytyczna dla systemu

#### **Komenda 3: `reset_market`**
```bash
python manage.py reset_market
```
- Usuwa wszystkie Bety
- Resetuje UserProfile.balance do 1000.00 € dla wszystkich
- Przydatna do testów i resetowania gry

---

### 7.8 Bezpieczeństwo i Walidacja

**Zapory Bezpieczeństwa:**

1. **Niemożliwe ujemne saldo:**
   ```python
   class UserProfile:
       def clean(self):
           if self.balance < 0:
               raise ValidationError('Saldo nie może być ujemne.')
       def save(self, *args, **kwargs):
           self.full_clean()  # Zawsze waliduje
   ```

2. **Niemożliwe obstawienie bez wystarczającego salda:**
   ```python
   if profile.balance < amount:
       messages.error(request, f"Masz za mało środków")
       return redirect('event_detail')
   ```

3. **Niemożliwe obstawienie po terminie:**
   ```python
   if event.end_date <= timezone.now():
       raise ValidationError('Wydarzenie już się zakończyło')
   ```

4. **Niemożliwe dwukrotne rozliczenie:**
   ```python
   # Szukamy tylko is_resolved=False
   unresolved_bets = Bet.objects.filter(
       option__event=event,
       is_resolved=False
   )
   ```

6. **Login Required dla chronionego contentu:**
   ```python
   @login_required(login_url='login')
   def dashboard(request):
       ...
   ```

### 7.10 Technologia

**Frontend:**
- Bootstrap 5 - responsywny design
- HTML - struktura
- CSS3 - stylizacja
- JavaScript - interaktywność (chat AI)

**Backend:**
- Django 6.0.3 - framework
- SQLite - baza danych (domyślnie)
- Python 3 - logika biznesowa

**AI**
- Google Gemini 2.5 Flash - Asystent AI
- API - komunikacja z chatbotem

**Database Models:**
- Relacyjna struktura (ForeignKey, OneToOneField)
- Walidacja na poziomie modelu