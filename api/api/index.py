from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar os serviços
from src.services.analyzer import LotteryAnalyzer
from src.services.advanced_analyzer import AdvancedAnalyzer
from src.services.probability_optimizer import ProbabilityOptimizer

app = Flask(__name__, 
            static_folder='../src/static',
            template_folder='../src/templates')

# Configurar rotas
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../src/static', path)

# Adicionar outras rotas conforme necessário

# Configuração para o Vercel
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
