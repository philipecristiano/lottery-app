from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from src.services.analyzer import (
    SUPPORTED_GAMES, fetch_results, fetch_last_n_results, 
    calculate_statistics, generate_numbers, check_hits,
    save_game, get_history, update_game_result
)
import json

# Criar blueprint para as rotas de visualização
views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Página inicial"""
    return render_template('index.html', games=SUPPORTED_GAMES)

@views_bp.route('/analyze')
@views_bp.route('/analyze/<lottery>')
def analyze(lottery='megasena'):
    """Página de análise estatística"""
    if lottery not in SUPPORTED_GAMES:
        flash(f'Loteria "{lottery}" não suportada. Redirecionando para Mega-Sena.', 'warning')
        return redirect(url_for('views.analyze', lottery='megasena'))
    
    return render_template(
        'analyze.html', 
        selected_lottery=lottery,
        selected_game=SUPPORTED_GAMES[lottery],
        games=SUPPORTED_GAMES
    )

@views_bp.route('/generate')
@views_bp.route('/generate/<lottery>')
def generate(lottery='megasena'):
    """Página de geração de jogos"""
    if lottery not in SUPPORTED_GAMES:
        flash(f'Loteria "{lottery}" não suportada. Redirecionando para Mega-Sena.', 'warning')
        return redirect(url_for('views.generate', lottery='megasena'))
    
    return render_template(
        'generate.html', 
        selected_lottery=lottery,
        selected_game=SUPPORTED_GAMES[lottery],
        games=SUPPORTED_GAMES
    )

@views_bp.route('/check')
@views_bp.route('/check/<lottery>')
def check(lottery='megasena'):
    """Página de verificação de jogos"""
    if lottery not in SUPPORTED_GAMES:
        flash(f'Loteria "{lottery}" não suportada. Redirecionando para Mega-Sena.', 'warning')
        return redirect(url_for('views.check', lottery='megasena'))
    
    return render_template(
        'check.html', 
        selected_lottery=lottery,
        selected_game=SUPPORTED_GAMES[lottery],
        games=SUPPORTED_GAMES
    )

@views_bp.route('/history')
@views_bp.route('/history/<lottery>')
def history(lottery=None):
    """Página de histórico de jogos"""
    if lottery is not None and lottery not in SUPPORTED_GAMES:
        flash(f'Loteria "{lottery}" não suportada. Mostrando todos os jogos.', 'warning')
        return redirect(url_for('views.history'))
    
    return render_template(
        'history.html', 
        selected_lottery=lottery,
        selected_game=SUPPORTED_GAMES.get(lottery) if lottery else None,
        games=SUPPORTED_GAMES
    )
