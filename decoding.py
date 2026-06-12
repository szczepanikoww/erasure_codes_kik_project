from reedsolo import RSCodec, ReedSolomonError

# Reed-Solomon
def decode_rs(encoded_data, ecc_symbols, erase_pos, N_original=None):
    block_size = 64
    if N_original is not None:
        ratio = ecc_symbols / N_original
    else:
        ratio = ecc_symbols / max(1, len(encoded_data) - ecc_symbols)
    ecc_per_block = max(1, int(block_size * ratio))
    encoded_block_size = block_size + ecc_per_block
    
    # jeśli oryginalna długość jest mała, dekodujemy jako jeden blok
    if len(encoded_data) <= encoded_block_size:
        rs = RSCodec(ecc_symbols)
        try:
            decoded_bytes, _, _ = rs.decode(bytearray(encoded_data), erase_pos=erase_pos)
            res = list(decoded_bytes)
            if N_original is not None:
                res = res[:N_original]
            return res
        except ReedSolomonError:
            return None
            
    rs = RSCodec(ecc_per_block)
    decoded_data = []
    erase_set = set(erase_pos)
    
    for block_idx in range(0, len(encoded_data), encoded_block_size):
        block = encoded_data[block_idx : block_idx + encoded_block_size]
        if len(block) < encoded_block_size:
            return None
            
        local_erase_pos = []
        for idx in range(encoded_block_size):
            global_idx = block_idx + idx
            if global_idx in erase_set:
                local_erase_pos.append(idx)
                
        try:
            decoded_block, _, _ = rs.decode(bytearray(block), erase_pos=local_erase_pos)
            decoded_data.extend(list(decoded_block))
        except ReedSolomonError:
            return None
            
    if N_original is not None:
        decoded_data = decoded_data[:N_original]
    return decoded_data

# Raptor (pre-kod + LT)
def decode_raptor(encoded_symbols, N_precoded, N_original):
    # 1. Dekodowanie LT przy użyciu zoptymalizowanego grafu i kolejki (złożoność O(K))
    decoded_precoded = [None] * N_precoded
    
    output_values = [sym for sym, _ in encoded_symbols]
    output_indices = [set(idxs) for _, idxs in encoded_symbols]
    
    source_to_outputs = [[] for _ in range(N_precoded)]
    for out_idx, idxs in enumerate(output_indices):
        for src_idx in idxs:
            source_to_outputs[src_idx].append(out_idx)
            
    degree_one_queue = [out_idx for out_idx, idxs in enumerate(output_indices) if len(idxs) == 1]
    
    num_resolved = 0
    while degree_one_queue:
        out_idx = degree_one_queue.pop(0)
        
        if len(output_indices[out_idx]) != 1:
            continue
            
        src_idx = next(iter(output_indices[out_idx]))
        
        if decoded_precoded[src_idx] is None:
            val = output_values[out_idx]
            decoded_precoded[src_idx] = val
            num_resolved += 1
            if num_resolved == N_precoded:
                break
                
            for neighbor_out_idx in source_to_outputs[src_idx]:
                if neighbor_out_idx == out_idx:
                    continue
                if src_idx in output_indices[neighbor_out_idx]:
                    output_values[neighbor_out_idx] ^= val
                    output_indices[neighbor_out_idx].remove(src_idx)
                    
                    if len(output_indices[neighbor_out_idx]) == 1:
                        degree_one_queue.append(neighbor_out_idx)

    # 2. Dekodowanie pre-kodu (odzyskiwanie z parzystości)
    missing_indices = [i for i, x in enumerate(decoded_precoded) if x is None]
    
    # jeśli brakuje tylko 1 oryginalnego symbolu, a mamy parzystość z pre-kodu
    if len(missing_indices) == 1 and missing_indices[0] < N_original:
        parity = decoded_precoded[-1]
        if parity is not None:
            recovered_val = parity
            for i in range(N_precoded - 1):
                if i != missing_indices[0] and decoded_precoded[i] is not None:
                    recovered_val ^= decoded_precoded[i]
            decoded_precoded[missing_indices[0]] = recovered_val

    # zwracamy tylko oryginalną część, o ile cała jest odzyskana
    original_message = decoded_precoded[:N_original]
    if all(s is not None for s in original_message):
        return original_message
    return None