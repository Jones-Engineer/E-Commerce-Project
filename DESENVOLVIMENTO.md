# Guia de Desenvolvimento - Dia 1

Este documento descreve a estrutura e as decisões de design do Dia 1 do projeto.

## Arquitetura

### Padrão MVC (Model-View-Controller)

A aplicação segue o padrão MVC:

- **Models** (`app/models.py`): Definem a estrutura dos dados (SQLAlchemy)
- **Views** (`app/templates/`): Templates HTML que renderizam os dados
- **Controllers** (`app/routes.py`): Rotas e lógica de negócio

### Blueprints

As rotas são organizadas em dois blueprints:

1. **auth_bp**: Rotas de autenticação (cadastro, login, logout)
2. **main_bp**: Rotas principais (produtos, perfil)

Isso facilita a modularização e a manutenção do código.

## Modelos de Dados

### Cliente
- Armazena informações do usuário
- Senha é armazenada com hash (não em texto plano)
- E-mail é único e indexado para buscas rápidas

### Produto
- Armazena informações de produtos
- Inclui preço e quantidade em estoque
- Relacionado com pedidos e carrinho

### Pedido
- Armazena informações de pedidos do cliente
- Relacionado com itens do pedido e pagamento

### ItemPedido
- Tabela de junção entre Pedido e Produto
- Armazena quantidade e preço unitário no momento da compra

### Pagamento
- Armazena informações de pagamento
- Relacionado com um único pedido

### CarrinhoCompras
- Armazena itens temporários do carrinho
- Pode estar associado a um cliente logado ou a uma sessão

## Segurança

### Hash de Senha

As senhas são hasheadas usando `werkzeug.security`:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Ao cadastrar
cliente.set_senha(senha)  # Gera hash

# Ao fazer login
cliente.verificar_senha(senha)  # Verifica hash
```

### Sessões

As sessões são usadas para manter o usuário logado:

```python
session['cliente_id'] = cliente.id
session['cliente_nome'] = cliente.nome
session['cliente_email'] = cliente.email
```

### Decorador de Autenticação

O decorador `@login_required` protege rotas que exigem login:

```python
@main_bp.route('/perfil')
@login_required
def perfil():
    # Apenas usuários logados podem acessar
    pass
```

## Validações

### Cadastro

1. Todos os campos são obrigatórios
2. Senhas devem ter pelo menos 6 caracteres
3. Senhas devem ser iguais (confirmação)
4. E-mail deve ser único

### Login

1. E-mail e senha são obrigatórios
2. E-mail deve existir no banco
3. Senha deve estar correta

## Banco de Dados

### Criação Automática

As tabelas são criadas automaticamente ao iniciar a aplicação:

```python
with app.app_context():
    db.create_all()
```

### Arquivo SQLite

O banco é armazenado em `loja_online.db` (arquivo local).

## Fluxo de Autenticação

```
1. Usuário acessa /cadastro
   ↓
2. Preenche formulário e submete
   ↓
3. Validações são feitas
   ↓
4. Cliente é criado com senha hasheada
   ↓
5. Usuário é redirecionado para login
   ↓
6. Usuário acessa /login
   ↓
7. Preenche e-mail e senha
   ↓
8. Credenciais são verificadas
   ↓
9. Sessão é criada
   ↓
10. Usuário é redirecionado para página inicial
```

## Próximos Passos (Dia 2)

### Carrinho de Compras

- Implementar lógica de adicionar ao carrinho
- Usar sessões para carrinhos de usuários não logados
- Usar banco de dados para carrinhos de usuários logados

### Pedidos e Checkout

- Criar rota de checkout
- Implementar lógica de finalização de pedido
- Atualizar estoque automaticamente

### Pagamentos

- Integrar com gateway de pagamento (simplificado)
- Registrar pagamentos no banco

## Testes Manuais

### Testar Cadastro

1. Acesse `http://localhost:5000/cadastro`
2. Preencha o formulário
3. Clique em "Cadastrar"
4. Verifique se a mensagem de sucesso aparece

### Testar Login

1. Acesse `http://localhost:5000/login`
2. Use o e-mail e senha cadastrados
3. Clique em "Entrar"
4. Verifique se você é redirecionado para a página inicial

### Testar Produtos

1. Acesse `http://localhost:5000/admin/seed` para popular o banco
2. Acesse `http://localhost:5000/` para ver a lista de produtos
3. Clique em "Ver Detalhes" para ver informações do produto

### Testar Perfil

1. Faça login
2. Clique em "Meu Perfil" na navegação
3. Verifique se seus dados aparecem

## Estrutura de Pastas Explicada

```
ecommerce_dia1/
├── app/                          # Pacote principal da aplicação
│   ├── __init__.py              # Factory da aplicação
│   ├── models.py                # Modelos SQLAlchemy
│   ├── routes.py                # Rotas e blueprints
│   ├── templates/               # Templates HTML
│   │   ├── base.html            # Template base (herança)
│   │   ├── cadastro.html        # Formulário de cadastro
│   │   ├── login.html           # Formulário de login
│   │   ├── index.html           # Listagem de produtos
│   │   ├── detalhes_produto.html # Detalhes do produto
│   │   └── perfil.html          # Perfil do cliente
│   └── static/                  # Arquivos estáticos
│       └── css/
│           └── style.css        # Estilos customizados
├── config.py                    # Configurações da aplicação
├── run.py                       # Script para executar
├── requirements.txt             # Dependências
├── .gitignore                   # Arquivos ignorados pelo Git
├── README.md                    # Instruções de uso
└── DESENVOLVIMENTO.md           # Este arquivo
```

## Dicas para o Desenvolvimento do Dia 2

1. **Modularidade**: Mantenha a lógica de carrinho em um módulo separado
2. **Reutilização**: Use os modelos existentes sem modificá-los desnecessariamente
3. **Testes**: Teste cada funcionalidade antes de passar para a próxima
4. **Commits**: Faça commits frequentes no Git
5. **Documentação**: Mantenha o código bem comentado

---

**Última atualização**: Dia 1 do projeto
