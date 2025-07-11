#gerador de codigo de autenticação TOTP em tempo real
#pode ser usado no iOS ou no Android através do app a-Shell ou similares

import pyotp
import time
import sys

def mostrar_totp_tempo_real():
    """Mostra código TOTP atualizando na mesma linha"""
    
    # Chave do .env
    chave = "SUA_CHAVE_SEGREDO_TOTP_AQUI"
    totp = pyotp.TOTP(chave)
    
    print("🔐 TOTP Supreme Auto - Tempo Real")
    print("Pressione Ctrl+C para sair\n")
    
    try:
        while True:
            # Pega código atual
            codigo = totp.now()
            
            # Calcula tempo restante
            timestamp = int(time.time())
            segundos_restantes = 30 - (timestamp % 30)
            
            # Barra de progresso simples
            progresso = "█" * (segundos_restantes // 2) + "░" * (15 - segundos_restantes // 2)
            
            # Atualiza na mesma linha
            linha = f"\rCódigo: {codigo} | Restam: {segundos_restantes:2d}s [{progresso}]"
            print(linha, end="", flush=True)
            
            # Aguarda 1 segundo
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Saindo...")

if __name__ == "__main__":
    mostrar_totp_tempo_real()
