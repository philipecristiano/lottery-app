# No início do arquivo, adicione:
from flask import Flask, render_template, request, jsonify
import os

# Certifique-se que a definição do app esteja assim:
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# No final do arquivo, substitua qualquer bloco if __name__ == "__main__" por:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# E adicione esta função para o Vercel:
@app.route('/')
def home():
    return render_template('index.html')
            if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

