import requests
import json
import random
from collections import Counter
import sqlite3
import os

# Configurações
DB_NAME = "lottery_history.db"
API_BASE_URL = "https://loteriascaixa-api.herokuapp.com/api"

SUPPORTED_GAMES = {
    "megasena": {"name": "Mega-Sena", "numbers": 6, "range": (1, 60)},
    "quina": {"name": "Quina", "numbers": 5, "range": (1, 80)},
    "lotofacil": {"name": "Lotofácil", "numbers": 15, "range": (1, 25)},
    "maismilionaria": {"name": "Mais Milionária", "numbers": 6, "range": (1, 50), "trevos": 2, "trevos_range": (1, 6)},
    "timemania": {"name": "Timemania", "numbers": 10, "range": (1, 80), "time_coracao": True},
}

def fetch_results(lottery_name, contest_number=None):
    """Busca resultados de um concurso específico ou o último resultado."""
    if contest_number:
        url = f"{API_BASE_URL}/{lottery_name}/{contest_number}"
    else:
        url = f"{API_BASE_URL}/{lottery_name}/latest"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar resultados para {lottery_name} (concurso {contest_number}): {e}")
        return None

def fetch_last_n_results(lottery_name, n=10):
    """Busca os últimos N resultados de uma loteria."""
    latest_data = fetch_results(lottery_name)
    if not latest_data or 'concurso' not in latest_data:
        return []
    
    last_contest = latest_data['concurso']
    all_results = []
    for i in range(max(1, last_contest - n + 1), last_contest + 1):
        result = fetch_results(lottery_name, i)
        if result:
            all_results.append(result)
    return all_results

def calculate_statistics(results):
    """Calcula estatísticas básicas (frequência, atraso) a partir dos resultados."""
    if not results:
        return {"frequency": Counter(), "delay": {}}

    all_numbers = [] 
    last_occurrence = {}
    latest_contest = results[-1]['concurso']

    # Determina o range máximo baseado nos dados
    max_num = 0
    for result in results:
        if 'dezenas' in result:
            all_numbers.extend([int(n) for n in result['dezenas']])
            current_max = max([int(n) for n in result['dezenas']])
            if current_max > max_num:
                max_num = current_max
            
            contest = result['concurso']
            for num in result['dezenas']:
                num_int = int(num)
                last_occurrence[num_int] = contest

    frequency = Counter(all_numbers)
    
    # Calcula o atraso (delay)
    delay = {}
    if max_num > 0:
        for i in range(1, max_num + 1):
            if i in last_occurrence:
                delay[i] = latest_contest - last_occurrence[i]
            else:
                delay[i] = len(results)

    return {"frequency": frequency, "delay": delay}

def generate_numbers(lottery_name, num_games=1, strategy="random", user_history=None):
    """Gera jogos com base em uma estratégia."""
    if lottery_name not in SUPPORTED_GAMES:
        return []

    game_info = SUPPORTED_GAMES[lottery_name]
    num_to_pick = game_info['numbers']
    min_num, max_num = game_info['range']
    
    generated_games = []

    # Implementação básica de estratégias
    if strategy == "random":
        for _ in range(num_games):
            game = sorted(random.sample(range(min_num, max_num + 1), num_to_pick))
            
            # Considerar trevos para +Milionária
            if 'trevos' in game_info:
                trevos_to_pick = game_info['trevos']
                min_trevo, max_trevo = game_info['trevos_range']
                trevos = sorted(random.sample(range(min_trevo, max_trevo + 1), trevos_to_pick))
                generated_games.append({"numbers": game, "trevos": trevos})
            # Considerar Time do Coração para Timemania
            elif 'time_coracao' in game_info:
                 # Lista simplificada de times
                 times = ["FLAMENGO", "CORINTHIANS", "PALMEIRAS", "SÃO PAULO", "SANTOS", 
                          "VASCO", "FLUMINENSE", "BOTAFOGO", "GRÊMIO", "INTERNACIONAL"]
                 time = random.choice(times)
                 generated_games.append({"numbers": game, "time_coracao": time})
            else:
                generated_games.append({"numbers": game})
    
    elif strategy == "hot_numbers" and user_history:
        # Implementação simplificada usando números mais frequentes
        results = fetch_last_n_results(lottery_name, 20)
        if results:
            stats = calculate_statistics(results)
            hot_numbers = [num for num, _ in stats['frequency'].most_common(max_num)]
            
            for _ in range(num_games):
                # Garantir que temos números suficientes
                if len(hot_numbers) >= num_to_pick:
                    game = sorted(random.sample(hot_numbers[:num_to_pick*2], num_to_pick))
                else:
                    game = sorted(random.sample(range(min_num, max_num + 1), num_to_pick))
                
                # Lógica para trevos e time do coração (igual à estratégia random)
                if 'trevos' in game_info:
                    trevos_to_pick = game_info['trevos']
                    min_trevo, max_trevo = game_info['trevos_range']
                    trevos = sorted(random.sample(range(min_trevo, max_trevo + 1), trevos_to_pick))
                    generated_games.append({"numbers": game, "trevos": trevos})
                elif 'time_coracao' in game_info:
                    times = ["FLAMENGO", "CORINTHIANS", "PALMEIRAS", "SÃO PAULO", "SANTOS", 
                             "VASCO", "FLUMINENSE", "BOTAFOGO", "GRÊMIO", "INTERNACIONAL"]
                    time = random.choice(times)
                    generated_games.append({"numbers": game, "time_coracao": time})
                else:
                    generated_games.append({"numbers": game})
        else:
            # Fallback para aleatório se não conseguir obter resultados
            return generate_numbers(lottery_name, num_games, "random")
    
    else:
        # Fallback para aleatório se a estratégia não for reconhecida
        return generate_numbers(lottery_name, num_games, "random")

    return generated_games

