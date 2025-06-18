from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('.', path)

# Adicione aqui as outras rotas do seu aplicativo

# Para desenvolvimento local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
