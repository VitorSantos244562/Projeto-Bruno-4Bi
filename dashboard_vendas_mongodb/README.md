# Dashboard de Vendas — MongoDB Atlas + Python

Projeto 10 (4º bimestre) de Banco de Dados, baseado na proposta de <https://github.com/perabru/ProjetoBD-4Bimestre> e ampliado para incluir **todos os 3 desafios extras**.

**Objetivo:** armazenar vendas didáticas na nuvem, impedir duplicações, agrupar por categoria com MongoDB `aggregate()`, gerar gráfico PNG e PDF, filtrar datas e mostrar os 5 produtos mais vendidos.

## 1. Estrutura do projeto

```text
dashboard_vendas_mongodb/
├── README.md                  ← explicação e tutorial de instalação
├── GUIA_APRESENTACAO.md       ← perguntas e testes para mostrar ao professor
├── .env.example               ← MODELO (não possui credenciais reais)
├── .gitignore                 ← impede publicar .env, venv e resultados
├── requirements.txt           ← PyMongo, dotenv, Matplotlib
├── conexao.py                 ← carrega .env, faz ping e seleciona o banco
├── p10_dashboard/
│   ├── __init__.py
│   ├── dados.py               ← vendas, idempotência e aggregate()
│   ├── relatorios.py          ← exporta gráfico PNG e PDF
│   └── main.py                ← controla a execução e o período
├── tests/
│   └── test_projeto.py        ← testes sem precisar de conta Atlas
├── scripts/
│   └── gerar_previa.py        ← prévia local, NÃO consulta o Atlas
└── exemplos/
    ├── previa_grafico.png     ← prévia ilustrativa sem o Atlas
    └── previa_relatorio.pdf   ← prévia ilustrativa sem o Atlas
```

**Importante:** os arquivos `grafico_vendas.png` e `relatorio_vendas.pdf` são gerados na pasta `p10_dashboard/` DEPOIS que o programa executar com o seu Atlas. Os arquivos na pasta `exemplos/` são apenas prévias, não evidências de conexão.

## 2. Configurar o Atlas na nuvem

1. Abra <https://www.mongodb.com/cloud/atlas> e entre ou crie uma conta.
2. Crie um projeto no Atlas (por exemplo, `LaboratorioPython`).
3. Em **Database / Clusters**, crie um *deployment* (cluster). Escolha uma opção gratuita, caso esteja disponível, e uma região próxima. Aguarde ficar disponível.
4. Em **Security / Database Access**, crie um **usuário de banco de dados** com nome e senha próprios. Recomendação: atribua somente a função `readWrite` sobre o banco `laboratorio_python` (se a interface oferecer essa escolha). Guarde a senha em segurança.
5. Em **Security / Network Access**, selecione **Add IP Address** e autorize **Add Current IP Address** (seu IP público atual). Evite abrir acesso a qualquer IP (`0.0.0.0/0`). Se seu endereço mudar, talvez tenha de atualizá-lo.
6. Entre no seu cluster, clique em **Connect → Drivers → Python**, e copie a URI `mongodb+srv://...`. Substitua os dados de usuário/senha pelos do **usuário de banco**, não da conta Atlas. Se a senha contiver caracteres especiais (por exemplo, `@`, `#`, `/`), codifique-os para uso em URI (URL encoding), ou use uma senha forte sem esses caracteres no exercício.

A posição e o texto dos botões podem mudar um pouco. Documentação oficial: <https://www.mongodb.com/docs/atlas/driver-connection/>.

## 3. Configurar o Python e VS Code (Windows)

Instale **Python 3.11+** e **VS Code** com a extensão **Python** da Microsoft. No VS Code use **Arquivo → Abrir Pasta** e escolha a pasta `dashboard_vendas_mongodb` (não só `p10_dashboard`). Abra **Terminal → Novo Terminal**, preferencialmente PowerShell:

```powershell
py --version
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, **não é necessário alterar políticas de segurança**; execute os mesmos comandos com `.venv\Scripts\python.exe` no lugar de `python`.

No VS Code pressione `Ctrl+Shift+P`, escolha **Python: Select Interpreter** e selecione `.venv\Scripts\python.exe`.

No Linux/macOS, use `python3 -m venv .venv`, `source .venv/bin/activate` e `python -m pip install -r requirements.txt`.

### Criar o `.env`

Na RAIZ do projeto, copie `.env.example` com o nome `.env` (pode usar o Explorer do VS Code). Dentro do novo arquivo coloque, numa única linha:

```ini
MONGO_URI=mongodb+srv://SEU_USUARIO:SUA_SENHA@SEU_CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

