import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, redirect, url_for
from src.routes.views import views_bp
from src.routes.api import api_bp

# Criar aplicação Flask
app = Flask(__name__)
app.secret_key = 'lottery_app_secret_key'  # Chave para sessões e flash messages

# Registrar blueprints
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

# Rota raiz
@app.route('/')
def index():
    return redirect(url_for('views.index'))

# Configuração para execução direta
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
