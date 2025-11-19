#!/usr/bin/env python
"""
Script para executar a aplicação Flask
"""
import os
from app import create_app

# Criar a aplicação
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Rodar em modo desenvolvimento
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
