import random
import numpy as np
from reedsolo import RSCodec

# Reed-Solomon
def encode_rs(binary_data, ecc_symbols):
    block_size = 64
    if len(binary_data) <= block_size:
        rs = RSCodec(ecc_symbols)
        return list(rs.encode(bytearray(binary_data)))
        
    ratio = ecc_symbols / len(binary_data)
    ecc_per_block = max(1, int(block_size * ratio))
    
    rs = RSCodec(ecc_per_block)
    encoded_data = []
    for i in range(0, len(binary_data), block_size):
        block = binary_data[i:i+block_size]
        if len(block) < block_size:
            block = block + [0] * (block_size - len(block))
        encoded_data.extend(list(rs.encode(bytearray(block))))
    return encoded_data

# Raptor (Pre-koder + LT)
def robust_soliton_distribution(K, c=0.2, delta=0.8):
    # rozkład Robust Soliton dla kodów LT
    if K == 1:
        return [1.0]
    rho = [0.0] * K
    rho[0] = 1.0 / K
    for i in range(2, K + 1):
        rho[i - 1] = 1.0 / (i * (i - 1))
        
    S = c * np.log(K / delta) * np.sqrt(K)
    if S < 1e-9:
        S = 0.1
    tau = [0.0] * K
    pivot = int(np.floor(K / S))
    pivot = max(1, min(pivot, K))
    for i in range(1, pivot):
        tau[i - 1] = S / (K * i)
    if pivot - 1 < K:
        tau[pivot - 1] = (S / K) * np.log(S / delta) if S > delta else 0.0
        
    total = [rho[i] + tau[i] for i in range(K)]
    total_sum = sum(total)
    if total_sum <= 0.0:
        return rho
    return [x / total_sum for x in total]

def generate_raptor_symbol(data, d):
    # generowanie jednego symbolu LT (XOR) o stopniu d
    N = len(data)
    chosen_indices = random.sample(range(N), int(d))
    encoded_symbol = 0
    for index in chosen_indices:
        encoded_symbol ^= data[index]
    return encoded_symbol, chosen_indices

def encode_raptor(binary_data, overhead_ratio=1.5):
    # 1. Pre-kodowanie (prosty XOR wszystkich bajtów)
    parity_symbol = 0
    for b in binary_data:
        parity_symbol ^= b
    
    precoded_data = binary_data + [parity_symbol]
    N_precoded = len(precoded_data)
    
    # 2. Generowanie symboli LT (fontanna)
    p = robust_soliton_distribution(N_precoded)
    num_encoded_symbols = int(N_precoded * overhead_ratio)
    
    # pre-generowanie stopni wszystkich symboli (ogromne przyspieszenie w numpy)
    degrees = np.random.choice(range(1, N_precoded + 1), size=num_encoded_symbols, p=p)
    
    encoded_symbols = []
    for d in degrees:
        symbol, indices = generate_raptor_symbol(precoded_data, d)
        encoded_symbols.append((symbol, indices))
        
    return encoded_symbols, N_precoded