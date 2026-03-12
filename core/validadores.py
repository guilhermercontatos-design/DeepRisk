# core/validadores.py - VALIDAÇÃO COM THE ODDS API (NÃO PODE FALHAR)
import requests
import time
import hashlib
import json
from datetime import datetime, timedelta

class ValidadorOdds:
    """
    Validador robusto com The Odds API
    Com cache inteligente e retry automático
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.cache = {}
        self.requisicoes_restantes = 500
        self.timeout = 10
        self.max_retries = 3
        
        # Headers para monitoramento
        self.headers = {
            'User-Agent': 'DeepRisk/4.0 (Analisador Profissional)'
        }
    
    def _fazer_requisicao(self, url, params, tentativa=1):
        """Faz requisição com retry automático e backoff exponencial"""
        
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Atualizar cotas
            if 'x-requests-remaining' in response.headers:
                self.requisicoes_restantes = int(response.headers['x-requests-remaining'])
            
            # Se deu certo
            if response.status_code == 200:
                return response.json()
            
            # Se erro de rate limit, esperar e tentar de novo
            elif response.status_code == 429:
                if tentativa < self.max_retries:
                    wait_time = (2 ** tentativa) * 5  # 10s, 20s, 40s
                    time.sleep(wait_time)
                    return self._fazer_requisicao(url, params, tentativa + 1)
                else:
                    return None
            
            # Outros erros
            else:
                return None
                
        except requests.exceptions.Timeout:
            if tentativa < self.max_retries:
                wait_time = (2 ** tentativa) * 2
                time.sleep(wait_time)
                return self._fazer_requisicao(url, params, tentativa + 1)
            return None
            
        except Exception as e:
            return None
    
    def buscar_odds_mercado(self, sport_key):
        """Busca odds atuais para um esporte"""
        
        # Verificar cache (5 minutos)
        cache_key = f"odds_{sport_key}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if datetime.now() - cache_time < timedelta(minutes=5):
                return cache_data
        
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "eu,uk,us,au,br",  # Múltiplas regiões
            "markets": "h2h,spreads,totals",  # Múltiplos mercados
            "oddsFormat": "decimal"
        }
        
        data = self._fazer_requisicao(url, params)
        
        if data:
            self.cache[cache_key] = (datetime.now(), data)
        
        return data
    
    def buscar_odds_evento_especifico(self, sport_key, event_id):
        """Busca odds de um evento específico"""
        
        url = f"{self.base_url}/sports/{sport_key}/events/{event_id}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "eu,uk,us,au,br",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
        
        return self._fazer_requisicao(url, params)
    
    def encontrar_evento_por_nome(self, eventos, nome_busca):
        """Encontra evento por nome (com fuzzy matching)"""
        nome_busca = nome_busca.lower()
        
        for evento in eventos:
            home = evento.get('home_team', '').lower()
            away = evento.get('away_team', '').lower()
            evento_nome = f"{home} vs {away}"
            
            # Verificar correspondência
            if home in nome_busca or away in nome_busca:
                return evento
            
            # Verificar similaridade (básica)
            palavras_busca = set(nome_busca.split())
            palavras_evento = set(evento_nome.split())
            
            if len(palavras_busca & palavras_evento) >= 2:
                return evento
        
        return None
    
    def calcular_estatisticas_odds(self, evento):
        """Calcula estatísticas das odds para um evento"""
        
        odds_list = []
        bookmakers_list = []
        
        for bookmaker in evento.get('bookmakers', []):
            nome_casa = bookmaker.get('title', 'Desconhecido')
            
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    odds_list.append(outcome['price'])
                    bookmakers_list.append({
                        'casa': nome_casa,
                        'mercado': outcome.get('name', ''),
                        'odds': outcome['price']
                    })
        
        if not odds_list:
            return None
        
        odds_array = sorted(odds_list)
        
        return {
            'media': sum(odds_list) / len(odds_list),
            'mediana': odds_array[len(odds_array)//2] if odds_array else 0,
            'min': min(odds_list),
            'max': max(odds_list),
            'q1': odds_array[len(odds_array)//4] if len(odds_array) >= 4 else min(odds_list),
            'q3': odds_array[3*len(odds_array)//4] if len(odds_array) >= 4 else max(odds_list),
            'std': (sum((x - (sum(odds_list)/len(odds_list)))**2 for x in odds_list) / len(odds_list))**0.5,
            'total_odds': len(odds_list),
            'total_bookmakers': len(set(b['casa'] for b in bookmakers_list)),
            'bookmakers': bookmakers_list[:10]  # Top 10
        }
    
    def validar_aposta(self, sport_key, nome_evento, odds_apostada, bet_id=None):
        """Valida uma aposta específica contra o mercado"""
        
        # Buscar odds do mercado
        dados_mercado = self.buscar_odds_mercado(sport_key)
        
        if not dados_mercado:
            return None
        
        # Encontrar o evento
        evento = self.encontrar_evento_por_nome(dados_mercado, nome_evento)
        
        if not evento:
            return None
        
        # Calcular estatísticas
        stats = self.calcular_estatisticas_odds(evento)
        
        if not stats:
            return None
        
        # Calcular desvios
        desvio_media = ((odds_apostada - stats['media']) / stats['media']) * 100
        desvio_mediana = ((odds_apostada - stats['mediana']) / stats['mediana']) * 100
        desvio_min = ((odds_apostada - stats['min']) / stats['min']) * 100
        desvio_max = ((odds_apostada - stats['max']) / stats['max']) * 100
        
        # Classificar
        if abs(desvio_media) > 20:
            classificacao = '🚨 CRÍTICO - MUITO ACIMA DO MERCADO' if desvio_media > 0 else '⚠️ MUITO ABAIXO DO MERCADO'
        elif abs(desvio_media) > 10:
            classificacao = '🔍 DESVIO SIGNIFICATIVO' if desvio_media > 0 else '📉 ABAIXO DO MERCADO'
        else:
            classificacao = '✅ DENTRO DO NORMAL'
        
        # Percentil aproximado
        odds_menores = sum(1 for o in stats['bookmakers'] if o['odds'] < odds_apostada)
        percentil = (odds_menores / stats['total_odds']) * 100 if stats['total_odds'] > 0 else 50
        
        return {
            'bet_id': bet_id,
            'evento': nome_evento,
            'odds_apostada': odds_apostada,
            'odds_media': round(stats['media'], 2),
            'odds_mediana': round(stats['mediana'], 2),
            'odds_min': stats['min'],
            'odds_max': stats['max'],
            'desvio_percentual': round(desvio_media, 1),
            'desvio_absoluto': round(odds_apostada - stats['media'], 2),
            'classificacao': classificacao,
            'percentil': round(percentil, 1),
            'total_odds_mercado': stats['total_odds'],
            'total_bookmakers': stats['total_bookmakers'],
            'timestamp': datetime.now().isoformat()
        }
    
    def validar_multiplas_apostas(self, apostas_df, mapping_ligas):
        """Valida múltiplas apostas de uma vez"""
        
        resultados = []
        
        for idx, aposta in apostas_df.iterrows():
            liga = aposta.get('Bet champs', '')
            sport_key = mapping_ligas.get(liga)
            
            if sport_key:
                odds_apostada = float(aposta['Bet prices'])
                nome_evento = aposta['Bet events']
                bet_id = aposta.get('Bet id', f'aposta_{idx}')
                
                resultado = self.validar_aposta(
                    sport_key, nome_evento, odds_apostada, bet_id
                )
                
                if resultado:
                    resultados.append(resultado)
                
                time.sleep(0.2)  # Rate limiting
            
            if idx % 10 == 0:
                time.sleep(1)  # Pausa a cada 10 requisições
        
        return resultados
    
    def verificar_health(self):
        """Verifica saúde da API e cotas restantes"""
        
        url = f"{self.base_url}/sports"
        params = {"apiKey": self.api_key}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            
            return {
                'status': 'OK',
                'requisicoes_restantes': remaining,
                'requisicoes_usadas': used,
                'total_esportes': len(response.json())
            }
        else:
            return {
                'status': 'ERROR',
                'codigo': response.status_code,
                'mensagem': response.text[:100]
            }
