# main.py
import random
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter

# moduły projektu
from text import text_to_binary, binary_to_text
from encoding import encode_rs, encode_raptor
from decoding import decode_rs, decode_raptor

def simulate_erasure_channel_rs(encoded_data, drop_probability):
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
    binary_data = text_to_binary(text)
    N_original = len(binary_data)
    print(f"Dane źródłowe: '{text}'")
    print(f"Długość wiadomości: {N_original} bajtów\n")

    # Reed-Solomon
    ecc_symbols = int(N_original * 1.0)
    
    start_time = perf_counter()
    rs_encoded = encode_rs(binary_data, ecc_symbols)
    rs_encode_time = (perf_counter() - start_time) * 1000
    
    rs_received, rs_erased_pos = simulate_erasure_channel_rs(rs_encoded, drop_rate)
    rs_lost_count = len(rs_erased_pos)
    
    start_time = perf_counter()
    rs_decoded = decode_rs(rs_received, ecc_symbols, rs_erased_pos, N_original)
    rs_decode_time = (perf_counter() - start_time) * 1000

    # Raptor
    overhead = 2.0
    
    start_time = perf_counter()
    raptor_encoded, N_precoded = encode_raptor(binary_data, overhead_ratio=overhead)
    raptor_encode_time = (perf_counter() - start_time) * 1000
    
    raptor_received = simulate_erasure_channel_raptor(raptor_encoded, drop_rate)
    raptor_lost_count = len(raptor_encoded) - len(raptor_received)
    
    start_time = perf_counter()
    raptor_decoded = decode_raptor(raptor_received, N_precoded, N_original)
    raptor_decode_time = (perf_counter() - start_time) * 1000

    # tabela wynikowa    
    print(f"| {'Cecha':<20} | {'Reed-Solomon':<15} | {'Raptor (LT)':<15} |")
    print(f"|{'-'*22}|{'-'*17}|{'-'*17}|")
    

    rs_status = "SUKCES" if rs_decoded else "PORAŻKA"
    raptor_status = "SUKCES" if raptor_decoded else "PORAŻKA"
    
    print(f"| {'Odzyskanie danych':<20} | {rs_status:<15} | {raptor_status:<15} |")
    print(f"| {'Czas kodowania':<20} | {rs_encode_time:>10.3f} ms | {raptor_encode_time:>10.3f} ms |")
    print(f"| {'Czas dekodowania':<20} | {rs_decode_time:>10.3f} ms | {raptor_decode_time:>10.3f} ms |")
    print(f"| {'Wysłane pakiety':<20} | {len(rs_encoded):>11} pkt | {len(raptor_encoded):>11} pkt |")
    print(f"| {'Utracone w drodze':<20} | {rs_lost_count:>11} pkt | {raptor_lost_count:>11} pkt |")
    print(f"{'='*60}\n")


def run_performance_simulation(messages, drop_rate=0.1):
    lengths = []
    rs_enc_times, rs_dec_times = [], []
    raptor_enc_times, raptor_dec_times = [], []

    for msg in messages:
        binary_data = text_to_binary(msg)
        N = len(binary_data)
        lengths.append(N)
        
        ecc_symbols = int(N * 1.0)
        
        start = perf_counter()
        rs_encoded = encode_rs(binary_data, ecc_symbols)
        rs_enc_times.append((perf_counter() - start) * 1000)
        
        rs_received, rs_erased = simulate_erasure_channel_rs(rs_encoded, drop_rate)
        start_time = perf_counter()
        decode_rs(rs_received, ecc_symbols, rs_erased, N)
        rs_dec_times.append((perf_counter() - start_time) * 1000)

        overhead = 2.0
        
        start = perf_counter()
        raptor_encoded, N_precoded = encode_raptor(binary_data, overhead_ratio=overhead)
        raptor_enc_times.append((perf_counter() - start) * 1000)
        
        raptor_received = simulate_erasure_channel_raptor(raptor_encoded, drop_rate)
        start = perf_counter()
        decode_raptor(raptor_received, N_precoded, N)
        raptor_dec_times.append((perf_counter() - start) * 1000)

    return lengths, rs_enc_times, rs_dec_times, raptor_enc_times, raptor_dec_times


def run_robustness_simulation(text, drop_rates, trials_per_rate=20):
    binary_data = text_to_binary(text)
    N = len(binary_data)
    ecc_symbols = int(N * 1.0) 
    overhead = 2.0             

    rs_success_rates = []
    raptor_success_rates = []

    for rate in drop_rates:
        rs_successes = 0
        raptor_successes = 0
        
        for _ in range(trials_per_rate):
            rs_encoded = encode_rs(binary_data, ecc_symbols)
            rs_received, rs_erased = simulate_erasure_channel_rs(rs_encoded, rate)
            if decode_rs(rs_received, ecc_symbols, rs_erased, N) is not None:
                rs_successes += 1
                
            raptor_encoded, N_precoded = encode_raptor(binary_data, overhead)
            raptor_received = simulate_erasure_channel_raptor(raptor_encoded, rate)
            if decode_raptor(raptor_received, N_precoded, N) is not None:
                raptor_successes += 1
                
        rs_success_rates.append((rs_successes / trials_per_rate) * 100)
        raptor_success_rates.append((raptor_successes / trials_per_rate) * 100)

    return rs_success_rates, raptor_success_rates