def check_hits(played_game, official_result):
    """Verifica quantos números foram acertados em um jogo."""
    if not official_result or 'dezenas' not in official_result:
        return None

    if 'numbers' not in played_game:
        return None

    played_numbers = set(played_game['numbers'])
    official_numbers = set([int(n) for n in official_result['dezenas']])
    
    hits = len(played_numbers.intersection(official_numbers))
    
    result_info = {
        "hits": hits,
        "played_numbers": sorted(list(played_numbers)),
        "official_numbers": sorted(list(official_numbers))
    }

    # Tratamento específico para +Milionária (trevos)
    if 'trevos' in played_game and 'trevos' in official_result and official_result['trevos']:
        played_trevos = set(played_game['trevos'])
        official_trevos = set([int(t) for t in official_result['trevos']])
        trevo_hits = len(played_trevos.intersection(official_trevos))
        result_info["trevo_hits"] = trevo_hits
        result_info["played_trevos"] = sorted(list(played_trevos))
        result_info["official_trevos"] = sorted(list(official_trevos))

    # Tratamento específico para Timemania (Time do Coração)
    if 'time_coracao' in played_game and 'timeCoracao' in official_result and official_result['timeCoracao']:
        time_hit = played_game['time_coracao'] == official_result['timeCoracao']
        result_info["time_hit"] = time_hit
        result_info["played_time"] = played_game['time_coracao']
        result_info["official_time"] = official_result['timeCoracao']
        
    # Adicionar informações sobre premiação
    if 'premiacoes' in official_result:
        result_info['prize_info'] = official_result['premiacoes']

    return result_info

# Funções para gerenciamento do histórico
def init_db():
    """Inicializa o banco de dados SQLite e cria a tabela de histórico se não existir."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lottery_type TEXT NOT NULL,
            contest_number INTEGER,
            played_numbers TEXT NOT NULL,
            played_trevos TEXT,
            played_time TEXT,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            official_numbers TEXT,
            official_trevos TEXT,
            official_time TEXT,
            hits INTEGER,
            trevo_hits INTEGER,
            time_hit BOOLEAN,
            prize_info TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_game(lottery_type, contest_number, played_game):
    """Salva um jogo realizado no histórico."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    played_numbers_str = json.dumps(sorted(played_game.get("numbers", [])))
    played_trevos_str = json.dumps(sorted(played_game.get("trevos", []))) if "trevos" in played_game else None
    played_time = played_game.get("time_coracao")

    cursor.execute("""
        INSERT INTO game_history 
            (lottery_type, contest_number, played_numbers, played_trevos, played_time)
        VALUES (?, ?, ?, ?, ?)
    """, (lottery_type, contest_number, played_numbers_str, played_trevos_str, played_time))
    
    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return game_id

def update_game_result(game_id, check_result):
    """Atualiza um jogo no histórico com os resultados da verificação."""
    if not check_result:
        return False
        
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    official_numbers_str = json.dumps(check_result.get("official_numbers", []))
    official_trevos_str = json.dumps(check_result.get("official_trevos", [])) if "official_trevos" in check_result else None
    official_time = check_result.get("official_time")
    hits = check_result.get("hits")
    trevo_hits = check_result.get("trevo_hits")
    time_hit = check_result.get("time_hit")
    prize_info_str = json.dumps(check_result.get("prize_info", {}))

    cursor.execute("""
        UPDATE game_history 
        SET official_numbers = ?, official_trevos = ?, official_time = ?, 
            hits = ?, trevo_hits = ?, time_hit = ?, prize_info = ?
        WHERE id = ?
    """, (official_numbers_str, official_trevos_str, official_time, 
          hits, trevo_hits, time_hit, prize_info_str, game_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_history(lottery_type=None, limit=50):
    """Busca o histórico de jogos, opcionalmente filtrado por tipo de loteria."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM game_history"
    params = []
    if lottery_type:
        query += " WHERE lottery_type = ?"
        params.append(lottery_type)
        
    query += " ORDER BY date_played DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    history = cursor.fetchall()
    conn.close()
    
    # Converte as linhas do DB para dicionários
    return [dict(row) for row in history]

# Inicializar o DB ao carregar o módulo
init_db()
