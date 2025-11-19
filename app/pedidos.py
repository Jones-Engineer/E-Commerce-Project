from flask import session, flash
from app import db
from app.models import Cliente, Produto, Pedido, ItemPedido, Pagamento
from app.carrinho import get_carrinho_itens, limpar_carrinho, calcular_total_carrinho
from sqlalchemy.exc import SQLAlchemyError

def finalizar_pedido(cliente_id, metodo_pagamento):
    """
    Processa a finalização do pedido:
    1. Cria um novo Pedido.
    2. Move os itens do Carrinho para ItensPedido.
    3. Atualiza o estoque dos produtos (decrementa).
    4. Cria um registro de Pagamento.
    5. Limpa o carrinho.
    """
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        flash('Cliente não encontrado.', 'danger')
        return None

    itens_carrinho = get_carrinho_itens(cliente_id=cliente_id)
    if not itens_carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return None

    total_pedido = calcular_total_carrinho(itens_carrinho)
    
    # 1. Cria um novo Pedido
    novo_pedido = Pedido(
        cliente_id=cliente_id,
        total=total_pedido,
        status='pendente' # O status será atualizado após o pagamento
    )
    db.session.add(novo_pedido)
    db.session.flush() # Para obter o ID do pedido antes do commit

    itens_pedido_list = []
    
    try:
        # 2. Move os itens do Carrinho para ItensPedido e 3. Atualiza o estoque
        for item_carrinho in itens_carrinho:
            produto = item_carrinho.produto
            quantidade = item_carrinho.quantidade
            
            # Validação final de estoque
            if produto.estoque < quantidade:
                db.session.rollback()
                flash(f'Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque}', 'danger')
                return None
            
            # Cria ItemPedido
            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=produto.id,
                quantidade=quantidade,
                preco_unitario=produto.preco # Preço no momento da compra
            )
            itens_pedido_list.append(item_pedido)
            
            # Atualiza o estoque (decrementa)
            produto.estoque -= quantidade
            db.session.add(produto)
        
        db.session.add_all(itens_pedido_list)
        
        # 4. Cria um registro de Pagamento (Simulado)
        novo_pagamento = Pagamento(
            pedido_id=novo_pedido.id,
            metodo=metodo_pagamento,
            status='aprovado' # Simulação de pagamento aprovado
        )
        db.session.add(novo_pagamento)
        
        # Atualiza o status do pedido para confirmado
        novo_pedido.status = 'confirmado'
        
        # 5. Limpa o carrinho
        limpar_carrinho(cliente_id=cliente_id)
        
        db.session.commit()
        flash(f'Pedido #{novo_pedido.id} finalizado com sucesso! Pagamento aprovado.', 'success')
        return novo_pedido
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Erro ao finalizar o pedido: {str(e)}', 'danger')
        return None

def get_pedidos_cliente(cliente_id):
    """Retorna todos os pedidos de um cliente."""
    return Pedido.query.filter_by(cliente_id=cliente_id).order_by(Pedido.data_pedido.desc()).all()

def get_detalhes_pedido(pedido_id, cliente_id):
    """Retorna os detalhes de um pedido específico, garantindo que pertença ao cliente."""
    return Pedido.query.filter_by(id=pedido_id, cliente_id=cliente_id).first_or_404()
