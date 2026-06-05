# main.py
import random
from time import perf_counter # Importujemy precyzyjny licznik

# Zakładam, że te importy masz już poprawne i pliki są w tym samym folderze
from text import text_to_binary, binary_to_text
from encoding import encode_rs, encode_raptor
from decoding import decode_rs, decode_raptor

def simulate_erasure_channel_rs(encoded_data, drop_probability):
    """Dla kodu RS zamienia utracone pakiety na zera i zapisuje ich indeksy (wymazywania)."""
    received = list(encoded_data)
    erased_indices = []
    for i in range(len(received)):
        if random.random() < drop_probability:
            received[i] = 0  
            erased_indices.append(i)
    return received, erased_indices

def simulate_erasure_channel_raptor(encoded_symbols, drop_probability):
    return [sym for sym in encoded_symbols if random.random() >= drop_probability]

def compare_codes(text, drop_rate=0.2):
    print(f"\n=== TESTOWANIE KODÓW (Prawdopodobieństwo utraty pakietu: {drop_rate*100}%) ===")
    binary_data = text_to_binary(text)
    N_original = len(binary_data)
    print(f"Dane źródłowe: '{text}' (Długość: {N_original} znaków)\n")

    # ==============================
    # TEST: KOD REEDA-SOLOMONA
    # ==============================
    print("--- 1. KOD REEDA-SOLOMONA ---")
    ecc_symbols = int(N_original * 1.0) 
    
    start_time = perf_counter() # Precyzyjny start
    rs_encoded = encode_rs(binary_data, ecc_symbols)
    rs_encode_time = perf_counter() - start_time # Obliczenie różnicy
    
    print(f"Wygenerowano {len(rs_encoded)} symboli (Danych: {N_original}, Parzystości: {ecc_symbols})")
    
    rs_received, rs_erased_pos = simulate_erasure_channel_rs(rs_encoded, drop_rate)
    print(f"Utracono {len(rs_erased_pos)} symboli z {len(rs_encoded)} w kanale przesyłowym.")
    
    start_time = perf_counter()
    rs_decoded = decode_rs(rs_received, ecc_symbols, rs_erased_pos)
    rs_decode_time = perf_counter() - start_time

    if rs_decoded:
        print(f"SUKCES! Odzyskany tekst: '{binary_to_text(rs_decoded)}'")
    else:
        print("PORAŻKA! Zbyt wiele błędów do naprawienia.")
        
    # Przeliczamy czas na milisekundy (x 1000) dla lepszej czytelności
    print(f"Czas kodowania: {rs_encode_time * 1000:.3f} ms | Czas dekodowania: {rs_decode_time * 1000:.3f} ms\n")

    # ==============================
    # TEST: KOD RAPTOR (Fontanna)
    # ==============================
    print("--- 2. KOD RAPTOR ---")
    overhead = 2.0 
    
    start_time = perf_counter()
    raptor_encoded, N_precoded = encode_raptor(binary_data, overhead_ratio=overhead)
    raptor_encode_time = perf_counter() - start_time
    
    print(f"Wygenerowano {len(raptor_encoded)} symboli (krople w fontannie)")
    
    raptor_received = simulate_erasure_channel_raptor(raptor_encoded, drop_rate)
    print(f"Do odbiorcy dotarło {len(raptor_received)} symboli z {len(raptor_encoded)}.")
    
    start_time = perf_counter()
    raptor_decoded = decode_raptor(raptor_received, N_precoded, N_original)
    raptor_decode_time = perf_counter() - start_time

    if raptor_decoded:
        print(f"SUKCES! Odzyskany tekst: '{binary_to_text(raptor_decoded)}'")
    else:
        print("PORAŻKA! Niewystarczająca liczba pakietów do otwarcia danych (dekoder LT utknął).")
        
    print(f"Czas kodowania: {raptor_encode_time * 1000:.3f} ms | Czas dekodowania: {raptor_decode_time * 1000:.3f} ms\n")


# Uruchomienie testów dla dłuższego tekstu
przykladowy_tekst = "To jest test kodow z wymazywaniem w architekturze projektowej. Sprawdzamy Reed-Solomona i Raptora!"
compare_codes(przykladowy_tekst, drop_rate=0.3)