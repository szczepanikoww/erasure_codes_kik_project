def text_to_binary(text):
    return [ord(char) for char in text]

def binary_to_text(binary_data):
    return ''.join(chr(num) for num in binary_data)