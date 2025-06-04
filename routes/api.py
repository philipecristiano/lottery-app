from flask import Blueprint, request, jsonify
import json
import random
from src.services.analyzer import LotteryAnalyzer
from src.services.advanced_analyzer import AdvancedAnalyzer
from src.services.probability_optimizer import ProbabilityOptimizer

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Instanciar analisadores
analyzer = LotteryAnalyzer()
advanced_analyzer = AdvancedAnalyzer()
probability_optimizer = ProbabilityOptimizer()

# Configurações das loterias
LOTTERY_CONFIG = {
    'megasena': {'numbers': 6, 'range': (1, 60)},
    'lotofacil': {'numbers': 15, 'range': (1, 25)},
    'quina': {'numbers': 5, 'range': (1, 80)},
    'timemania': {'numbers': 10, 'range': (1, 80), 'has_team': True},
    'maismilionaria': {'numbers': 6, 'range': (1, 50), 'trevos': 2, 'trevos_range': (1, 6)}
}

@api_bp.route('/latest-results', methods=['GET'])
def get_latest_results():
    """Retorna os resultados mais recentes das loterias."""
    try:
        results = analyzer.get_latest_results()
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/lottery-stats', methods=['POST'])
def get_lottery_stats():
    """Retorna estatísticas detalhadas para uma loteria específica."""
    data = request.json
    lottery = data.get('lottery', 'megasena')
    
    try:
        # Estatísticas básicas
        frequency = analyzer.get_number_frequency(lottery)
        delay = analyzer.get_number_delay(lottery)
        
        # Estatísticas avançadas
        advanced_stats = advanced_analyzer.get_advanced_stats(lottery)
        
        return jsonify({
            'basic': {
                'frequency': frequency,
                'delay': delay
            },
            'advanced': advanced_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/preview-game', methods=['POST'])
def preview_game():
    """Gera uma visualização prévia de um jogo com base na estratégia selecionada."""
    data = request.json
    lottery = data.get('lottery', 'megasena')
    strategy = data.get('strategy', 'random')
    
    try:
        # Obter configuração da loteria
        config = LOTTERY_CONFIG.get(lottery)
        if not config:
            return jsonify({'error': f'Loteria não suportada: {lottery}'}), 400
        
        # Gerar jogo com base na estratégia
        game = generate_game_by_strategy(lottery, strategy, data)
        
        # Calcular probabilidade relativa
        probability = probability_optimizer.calculate_probability(lottery, game['numbers'])
        game['probability'] = probability
        
        return jsonify({'preview_game': game})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/generate-games', methods=['POST'])
def generate_games():
    """Gera múltiplos jogos com base na estratégia selecionada."""
    data = request.json
    lottery = data.get('lottery', 'megasena')
    strategy = data.get('strategy', 'random')
    num_games = data.get('num_games', 1)
    save_to_history = data.get('save_to_history', True)
    
    try:
        # Validar número de jogos
        if num_games < 1 or num_games > 15:
            return jsonify({'error': 'Número de jogos deve estar entre 1 e 15'}), 400
        
        # Gerar jogos
        games = []
        for _ in range(num_games):
            game = generate_game_by_strategy(lottery, strategy, data)
            
            # Calcular probabilidade relativa
            probability = probability_optimizer.calculate_probability(lottery, game['numbers'])
            game['optimization_score'] = probability.get('relative_score', 50)
            
            games.append(game)
        
        # Salvar no histórico se solicitado
        if save_to_history:
            for game in games:
                analyzer.save_game_to_history(lottery, game)
        
        return jsonify({'games': games})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/check-game', methods=['POST'])
def check_game():
    """Verifica um jogo contra o resultado oficial."""
    data = request.json
    lottery = data.get('lottery', 'megasena')
    numbers = data.get('numbers', [])
    contest = data.get('contest')
    
    try:
        result = analyzer.check_game(lottery, numbers, contest)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/game-history', methods=['GET'])
def get_game_history():
    """Retorna o histórico de jogos."""
    lottery = request.args.get('lottery')
    
    try:
        history = analyzer.get_game_history(lottery)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_game_by_strategy(lottery, strategy, params=None):
    """Gera um jogo com base na estratégia selecionada."""
    if params is None:
        params = {}
    
    config = LOTTERY_CONFIG.get(lottery)
    if not config:
        raise ValueError(f'Loteria não suportada: {lottery}')
    
    numbers_count = config['numbers']
    min_num, max_num = config['range']
    
    # Estratégia aleatória
    if strategy == 'random':
        numbers = random.sample(range(min_num, max_num + 1), numbers_count)
    
    # Estratégia de números quentes (mais frequentes)
    elif strategy == 'hot_numbers':
        frequency = analyzer.get_number_frequency(lottery)
        if not frequency:
            # Fallback para aleatório se não houver dados de frequência
            numbers = random.sample(range(min_num, max_num + 1), numbers_count)
        else:
            # Ordenar números por frequência (decrescente)
            sorted_numbers = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            # Pegar os números mais frequentes com alguma aleatoriedade
            top_numbers = [int(num) for num, _ in sorted_numbers[:int(numbers_count * 1.5)]]
            numbers = random.sample(top_numbers, min(numbers_count, len(top_numbers)))
            # Completar com números aleatórios se necessário
            if len(numbers) < numbers_count:
                remaining = numbers_count - len(numbers)
                available = [n for n in range(min_num, max_num + 1) if n not in numbers]
                numbers.extend(random.sample(available, remaining))
    
    # Estratégia de números frios (menos frequentes)
    elif strategy == 'cold_numbers':
        delay = analyzer.get_number_delay(lottery)
        if not delay:
            # Fallback para aleatório se não houver dados de atraso
            numbers = random.sample(range(min_num, max_num + 1), numbers_count)
        else:
            # Ordenar números por atraso (decrescente)
            sorted_numbers = sorted(delay.items(), key=lambda x: x[1], reverse=True)
            # Pegar os números mais atrasados com alguma aleatoriedade
            top_numbers = [int(num) for num, _ in sorted_numbers[:int(numbers_count * 1.5)]]
            numbers = random.sample(top_numbers, min(numbers_count, len(top_numbers)))
            # Completar com números aleatórios se necessário
            if len(numbers) < numbers_count:
                remaining = numbers_count - len(numbers)
                available = [n for n in range(min_num, max_num + 1) if n not in numbers]
                numbers.extend(random.sample(available, remaining))
    
    # Estratégia baseada na média dos últimos 5 jogos
    elif strategy == 'last_5_avg':
        numbers = advanced_analyzer.generate_game_based_on_last_5(lottery, numbers_count)
    
    # Estratégia personalizada (pares/ímpares)
    elif strategy == 'custom_even_odd':
        even_count = params.get('even_count', numbers_count // 2)
        odd_count = params.get('odd_count', numbers_count - even_count)
        
        if even_count + odd_count != numbers_count:
            raise ValueError(f'A soma de números pares e ímpares deve ser igual a {numbers_count}')
        
        # Gerar números pares
        even_numbers = [n for n in range(min_num, max_num + 1) if n % 2 == 0]
        selected_even = random.sample(even_numbers, even_count)
        
        # Gerar números ímpares
        odd_numbers = [n for n in range(min_num, max_num + 1) if n % 2 != 0]
        selected_odd = random.sample(odd_numbers, odd_count)
        
        # Combinar e ordenar
        numbers = selected_even + selected_odd
    
    # Estratégia otimizada por IA
    elif strategy == 'optimized':
        numbers = probability_optimizer.generate_optimized_game(lottery)
    
    else:
        raise ValueError(f'Estratégia não suportada: {strategy}')
    
    # Ordenar números
    numbers.sort()
    
    # Criar objeto do jogo
    game = {
        'numbers': numbers,
        'strategy': strategy
    }
    
    # Adicionar trevos para +Milionária
    if lottery == 'maismilionaria' and 'trevos' in config:
        min_trevo, max_trevo = config['trevos_range']
        trevos_count = config['trevos']
        game['trevos'] = random.sample(range(min_trevo, max_trevo + 1), trevos_count)
    
    # Adicionar Time do Coração para Timemania
    if lottery == 'timemania' and config.get('has_team', False):
        teams = analyzer.get_available_teams()
        if teams:
            game['time_coracao'] = random.choice(teams)
    
    return game
