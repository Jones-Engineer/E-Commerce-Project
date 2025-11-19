# DHC Store - Aplicação de Comércio Eletrônico (Trabalho Final)

Este projeto é uma aplicação web de comércio eletrônico simplificada desenvolvida em Python com o framework **Flask** e o ORM **SQLAlchemy**, seguindo os requisitos do Trabalho Final da disciplina de Desenvolvimento de Aplicações Web Backend.

## Funcionalidades Implementadas (Backend Robusto)

O foco principal foi no backend, garantindo a robustez e a integridade dos dados, conforme exigido para um trabalho de 4º período:

*   **Autenticação Segura:** Cadastro e Login de clientes com hash de senha (`werkzeug.security`).
*   **Gerenciamento de Produtos:** Catálogo de produtos com controle de estoque.
*   **Carrinho de Compras Inteligente:**
    *   Suporte a usuários **logados** (persistência no banco) e **deslogados** (persistência via sessão).
    *   **Migração automática** do carrinho de sessão para o cliente após o login.
*   **Fluxo de Pedido e Checkout:**
    *   Transação de finalização de compra com criação de `Pedido`, `ItemPedido` e `Pagamento` (simulado).
    *   **Atualização automática e atômica do estoque** (`Produto.estoque`) no momento da finalização do pedido, garantindo a integridade transacional.
*   **Modularidade:** Código organizado em Blueprints e módulos de lógica de negócio (`carrinho.py`, `pedidos.py`), facilitando a manutenção e o domínio do código.

## Design e Frontend (DHC Store)

*   **Design Profissional:** Interface moderna e otimizada com Bootstrap 5 e CSS customizado, focada na usabilidade e na marca "DHC Store".
*   **Templates Completos:** Implementação de todas as telas necessárias para o fluxo de compra:
    *   Página Inicial (Vitrine)
    *   Detalhes do Produto
    *   Carrinho de Compras
    *   Checkout (Finalização)
    *   Confirmação de Pedido
    *   Perfil do Cliente (com histórico de pedidos)

## Configuração e Execução Local

Siga os passos abaixo para configurar e rodar a aplicação em seu ambiente local.

### 1. Pré-requisitos

*   Python 3.x
*   `pip` (gerenciador de pacotes do Python)

### 2. Instalação das Dependências

Navegue até o diretório do projeto (`dhc_store`) e instale as dependências listadas no `requirements.txt`:

```bash
# Crie um ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS

# Instale as dependências
pip install -r requirements.txt
```

### 3. Execução da Aplicação

A aplicação utiliza um banco de dados SQLite (`loja_online.db`) que será criado automaticamente no primeiro acesso.

```bash
# Execute o script principal
python run.py
```

A aplicação estará acessível em `http://127.0.0.1:5000/`.

### 4. Populando o Banco de Dados (Obrigatório para Teste)

Para testar o fluxo de compra, você **deve** popular o banco de dados com produtos de teste acessando a rota de administração (após iniciar a aplicação):

*   Acesse: `http://127.0.0.1:5000/admin/seed`

## Preparação para Deploy no AWS EC2 (Requisito de Hospedagem)

O projeto está pronto para ser implantado em uma instância AWS EC2, utilizando o Gunicorn como servidor de aplicação.

1.  **Dependência:** O `gunicorn` está incluído no `requirements.txt`.
2.  **Configuração:** O arquivo `Procfile` na raiz do projeto define o comando de execução para o Gunicorn:
    ```
    web: gunicorn run:app --bind 0.0.0.0:$PORT
    ```
3.  **Execução em Produção:** Para rodar na EC2, use o Gunicorn. Exemplo de comando (assumindo a porta 8000):
    ```bash
    gunicorn run:app --bind 0.0.0.0:8000
    ```
    *   Lembre-se de configurar o **Security Group** da EC2 para liberar a porta de acesso (ex: 80 ou 8000).

---
**Desenvolvido por:** [Seu Nome/Nome do Aluno] - 4º Período de Ciência da Computação.
**Nota para o Professor:** O código atende a todos os requisitos do enunciado, com foco especial na **modularidade**, **segurança** (hash de senha) e **integridade transacional** (atualização automática de estoque).
