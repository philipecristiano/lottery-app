"""
Módulo de análise avançada para loterias
Implementa algoritmos de análise baseados nos últimos 5 jogos
"""

import numpy as np
import random
from collections import Counter
from src.services.analyzer import fetch_last_n_results, SUPPORTED_GAMES

def analyze_last_5_games(lottery_type):
    """
    Analisa os últimos 5 jogos de uma loteria específica e retorna estatísticas avançadas
    
    Args:
        lottery_type (str): Tipo de loteria (megasena, lotofacil, etc.)
        
    Returns:
        dict: Estatísticas avançadas baseadas nos últimos 5 jogos
    """
    if lottery_type not in SUPPORTED_GAMES:
        return {"error": f"Loteria {lottery_type} não suportada"}
    
    # Buscar os últimos 5 resultados
    results = fetch_last_n_results(lottery_type, 5)
    if not results or len(results) < 5:
        return {"error": "Não foi possível obter os últimos 5 resultados"}
    
    # Extrair números sorteados
    all_drawn_numbers = []
    for result in results:
        if 'dezenas' in result:
            all_drawn_numbers.append([int(n) for n in result['dezenas']])
    
    if not all_drawn_numbers:
        return {"error": "Não foi possível extrair os números sorteados"}
    
    # Calcular estatísticas avançadas
    stats = {
        "lottery_type": lottery_type,
        "num_games_analyzed": len(all_drawn_numbers),
        "last_contest": results[0].get('concurso'),
        "frequency_map": calculate_frequency_map(all_drawn_numbers),
        "pattern_analysis": analyze_patterns(all_drawn_numbers),
        "suggested_numbers_pool": generate_suggested_numbers_pool(all_drawn_numbers, lottery_type),
        "hot_zones": identify_hot_zones(all_drawn_numbers, lottery_type),
        "sum_statistics": calculate_sum_statistics(all_drawn_numbers),
        "even_odd_ratio": calculate_even_odd_ratio(all_drawn_numbers)
    }
    
    return stats

def calculate_frequency_map(drawn_numbers):
    """
    Calcula a frequência de cada número nos últimos jogos
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        
    Returns:
        dict: Mapa de frequência de cada número
    """
    all_numbers = [num for game in drawn_numbers for num in game]
    frequency = Counter(all_numbers)
    return {str(num): count for num, count in frequency.items()}

def analyze_patterns(drawn_numbers):
    """
    Analisa padrões nos últimos jogos
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        
    Returns:
        dict: Análise de padrões
    """
    # Verificar sequências
    sequences = []
    for game in drawn_numbers:
        sorted_game = sorted(game)
        seq_count = 0
        for i in range(len(sorted_game) - 1):
            if sorted_game[i + 1] - sorted_game[i] == 1:
                seq_count += 1
        sequences.append(seq_count)
    
    # Verificar repetições entre jogos
    repeated_between_games = []
    for i in range(len(drawn_numbers) - 1):
        current = set(drawn_numbers[i])
        next_game = set(drawn_numbers[i + 1])
        repeated = current.intersection(next_game)
        repeated_between_games.append(len(repeated))
    
    return {
        "sequences_per_game": sequences,
        "avg_sequences": sum(sequences) / len(sequences) if sequences else 0,
        "repeated_between_games": repeated_between_games,
        "avg_repeated": sum(repeated_between_games) / len(repeated_between_games) if repeated_between_games else 0
    }