def generate_charts():
    test_messages = [
        "A" * 60,
        "B" * 250,
        "C" * 1000,
        "D" * 3000
    ]

    lengths, rs_enc, rs_dec, rap_enc, rap_dec = run_performance_simulation(test_messages)
    drop_rates = np.linspace(0.0, 0.9, 20) 
    rs_succ, rap_succ = run_robustness_simulation(
        "Tekst referencyjny do testowania gubienia danych w kanale transmisyjnym o zmiennych parametrach. "
        "Im dluzszy tekst, tym gorzej poradzi sobie tradycyjny kod blokowy typu Reed-Solomon w wersji chunked, "
        "poniewaz wystarczy awaria jednego bloku, aby cala transmisja pliku zakonczyla sie niepowodzeniem. "
        "Kody fontannowe (w tym Raptor) dzieki globalnej dystrybucji i braku podzialu na bloki radza sobie doskonale!", 
        drop_rates
    )

    plt.style.use('seaborn-v0_8-darkgrid')
    fig = plt.figure(figsize=(16, 10))
    fig.canvas.manager.set_window_title('Analiza Kodów z Wymazywaniem')

    ax1 = plt.subplot(2, 2, 1)
    bar_width = 0.35
    index = np.arange(len(lengths))
    ax1.bar(index, rs_enc, bar_width, label='Reed-Solomon', color='#2980b9', alpha=0.8)
    ax1.bar(index + bar_width, rap_enc, bar_width, label='Raptor', color='#e74c3c', alpha=0.8)
    ax1.set_xlabel('Rozmiar wiadomości (bajty)')
    ax1.set_ylabel('Czas (ms)')
    ax1.set_title('Czas KODOWANIA vs Rozmiar Wiadomości', fontsize=12, fontweight='bold')
    ax1.set_xticks(index + bar_width / 2)
    ax1.set_xticklabels(lengths)
    ax1.legend()

    ax2 = plt.subplot(2, 2, 2)
    ax2.bar(index, rs_dec, bar_width, label='Reed-Solomon', color='#27ae60', alpha=0.8)
    ax2.bar(index + bar_width, rap_dec, bar_width, label='Raptor', color='#f39c12', alpha=0.8)
    ax2.set_xlabel('Rozmiar wiadomości (bajty)')
    ax2.set_ylabel('Czas (ms)')
    ax2.set_title('Czas DEKODOWANIA vs Rozmiar Wiadomości', fontsize=12, fontweight='bold')
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(lengths)
    ax2.legend()

    ax3 = plt.subplot(2, 1, 2)
    ax3.plot(drop_rates * 100, rs_succ, marker='o', linewidth=3, label='Reed-Solomon', color='#8e44ad')
    ax3.plot(drop_rates * 100, rap_succ, marker='s', linewidth=3, linestyle='--', label='Raptor (Fontanna)', color='#d35400')
    ax3.axvline(x=50, color='red', linestyle=':', linewidth=2, label='Teoretyczny limit RS (50% strat)')
    ax3.set_xlabel('Utrata pakietów w sieci (%)', fontsize=11)
    ax3.set_ylabel('Szansa na poprawne odzyskanie pliku (%)', fontsize=11)
    ax3.set_title('Niezawodność algorytmów (Odporność na degradację kanału)', fontsize=14, fontweight='bold')
    ax3.set_ylim([-5, 105])
    ax3.set_xlim([0, 90])
    ax3.legend(loc='lower left', fontsize=11)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    maly_tekst = "Krotka wiadomosc"
    compare_codes(maly_tekst, drop_rate=0.30)

    duzy_tekst = (
        "Dluga wieloblokowa wiadomosc testowa sluzaca do wykazania roznic "
        "w skalowalnosci i odpornosci obu algorytmow. "
        "Dla duzych wiadomosci klasyczny kod Reed-Solomona musi zostac podzielony "
        "na wiele malych blokow (chunking), co drastycznie zwieksza jego podatnosc "
        "na losowe straty w kanale transmisyjnym - wystarczy utrata zbyt wielu symboli "
        "w jednym bloku, aby cale dekodowanie pliku zakonczylo sie niepowodzeniem. "
        "Z kolei kod Raptor koduje cala wiadomosc globalnie jako jeden blok. "
        "Sprawia to, ze straty rozkladaja sie rownomiernie i prawdopodobienstwo "
        "sukcesu dekodowania jest o wiele wyzsze. Ponadto zlozonosc obliczeniowa "
        "kodu Raptor jest liniowa O(K), podczas gdy dla kodu Reed-Solomona rosnie kwadratowo, "
        "co widac w czasach wykonywania operacji dla coraz wiekszych rozmiarow danych. "
        "Dzieki temu Raptor jest nieporownywalnie szybszy dla duzych plikow."
    )
    compare_codes(duzy_tekst, drop_rate=0.30)

    generate_charts()
