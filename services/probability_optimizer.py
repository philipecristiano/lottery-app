"""
Módulo de otimização de probabilidade para loterias
Implementa algoritmos para maximizar a probabilidade de prêmio total
"""

import random
import numpy as np
from collections import Counter
from src.services.analyzer import fetch_last_n_results, SUPPORTED_GAMES

class ProbabilityOptimizer:
    """
    Classe para otimização de probabilidade de jogos de loteria
    """
    
    def __init__(self, lottery_type):
        """
        Inicializa o otimizador para um tipo específico de loteria
        
        Args:
            lottery_type (str): Tipo de loteria (megasena, lotofacil, etc.)
        """
        self.lottery_type = lottery_type
        self.game_info = SUPPORTED_GAMES.get(lottery_type)
        
        if not self.game_info:
            raise ValueError(f"Loteria {lottery_type} não suportada")
        
        # Carregar dados históricos
        self.historical_data = self._load_historical_data()
        
        # Inicializar métricas
        self.metrics = self._calculate_metrics()
    
    def _load_historical_data(self, num_results=100):
        """
        Carrega dados históricos para análise
        
        Args:
            num_results (int): Número de resultados a carregar
            
        Returns:
            list: Lista de resultados históricos
        """
        results = fetch_last_n_results(self.lottery_type, num_results)
        
        # Extrair números sorteados
        drawn_numbers = []
        for result in results:
            if 'dezenas' in result:
                drawn_numbers.append([int(n) for n in result['dezenas']])
        
        return drawn_numbers
    
    def _calculate_metrics(self):
        """
        Calcula métricas importantes para otimização
        
        Returns:
            dict: Métricas calculadas
        """
        if not self.historical_data:
            return {}
        
        # Frequência de cada número
        all_numbers = [num for game in self.historical_data for num in game]
        frequency = Counter(all_numbers)
        
        # Calcular atraso de cada número
        delay = {}
        min_num, max_num = self.game_info['range']
        for num in range(min_num, max_num + 1):
            delay[num] = 0
            
        for i, game in enumerate(self.historical_data):
            for num in range(min_num, max_num + 1):
                if num in game:
                    break
                delay[num] += 1
        
        # Calcular distribuição de pares/ímpares
        even_odd_distribution = []
        for game in self.historical_data:
            even_count = len([n for n in game if n % 2 == 0])
            odd_count = len(game) - even_count
            even_odd_distribution.append((even_count, odd_count))
        
        # Calcular distribuição por dezenas
        decade_distribution = []
        for game in self.historical_data:
            decades = {}
            for n in range(min_num, max_num + 1, 10):
                decade = f"{n}-{min(n+9, max_num)}"
                decades[decade] = 0
            
            for num in game:
                decade_start = (num // 10) * 10
                if decade_start == 0:
                    decade_start = 1
                decade_end = min(decade_start + 9, max_num)
                decade = f"{decade_start}-{decade_end}"
                decades[decade] = decades.get(decade, 0) + 1
            
            decade_distribution.append(decades)
        
        # Calcular somas e médias
        sums = [sum(game) for game in self.historical_data]
        
        # Calcular sequências
        sequences = []
        for game in self.historical_data:
            sorted_game = sorted(game)
            seq_count = 0
            for i in range(len(sorted_game) - 1):
                if sorted_game[i + 1] - sorted_game[i] == 1:
                    seq_count += 1
            sequences.append(seq_count)
        
        # Calcular repetições entre jogos consecutivos
        repetitions = []
        for i in range(len(self.historical_data) - 1):
            current = set(self.historical_data[i])
            next_game = set(self.historical_data[i + 1])
            repetitions.append(len(current.intersection(next_game)))
        
        return {
            'frequency': frequency,
            'delay': delay,
            'even_odd_distribution': even_odd_distribution,
            'decade_distribution': decade_distribution,
            'sums': sums,
            'sequences': sequences,
            'repetitions': repetitions
        }
    
    def generate_optimized_game(self):
        """
        Gera um jogo otimizado para maximizar a probabilidade de prêmio total
        
        Returns:
            dict: Jogo otimizado
        """
        if not self.metrics:
            return {"error": "Não foi possível calcular métricas para otimização"}
        
        # Parâmetros do jogo
        min_num, max_num = self.game_info['range']
        num_to_pick = self.game_info['numbers']
        
        # Calcular pontuação para cada número
        scores = {}
        for num in range(min_num, max_num + 1):
            # Pontuação baseada em frequência (normalizada)
            freq_score = self.metrics['frequency'].get(num, 0) / max(self.metrics['frequency'].values()) if self.metrics['frequency'] else 0
            
            # Pontuação baseada em atraso (normalizada)
            delay_score = self.metrics['delay'].get(num, 0) / max(self.metrics['delay'].values()) if self.metrics['delay'] else 0
            
            # Combinar pontuações (pesos ajustáveis)
            # Frequência tem peso maior para números que aparecem mais
            # Atraso tem peso maior para números que estão atrasados
            scores[num] = freq_score * 0.6 + delay_score * 0.4
        
        # Determinar distribuição ideal de pares/ímpares
        even_odd_counts = [count for count, _ in self.metrics['even_odd_distribution']]
        ideal_even = int(np.median([count for count in even_odd_counts]))
        ideal_odd = num_to_pick - ideal_even
        
        # Determinar soma ideal
        ideal_sum = int(np.median(self.metrics['sums']))
        
        # Determinar número ideal de sequências
        ideal_sequences = int(np.median(self.metrics['sequences']))
        
        # Gerar múltiplos jogos candidatos
        num_candidates = 100
        candidates = []
        
        for _ in range(num_candidates):
            # Gerar jogo candidato
            candidate = self._generate_candidate(scores, ideal_even, ideal_odd, ideal_sum, ideal_sequences)
            
            # Calcular pontuação do candidato
            score = self._score_candidate(candidate, ideal_even, ideal_odd, ideal_sum, ideal_sequences)
            
            candidates.append((candidate, score))
        
        # Selecionar o melhor candidato
        best_candidate, best_score = max(candidates, key=lambda x: x[1])
        
        # Criar o jogo
        game = {
            "numbers": sorted(best_candidate),
            "strategy": "optimized",
            "optimization_score": best_score,
            "stats": {
                "even_odd_ratio": {
                    "even": len([n for n in best_candidate if n % 2 == 0]),
                    "odd": len([n for n in best_candidate if n % 2 != 0])
                },
                "sum": sum(best_candidate),
                "sequences": self._count_sequences(best_candidate),
                "decade_distribution": self._get_decade_distribution(best_candidate)
            }
        }
        
        # Adicionar trevos para +Milionária
        if self.lottery_type == "maismilionaria" and "trevos" in self.game_info:
            trevos_to_pick = self.game_info["trevos"]
            min_trevo, max_trevo = self.game_info["trevos_range"]
            game["trevos"] = sorted(random.sample(range(min_trevo, max_trevo + 1), trevos_to_pick))
        
        # Adicionar Time do Coração para Timemania
        if self.lottery_type == "timemania" and "time_coracao" in self.game_info:
            times = ["FLAMENGO", "CORINTHIANS", "PALMEIRAS", "SÃO PAULO", "SANTOS", 
                    "VASCO", "FLUMINENSE", "BOTAFOGO", "GRÊMIO", "INTERNACIONAL"]
            game["time_coracao"] = random.choice(times)
        
        return game
    
    def _generate_candidate(self, scores, ideal_even, ideal_odd, ideal_sum, ideal_sequences):
        """
        Gera um jogo candidato com base nas pontuações e métricas ideais
        
        Args:
            scores (dict): Pontuações para cada número
            ideal_even (int): Quantidade ideal de números pares
            ideal_odd (int): Quantidade ideal de números ímpares
            ideal_sum (int): Soma ideal dos números
            ideal_sequences (int): Quantidade ideal de sequências
            
        Returns:
            list: Jogo candidato
        """
        min_num, max_num = self.game_info['range']
        num_to_pick = self.game_info['numbers']
        
        # Separar números pares e ímpares
        even_numbers = [(num, scores[num]) for num in range(min_num, max_num + 1) if num % 2 == 0]
        odd_numbers = [(num, scores[num]) for num in range(min_num, max_num + 1) if num % 2 != 0]
        
        # Ordenar por pontuação
        even_numbers.sort(key=lambda x: x[1], reverse=True)
        odd_numbers.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar números com base nas quantidades ideais
        selected_even = [num for num, _ in even_numbers[:ideal_even]]
        selected_odd = [num for num, _ in odd_numbers[:ideal_odd]]
        
        # Combinar e garantir que temos números suficientes
        candidate = selected_even + selected_odd
        
        # Se não tivermos números suficientes, adicionar mais
        if len(candidate) < num_to_pick:
            remaining = num_to_pick - len(candidate)
            available = [num for num in range(min_num, max_num + 1) if num not in candidate]
            candidate.extend(random.sample(available, remaining))
        
        # Se tivermos números demais, remover alguns
        if len(candidate) > num_to_pick:
            candidate = random.sample(candidate, num_to_pick)
        
        return candidate
    
    def _score_candidate(self, candidate, ideal_even, ideal_odd, ideal_sum, ideal_sequences):
        """
        Calcula a pontuação de um jogo candidato
        
        Args:
            candidate (list): Jogo candidato
            ideal_even (int): Quantidade ideal de números pares
            ideal_odd (int): Quantidade ideal de números ímpares
            ideal_sum (int): Soma ideal dos números
            ideal_sequences (int): Quantidade ideal de sequências
            
        Returns:
            float: Pontuação do candidato
        """
        # Contar números pares e ímpares
        even_count = len([n for n in candidate if n % 2 == 0])
        odd_count = len(candidate) - even_count
        
        # Calcular diferença em relação ao ideal
        even_diff = abs(even_count - ideal_even)
        odd_diff = abs(odd_count - ideal_odd)
        
        # Calcular soma
        sum_value = sum(candidate)
        sum_diff = abs(sum_value - ideal_sum)
        
        # Calcular sequências
        sequences = self._count_sequences(candidate)
        seq_diff = abs(sequences - ideal_sequences)
        
        # Calcular distribuição por dezenas
        decade_dist = self._get_decade_distribution(candidate)
        decades_used = len([d for d in decade_dist.values() if d > 0])
        
        # Calcular pontuação final (quanto menor a diferença, melhor)
        score = (
            (1 / (even_diff + 1)) * 25 +  # 25% para distribuição par/ímpar
            (1 / (sum_diff + 1)) * 25 +   # 25% para soma
            (1 / (seq_diff + 1)) * 25 +   # 25% para sequências
            (decades_used / len(decade_dist)) * 25  # 25% para distribuição por dezenas
        )
        
        return score
    
    def _count_sequences(self, numbers):
        """
        Conta o número de sequências em um jogo
        
        Args:
            numbers (list): Lista de números
            
        Returns:
            int: Número de sequências
        """
        sorted_numbers = sorted(numbers)
        sequences = 0
        
        for i in range(len(sorted_numbers) - 1):
            if sorted_numbers[i + 1] - sorted_numbers[i] == 1:
                sequences += 1
        
        return sequences
    
    def _get_decade_distribution(self, numbers):
        """
        Calcula a distribuição por dezenas de um jogo
        
        Args:
            numbers (list): Lista de números
            
        Returns:
            dict: Distribuição por dezenas
        """
        min_num, max_num = self.game_info['range']
        decades = {}
        
        for n in range(min_num, max_num + 1, 10):
            decade = f"{n}-{min(n+9, max_num)}"
            decades[decade] = 0
        
        for num in numbers:
            decade_start = (num // 10) * 10
            if decade_start == 0:
                decade_start = 1
            decade_end = min(decade_start + 9, max_num)
            decade = f"{decade_start}-{decade_end}"
            decades[decade] = decades.get(decade, 0) + 1
        
        return decades
    
    def get_detailed_analysis(self):
        """
        Retorna uma análise detalhada para determinar melhores estratégias
        
        Returns:
            dict: Análise detalhada
        """
        if not self.metrics:
            return {"error": "Não foi possível calcular métricas para análise"}
        
        min_num, max_num = self.game_info['range']
        
        # Análise de frequência
        frequency = self.metrics['frequency']
        sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Top 10 números mais frequentes
        hot_numbers = sorted_frequency[:10]
        
        # Top 10 números menos frequentes
        cold_numbers = sorted_frequency[-10:]
        
        # Análise de atraso
        delay = self.metrics['delay']
        sorted_delay = sorted(delay.items(), key=lambda x: x[1], reverse=True)
        
        # Top 10 números mais atrasados
        most_delayed = sorted_delay[:10]
        
        # Análise de distribuição par/ímpar
        even_odd_dist = self.metrics['even_odd_distribution']
        even_counts = [count for count, _ in even_odd_dist]
        odd_counts = [count for _, count in even_odd_dist]
        
        # Distribuição mais comum
        common_even = max(set(even_counts), key=even_counts.count)
        common_odd = max(set(odd_counts), key=odd_counts.count)
        
        # Análise de soma
        sums = self.metrics['sums']
        avg_sum = sum(sums) / len(sums) if sums else 0
        min_sum = min(sums) if sums else 0
        max_sum = max(sums) if sums else 0
        
        # Faixas de soma mais comuns
        sum_ranges = {}
        range_size = 20
        for s in sums:
            range_start = (s // range_size) * range_size
            range_end = range_start + range_size - 1
            range_key = f"{range_start}-{range_end}"
            sum_ranges[range_key] = sum_ranges.get(range_key, 0) + 1
        
        # Faixa de soma mais comum
        most_common_sum_range = max(sum_ranges.items(), key=lambda x: x[1]) if sum_ranges else None
        
        # Análise de sequências
        sequences = self.metrics['sequences']
        avg_sequences = sum(sequences) / len(sequences) if sequences else 0
        
        # Quantidade mais comum de sequências
        common_sequences = max(set(sequences), key=sequences.count) if sequences else 0
        
        # Análise de repetições entre jogos
        repetitions = self.metrics['repetitions']
        avg_repetitions = sum(repetitions) / len(repetitions) if repetitions else 0
        
        # Análise de distribuição por dezenas
        decade_dist = self.metrics['decade_distribution']
        
        # Calcular média de números por dezena
        avg_decade_dist = {}
        for decade_dict in decade_dist:
            for decade, count in decade_dict.items():
                if decade not in avg_decade_dist:
                    avg_decade_dist[decade] = []
                avg_decade_dist[decade].append(count)
        
        for decade, counts in avg_decade_dist.items():
            avg_decade_dist[decade] = sum(counts) / len(counts)
        
        # Dezenas mais e menos utilizadas
        sorted_decades = sorted(avg_decade_dist.items(), key=lambda x: x[1], reverse=True)
        most_used_decades = sorted_decades[:3]
        least_used_decades = sorted_decades[-3:]
        
        # Recomendações estratégicas
        recommendations = [
            f"Utilize aproximadamente {common_even} números pares e {common_odd} números ímpares",
            f"Busque uma soma total próxima de {int(avg_sum)}",
            f"Inclua cerca de {common_sequences} sequências (números consecutivos)",
            f"Distribua os números entre {len(most_used_decades)} e {len(sorted_decades)} dezenas diferentes",
            f"Priorize as dezenas {', '.join([decade for decade, _ in most_used_decades])}"
        ]
        
        return {
            "hot_numbers": hot_numbers,
            "cold_numbers": cold_numbers,
            "most_delayed": most_delayed,
            "even_odd_distribution": {
                "common_even": common_even,
                "common_odd": common_odd,
                "distribution": list(zip(even_counts, odd_counts))
            },
            "sum_statistics": {
                "average": avg_sum,
                "min": min_sum,
                "max": max_sum,
                "most_common_range": most_common_sum_range
            },
            "sequence_statistics": {
                "average": avg_sequences,
                "most_common": common_sequences
            },
            "repetition_statistics": {
                "average": avg_repetitions
            },
            "decade_distribution": {
                "average": avg_decade_dist,
                "most_used": most_used_decades,
                "least_used": least_used_decades
            },
            "recommendations": recommendations
        }

def generate_optimized_games(lottery_type, num_games=1):
    """
    Gera jogos otimizados para maximizar a probabilidade de prêmio total
    
    Args:
        lottery_type (str): Tipo de loteria
        num_games (int): Número de jogos a gerar
        
    Returns:
        list: Lista de jogos otimizados
    """
    try:
        optimizer = ProbabilityOptimizer(lottery_type)
        games = []
        
        for _ in range(num_games):
            game = optimizer.generate_optimized_game()
            games.append(game)
        
        return games
    except Exception as e:
        return [{"error": str(e)}]

def get_detailed_lottery_analysis(lottery_type):
    """
    Retorna uma análise detalhada para determinar melhores estratégias
    
    Args:
        lottery_type (str): Tipo de loteria
        
    Returns:
        dict: Análise detalhada
    """
    try:
        optimizer = ProbabilityOptimizer(lottery_type)
        return optimizer.get_detailed_analysis()
    except Exception as e:
        return {"error": str(e)}
