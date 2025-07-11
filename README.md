# Supreme Auto - Sistema de Gestão

Sistema de gestão empresarial desenvolvido em Python com interface gráfica Tkinter, integração com Mercado Pago e funcionalidades de controle de estoque, pedidos e financeiro.

## 🚀 Funcionalidades

- **Gestão de Clientes**: Cadastro e gerenciamento de clientes
- **Controle de Estoque**: Gestão de produtos e categorias
- **Criação de Pedidos**: Sistema completo de pedidos com integração ao Mercado Pago
- **Módulo Financeiro**: Controle financeiro com autenticação 2FA (TOTP)
- **Gestão de Contratos**: Upload e download de contratos em PDF
- **Cobrança**: Sistema de cobrança integrado
- **Notificações**: Integração com Discord para notificações
- **Gerador TOTP**: Ferramenta para gerar chaves secretas RFC 6238
- **Monitor TOTP**: Visualizador em tempo real de códigos TOTP

## 📋 Pré-requisitos

- Python 3.7+
- Conta no Mercado Pago (para pagamentos)
- Webhook do Discord (opcional, para notificações)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd supreme_auto
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

4. Edite o arquivo `.env` com suas credenciais:
```env
MERCADOPAGO_TEST_TOKEN=seu_token_de_teste_aqui
MERCADOPAGO_PRODUCTION_TOKEN=seu_token_de_producao_aqui
MERCADOPAGO_WEBHOOK_URL=sua_url_webhook_aqui
TOTP_SECRET_KEY=sua_chave_totp_aqui
DISCORD_WEBHOOK_URL=sua_url_webhook_discord_aqui
```

## 🚀 Como usar

### Executando o sistema

Execute o arquivo principal:
```bash
python main.py
```

Ou use o arquivo batch (Windows):
```bash
start.bat
```

### Configuração inicial

1. **Mercado Pago**: 
   - Crie uma conta no [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
   - Obtenha seus tokens de teste e produção
   - Configure o webhook para receber notificações de pagamento

2. **Autenticação 2FA (TOTP)**:
   - Use o gerador de chaves: `TOTP/gerar_segredo.py`
   - Insira sua chave no arquivo: `TOTP/totp.py`

3. **Discord (Opcional)**:
   - Crie um webhook no seu servidor Discord
   - Configure a URL no arquivo `.env`

### Modo Debug

Quando `DEBUG_MODE=True` no arquivo `.env`:
- A autenticação TOTP no módulo financeiro pode ser bypassada
- Use os códigos especiais: `debug`, `bypass` ou `dev`
- ⚠️ **IMPORTANTE**: Sempre configure `DEBUG_MODE=False` em produção

## 📁 Estrutura do Projeto

```
supreme_auto/
├── main.py                 # Arquivo principal
├── apiMP.py               # Integração com Mercado Pago
├── estoque.py             # Gestão de estoque
├── requirements.txt       # Dependências do projeto
├── start.bat             # Script para iniciar (Windows)
├── .env.example          # Exemplo de configuração
├── .gitignore           # Arquivos ignorados pelo Git
├── assets/              # Recursos estáticos
│   ├── ico.ico
│   └── logo.png
├── TOTP/                # Ferramentas TOTP
│   ├── gerar_segredo.py  # Gerador de chaves secretas
│   └── totp.py          # Monitor TOTP em tempo real
└── ui/                  # Interface gráfica
    ├── __init__.py
    ├── atrelamento_contratos.py
    ├── cadastro_categorias.py
    ├── cadastro_clientes.py
    ├── criacao_produtos.py
    ├── cobranca.py
    ├── criacao_pedidos.py
    ├── financeiro.py
    ├── menu_principal.py
    └── pedidos_pagos.py
```

## � Ferramentas TOTP

O sistema inclui ferramentas avançadas para geração e monitoramento de códigos TOTP:

### Gerador de Chaves RFC 6238

```bash
python .\TOTP\gerar_segredo.py
```

**Funcionalidades:**
- Gera chaves seguras de 160 bits conforme RFC 6238
- Validação automática de segurança
- Atualização automática do arquivo `.env`
- Geração de QR codes para configuração fácil
- URI compatível com todos os apps autenticadores

### Monitor TOTP em Tempo Real

```bash
python .\TOTP\totp.py
```

**Funcionalidades:**
- Exibe códigos TOTP atualizando em tempo real
- Barra de progresso visual
- Contador de tempo restante
- Interface limpa sem poluir o terminal
- Compatível com iOS/Android via a-Shell

### Localização das Ferramentas

As ferramentas TOTP também estão disponíveis na pasta `TOTP/`:
- `TOTP/totp.py` - Monitor em tempo real (compatível com mobile)

## �🔒 Segurança

- **Nunca commite credenciais**: Todas as informações sensíveis devem estar no arquivo `.env`
- **Autenticação 2FA RFC 6238**: O módulo financeiro usa TOTP com chaves de 160 bits
- **Geração segura de chaves**: Usa `secrets.token_bytes()` para máxima segurança
- **Validação de entrada**: Todos os inputs são validados antes do processamento
- **Banco de dados local**: SQLite para armazenamento seguro local
- **Modo debug controlado**: Bypass de autenticação apenas em desenvolvimento

## 🛠️ Desenvolvimento

### Configuração do ambiente de desenvolvimento

1. **Clone e configure o projeto:**
```bash
git clone <url-do-repositorio>
cd supreme_auto
pip install -r requirements.txt
cp .env.example .env
```

2. **Gere uma chave TOTP segura:**
```bash
python gerar_chave_rfc6238.py
```

3. **Configure autenticação 2FA:**
   - Use o QR code gerado ou configure manualmente
   - Teste com: `python totp_tempo_real.py`

### Adicionando novas funcionalidades

1. Crie novos módulos na pasta `ui/`
2. Importe no `main.py`
3. Adicione à navegação no menu principal

### Banco de dados

O sistema usa SQLite com as seguintes tabelas principais:
- `clientes`: Informações dos clientes
- `categorias`: Categorias de produtos
- `produtos`: Catálogo de produtos
- `pedidos`: Pedidos realizados
- `itens_pedido`: Itens de cada pedido
- `pagamentos`: Status dos pagamentos

## 📝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## ⚠️ Configuração para Produção

Para usar em produção:

1. **Gere uma nova chave TOTP de produção:**
```bash
python gerar_chave_rfc6238.py
```

2. Configure o arquivo `.env` de produção:
```env
DEBUG_MODE=False
TOTP_SECRET_KEY=<chave_gerada_160_bits>
MERCADOPAGO_PRODUCTION_TOKEN=<token_real>
```

3. Configure SSL/HTTPS para webhooks
4. Faça backup regular do banco de dados
5. Configure logs adequados
6. Teste a autenticação 2FA em ambiente isolado

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação do [Mercado Pago](https://www.mercadopago.com.br/developers)

## 🔄 Atualizações

Mantenha suas dependências atualizadas:
```bash
pip install --upgrade -r requirements.txt
```
