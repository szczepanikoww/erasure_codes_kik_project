# Projekt: Porównanie Kodów z Wymazywaniem (Erasure Codes)

Ten projekt stanowi implementację i środowisko testowe do analizy dwóch różnych podejść z dziedziny kodowania kanałowego odpornego na straty danych (Erasure Coding).

## Opis Implementowanych Kodów

### 1. Kody Reeda-Solomona (RS)
Klasyczny kod blokowy, powszechnie stosowany w płytach CD, kodach QR i komunikacji kosmicznej. 
* **Jak to działa?** Używa potężnej algebry (Ciała Galois), aby dołożyć ustaloną na sztywno liczbę znaków parzystości.
* **Cechy:** Jest w 100% deterministyczny. Jeśli dodasz $M$ znaków nadmiarowych, możesz odzyskać dane niezależnie od tego, których $M$ znaków uległo wymazaniu. Jednak jest kosztowny obliczeniowo przy wielkich plikach.

### 2. Kody Raptor (Rozszerzony kod fontannowy LT)
Wykorzystywane w streamingu wideo (3GPP) i systemach satelitarnych.
* **Jak to działa?** Działa jak ciągła fontanna danych (może wygenerować z pliku nieskończoną ilość pakietów). Ulepsza on kod LT o fazę **pre-kodowania** (w tym projekcie symulowaną przez dodanie sumy kontrolnej XOR).
* **Cechy:** Działa w oparciu o operację logiczną XOR na grafach (rozkład Solitona), co sprawia, że jest niezwykle szybki. Należy odebrać minimalnie więcej pakietów niż liczyła oryginalna wiadomość, aby z sukcesem poskładać układankę. Pre-kod zapobiega problemowi "utykania" końcowych bitów w kodach LT.

## Wymagania i uruchomienie
Wymagane pakiety: `pip install numpy reedsolo`
Aby uruchomić testy i zobaczyć porównanie czasowe algorytmów:
`python main.py`