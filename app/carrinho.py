from flask import session, flash
from app import db
from app.models import Produto, CarrinhoCompras
from sqlalchemy.exc import SQLAlchemyError

def get_session_id():
    """Retorna o ID da sessão para usuários não logados."""
    if 'session_id' not in session:
        # Gera um ID de sessão simples, pode ser melhorado para um UUID
        session['session_id'] = db.session.query(db.func.uuid_v4()).scalar()
    return session['session_id']

def get_carrinho_itens(cliente_id=None):
    """
    Retorna os itens do carrinho.
    Prioriza o cliente_id se logado, senão usa o session_id.
    """
    if cliente_id:
        return CarrinhoCompras.query.filter_by(cliente_id=cliente_id).all()
    
    session_id = session.get('session_id')
    if session_id:
        return CarrinhoCompras.query.filter_by(sessao_id=session_id).all()
        
    return []

def adicionar_ao_carrinho(produto_id, quantidade=1):
    """Adiciona um produto ao carrinho."""
    produto = Produto.query.get(produto_id)
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return False

    if produto.estoque < quantidade:
        flash(f'Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque}', 'danger')
        return False

    cliente_id = session.get('cliente_id')
    sessao_id = get_session_id() if not cliente_id else None

    # Tenta encontrar o item no carrinho
    if cliente_id:
        item_carrinho = CarrinhoCompras.query.filter_by(cliente_id=cliente_id, produto_id=produto_id).first()
    else:
        item_carrinho = CarrinhoCompras.query.filter_by(sessao_id=sessao_id, produto_id=produto_id).first()

    try:
        if item_carrinho:
            # Se o item já existe, apenas atualiza a quantidade
            item_carrinho.quantidade += quantidade
        else:
            # Se o item não existe, cria um novo
            item_carrinho = CarrinhoCompras(
                cliente_id=cliente_id,
                produto_id=produto_id,
                quantidade=quantidade,
                sessao_id=sessao_id
            )
            db.session.add(item_carrinho)
        
        db.session.commit()
        flash(f'{quantidade}x {produto.nome} adicionado(s) ao carrinho.', 'success')
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Erro ao adicionar ao carrinho: {str(e)}', 'danger')
        return False

def remover_do_carrinho(item_carrinho_id):
    """Remove um item específico do carrinho."""
    item = CarrinhoCompras.query.get(item_carrinho_id)
    if not item:
        flash('Item do carrinho não encontrado.', 'danger')
        return False

    # Verifica se o item pertence ao usuário logado ou à sessão
    cliente_id = session.get('cliente_id')
    sessao_id = session.get('session_id')

    if (cliente_id and item.cliente_id == cliente_id) or (not cliente_id and item.sessao_id == sessao_id):
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Item removido do carrinho.', 'info')
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao remover do carrinho: {str(e)}', 'danger')
            return False
    else:
        flash('Acesso negado ao item do carrinho.', 'danger')
        return False

def calcular_total_carrinho(itens_carrinho):
    """Calcula o valor total do carrinho."""
    total = 0.0
    for item in itens_carrinho:
        total += item.produto.preco * item.quantidade
    return total

def limpar_carrinho(cliente_id=None):
    """Limpa o carrinho após a finalização do pedido."""
    if cliente_id:
        CarrinhoCompras.query.filter_by(cliente_id=cliente_id).delete()
    else:
        session_id = session.get('session_id')
        if session_id:
            CarrinhoCompras.query.filter_by(sessao_id=session_id).delete()
    
    try:
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def migrar_carrinho_sessao_para_cliente(cliente_id):
    """Migra itens do carrinho de sessão para o cliente logado."""
    sessao_id = session.get('session_id')
    if sessao_id:
        itens_sessao = CarrinhoCompras.query.filter_by(sessao_id=sessao_id).all()
        for item in itens_sessao:
            # Verifica se o produto já está no carrinho do cliente
            item_existente = CarrinhoCompras.query.filter_by(cliente_id=cliente_id, produto_id=item.produto_id).first()
            if item_existente:
                item_existente.quantidade += item.quantidade
                db.session.delete(item) # Remove o item duplicado da sessão
            else:
                item.cliente_id = cliente_id
                item.sessao_id = None
        
        try:
            db.session.commit()
            # O session_id pode ser mantido para o caso de logout, mas o carrinho agora é do cliente
            # session.pop('session_id', None)
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False
    return False
