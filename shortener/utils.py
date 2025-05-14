import hashlib

def generate_short_code(original_url, length):
    hash_object = hashlib.sha256(original_url.encode())
    short_hash = hash_object.hexdigest()[:length]
    return short_hash
