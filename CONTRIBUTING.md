# Guia de Contribuição

Obrigado por considerar contribuir para o projeto Supreme Auto! Este documento fornece diretrizes para contribuições.

## 🤝 Como Contribuir

### 1. Reportando Bugs
- Use a seção Issues do GitHub
- Descreva o problema detalhadamente
- Inclua passos para reproduzir o bug
- Adicione screenshots se aplicável

### 2. Sugerindo Melhorias
- Abra uma Issue com a tag "enhancement"
- Descreva a funcionalidade desejada
- Explique o caso de uso
- Considere a compatibilidade com o sistema atual

### 3. Enviando Pull Requests

#### Antes de começar:
1. Fork o repositório
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Configure seu ambiente de desenvolvimento

#### Durante o desenvolvimento:
1. Siga o padrão de código existente
2. Adicione comentários quando necessário
3. Teste suas mudanças localmente
4. Mantenha commits pequenos e focados

#### Enviando o PR:
1. Commit suas mudanças: `git commit -am 'Adiciona nova funcionalidade'`
2. Push para a branch: `git push origin feature/nova-funcionalidade`
3. Abra um Pull Request no GitHub

## 📝 Padrões de Código

### Python
- Siga a PEP 8
- Use nomes descritivos para variáveis e funções
- Adicione docstrings para funções públicas
- Mantenha funções pequenas e focadas

### Estrutura de Arquivos
- Módulos UI na pasta `ui/`
- Configurações no arquivo `config.py`
- Documentação em arquivos `.md`

### Exemplo de código:
```python
def process_payment(external_reference: str, amount: float) -> bool:
    """
    Processa um pagamento no sistema.
    
    Args:
        external_reference: Referência externa do pedido
        amount: Valor do pagamento
        
    Returns:
        True se o pagamento foi processado com sucesso
    """
    # Implementação aqui
    pass
```

## 🔒 Segurança

### Obrigatório:
- NUNCA inclua credenciais reais no código
- Use variáveis de ambiente para informações sensíveis
- Teste com dados fictícios
- Valide todas as entradas do usuário

### Informações Sensíveis:
- Tokens de API
- Chaves de criptografia
- URLs de webhook
- Dados pessoais de clientes

## 🧪 Testes

### Antes de enviar:
1. Teste a funcionalidade manualmente
2. Verifique se não quebrou funcionalidades existentes
3. Teste com dados de exemplo
4. Valide a interface do usuário

### Cenários de teste:
- Dados válidos e inválidos
- Casos extremos (strings vazias, números negativos)
- Interrupções de rede (para APIs)
- Diferentes resoluções de tela (UI)

## 📋 Checklist do Pull Request

Antes de enviar seu PR, verifique:

- [ ] Código segue os padrões estabelecidos
- [ ] Funcionalidade foi testada localmente
- [ ] Não inclui informações sensíveis
- [ ] Documentação foi atualizada se necessário
- [ ] Commit messages são descritivos
- [ ] Branch está atualizada com main

## 🏷️ Convenções de Commit

Use mensagens de commit descritivas:

```
feat: adiciona integração com novo gateway de pagamento
fix: corrige erro na validação de CPF
docs: atualiza instruções de instalação
style: formata código seguindo PEP 8
refactor: reorganiza estrutura de banco de dados
test: adiciona testes para módulo de estoque
```

## 🚀 Processo de Review

### O que esperamos:
1. Código limpo e bem documentado
2. Funcionalidade testada
3. Compatibilidade com sistema existente
4. Seguimento das diretrizes de segurança

### Processo:
1. Review automático (linting, testes)
2. Review manual por mantenedores
3. Discussão e ajustes se necessário
4. Merge após aprovação

## 📚 Recursos Úteis

### Documentação:
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Mercado Pago API](https://www.mercadopago.com.br/developers/pt/docs)

### Ferramentas:
- [SQLite Browser](https://sqlitebrowser.org/) para visualizar o banco
- [pyotp](https://pyotp.readthedocs.io/) para TOTP
- [requests](https://docs.python-requests.org/) para APIs

## 🎯 Áreas que Precisam de Contribuição

### Prioridade Alta:
- Testes automatizados
- Validação de entrada mais robusta
- Logs estruturados
- Backup automático do banco

### Prioridade Média:
- Interface mais moderna
- Relatórios em PDF
- Integração com outros gateways
- Notificações por email

### Prioridade Baixa:
- Temas da interface
- Atalhos de teclado
- Importação/exportação de dados
- API REST

## 📞 Contato

Para dúvidas sobre contribuições:
- Abra uma Issue no GitHub
- Use as Discussions para conversas gerais
- Entre em contato com os mantenedores

## 🙏 Reconhecimento

Todos os contribuidores serão reconhecidos no projeto. Obrigado por ajudar a melhorar o Supreme Auto!

---

**Vamos construir algo incrível juntos! 🚀**
