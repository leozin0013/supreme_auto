# Gera chave secreta TOTP

import secrets
import base64

def gerar_segredo_totp():
    """Gera uma chave secreta TOTP de 160 bits"""
    
    # Gera 20 bytes aleatórios (160 bits)
    segredo_bytes = secrets.token_bytes(20)
    
    # Converte para Base32
    segredo_base32 = base64.b32encode(segredo_bytes).decode('ascii')
    
    return segredo_base32

if __name__ == "__main__":
    segredo = gerar_segredo_totp()
    print(segredo)
