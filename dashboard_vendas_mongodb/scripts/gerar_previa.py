"""Cria uma prévia visual sem MongoDB. NÃO substitui o teste no Atlas."""
from collections import defaultdict
from pathlib import Path

from p10_dashboard.dados import VENDAS_DIDATICAS
from p10_dashboard.relatorios import gerar_grafico, gerar_pdf, reais


def calcular_previa():
    por_categoria = defaultdict(lambda: {'faturamento': 0, 'unidades': 0})
    por_produto = defaultdict(lambda: {'faturamento': 0, 'unidades': 0})

    for _, categoria, produto, quantidade, preco_centavos, _ in VENDAS_DIDATICAS:
        total = quantidade * preco_centavos
        for grupo, chave in [(por_categoria, categoria), (por_produto, produto)]:
            grupo[chave]['faturamento'] += total
            grupo[chave]['unidades'] += quantidade

    categorias = [dict(_id=nome, **dados) for nome, dados in por_categoria.items()]
    categorias.sort(key=lambda d: (-d['faturamento'], d['_id']))
    produtos = [dict(_id=nome, **dados) for nome, dados in por_produto.items()]
    produtos.sort(key=lambda d: (-d['unidades'], -d['faturamento'], d['_id']))
    return categorias, produtos[:5]


def main():
    categorias, produtos = calcular_previa()
    pasta = Path(__file__).resolve().parent.parent / 'exemplos'
    grafico = gerar_grafico(categorias, pasta / 'previa_grafico.png',
                            'Todos os períodos', previa=True)
    pdf = gerar_pdf(categorias, produtos, len(VENDAS_DIDATICAS),
                    pasta / 'previa_relatorio.pdf', 'Todos os períodos', previa=True)
    print('PRÉVIA DIDÁTICA: números calculados localmente, NÃO consultados do Atlas!')
    print('Registros:', len(VENDAS_DIDATICAS))
    for item in categorias:
        print(f"{item['_id']}: {reais(item['faturamento'])}, {item['unidades']} unidades")
    print('Total:', reais(sum(item['faturamento'] for item in categorias)))
    print('Gráfico:', grafico)
    print('PDF:', pdf)


if __name__ == '__main__':
    main()