**Atenção:** a URI acima é apenas ilustrativa. Use a URI copiada do seu cluster; não use literalmente `SEU_CLUSTER`. Não compartilhe `.env`, pois ele pode conter senha e credenciais.

## 4. Testar `conexao.py` (ping real)

Execute no terminal, estando na raiz:

```powershell
python conexao.py
```

Saída esperada após configurar corretamente o Atlas:

```text
Ping realizado com sucesso!
Conectado ao banco: laboratorio_python
```

Se houver erro, confira: IP liberado no Atlas, string do cluster, usuário de banco, senha e se a internet está disponível. **O banco só aparece no Compass/Atlas depois que houver documentos gravados**.

## 5. Executar o dashboard completo

```powershell
python -m p10_dashboard.main
```

Esse comando prepara **16 vendas didáticas** com as mesmas categorias/produtos do exemplo do professor, mais outras vendas em datas de setembro a novembro/2026 para exercitar o filtro. Na primeira execução, 16 documentos novos (se coleção vazia). Na segunda, 0 novos. O script imprime o resumo de categorias, o top 5 e grava:

- `p10_dashboard/grafico_vendas.png`
- `p10_dashboard/relatorio_vendas.pdf`

### Resultado esperado em uma coleção sem vendas extras

| Categoria | Faturamento (todos os períodos) |
|---|---:|
| Informática | R$ 4.018,60 |
| Acessórios | R$ 1.008,60 |
| Papelaria | R$ 560,20 |
| **Total (16 vendas / 91 unidades)** | **R$ 5.587,40** |

Na seleção exclusiva de **outubro de 2026**, as 7 vendas previstas somam **R$ 3.200,50**. Se você adicionar outros documentos no Compass, esses totais mudarão, pois a consulta considera todas as vendas da coleção que passam pelo filtro.

### Extra 1 — Filtrar por período (datas inclusivas)

```powershell
python -m p10_dashboard.main --inicio 2026-10-01 --fim 2026-10-31
```

Também vale informar apenas `--inicio` ou apenas `--fim`. O fim do período inclui todo o dia final. Quando não há vendas, o dashboard informa que o filtro não encontrou dados, sem quebrar.

### Extra 2 — Cinco produtos mais vendidos

Executa automaticamente em qualquer um dos comandos acima. **Mais vendido significa maior quantidade total de unidades** (não maior preço). Um único produto pode aparecer em vários documentos de venda; suas unidades são somadas com `$group` e `$sum`, ordenadas com `$sort` e limitadas a 5 com `$limit`.

### Extra 3 — Relatório PDF

O arquivo `p10_dashboard/relatorio_vendas.pdf` é gerado automaticamente com o Matplotlib em duas páginas: resumo + gráfico, depois ranking de produtos. Portanto, **não é necessária biblioteca adicional**.

### Opcional: consultar apenas os registros já gravados

```powershell
python -m p10_dashboard.main --nao-popular
```

Isso evita atualizar o conjunto didático caso queira conferir alterações feitas manualmente no Compass. **Cuidado:** ao executar normalmente, os exemplos de códigos `V001` a `V016` serão atualizados para os valores didáticos, mas outras vendas com outros códigos não serão apagadas.

## 6. Como a idempotência funciona

A coleção se chama `vendas_p10` e pertence ao banco `laboratorio_python`. O campo `codigo` recebe um índice único:

```python
colecao.create_index('codigo', unique=True)
colecao.update_one({'codigo': codigo}, {'$set': registro}, upsert=True)
```

- Se o código não existe, `upsert=True` insere uma venda nova.
- Se já existe, `$set` atualiza a mesma venda.
- O índice único reforça que não devem existir dois documentos com o mesmo `codigo`.
- Executar duas vezes mantém **16 registros didáticos**, e não 32 (desde que a coleção estivesse inicialmente vazia e não haja outros registros criados manualmente).

**Modelagem de exemplo:**

