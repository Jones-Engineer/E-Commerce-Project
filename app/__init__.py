from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Carregar configuração
    from config import config
    app.config.from_object(config[config_name])
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Registrar blueprints (rotas)
    from app.routes import auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return app
