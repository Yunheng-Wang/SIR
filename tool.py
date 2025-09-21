import secrets

def generate_id():
    return secrets.token_hex(8)



