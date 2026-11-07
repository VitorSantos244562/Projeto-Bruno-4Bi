"""Projeto 10 - Dashboard de Vendas com MongoDB Atlas e Matplotlib.

Executar da RAIZ do projeto:
  python -m p10_dashboard.main
  python -m p10_dashboard.main --inicio 2026-10-01 --fim 2026-10-31
"""
import argparse
from pathlib import Path

from pymongo.errors import PyMongoError

from conexao import conectar
from p10_dashboard.dados import (
    VENDAS_DIDATICAS,
    cinco_produtos_mais_vendidos,
    criar_filtro_periodo,
    popular_vendas,
    resumo_por_categoria,
)
from p10_dashboard.relatorios import (
    descrever_periodo,
    gerar_grafico,
    gerar_pdf,
    reais,
)

PASTA = Path(__file__).parent


def executar(inicio=None, fim=None, nao_popular=False):
    """Fluxo: conecta -> insere/atualiza -> consulta -> gera PNG e PDF."""
    filtro = criar_filtro_periodo(inicio, fim)
    cliente, banco = conectar()
    try:
        vendas = banco['vendas_p10']
        if not nao_popular:
            novos = popular_vendas(vendas)
            print(f'Dados didáticos preparados: {len(VENDAS_DIDATICAS)} vendas; '
                  f'{novos} documentos novos.')
        else:
            print('Inserção de dados didáticos ignorada (--nao-popular).')

        # As duas agregações são executadas no SERVIDOR MongoDB.
        categorias = resumo_por_categoria(vendas, filtro)
        produtos = cinco_produtos_mais_vendidos(vendas, filtro)
        quantidade_vendas = vendas.count_documents(filtro)
    finally:
        cliente.close()

    total = sum(item['faturamento'] for item in categorias)
    periodo = descrever_periodo(inicio, fim)
    print('\n=== DASHBOARD DE VENDAS ===')
    print('Período:', periodo)
    print('Número de documentos de venda:', quantidade_vendas)
    print('\nFATURAMENTO POR CATEGORIA')
    if not categorias:
        print('Nenhuma venda encontrada nesse período.')
    for item in categorias:
        print(f"  {item['_id']}: {item['unidades']} unidades | "
              f"{reais(item['faturamento'])}")
    print('TOTAL:', reais(total))

    print('\nTOP 5 PRODUTOS (POR UNIDADES)')
    for posicao, item in enumerate(produtos, 1):
        print(f"  {posicao}. {item['_id']} - {item['unidades']} unidades | "
              f"{reais(item['faturamento'])}")

    imagem = gerar_grafico(categorias, PASTA / 'grafico_vendas.png', periodo)
    pdf = gerar_pdf(categorias, produtos, quantidade_vendas,
                    PASTA / 'relatorio_vendas.pdf', periodo)
    print('\nPNG gerado:', imagem)
    print('PDF gerado:', pdf)
    print('Confira no Compass: laboratorio_python > vendas_p10')


def main():
    parser = argparse.ArgumentParser(description='Dashboard de Vendas - MongoDB Atlas')
    parser.add_argument('--inicio', help='Data inicial AAAA-MM-DD (inclusiva)')
    parser.add_argument('--fim', help='Data final AAAA-MM-DD (inclusiva)')
    parser.add_argument('--nao-popular', action='store_true',
                        help='Não insere/atualiza os dados didáticos desta vez')
    args = parser.parse_args()
    try:
        executar(args.inicio, args.fim, args.nao_popular)
    except (ValueError, ConnectionError, PyMongoError) as erro:
        print('ERRO:', erro)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
