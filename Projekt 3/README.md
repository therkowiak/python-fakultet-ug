# Projekt 3: Detekcja dodatków aromatyzujących (Mentol) na podstawie bazowego profilu chemicznego papierosów

## Opis i cel projektu
Celem projektu było rozwiązanie problemu binarnej klasyfikacji mającej na celu rozpoznanie, czy dany papieros jest mentolowy, wyłącznie na podstawie jego profilu chemicznego. Głównym zadaniem badawczym było sprawdzenie, czy dodatek aromatu mentolowego istotnie wpływa na zmianę proporcji bazowych substancji toksycznych.

Do analizy wykorzystano zbiór danych zawierający parametry papierosów (m.in. tlenek węgla, substancje smoliste, nikotynę), pochodzący z badań amerykańskiego Federal Trade Comission, analizujący papierosy sprzedawane w latach 1998-2000.

## Struktura projektu

Katalog projektu został odchudzony ze zbędnych plików i ma następującą, logiczną strukturę:

* `main.py` – główny skrypt aplikacji zawierający kompletną logikę: od wczytania danych i pre-processingu, przez pętlę strojenia hiperparametrów k-NN, aż po trenowanie, ewaluację modeli i generowanie wykresów.
* `cigs.csv` – surowy zbiór danych (dane FTC) zawierający parametry papierosów.
* `requirements.txt` – spis bibliotek niezbędnych do poprawnego uruchomienia środowiska i skryptu.
* `README.md` – pełna dokumentacja projektu wraz z wnioskami badawczymi (ten plik).
* `*.png` – pliki graficzne z wykresami generowane automatycznie przy każdym uruchomieniu programu:
    * `krzywa_mentol_[Nazwa_Modelu].png` – wykresy krzywych uczenia się.
    * `macierz_mentol_[Nazwa_Modelu].png` – graficzne macierze błędów.
    * `podsumowanie_mentol.png` – zbiorczy wykres słupkowy porównujący dokładność wszystkich 5 algorytmów.

## Instrukcja instalacji i uruchomienia
Aby odtworzyć eksperyment w środowisku lokalnym, wykonaj poniższe kroki w terminalu systemowym:

### 1. Klonowanie projektu
Upewnij się, że w jednym głównym folderze znajdują się pliki: `main.py`, laboratoryjna baza danych `cigs.csv` oraz `requirements.txt`.

### 2. Instalacja zależności środowiskowych
Otwórz terminal we wspomnianym folderze i zainstaluj niezbędne biblioteki za pomocą menedżera pakietów `pip`:
```bash
pip install -r requirements.txt
```
### 3. Uruchomienie obliczeń
Aby rozpocząć proces pre-processingu, automatyczne strojenie hiperparametru k oraz trenowanie wszystkich 5 modeli ML, uruchom skrypt główny:
```bash
python main.py
```

## Technologie i pre-processing
Projekt został napisany w języku Python. Wykorzystane biblioteki: `pandas`, `numpy`, `scikit-learn`, `matplotlib`.

**Pre-processing danych obejmował:**
1. Usunięcie brakujących danych (obsługa wartości `NaN` w kolumnie *menthol*).
2. Konwersję zmiennej kategorycznej do postaci numerycznej (zamiana "yes"/"no" na wartości 1/0).
3. Standaryzację zmiennych chemicznych (CO, nic, tar) przy użyciu `StandardScaler`, co jest kluczowe dla prawidłowego działania algorytmów opartych na odległości oraz sieci neuronowych.


