# Roteiro de apresentação para o professor

## Demonstração (ordem sugerida)

1. Explique que `laboratorio_python` é o banco e `vendas_p10` é a coleção.
2. Abra `conexao.py`: mostre `load_dotenv`, `MongoClient`, `ping` e seleção do banco.
3. Execute `python conexao.py` com a sua URI correta: o terminal deve mostrar sucesso.
4. Abra `p10_dashboard/dados.py`: explique a lista de exemplos, `create_index`, `update_one` e `upsert=True`.
5. Execute `python -m p10_dashboard.main`: verifique os totais, o gráfico e o PDF.
6. Repita o comando: o terminal deve indicar **0 novos documentos didáticos**; confira os mesmos códigos no Compass.
7. Mostre `resumo_por_categoria()` usando `$group` e `$sum` para o faturamento.
8. Execute `python -m p10_dashboard.main --inicio 2026-10-01 --fim 2026-10-31` para mostrar o filtro.
9. Mostre `cinco_produtos_mais_vendidos()`: `$sort` por unidades e `$limit` de 5.
10. Abra os arquivos `grafico_vendas.png` e `relatorio_vendas.pdf` recém-gerados.

## Perguntas prováveis

**1. O que é idempotência?**
Executar a operação uma vez ou várias vezes deve deixar o mesmo conjunto de vendas didáticas, sem criar duplicatas. Aqui `update_one(..., upsert=True)` cria quando não existe e atualiza quando já existe; `codigo` tem um índice único.

**2. Qual a diferença entre banco, coleção e documento?**
Banco: `laboratorio_python`. Coleção: `vendas_p10`. Documento: uma venda, como `V001`, contendo produto, categoria, quantidade, data e total.

**3. O que `MongoClient` faz?**
Cria o cliente do PyMongo para se comunicar com o cluster. O `ping` realmente testa se o servidor responde.

**4. Por que existe o arquivo `.env`?**
Para armazenar a URI com senha fora do código-fonte. O `.gitignore` impede sua publicação acidental em um repositório Git, mas o próprio ZIP também deve excluir `.env`.

**5. O que significa `$match`?**
Filtra documentos por período antes dos agrupamentos.

**6. O que faz `$group`?**
Agrupa documentos por categoria ou produto, definido pelo campo `_id` do agrupamento.

**7. O que faz `$sum`?**
Soma `total_centavos` ou `quantidade` de todos os documentos de um mesmo grupo.

**8. O que faz `$sort`?**
Ordena resultados. `-1` representa ordem decrescente, ou seja, do maior para o menor.

**9. O que é `$limit: 5`?**
Retorna somente os cinco primeiros produtos depois da ordenação por unidades.

**10. Por que guardar dinheiro em centavos?**
Para usar inteiros e evitar erros de precisão de números decimais em cálculos monetários simples.

**11. Como o filtro inclui o dia final?**
Transformamos a data final no início do dia seguinte e usamos `$lt`. Assim, todas as horas do dia final são incluídas.

**12. Qual é a função do Matplotlib?**
Transformar os dados agregados em gráfico PNG e relatório PDF. As consultas acontecem antes, no MongoDB.

**13. O Compass é o banco?**
Não. O banco está no Atlas; o Compass é uma interface visual para inspecioná-lo.

**14. O projeto funciona sem internet?**
Os testes unitários e as prévias sim. Para consultar a coleção do Atlas é necessário acesso à internet e autorização de conexão.

## Checklist antes de entregar

- [ ] `.env` configurado SOMENTE no meu computador.
- [ ] `python conexao.py` mostra que o `ping` funcionou.
- [ ] `python -m p10_dashboard.main` rodou no meu Atlas.
- [ ] `laboratorio_python > vendas_p10` existe no Compass.
- [ ] A segunda execução não duplicou os registros de exemplo.
- [ ] `grafico_vendas.png` reflete o resultado agregado do Atlas.
- [ ] `relatorio_vendas.pdf` foi criado e contém o Top 5.
- [ ] Testei filtro do mês de outubro/2026.
- [ ] Fiz capturas reais de tela para apresentar ao professor.
- [ ] Meu ZIP e meu GitHub NÃO contêm o arquivo `.env` verdadeiro.
