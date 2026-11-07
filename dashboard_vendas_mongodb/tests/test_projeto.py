"""Testes SEM internet/Atlas. Para validar Atlas, execute main.py."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock

from p10_dashboard.dados import (
    VENDAS_DIDATICAS,
    criar_filtro_periodo,
    cinco_produtos_mais_vendidos,
    popular_vendas,
    resumo_por_categoria,
)
from p10_dashboard.relatorios import gerar_grafico, gerar_pdf


class ColecaoFalsa:
    """Simula apenas upsert e índice para testar idempotência."""
    def __init__(self):
        self.documentos = {}
        self.indice = None

    def create_index(self, campo, unique=False):
        self.indice = (campo, unique)

    def update_one(self, filtro, atualizacao, upsert=False):
        assert upsert is True
        codigo = filtro['codigo']
        novo = codigo not in self.documentos
        self.documentos[codigo] = atualizacao['$set'].copy()
        return SimpleNamespace(upserted_id=codigo if novo else None)


class TestDashboard(unittest.TestCase):
    def test_idempotencia_ao_executar_duas_vezes(self):
        colecao = ColecaoFalsa()
        primeiros = popular_vendas(colecao)
        segundos = popular_vendas(colecao)
        self.assertEqual(primeiros, len(VENDAS_DIDATICAS))
        self.assertEqual(segundos, 0)
        self.assertEqual(len(colecao.documentos), len(VENDAS_DIDATICAS))
        self.assertEqual(colecao.indice, ('codigo', True))
        self.assertEqual(colecao.documentos['V001']['total_centavos'], 17980)

    def test_totais_das_vendas_didaticas(self):
        totais = {}
        for _, categoria, _, quantidade, preco, _ in VENDAS_DIDATICAS:
            totais[categoria] = totais.get(categoria, 0) + quantidade * preco
        self.assertEqual(totais, {
            'Informática': 401860,
            'Papelaria': 56020,
            'Acessórios': 100860,
        })
        self.assertEqual(sum(totais.values()), 558740)
        outubro = [v for v in VENDAS_DIDATICAS if v[-1].startswith('2026-10')]
        self.assertEqual(len(outubro), 7)
        self.assertEqual(sum(v[3] * v[4] for v in outubro), 320050)

    def test_filtro_inclui_ultimo_dia(self):
        filtro = criar_filtro_periodo('2026-10-01', '2026-10-31')
        self.assertEqual(filtro['data']['$gte'].isoformat(), '2026-10-01T00:00:00+00:00')
        self.assertEqual(filtro['data']['$lt'].isoformat(), '2026-11-01T00:00:00+00:00')
        self.assertEqual(criar_filtro_periodo(), {})
        with self.assertRaises(ValueError):
            criar_filtro_periodo('2026-12-01', '2026-10-01')
        with self.assertRaises(ValueError):
            criar_filtro_periodo('31/10/2026', None)

    def test_pipeline_categoria_usa_group_sum_e_sort(self):
        colecao = Mock()
        colecao.aggregate.return_value = iter([{'_id': 'Papelaria', 'faturamento': 1000, 'unidades': 2}])
        resultado = resumo_por_categoria(colecao, {})
        self.assertEqual(len(resultado), 1)
        pipeline = colecao.aggregate.call_args.args[0]
        self.assertEqual(pipeline[1]['$group']['faturamento']['$sum'], '$total_centavos')
        self.assertEqual(pipeline[1]['$group']['unidades']['$sum'], '$quantidade')
        self.assertIn('$sort', pipeline[2])

    def test_pipeline_top_cinco_limita_a_5(self):
        colecao = Mock()
        colecao.aggregate.return_value = iter([])
        cinco_produtos_mais_vendidos(colecao, {})
        pipeline = colecao.aggregate.call_args.args[0]
        self.assertEqual(pipeline[-1], {'$limit': 5})
        self.assertEqual(pipeline[-2]['$sort']['unidades'], -1)

    def test_gera_png_e_pdf_com_resultados(self):
        categorias = [
            {'_id': 'Informática', 'faturamento': 300000, 'unidades': 30},
            {'_id': 'Papelaria', 'faturamento': 50000, 'unidades': 20},
        ]
        produtos = [
            {'_id': 'Mouse', 'faturamento': 80000, 'unidades': 18},
            {'_id': 'Caderno', 'faturamento': 20000, 'unidades': 10},
        ]
        with tempfile.TemporaryDirectory() as pasta:
            png = gerar_grafico(categorias, Path(pasta) / 'grafico.png', 'Teste')
            pdf = gerar_pdf(categorias, produtos, 10, Path(pasta) / 'relatorio.pdf', 'Teste')
            self.assertEqual(png.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(pdf.read_bytes()[:4], b'%PDF')
            self.assertGreater(png.stat().st_size, 15000)
            self.assertGreater(pdf.stat().st_size, 10000)


if __name__ == '__main__':
    unittest.main()
