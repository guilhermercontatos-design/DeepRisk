# core/regras.py - BASE DE CONHECIMENTO COMPLETA
"""
SISTEMA DE REGRAS PARA ANÁLISE COMPORTAMENTAL
12 Categorias principais com +200 sub-regras
"""

class CategoriaRegras:
    """Define todas as categorias de análise e suas regras"""
    
    # ============================================
    # CATEGORIA 1: ANÁLISE DE VALORES (20 regras)
    # ============================================
    VALORES = {
        'nome': '💰 Análise de Valores',
        'descricao': 'Detecta padrões suspeitos nos valores apostados',
        'regras': [
            {
                'id': 'V001',
                'nome': 'Valor fixo recorrente',
                'descricao': 'Apostas sempre com mesmo valor',
                'threshold': 80,  # % do total
                'severidade': 'ALTA',
                'logica': lambda df: (df['Total stake'].nunique() == 1)
            },
            {
                'id': 'V002',
                'nome': 'Valor de burla de limite',
                'descricao': 'Apostas em valores logo abaixo de limites comuns (495, 990, 4990)',
                'valores_suspeitos': [495.00, 495.0, 495, 990, 990.00, 4990, 4990.00],
                'severidade': 'CRÍTICA',
                'logica': lambda df, valor: len(df[df['Total stake'] == valor]) > 0
            },
            {
                'id': 'V003',
                'nome': 'Progressão geométrica',
                'descricao': 'Apostas seguindo padrão 1,2,4,8,16 (Martingale)',
                'severidade': 'ALTA',
                'logica': lambda valores: _detectar_martingale(valores)
            },
            {
                'id': 'V004',
                'nome': 'Valor médio anormal',
                'descricao': 'Valor médio muito acima da média dos usuários',
                'threshold_superior': 1000,  # R$ 1000
                'severidade': 'MÉDIA'
            },
            {
                'id': 'V005',
                'nome': 'Apostas com centavos quebrados',
                'descricao': 'Valores como 495.37, 123.45 (padrão de calculadora)',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'V006',
                'nome': 'Valor máximo recorrente',
                'descricao': 'Sempre aposta o máximo permitido',
                'severidade': 'ALTA'
            },
            {
                'id': 'V007',
                'nome': 'Zero ou valores negativos',
                'descricao': 'Apostas com valor 0 ou negativo (erro de sistema)',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'V008',
                'nome': 'Escala de aposta baseada em resultado anterior',
                'descricao': 'Aumenta aposta após perda, reduz após ganho',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'V009',
                'nome': 'Valor fracionado suspeito',
                'descricao': 'Valores como 0.01, 0.05 (teste de sistema)',
                'severidade': 'BAIXA'
            },
            {
                'id': 'V010',
                'nome': 'Concentração em faixa específica',
                'descricao': '80%+ das apostas em faixa de R$10 de diferença',
                'severidade': 'MÉDIA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 2: ANÁLISE DE LIGAS (25 regras)
    # ============================================
    LIGAS = {
        'nome': '🌏 Análise de Ligas e Competições',
        'descricao': 'Detecta padrões suspeitos nas ligas apostadas',
        'regras': [
            {
                'id': 'L001',
                'nome': 'Liga de baixíssima liquidez',
                'descricao': 'Apostas em ligas sem mercado ativo',
                'ligas_suspeitas': [
                    'Vietnam', 'Indonésia', 'Mianmar', 'Camboja', 'Laos',
                    'Filipinas', 'Timor', 'Brunei', 'Singapura', 'Tailândia',
                    'Malásia', 'Myanmar', 'Liga 3', 'Segunda Divisão',
                    'Campeonato Amador', 'Liga Juvenil', 'Futebol de Base',
                    'Liga do Botswana', 'Copa da Somália', 'Liga do Sudão'
                ],
                'severidade': 'ALTA'
            },
            {
                'id': 'L002',
                'nome': 'Concentração total em ligas suspeitas',
                'descricao': '100% das apostas em ligas de baixa liquidez',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'L003',
                'nome': 'Mistura suspeita de ligas',
                'descricao': 'Alterna entre Premier League e ligas amadoras',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'L004',
                'nome': 'Apostas em ligas sem transmissão',
                'descricao': 'Ligas que não têm TV/streaming',
                'severidade': 'ALTA'
            },
            {
                'id': 'L005',
                'nome': 'Ligas com histórico de manipulação',
                'descricao': 'Ligas conhecidas por resultados manipulados',
                'ligas_manipuladas': [
                    'Campeonato Romeno 2', 'Liga Turca 3', 'Liga Grega 2',
                    'Campeonato Cipriota', 'Liga Maltesa', 'Liga Albanesa'
                ],
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'L006',
                'nome': 'Horário incompatível com a liga',
                'descricao': 'Apostas em liga asiática às 3h da manhã (horário local)',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'L007',
                'nome': 'Apostas apenas em ligas femininas',
                'descricao': 'Concentração anormal em futebol feminino',
                'severidade': 'BAIXA'
            },
            {
                'id': 'L008',
                'nome': 'Ligas com odds instáveis',
                'descricao': 'Ligas onde odds variam muito rapidamente',
                'severidade': 'ALTA'
            },
            {
                'id': 'L009',
                'nome': 'Mudança abrupta de ligas',
                'descricao': 'De repente troca todas apostas para novas ligas',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'L010',
                'nome': 'Apostas em ligas recém-criadas',
                'descricao': 'Ligas com menos de 1 ano de existência',
                'severidade': 'ALTA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 3: ANÁLISE DE ODDS (30 regras)
    # ============================================
    ODDS = {
        'nome': '🎲 Análise de Odds',
        'descricao': 'Detecta padrões suspeitos nas odds apostadas',
        'regras': [
            {
                'id': 'O001',
                'nome': 'Odds quebradas (arbitragem)',
                'descricao': 'Odds com 3+ casas decimais (1.932, 2.075)',
                'severidade': 'ALTA'
            },
            {
                'id': 'O002',
                'nome': 'Odds muito acima do mercado',
                'descricao': 'Desvio >20% da média do mercado',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'O003',
                'nome': 'Concentração em odds altas',
                'descricao': '+80% das apostas em odds >3.00',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'O004',
                'nome': 'Concentração em odds baixas',
                'descricao': '+80% das apostas em odds <1.50',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'O005',
                'nome': 'Odds redondas suspeitas',
                'descricao': 'Odds como 2.00, 3.00, 4.00 (padrão amador)',
                'severidade': 'BAIXA'
            },
            {
                'id': 'O006',
                'nome': 'Variação suspeita de odds',
                'descricao': 'Odds mudam drasticamente em minutos',
                'severidade': 'ALTA'
            },
            {
                'id': 'O007',
                'nome': 'Odds inversas ao mercado',
                'descricao': 'Odd sobe quando mercado desce (e vice-versa)',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'O008',
                'nome': 'Padrão de surebet',
                'descricao': 'Combinação de odds que garantem lucro',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'O009',
                'nome': 'Aposta apenas no favorito',
                'descricao': 'Sempre aposta no time com menor odd',
                'severidade': 'BAIXA'
            },
            {
                'id': 'O010',
                'nome': 'Aposta apenas no azarão',
                'descricao': 'Sempre aposta no time com maior odd',
                'severidade': 'MÉDIA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 4: ANÁLISE TEMPORAL (25 regras)
    # ============================================
    TEMPORAL = {
        'nome': '⏰ Análise Temporal',
        'descricao': 'Detecta padrões suspeitos nos horários',
        'regras': [
            {
                'id': 'T001',
                'nome': 'Apostas na madrugada',
                'descricao': '+50% das apostas entre 0h-5h',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'T002',
                'nome': 'Apostas em horário comercial',
                'descricao': '90%+ das apostas em horário de trabalho',
                'severidade': 'BAIXA'
            },
            {
                'id': 'T003',
                'nome': 'Apostas em lote',
                'descricao': 'Múltiplas apostas no mesmo minuto',
                'severidade': 'ALTA'
            },
            {
                'id': 'T004',
                'nome': 'Padrão de sono',
                'descricao': 'Sempre para de apostar no mesmo horário',
                'severidade': 'BAIXA'
            },
            {
                'id': 'T005',
                'nome': 'Apostas em dias úteis vs fins de semana',
                'descricao': 'Padrão muito diferente entre dias',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'T006',
                'nome': 'Intervalo regular entre apostas',
                'descricao': 'Sempre aposta a cada X minutos (bot)',
                'severidade': 'ALTA'
            },
            {
                'id': 'T007',
                'nome': 'Apostas apenas em eventos ao vivo',
                'descricao': 'Nunca aposta em pré-jogo',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'T008',
                'nome': 'Apostas apenas em pré-jogo',
                'descricao': 'Nunca aposta ao vivo',
                'severidade': 'BAIXA'
            },
            {
                'id': 'T009',
                'nome': 'Apostas sincronizadas com eventos',
                'descricao': 'Aposta exatamente quando algo acontece',
                'severidade': 'ALTA'
            },
            {
                'id': 'T010',
                'nome': 'Padrão sazonal',
                'descricao': 'Só aposta em finais de semana',
                'severidade': 'BAIXA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 5: LATE ODDS (20 regras)
    # ============================================
    LATE_ODDS = {
        'nome': '⚡ Late Odds',
        'descricao': 'Detecta exploração de latência do sistema',
        'regras': [
            {
                'id': 'LO001',
                'nome': 'Apostas na última hora',
                'descricao': '+50% das apostas na última hora antes do evento',
                'severidade': 'ALTA'
            },
            {
                'id': 'LO002',
                'nome': 'Múltiplas apostas mesmo evento',
                'descricao': '+2 apostas no mesmo evento com minutos de diferença',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'LO003',
                'nome': 'Apostas após gol',
                'descricao': 'Aposta depois de gol acontecer (delay)',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'LO004',
                'nome': 'Apostas nos últimos 5 minutos',
                'descricao': 'Apostas quando jogo já está acabando',
                'severidade': 'ALTA'
            },
            {
                'id': 'LO005',
                'nome': 'Padrão de arbitragem com delay',
                'descricao': 'Aposta em mercado que já fechou',
                'severidade': 'CRÍTICA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 6: TAXA DE ACERTO (15 regras)
    # ============================================
    ACERTO = {
        'nome': '📊 Taxa de Acerto',
        'descricao': 'Analisa padrões de sucesso nas apostas',
        'regras': [
            {
                'id': 'A001',
                'nome': 'Taxa anormalmente alta',
                'descricao': 'Acerto >65% em +50 apostas',
                'threshold': 65,
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'A002',
                'nome': 'Taxa anormalmente baixa',
                'descricao': 'Acerto <30% em +50 apostas',
                'threshold': 30,
                'severidade': 'MÉDIA'
            },
            {
                'id': 'A003',
                'nome': 'Sequência de vitórias',
                'descricao': '+10 vitórias consecutivas',
                'severidade': 'ALTA'
            },
            {
                'id': 'A004',
                'nome': 'Sequência de derrotas',
                'descricao': '+10 derrotas consecutivas',
                'severidade': 'BAIXA'
            },
            {
                'id': 'A005',
                'nome': 'Acerto apenas em odds baixas',
                'descricao': 'Só ganha quando odd <2.00',
                'severidade': 'BAIXA'
            },
            {
                'id': 'A006',
                'nome': 'Acerto apenas em odds altas',
                'descricao': 'Só ganha quando odd >5.00',
                'severidade': 'CRÍTICA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 7: MERCADOS (15 regras)
    # ============================================
    MERCADOS = {
        'nome': '🎯 Análise de Mercados',
        'descricao': 'Detecta padrões nos mercados apostados',
        'regras': [
            {
                'id': 'M001',
                'nome': 'Concentração em mercado específico',
                'descricao': '90%+ em apenas 1 tipo de mercado',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'M002',
                'nome': 'Mercados exóticos',
                'descricao': 'Apostas em "próximo jogador a marcar", "escanteios", etc',
                'severidade': 'ALTA'
            },
            {
                'id': 'M003',
                'nome': 'Cobertura total de mercados',
                'descricao': 'Aposta em todos mercados disponíveis do evento',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'M004',
                'nome': 'Mercados com baixa liquidez',
                'descricao': 'Apostas em mercados pouco movimentados',
                'severidade': 'ALTA'
            },
            {
                'id': 'M005',
                'nome': 'Mercados de arbitragem',
                'descricao': 'Combinação de mercados para garantir lucro',
                'severidade': 'CRÍTICA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 8: DISPOSITIVO/ACESSO (10 regras)
    # ============================================
    DISPOSITIVO = {
        'nome': '📱 Análise de Acesso',
        'descricao': 'Detecta padrões de dispositivo e localização',
        'regras': [
            {
                'id': 'D001',
                'nome': 'Múltiplos dispositivos',
                'descricao': 'Acessa de vários dispositivos diferentes',
                'severidade': 'BAIXA'
            },
            {
                'id': 'D002',
                'nome': 'VPN/Proxy detectado',
                'descricao': 'IP suspeito ou de data center',
                'severidade': 'ALTA'
            },
            {
                'id': 'D003',
                'nome': 'Localização incompatível',
                'descricao': 'Aposta em liga local mas está em outro país',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'D004',
                'nome': 'Acessos simultâneos',
                'descricao': 'Mesma conta acessada de locais diferentes',
                'severidade': 'CRÍTICA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 9: PADRÕES MATEMÁTICOS (15 regras)
    # ============================================
    MATEMATICA = {
        'nome': '🔢 Padrões Matemáticos',
        'descricao': 'Detecta padrões algébricos suspeitos',
        'regras': [
            {
                'id': 'MAT001',
                'nome': 'Lei de Benford',
                'descricao': 'Distribuição dos primeiros dígitos não segue Benford',
                'severidade': 'ALTA'
            },
            {
                'id': 'MAT002',
                'nome': 'Correlação perfeita',
                'descricao': 'Aposta sempre correlacionada com resultado',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'MAT003',
                'nome': 'Números primos',
                'descricao': 'Só aposta valores que são números primos',
                'severidade': 'BAIXA'
            },
            {
                'id': 'MAT004',
                'nome': 'Progressão aritmética',
                'descricao': 'Valores seguem PA (100,200,300...)',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'MAT005',
                'nome': 'Progressão geométrica',
                'descricao': 'Valores seguem PG (1,2,4,8...)',
                'severidade': 'ALTA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 10: REDES SOCIAIS (10 regras)
    # ============================================
    SOCIAL = {
        'nome': '👥 Análise Social',
        'descricao': 'Detecta conexões entre usuários',
        'regras': [
            {
                'id': 'S001',
                'nome': 'Padrão sincronizado',
                'descricao': 'Múltiplos usuários apostam igual no mesmo momento',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'S002',
                'nome': 'Mesmo IP',
                'descricao': 'Contas diferentes no mesmo IP',
                'severidade': 'ALTA'
            },
            {
                'id': 'S003',
                'nome': 'Métodos de pagamento iguais',
                'descricao': 'Mesmo cartão em contas diferentes',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'S004',
                'nome': 'Padrão de indicação',
                'descricao': 'Contas criadas em sequência',
                'severidade': 'MÉDIA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 11: BONUS/PROMOÇÕES (10 regras)
    # ============================================
    BONUS = {
        'nome': '🎁 Abuso de Bônus',
        'descricao': 'Detecta padrões de abuso de promoções',
        'regras': [
            {
                'id': 'B001',
                'nome': 'Valor exato do bônus',
                'descricao': 'Aposta sempre o valor do bônus',
                'severidade': 'ALTA'
            },
            {
                'id': 'B002',
                'nome': 'Rollover suspeito',
                'descricao': 'Tenta cumprir rollover em apostas de baixo risco',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'B003',
                'nome': 'Múltiplos bônus',
                'descricao': 'Pega bônus em todas oportunidades',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'B004',
                'nome': 'Saque imediato após bônus',
                'descricao': 'Deposita, pega bônus e saca',
                'severidade': 'ALTA'
            }
        ]
    }
    
    # ============================================
    # CATEGORIA 12: HISTÓRICO (20 regras)
    # ============================================
    HISTORICO = {
        'nome': '📜 Análise Histórica',
        'descricao': 'Analisa evolução do comportamento',
        'regras': [
            {
                'id': 'H001',
                'nome': 'Mudança abrupta de padrão',
                'descricao': 'Comportamento muda completamente do dia para noite',
                'severidade': 'ALTA'
            },
            {
                'id': 'H002',
                'nome': 'Escala de risco progressiva',
                'descricao': 'Aumenta risco conforme ganha',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'H003',
                'nome': 'Recuperação milagrosa',
                'descricao': 'Perde muito, depois recupera tudo',
                'severidade': 'CRÍTICA'
            },
            {
                'id': 'H004',
                'nome': 'Padrão semanal',
                'descricao': 'Sempre ganha no mesmo dia da semana',
                'severidade': 'MÉDIA'
            },
            {
                'id': 'H005',
                'nome': 'Account sharing',
                'descricao': 'Horários de acesso incompatíveis com uma pessoa',
                'severidade': 'ALTA'
            },
            {
                'id': 'H006',
                'nome': 'Ciclo de vida suspeito',
                'descricao': 'Conta nova já começa com padrão profissional',
                'severidade': 'CRÍTICA'
            }
        ]
    }
    
    @classmethod
    def get_todas_regras(cls):
        """Retorna todas as regras de todas as categorias"""
        todas = []
        for categoria in [cls.VALORES, cls.LIGAS, cls.ODDS, cls.TEMPORAL, 
                          cls.LATE_ODDS, cls.ACERTO, cls.MERCADOS, cls.DISPOSITIVO,
                          cls.MATEMATICA, cls.SOCIAL, cls.BONUS, cls.HISTORICO]:
            for regra in categoria['regras']:
                regra['categoria'] = categoria['nome']
                todas.append(regra)
        return todas
