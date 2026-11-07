"""Dados didáticos e consultas de agregação do Projeto 10."""
from datetime import datetime, timedelta, timezone

# Cada linha representa uma venda: código, categoria, produto,
# quantidade, preço unitário EM CENTAVOS e data (AAAA-MM-DD).
# Os cinco primeiros produtos seguem os exemplos do professor.
VENDAS_DIDATICAS = [
    ('V001', 'Informática', 'Teclado', 2, 8990, '2026-09-05'),
    ('V002', 'Informática', 'Mouse', 4, 4590, '2026-09-07'),
    ('V003', 'Papelaria', 'Caderno', 5, 2490, '2026-09-12'),
    ('V004', 'Papelaria', 'Caneta', 20, 350, '2026-09-18'),
    ('V005', 'Informática', 'Monitor', 1, 89900, '2026-09-22'),
    ('V006', 'Informática', 'Teclado', 3, 8990, '2026-10-03'),
    ('V007', 'Informática', 'Mouse', 8, 4590, '2026-10-07'),
    ('V008', 'Papelaria', 'Caderno', 7, 2490, '2026-10-10'),
    ('V009', 'Papelaria', 'Caneta', 12, 350, '2026-10-14'),
    ('V010', 'Acessórios', 'Garrafa', 4, 3990, '2026-10-18'),
    ('V011', 'Acessórios', 'Mochila', 3, 12990, '2026-10-20'),
    ('V012', 'Informática', 'Monitor', 2, 89900, '2026-10-23'),
    ('V013', 'Acessórios', 'Garrafa', 5, 3990, '2026-11-01'),
    ('V014', 'Acessórios', 'Mochila', 2, 12990, '2026-11-03'),
    ('V015', 'Papelaria', 'Caderno', 6, 2490, '2026-11-05'),
    ('V016', 'Informática', 'Mouse', 7, 4590, '2026-11-06'),
]


def ler_data(texto):
    """Converte AAAA-MM-DD para datetime UTC. Rejeita datas inválidas."""
    try:
        return datetime.strptime(texto, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError as erro:
        raise ValueError(f'Data inválida: {texto}. Use AAAA-MM-DD.') from erro


def popular_vendas(colecao):
    """Insere ou ATUALIZA exemplos pelo código, sem criar duplicatas."""
    colecao.create_index('codigo', unique=True)
    novos = 0

    for codigo, categoria, produto, quantidade, preco_centavos, data in VENDAS_DIDATICAS:
        registro = {
            'codigo': codigo,
            'categoria': categoria,
            'produto': produto,
            'quantidade': quantidade,
            'preco_unitario_centavos': preco_centavos,
            'total_centavos': quantidade * preco_centavos,
            'data': ler_data(data),
        }
        resultado = colecao.update_one(
            {'codigo': codigo},
            {'$set': registro},
            upsert=True,
        )
        if resultado.upserted_id is not None:
            novos += 1

    return novos


def criar_filtro_periodo(inicio=None, fim=None):
    """Cria $gte/$lt, incluindo o dia final inteiro no período."""
    if not inicio and not fim:
        return {}

    filtro_data = {}
    if inicio:
        filtro_data['$gte'] = ler_data(inicio)
    if fim:
        # O filtro usa < 00:00 do dia seguinte, então inclui todo o dia final.
        filtro_data['$lt'] = ler_data(fim) + timedelta(days=1)
    if inicio and fim and ler_data(inicio) > ler_data(fim):
        raise ValueError('A data inicial não pode ser maior que a data final.')

    return {'data': filtro_data}


def resumo_por_categoria(colecao, filtro):
    """Agrupa o faturamento em centavos e unidades por categoria no MongoDB."""
    pipeline = [
        {'$match': filtro},
        {'$group': {
            '_id': '$categoria',
            'faturamento': {'$sum': '$total_centavos'},
            'unidades': {'$sum': '$quantidade'},
        }},
        {'$sort': {'faturamento': -1, '_id': 1}},
    ]
    return list(colecao.aggregate(pipeline))


def cinco_produtos_mais_vendidos(colecao, filtro):
    """Top 5 POR UNIDADES vendidas, não por faturamento."""
    pipeline = [
        {'$match': filtro},
        {'$group': {
            '_id': '$produto',
            'unidades': {'$sum': '$quantidade'},
            'faturamento': {'$sum': '$total_centavos'},
        }},
        {'$sort': {'unidades': -1, 'faturamento': -1, '_id': 1}},
        {'$limit': 5},
    ]
    return list(colecao.aggregate(pipeline))
