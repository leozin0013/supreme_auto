# Utilitário para carregar variáveis de ambiente
import os
from typing import Optional

def load_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Carrega uma variável de ambiente, com fallback para valor padrão.
    
    Args:
        key: Nome da variável de ambiente
        default: Valor padrão se a variável não existir
        
    Returns:
        Valor da variável de ambiente ou padrão
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Variável de ambiente '{key}' não encontrada e nenhum valor padrão fornecido")
    return value

def load_bool_env_var(key: str, default: bool = False) -> bool:
    """
    Carrega uma variável de ambiente booleana.
    
    Args:
        key: Nome da variável de ambiente
        default: Valor padrão se a variável não existir
        
    Returns:
        Valor booleano da variável
    """
    value = os.environ.get(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

# Carrega arquivo .env se existir
def load_env_file():
    """Carrega variáveis do arquivo .env se existir"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Carrega as variáveis de ambiente
load_env_file()