## Wykorzystane algorytmy ML
W projekcie wytrenowano i porównano 5 drastycznie różniących się od siebie modeli uczenia maszynowego:
1. **Naiwny Bayes** – model czysto probabilistyczny.
2. **K-Najbliższych Sąsiadów (KNeighborsClassifier)** – model oparty na metryce odległości w przestrzeni cech. Zastosowano tu eksperyment ze **strojeniem hiperparametrów** (automatyczna pętla przetestowała wartości *k* od 3 do 15, wybierając optymalne *k*).
3. **Drzewo Decyzyjne (DecisionTreeClassifier)** – model oparty na logicznych regułach podziału (zastosowano eksperymentalną optymalizację maksymalnej głębokości drzewa).
4. **Las Losowy (RandomForestClassifier)** – model zespołowy bazujący na wielu drzewach. Zoptymalizowano liczbę estymatorów (`n_estimators`), dziedzicząc jednocześnie optymalną głębokość wyznaczoną w eksperymencie z Drzewem Decyzyjnym.
5. **Sieć Neuronowa (MLPClassifier)** – Architektura została celowo zredukowana do 10 neuronów w ukrytej warstwie i wsparta regularyzacją (`alpha=0.01`, solver `lbfgs`), aby ułatwić optymalizację i ograniczyć ostrzeżenia dotyczące nadmiernej ilości iteracji w terminalu.

## Metryki i wnioski badawcze
Modele zostały poddane ewaluacji na podstawie dokładności (Test Accuracy), straty logarytmicznej (Log Loss), macierzy błędów (Confusion Matrix) oraz wygenerowanych krzywych uczenia (Learning Curves).

## Metryki i wnioski badawcze
Modele zostały poddane ewaluacji wielowymiarowej na podstawie dokładności (Test Accuracy), straty logarytmicznej (Log Loss), macierzy błędów (Confusion Matrix) oraz analizy graficznej krzywych uczenia się. 

Zaimplementowany algorytm podsumowujący klasyfikuje modele na podstawie kompromisu (trade-off) pomiędzy najwyższą ogólną dokładnością a najniższą stratą (Log Loss).

**Główne wnioski analityczne:**
* **Dokładność (Accuracy) vs Pewność (Log Loss):** Choć algorytmy oparte na regułach, takie jak Drzewo Decyzyjne, wykazały najwyższą dokładność nominalną (~79.8%), cechowały się jednocześnie skrajnie wysokim wskaźnikiem straty (Log Loss > 2.2). Wykresy krzywych uczenia potwierdziły, że wynikało to ze zjawiska przeuczenia (overfittingu) modelu treningowego.
* **Najlepsze modele badawcze:** Zwycięzcami pod kątem stabilności są Las Losowy (Accuracy ~79.5%, Log Loss ~0.47) oraz Sieć Neuronowa (Accuracy ~78.4%, Log Loss ~0.45). Udało im się połączyć wysoką skuteczność ze zdrowym rozsądkiem – kiedy modele nie były pewne odpowiedzi, odpowiednio to sygnalizowały (niski Log Loss), zamiast podejmować skrajnie ryzykowne decyzje.
* **Rozwiązanie problemu badawczego:** Żaden z 5 zaawansowanych algorytmów nie był w stanie przekroczyć "szklanego sufitu" 80% dokładności na danych testowych. Modele masowo generowały błędy zjawiska *False Positive* w analizowanych macierzach. Udowadnia to ostatecznie tezę badawczą: dodatek aromatu mentolowego jest chemicznie "niewidzialny" dla profilu bazowego (CO, substancje smoliste, nikotyna). Profil chemiczno-fizyczny wyrobów mentolowych w sposób nieliniowy i głęboki przenika się z wyrobami standardowymi.

##  Oświadczenie o wykorzystaniu AI oraz źródłach
* **Kod autorski oraz wkład własny:** Wybór zbioru danych, określenie problemu badawczego, wprowadzenie automatycznego strojenia hiperparametrów (pętla optymalizująca *k* w k-NN), interwencja w parametry sieci neuronowej (usunięcie problemu braku zbieżności poprzez zmianę solvera i regularyzację), weryfikacja poprawności oraz ostateczna analiza i interpretacja krzywych uczenia i macierzy błędów.
* **Wsparcie AI:** Część szkieletu kodu w pliku `main.py` (głównie funkcje do generowania i stylizowania wykresów z użyciem *matplotlib*) została wygenerowana przy asyście sztucznej inteligencji.
* **Narzędzie AI:** Gemini 1.5 Pro (Google), Data dostępu: 26.05.2026.
* **Źródło zbioru danych:** FTC Cigarettes by Darrin Speefle: https://www.kaggle.com/datasets/speegled/ftc-cigarettes?resource=download&select=cigs.csv