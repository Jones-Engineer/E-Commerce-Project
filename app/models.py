from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Cliente(db.Model):
    """Modelo de Cliente"""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True, cascade='all, delete-orphan')
    
    def set_senha(self, senha):
        """Hash da senha e armazena"""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Cliente {self.email}>'


class Produto(db.Model):
    """Modelo de Produto"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True, cascade='all, delete-orphan')
    itens_carrinho = db.relationship('CarrinhoCompras', backref='produto', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Produto {self.nome}>'


class Pedido(db.Model):
    """Modelo de Pedido"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pendente')  # pendente, confirmado, enviado, entregue, cancelado
    
    # Relacionamentos
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    pagamento = db.relationship('Pagamento', backref='pedido', uselist=False, lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido {self.id}>'


class ItemPedido(db.Model):
    """Modelo de Item do Pedido"""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ItemPedido {self.id}>'


class Pagamento(db.Model):
    """Modelo de Pagamento"""
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False, unique=True)
    metodo = db.Column(db.String(50), nullable=False)  # cartao, boleto, pix, etc
    status = db.Column(db.String(50), default='pendente')  # pendente, aprovado, recusado
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pagamento {self.id}>'


class CarrinhoCompras(db.Model):
    """Modelo de Carrinho de Compras"""
    __tablename__ = 'carrinho_compras'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))  # Pode ser NULL para usuários não logados
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)
    sessao_id = db.Column(db.String(255))  # Para rastrear carrinhos de usuários não logados
    
    def __repr__(self):
        return f'<CarrinhoCompras {self.id}>'
