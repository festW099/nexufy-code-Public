def xor_encrypt(text, key):
    return bytes([text[i] ^ key[i % len(key)] for i in range(len(text))])

text = b"Secret Message"
key = b"KEY"
encrypted = xor_encrypt(text, key)
decrypted = xor_encrypt(encrypted, key)