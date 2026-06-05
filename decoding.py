from reedsolo import RSCodec, ReedSolomonError

# ==========================================
# 1. KOD REEDA-SOLOMONA (RS)
# ==========================================
def decode_rs(encoded_data, ecc_symbols, erase_pos):
    """
    Dekoduje dane za pomocą Reeda-Solomona wiedząc, na których pozycjach wystąpiło wymazanie (erase_pos).
    Kod RS potrafi zdekodować N wymazań, jeśli mamy N symboli nadmiarowych.
    """
    rs = RSCodec(ecc_symbols)
    try:
        # Dekodowanie z uwzględnieniem wymazanych pozycji
        decoded_bytes, decoded_ecc, err_locations = rs.decode(
            bytearray(encoded_data), erase_pos=erase_pos
        )
        return list(decoded_bytes)
    except ReedSolomonError:
        return None # Nie udało się naprawić błędu (zbyt wiele utraconych pakietów)

# ==========================================
# 2. KOD RAPTOR
# ==========================================
def decode_raptor(encoded_symbols, N_precoded, N_original):
    """
    Dekodowanie kodu Raptor (Dekodowanie LT + Dekodowanie Pre-kodu).
    """
    # ETAP 1: Odzyskiwanie przy użyciu klasycznego dekodera LT
    decoded_precoded = [None] * N_precoded
    
    while any(symbol is None for symbol in decoded_precoded):
        progress = False
        for i, (encoded_symbol, indices) in enumerate(encoded_symbols):
            if len(indices) == 1:
                index = indices[0]
                if decoded_precoded[index] is None:
                    decoded_precoded[index] = encoded_symbol
                    progress = True
                    for j, (es, idxs) in enumerate(encoded_symbols):
                        if j != i and index in idxs:
                            encoded_symbols[j] = (es ^ encoded_symbol, [idx for idx in idxs if idx != index])
        if not progress:
            break # Utykamy - brak symboli stopnia 1

    # ETAP 2: Dekodowanie Pre-kodu (Naprawa z parzystości)
    # Jeśli dekoder LT "utknął", ale brakuje nam tylko JEDNEGO oryginalnego symbolu, 
    # a mamy odzyskany symbol parzystości z pre-kodu, możemy go uratować!
    missing_indices = [i for i, x in enumerate(decoded_precoded) if x is None]
    
    if len(missing_indices) == 1 and missing_indices[0] < N_original:
        # Brakuje tylko jednego bitu wiadomości. Używamy parzystości na końcu do odtworzenia go!
        # Parzystość to ostatni indeks: decoded_precoded[-1]
        parity = decoded_precoded[-1]
        if parity is not None:
            recovered_val = parity
            for i in range(N_precoded - 1):
                if i != missing_indices[0] and decoded_precoded[i] is not None:
                    recovered_val ^= decoded_precoded[i]
            decoded_precoded[missing_indices[0]] = recovered_val

    # Sprawdzamy czy mamy oryginalną wiadomość
    original_message = decoded_precoded[:N_original]
    if all(s is not None for s in original_message):
        return original_message
    return None