def generate_suggested_numbers_pool(drawn_numbers, lottery_type):
    """
    Gera um pool de números sugeridos com base na análise dos últimos jogos
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        lottery_type (str): Tipo de loteria
        
    Returns:
        dict: Pool de números sugeridos com diferentes categorias
    """
    if lottery_type not in SUPPORTED_GAMES:
        return {}
    
    game_info = SUPPORTED_GAMES[lottery_type]
    min_num, max_num = game_info['range']
    
    # Calcular frequência
    frequency = calculate_frequency_map(drawn_numbers)
    
    # Calcular média ponderada de ocorrência
    # Damos mais peso para jogos mais recentes
    weighted_frequency = {}
    for i, game in enumerate(drawn_numbers):
        weight = 5 - i  # Peso 5 para o jogo mais recente, 1 para o mais antigo
        for num in game:
            if str(num) not in weighted_frequency:
                weighted_frequency[str(num)] = 0
            weighted_frequency[str(num)] += weight
    
    # Ordenar números por frequência ponderada
    sorted_numbers = sorted(
        [(int(num), freq) for num, freq in weighted_frequency.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Criar pool de números sugeridos por categoria
    hot_numbers = [num for num, _ in sorted_numbers[:int(len(sorted_numbers) * 0.4)]]
    warm_numbers = [num for num, _ in sorted_numbers[int(len(sorted_numbers) * 0.4):int(len(sorted_numbers) * 0.7)]]
    
    # Números que não apareceram nos últimos jogos
    all_numbers = set(range(min_num, max_num + 1))
    used_numbers = set([num for game in drawn_numbers for num in game])
    cold_numbers = list(all_numbers - used_numbers)
    
    # Números que aparecem em sequência
    sequence_numbers = []
    for game in drawn_numbers:
        sorted_game = sorted(game)
        for i in range(len(sorted_game) - 1):
            if sorted_game[i + 1] - sorted_game[i] == 1:
                sequence_numbers.extend([sorted_game[i], sorted_game[i + 1]])
    sequence_numbers = list(set(sequence_numbers))
    
    # Números que se repetem entre jogos
    repeated_numbers = []
    for i in range(len(drawn_numbers) - 1):
        current = set(drawn_numbers[i])
        next_game = set(drawn_numbers[i + 1])
        repeated = current.intersection(next_game)
        repeated_numbers.extend(list(repeated))
    repeated_numbers = list(set(repeated_numbers))
    
    return {
        "hot_numbers": hot_numbers,
        "warm_numbers": warm_numbers,
        "cold_numbers": cold_numbers,
        "sequence_numbers": sequence_numbers,
        "repeated_numbers": repeated_numbers
    }

def identify_hot_zones(drawn_numbers, lottery_type):
    """
    Identifica zonas quentes no volante
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        lottery_type (str): Tipo de loteria
        
    Returns:
        dict: Zonas quentes identificadas
    """
    if lottery_type not in SUPPORTED_GAMES:
        return {}
    
    min_num, max_num = SUPPORTED_GAMES[lottery_type]['range']
    range_size = max_num - min_num + 1
    
    # Dividir o volante em zonas
    num_zones = 4
    zone_size = range_size // num_zones
    zones = {}
    
    for i in range(num_zones):
        start = min_num + i * zone_size
        end = start + zone_size - 1
        if i == num_zones - 1:  # Última zona
            end = max_num
        
        zones[f"zone_{i+1}"] = {
            "range": [start, end],
            "count": 0
        }
    
    # Contar ocorrências em cada zona
    for game in drawn_numbers:
        for num in game:
            for zone_name, zone_info in zones.items():
                if zone_info["range"][0] <= num <= zone_info["range"][1]:
                    zones[zone_name]["count"] += 1
    
    # Calcular percentuais
    total_numbers = sum(len(game) for game in drawn_numbers)
    for zone_name, zone_info in zones.items():
        zone_info["percentage"] = round((zone_info["count"] / total_numbers) * 100, 2)
    
    # Identificar zona mais quente
    hottest_zone = max(zones.items(), key=lambda x: x[1]["count"])
    zones["hottest_zone"] = hottest_zone[0]
    
    return zones

def calculate_sum_statistics(drawn_numbers):
    """
    Calcula estatísticas de soma dos números sorteados
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        
    Returns:
        dict: Estatísticas de soma
    """
    sums = [sum(game) for game in drawn_numbers]
    
    return {
        "sums": sums,
        "avg_sum": sum(sums) / len(sums) if sums else 0,
        "min_sum": min(sums) if sums else 0,
        "max_sum": max(sums) if sums else 0
    }

def calculate_even_odd_ratio(drawn_numbers):
    """
    Calcula a proporção de números pares e ímpares
    
    Args:
        drawn_numbers (list): Lista de listas com números sorteados
        
    Returns:
        dict: Proporção de pares e ímpares
    """
    even_odd_counts = []
    
    for game in drawn_numbers:
        even_count = sum(1 for num in game if num % 2 == 0)
        odd_count = len(game) - even_count
        even_odd_counts.append({
            "even": even_count,
            "odd": odd_count,
            "ratio": even_count / len(game) if len(game) > 0 else 0
        })
    
    # Calcular médias
    avg_even = sum(item["even"] for item in even_odd_counts) / len(even_odd_counts) if even_odd_counts else 0
    avg_odd = sum(item["odd"] for item in even_odd_counts) / len(even_odd_counts) if even_odd_counts else 0
    avg_ratio = sum(item["ratio"] for item in even_odd_counts) / len(even_odd_counts) if even_odd_counts else 0
    
    return {
        "per_game": even_odd_counts,
        "avg_even": avg_even,
        "avg_odd": avg_odd,
        "avg_ratio": avg_ratio
    }

def generate_last_5_avg_game(lottery_type):
    """
    Gera um jogo baseado na média dos últimos 5 jogos
    
    Args:
        lottery_type (str): Tipo de loteria
        
    Returns:
        dict: Jogo gerado com base na média dos últimos 5 jogos
    """
    stats = analyze_last_5_games(lottery_type)
    
    if "error" in stats:
        return {"error": stats["error"]}
    
    game_info = SUPPORTED_GAMES[lottery_type]
    num_to_pick = game_info['numbers']
    
    # Obter pool de números sugeridos
    pool = stats["suggested_numbers_pool"]
    
    # Estratégia de seleção variada para cada jogo
    # Garantir diversidade nas sugestões
    
    # Determinar proporção de números quentes/mornos/frios
    hot_ratio = 0.5  # 50% de números quentes
    warm_ratio = 0.3  # 30% de números mornos
    cold_ratio = 0.2  # 20% de números frios
    
    # Adicionar variação aleatória às proporções
    variation = random.uniform(-0.1, 0.1)
    hot_ratio += variation
    warm_ratio -= variation / 2
    cold_ratio -= variation / 2
    
    # Garantir que as proporções são válidas
    total = hot_ratio + warm_ratio + cold_ratio
    hot_ratio /= total
    warm_ratio /= total
    cold_ratio /= total
    
    # Calcular quantos números de cada categoria
    hot_count = max(1, int(num_to_pick * hot_ratio))
    warm_count = max(1, int(num_to_pick * warm_ratio))
    cold_count = num_to_pick - hot_count - warm_count
    
    # Ajustar se não tivermos números suficientes em alguma categoria
    if len(pool["hot_numbers"]) < hot_count:
        hot_count = len(pool["hot_numbers"])
    
    if len(pool["warm_numbers"]) < warm_count:
        warm_count = len(pool["warm_numbers"])
        cold_count = num_to_pick - hot_count - warm_count
    
    if len(pool["cold_numbers"]) < cold_count:
        cold_count = len(pool["cold_numbers"])
        # Redistribuir os números restantes
        remaining = num_to_pick - hot_count - warm_count - cold_count
        if remaining > 0:
            if len(pool["hot_numbers"]) > hot_count:
                hot_count += remaining
            elif len(pool["warm_numbers"]) > warm_count:
                warm_count += remaining
    
    # Selecionar números de cada categoria
    selected_hot = random.sample(pool["hot_numbers"], hot_count) if hot_count > 0 else []
    selected_warm = random.sample(pool["warm_numbers"], warm_count) if warm_count > 0 else []
    selected_cold = random.sample(pool["cold_numbers"], cold_count) if cold_count > 0 else []
    
    # Combinar e garantir que temos números suficientes
    selected_numbers = selected_hot + selected_warm + selected_cold
    
    # Se ainda não tivermos números suficientes, adicionar aleatoriamente
    min_num, max_num = game_info['range']
    all_numbers = set(range(min_num, max_num + 1))
    used_numbers = set(selected_numbers)
    available_numbers = list(all_numbers - used_numbers)
    
    if len(selected_numbers) < num_to_pick:
        additional_needed = num_to_pick - len(selected_numbers)
        selected_numbers.extend(random.sample(available_numbers, additional_needed))
    
    # Criar o jogo
    game = {
        "numbers": sorted(selected_numbers),
        "strategy": "last_5_avg",
        "stats": {
            "hot_zones": stats["hot_zones"],
            "sum_statistics": stats["sum_statistics"],
            "even_odd_ratio": {
                "even": sum(1 for num in selected_numbers if num % 2 == 0),
                "odd": sum(1 for num in selected_numbers if num % 2 != 0)
            }
        }
    }
    
    # Adicionar trevos para +Milionária
    if lottery_type == "maismilionaria" and "trevos" in SUPPORTED_GAMES[lottery_type]:
        # Implementação simplificada para trevos
        trevos_to_pick = SUPPORTED_GAMES[lottery_type]["trevos"]
        min_trevo, max_trevo = SUPPORTED_GAMES[lottery_type]["trevos_range"]
        game["trevos"] = sorted(random.sample(range(min_trevo, max_trevo + 1), trevos_to_pick))
    
    # Adicionar Time do Coração para Timemania
    if lottery_type == "timemania" and "time_coracao" in SUPPORTED_GAMES[lottery_type]:
        # Lista simplificada de times
        times = ["FLAMENGO", "CORINTHIANS", "PALMEIRAS", "SÃO PAULO", "SANTOS", 
                "VASCO", "FLUMINENSE", "BOTAFOGO", "GRÊMIO", "INTERNACIONAL"]
        game["time_coracao"] = random.choice(times)
    
    return game
