#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import Cliente, Produto, Pedido
from app.carrinho import adicionar_ao_carrinho, remover_do_carrinho, get_carrinho_itens, calcular_total_carrinho, migrar_carrinho_sessao_para_cliente
from app.pedidos import finalizar_pedido, get_pedidos_cliente
from functools import wraps

# Criar blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

# ==================== DECORADORES ====================

def login_required(f):
    """Decorador para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'cliente_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Rota para cadastro de novo cliente"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        if not all([nome, email, senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if senha != confirmar_senha:
            flash('As senhas não correspondem.', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        cliente_existente = Cliente.query.filter_by(email=email).first()
        if cliente_existente:
            flash('Este e-mail já está cadastrado.', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        novo_cliente = Cliente(nome=nome, email=email)
        novo_cliente.set_senha(senha)
        
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return redirect(url_for('auth.cadastro'))
    
    return render_template('cadastro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de cliente"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('E-mail e senha são obrigatórios.', 'danger')
            return redirect(url_for('auth.login'))
        
        cliente = Cliente.query.filter_by(email=email).first()
        
        if cliente and cliente.verificar_senha(senha):
            session['cliente_id'] = cliente.id
            session['cliente_nome'] = cliente.nome
            session['cliente_email'] = cliente.email
            session.permanent = True
            
            migrar_carrinho_sessao_para_cliente(cliente.id)
            
            flash(f'Bem-vindo, {cliente.nome}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Rota para logout"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.index'))


# ==================== ROTAS PRINCIPAIS ====================

@main_bp.route('/')
def index():
    """Página inicial - Lista de produtos"""
    page = request.args.get('page', 1, type=int)
    produtos = Produto.query.paginate(page=page, per_page=12)
    return render_template('index.html', produtos=produtos)


@main_bp.route('/produto/<int:produto_id>')
def detalhes_produto(produto_id):
    """Página de detalhes do produto"""
    produto = Produto.query.get_or_404(produto_id)
    return render_template('detalhes_produto.html', produto=produto)


@main_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do cliente logado e edição de dados."""
    cliente = Cliente.query.get(session.get('cliente_id'))

    if request.method == 'POST':
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()

        cliente.endereco = endereco
        cliente.telefone = telefone

        try:
            db.session.commit()
            flash('Seu perfil foi atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
        
        return redirect(url_for('main.perfil'))

    pedidos = get_pedidos_cliente(cliente.id)
    return render_template('perfil.html', cliente=cliente, pedidos=pedidos)


@main_bp.route('/adicionar_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_carrinho(produto_id):
    """Adiciona um produto ao carrinho."""
    quantidade = request.form.get('quantidade', 1, type=int)
    adicionar_ao_carrinho(produto_id, quantidade)
    return redirect(url_for('main.carrinho'))


@main_bp.route('/remover_carrinho/<int:item_carrinho_id>', methods=['POST'])
def remover_carrinho(item_carrinho_id):
    """Remove um item do carrinho."""
    remover_do_carrinho(item_carrinho_id)
    return redirect(url_for('main.carrinho'))


@main_bp.route('/carrinho')
def carrinho():
    """Página do carrinho de compras."""
    cliente_id = session.get('cliente_id')
    itens_carrinho = get_carrinho_itens(cliente_id)
    total = calcular_total_carrinho(itens_carrinho)
    return render_template('carrinho.html', itens_carrinho=itens_carrinho, total=total)


@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Página de finalização de pedido."""
    cliente_id = session.get('cliente_id')
    itens_carrinho = get_carrinho_itens(cliente_id)
    total = calcular_total_carrinho(itens_carrinho)

    if not itens_carrinho:
        flash('Seu carrinho está vazio. Adicione produtos para finalizar a compra.', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        metodo_pagamento = request.form.get('metodo_pagamento')
        
        if not metodo_pagamento:
            flash('Selecione um método de pagamento.', 'danger')
            return redirect(url_for('main.checkout'))

        pedido = finalizar_pedido(cliente_id, metodo_pagamento)
        
        if pedido:
            return redirect(url_for('main.pedido_confirmado', pedido_id=pedido.id))
        else:
            return redirect(url_for('main.carrinho'))

    cliente = Cliente.query.get(cliente_id)
    return render_template('checkout.html', itens_carrinho=itens_carrinho, total=total, cliente=cliente)


@main_bp.route('/pedido_confirmado/<int:pedido_id>')
@login_required
def pedido_confirmado(pedido_id):
    """Página de confirmação de pedido."""
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.cliente_id != session.get('cliente_id'):
        flash('Você não tem permissão para visualizar este pedido.', 'danger')
        return redirect(url_for('main.perfil'))
    
    return render_template('pedido_confirmado.html', pedido=pedido)


@main_bp.route('/pedido/<int:pedido_id>')
@login_required
def detalhes_pedido(pedido_id):
    """Página de detalhes de um pedido específico."""
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.cliente_id != session.get('cliente_id'):
        flash('Você não tem permissão para visualizar este pedido.', 'danger')
        return redirect(url_for('main.perfil'))
    
    return render_template('detalhes_pedido.html', pedido=pedido)


# ==================== ROTAS DE TESTE ====================

@main_bp.route('/admin/seed')
def seed_produtos():
    """Rota para popular o banco com produtos de teste (APENAS PARA DESENVOLVIMENTO)"""
    if Produto.query.first():
        return 'Produtos já existem no banco de dados.', 400
    
    produtos_teste = [
        Produto(nome='Notebook Gamer Pro', descricao='Notebook de alta performance com placa de vídeo dedicada.', preco=5500.00, estoque=10),
        Produto(nome='Mouse Ergonômico', descricao='Mouse sem fio com design ergonômico para longas horas de uso.', preco=250.00, estoque=50),
        Produto(nome='Teclado Mecânico RGB', descricao='Teclado com switches mecânicos e iluminação RGB customizável.', preco=450.00, estoque=30),
        Produto(nome='Monitor Ultrawide 29"', descricao='Monitor com proporção 21:9 para maior produtividade.', preco=1200.00, estoque=15),
        Produto(nome='Webcam 4K Pro', descricao='Webcam com resolução 4K e microfone integrado.', preco=850.00, estoque=25),
        Produto(nome='Headset Surround 7.1', descricao='Headset com som surround 7.1 para imersão total em jogos.', preco=650.00, estoque=40),
    ]
    
    try:
        db.session.add_all(produtos_teste)
        db.session.commit()
        return 'Produtos de teste adicionados com sucesso!', 200
    except Exception as e:
        db.session.rollback()
        return f'Erro ao adicionar produtos: {str(e)}', 500