```javascript
{
  "codigo": "V001",
  "categoria": "Informática",
  "produto": "Teclado",
  "quantidade": 2,
  "preco_unitario_centavos": 8990,
  "total_centavos": 17980,
  "data": ISODate("2026-09-05T00:00:00.000Z")
}
```

O `_id` é acrescentado automaticamente pelo MongoDB. Os valores monetários são guardados em **centavos inteiros** (17980 = R$ 179,80), reduzindo problemas de arredondamento.

## 7. Entender a agregação

O agrupamento por categoria é executado dentro do MongoDB e não apenas no Python:

```python
pipeline = [
    {'$match': filtro},
    {'$group': {
        '_id': '$categoria',
        'faturamento': {'$sum': '$total_centavos'},
        'unidades': {'$sum': '$quantidade'}
    }},
    {'$sort': {'faturamento': -1, '_id': 1}}
]
dados = list(vendas.aggregate(pipeline))
```

`$match` filtra datas; `$group` reúne documentos pela categoria; `$sum` soma valores; `$sort` ordena os maiores faturamentos primeiro. O ranking de produtos usa outro `$group` e acrescenta `$limit: 5`.

## 8. Conferir pelo MongoDB Compass

1. Abra o **MongoDB Compass** e clique em **New Connection**.
2. Cole sua URI `mongodb+srv://...` do Atlas (com seu usuário/senha) e conecte.
3. Expanda o banco `laboratorio_python`.
4. Clique na coleção `vendas_p10` (termina em **p10**, conforme o professor).
5. Abra **Documents** e procure `V001`, `V002` etc.; verifique `categoria`, `quantidade`, `total_centavos` e `data`.
6. Execute novamente `python -m p10_dashboard.main`, atualize o Compass e confirme que **não duplicou os 16 códigos**.
7. Para verificar o total de vendas por categoria, compare a saída do terminal com os documentos armazenados (ou use a aba **Aggregations** com o pipeline do arquivo `dados.py`).

**Importante:** o Compass não hospeda o banco; ele é o programa de inspeção. O Atlas hospeda, o PyMongo conecta, o Matplotlib desenha.

## 9. Testes e evidências para entrega

Para executar **testes offline de código** (sem acesso ao Atlas):

```powershell
python -m unittest discover -s tests -v
```

Estes testes verificam idempotência simulada, filtros, definição das agregações e criação dos arquivos PNG/PDF. **Não provam que sua URI conecta ao Atlas nem que as agregações rodaram no servidor**: isso precisa ser conferido com `python conexao.py` e `python -m p10_dashboard.main` usando sua conta.

Capturas de tela sugeridas para a entrega:

1. `python conexao.py` com ping de sucesso;
2. execução do dashboard no terminal, mostrando os totais;
3. `vendas_p10` aberta no Compass, com 16 vendas;
4. `grafico_vendas.png` aberto no VS Code ou visualizador;
5. `relatorio_vendas.pdf` aberto; e
6. execução filtrada e repetição sem duplicação.

> Os arquivos `exemplos/` demonstram a aparência dos relatórios, mas **não são capturas de uma execução conectada ao Atlas**.

## 10. Principais problemas

| Erro | Possível causa / solução |
|---|---|
| `MONGO_URI` não configurada | Crie `.env` na raiz e cole a URI verdadeira. |
| `ServerSelectionTimeoutError` | IP não autorizado, rede/DNS ou endereço do cluster incorreto. |
| `Authentication failed` | Usuário de banco/senha incorretos ou caracteres especiais não codificados. |
| `No module named pymongo` | Ative a `.venv` ou selecione o interpretador correto. |
| `No module named p10_dashboard` | Execute `python -m p10_dashboard.main` da **raiz** do projeto. |
| PDF/PNG não aparece | Confira a pasta `p10_dashboard/` após uma execução com o Atlas. |
| Nada aparece no Compass | Execute primeiro `main.py` e atualize a árvore do banco. |

## Referências

- Professor: <https://github.com/perabru/ProjetoBD-4Bimestre>
- Conexão Atlas: <https://www.mongodb.com/docs/atlas/driver-connection/>
- Python + MongoDB: <https://www.mongodb.com/docs/languages/python/pymongo-driver/current/>
- Matplotlib: <https://matplotlib.org/stable/>
