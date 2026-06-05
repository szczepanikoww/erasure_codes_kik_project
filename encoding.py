import random
import numpy as np
from reedsolo import RSCodec

# ==========================================
# 1. KOD REEDA-SOLOMONA (RS)
# ==========================================
def encode_rs(binary_data, ecc_symbols):
    """
    Kodowanie za pomocą algorytmu Reeda-Solomona.
    Dodaje na końcu wiadomości `ecc_symbols` znaków nadmiarowych.
    """
    rs = RSCodec(ecc_symbols)
    # rs.encode przyjmuje bytearray i zwraca bytearray (dane + nadmiarowość)
    encoded_bytes = rs.encode(bytearray(binary_data))
    return list(encoded_bytes)

# ==========================================
# 2. KOD RAPTOR (Fontannowy = Pre-koder + LT)
# ==========================================
def soliton_distribution(N):
    """Rozkład Solitona dla części LT kodu Raptor."""
    p = [0] * N
    p[0] = 1 / N
    for i in range(2, N + 1):
        p[i - 1] = 1 / (i * (i - 1))
    total = sum(p)
    return [x / total for x in p]

def generate_raptor_symbol(data, p):
    """Generuje pojedynczy symbol fontannowy (XOR)"""
    N = len(data)
    d = np.random.choice(range(1, N + 1), p=p)
    chosen_indices = random.sample(range(N), d)
    encoded_symbol = 0
    for index in chosen_indices:
        encoded_symbol ^= data[index]
    return encoded_symbol, chosen_indices

def encode_raptor(binary_data, overhead_ratio=1.5):
    """
    KOD RAPTOR: Składa się z 2 etapów.
    Etap 1: Pre-kodowanie (np. dodanie globalnej parzystości XOR).
            W komercyjnych kodach Raptor używa się skomplikowanych kodów LDPC.
            Tutaj, dla celu edukacyjnego, tworzymy prosty blok parzystości z całej wiadomości.
    Etap 2: Standardowe kodowanie LT na pre-kodowanych danych.
    """
    # ETAP 1: Pre-kodowanie (Dodajemy 1 dodatkowy symbol będący wynikiem XOR wszystkich danych)
    parity_symbol = 0
    for b in binary_data:
        parity_symbol ^= b
    
    precoded_data = binary_data + [parity_symbol]
    N_precoded = len(precoded_data)
    
    # ETAP 2: Generowanie fontanny (Kody LT)
    p = soliton_distribution(N_precoded)
    num_encoded_symbols = int(N_precoded * overhead_ratio)
    
    encoded_symbols = []
    for _ in range(num_encoded_symbols):
        symbol, indices = generate_raptor_symbol(precoded_data, p)
        encoded_symbols.append((symbol, indices))
        
    return encoded_symbols, N_precoded