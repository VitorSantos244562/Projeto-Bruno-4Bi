"""Exportação do gráfico PNG e do relatório PDF utilizando Matplotlib."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Salva imagens sem precisar abrir uma janela gráfica.
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

AZUL = '#17365d'
AZUL_CLARO = '#3b82c4'
VERDE = '#0c8b78'
CINZA = '#536375'


def reais(centavos):
    """Formata um valor inteiro em centavos para R$ 1.234,56."""
    valor = f'{centavos / 100:,.2f}'
    return 'R$ ' + valor.replace(',', 'X').replace('.', ',').replace('X', '.')


def descrever_periodo(inicio, fim):
    if inicio and fim:
        return f'De {inicio} até {fim} (inclusive)'
    if inicio:
        return f'Desde {inicio}'
    if fim:
        return f'Até {fim} (inclusive)'
    return 'Todos os períodos'


def desenhar_barras(ax, categorias, titulo='Faturamento por categoria'):
    """Desenha no eixo informado; reutilizado no PNG e no PDF."""
    nomes = [item['_id'] for item in categorias]
    valores = [item['faturamento'] / 100 for item in categorias]
    if not nomes:
        ax.text(0.5, 0.5, 'Nenhuma venda encontrada no período.',
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_axis_off()
        return

    cores = [AZUL_CLARO, VERDE, '#7896b4', '#9aa9bb']
    barras = ax.bar(nomes, valores, color=[cores[i % len(cores)] for i in range(len(nomes))], width=0.58)
    ax.set_title(titulo, loc='left', color=AZUL, fontsize=14, pad=16, fontweight='bold')
    ax.set_ylabel('Faturamento (R$)', color=CINZA)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: reais(round(x * 100))))
    ax.grid(axis='y', alpha=0.16)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='x', labelsize=10)
    ax.margins(y=0.22)
    ax.bar_label(barras, labels=[reais(int(item['faturamento'])) for item in categorias],
                 padding=5, fontsize=9, color=AZUL)


def gerar_grafico(categorias, destino, periodo, previa=False):
    """Salva sempre um PNG com as categorias retornadas pela agregação."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    fig.subplots_adjust(left=0.14, right=0.96, top=0.80, bottom=0.16)
    fig.suptitle('DASHBOARD DE VENDAS', x=0.14, y=0.96,
                 ha='left', fontsize=18, fontweight='bold', color=AZUL)
    fig.text(0.14, 0.88, f'Período: {periodo}', fontsize=10, color=CINZA)
    if previa:
        fig.text(0.14, 0.835, 'PRÉVIA DIDÁTICA - sem conexão com o Atlas', fontsize=9, color=VERDE)
    desenhar_barras(ax, categorias)
    fig.savefig(destino, dpi=170, facecolor='white')
    plt.close(fig)
    return destino


def gerar_pdf(categorias, produtos, quantidade_vendas, destino, periodo, previa=False):
    """Exporta PDF em 2 páginas (resumo/gráfico e ranking de produtos)."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    total_centavos = sum(item['faturamento'] for item in categorias)
    unidades = sum(item['unidades'] for item in categorias)

    with PdfPages(destino) as pdf:
        # Página 1: KPIs e gráfico por categoria.
        fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
        fig.text(0.09, 0.93, 'RELATÓRIO DE VENDAS', color=AZUL,
                 fontsize=22, weight='bold')
        fig.text(0.09, 0.885, f'Período analisado: {periodo}', fontsize=10, color=CINZA)
        fig.text(0.09, 0.858, 'Fonte: laboratorio_python.vendas_p10', fontsize=9, color=CINZA)
        if previa:
            fig.text(0.09, 0.830, 'Prévia didática: dados de exemplo, sem consulta ao Atlas.',
                     fontsize=9, color=VERDE)

        fig.text(0.09, 0.755, 'FATURAMENTO', color=CINZA, fontsize=10)
        fig.text(0.09, 0.712, reais(total_centavos), color=AZUL,
                 fontsize=23, weight='bold')
        fig.text(0.55, 0.755, 'VENDAS / UNIDADES', color=CINZA, fontsize=10)
        fig.text(0.55, 0.712, f'{quantidade_vendas} / {unidades}', color=AZUL,
                 fontsize=23, weight='bold')

        ax = fig.add_axes([0.12, 0.29, 0.78, 0.35])
        desenhar_barras(ax, categorias)
        fig.text(0.09, 0.16, f'Categorias encontradas: {len(categorias)}',
                 fontsize=11, color=AZUL)
        fig.text(0.09, 0.105, 'Faturamento = soma de quantidade x preço unitário.',
                 fontsize=9, color=CINZA)
        fig.text(0.09, 0.075, 'Valores monetários são armazenados em centavos para evitar',
                 fontsize=9, color=CINZA)
        fig.text(0.09, 0.058, 'arredondamentos imprecisos com números decimais.',
                 fontsize=9, color=CINZA)
        pdf.savefig(fig, facecolor='white')
        plt.close(fig)

        # Página 2: ranking dos cinco produtos com maior QUANTIDADE vendida.
        fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
        fig.text(0.09, 0.93, 'TOP 5 PRODUTOS', color=AZUL,
                 fontsize=22, weight='bold')
        fig.text(0.09, 0.885, 'Ordenação: quantidade total de unidades vendidas.',
                 fontsize=11, color=CINZA)
        fig.text(0.09, 0.855, f'Período: {periodo}', fontsize=10, color=CINZA)
        if previa:
            fig.text(0.09, 0.822, 'Prévia didática - não comprova conexão com o MongoDB.',
                     fontsize=9, color=VERDE)

        linhas = [[str(posicao), item['_id'], str(item['unidades']),
                   reais(item['faturamento'])]
                  for posicao, item in enumerate(produtos, 1)]
        if not linhas:
            linhas = [['-', 'Sem vendas no período', '-', '-']]

        ax = fig.add_axes([0.09, 0.40, 0.82, 0.35])
        ax.axis('off')
        tabela = ax.table(
            cellText=linhas,
            colLabels=['#', 'Produto', 'Unidades', 'Faturamento'],
            colWidths=[0.08, 0.37, 0.20, 0.35],
            cellLoc='left',
            loc='upper center',
        )
        tabela.auto_set_font_size(False)
        tabela.set_fontsize(10)
        tabela.scale(1, 2.0)
        for (linha, _coluna), celula in tabela.get_celld().items():
            celula.set_edgecolor('#e2e8ef')
            if linha == 0:
                celula.set_facecolor(AZUL)
                celula.set_text_props(color='white', weight='bold')
            elif linha % 2 == 0:
                celula.set_facecolor('#f2f6fa')

        fig.text(0.09, 0.28, 'COMO OS DADOS FORAM CALCULADOS', color=AZUL,
                 fontsize=12, weight='bold')
        fig.text(0.09, 0.245, 'MongoDB aggregate(): $match, $group, $sum, $sort e $limit.',
                 fontsize=10, color=CINZA)
        fig.text(0.09, 0.214, 'O filtro de período é aplicado antes das agregações.',
                 fontsize=10, color=CINZA)
        fig.text(0.09, 0.183, 'Vendas de demonstração são atualizadas por código (upsert).',
                 fontsize=10, color=CINZA)
        fig.text(0.09, 0.085, 'Projeto escolar - Dashboard de Vendas - MongoDB + Python',
                 fontsize=9, color=CINZA)
        pdf.savefig(fig, facecolor='white')
        plt.close(fig)

    return destino
