# text.py
def text_to_binary(text):
    """
    Konwertuje tekst na listę wartości liczbowych (bajtów).
    Przykład: "ABC" -> [65, 66, 67]
    """
    return [ord(char) for char in text]

def binary_to_text(binary_data):
    """
    Konwertuje listę wartości liczbowych (bajtów) z powrotem na tekst.
    Przykład: [65, 66, 67] -> "ABC"
    """
    return ''.join(chr(num) for num in binary_data)