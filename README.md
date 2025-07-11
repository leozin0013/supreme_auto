# Supreme Auto - Sistema de Gestão

Sistema de gestão empresarial desenvolvido em Python com interface gráfica Tkinter, integração com Mercado Pago e funcionalidades de controle de estoque, pedidos e financeiro.

## 🚀 Funcionalidades

- **Gestão de Clientes**: Cadastro e gerenciamento de clientes
- **Controle de Estoque**: Gestão de produtos e categorias
- **Criação de Pedidos**: Sistema completo de pedidos com integração ao Mercado Pago
- **Módulo Financeiro**: Controle financeiro com autenticação 2FA
- **Gestão de Contratos**: Upload e download de contratos em PDF
- **Cobrança**: Sistema de cobrança integrado
- **Notificações**: Integração com Discord para notificações

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
   - Gere uma chave secreta TOTP
   - Use um app como Google Authenticator para gerar códigos

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
└── ui/                  # Interface gráfica
    ├── menu_principal.py
    ├── cadastro_clientes.py
    ├── cadastro_produtos.py
    ├── criacao_pedidos.py
    ├── financeiro.py
    └── ...
```

## 🔒 Segurança

- **Nunca commite credenciais**: Todas as informações sensíveis devem estar no arquivo `.env`
- **Autenticação 2FA**: O módulo financeiro usa TOTP para segurança adicional
- **Validação de entrada**: Todos os inputs são validados antes do processamento
- **Banco de dados local**: SQLite para armazenamento seguro local

## 🛠️ Desenvolvimento

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

1. Configure `DEBUG_MODE=False` no arquivo `.env`
2. Use tokens de produção do Mercado Pago
3. Configure SSL/HTTPS para webhooks
4. Faça backup regular do banco de dados
5. Configure logs adequados

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
