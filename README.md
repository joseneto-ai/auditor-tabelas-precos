# Auditor de Tabelas de Preços

Compara duas versões da tabela de preços de um fornecedor e mostra o que mudou, mesmo quando os nomes e os códigos dos produtos variam entre as planilhas.

> Versão 1 (protótipo). Todos os dados do repositório são fictícios.



https://github.com/user-attachments/assets/dfe0ae77-5000-4afe-9b42-edcd51e69939



**Demo online**: https://auditor-tabelas-precos.streamlit.app/

## O problema

Quando o fornecedor envia uma tabela nova, descobrir o que mudou dá trabalho. Os produtos aparecem com nomes escritos de outro jeito, os códigos às vezes mudam e reajustes grandes passam despercebidos no meio de centenas de linhas.

## O que o programa faz

- Lê duas planilhas `.xlsx` (tabela anterior e tabela nova).
- Descobre qual produto é qual, primeiro pelo código e depois pela semelhança da descrição.
- Calcula a variação de preço de cada item.
- Separa os casos de que não tem certeza para uma pessoa conferir, em vez de assumir.
- Lista os itens novos e os descontinuados.
- Gera um relatório em Excel com 5 abas: Resumo, Comparados, Revisar, Novos e Descontinuados.

## Resultado com os dados fictícios

Com as tabelas geradas pelo script do projeto (77 itens na anterior e 79 na nova) e alerta a partir de 10%:

| Indicador | Valor |
|---|---|
| Itens comparados | 66 |
| Reajuste médio | 3,83% |
| Reajustes acima de 10% | 6 |
| Casos para revisão | 5 |
| Itens novos | 8 |
| Itens descontinuados | 6 |

## Como funciona o casamento de produtos

1. **Mesmo código:** é o mesmo produto. Se a unidade for diferente, o caso vai para revisão.
2. **Sem código igual:** o programa compara as descrições depois de arrumá-las (minúsculas, sem acento, sem pontuação, número separado da letra).
3. **Números precisam ser iguais:** `40 mm` e `50 mm` nunca são considerados o mesmo produto, mesmo que o texto seja quase igual.
4. **Nota de semelhança de 0 a 100:** 90 ou mais com a mesma unidade é aceito automaticamente; de 70 a 89 vai para revisão; abaixo de 70 o produto fica sem par.
5. Cada item da tabela nova só pode ser usado uma vez.

## Como rodar

Precisa de Python 3.10 ou mais novo.

```
git clone https://github.com/joseneto-ai/auditor-tabelas-precos.git
cd auditor-tabelas-precos
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No Mac ou Linux, ative o ambiente com `source .venv/bin/activate`.

O navegador abre em `http://localhost:8501`. Envie `dados/tabela_anterior.xlsx` e `dados/tabela_nova.xlsx` para testar.

Para gerar os dados fictícios de novo:

```
python scripts/gerar_dados_ficticios.py
```

Para rodar os testes:

```
python -m pytest -q
```

## Estrutura do projeto

```
app.py                       interface em Streamlit
comparador/
    excecoes.py              erro próprio para planilhas inválidas
    modelos.py               estruturas de dados (Item, Par, ResultadoComparacao)
    normalizacao.py          padroniza textos e unidades
    leitura.py               lê e valida as planilhas
    casamento.py             descobre qual produto é qual
    relatorio.py             tabelas, resumo e relatório em Excel
scripts/gerar_dados_ficticios.py
dados/                       planilhas fictícias de exemplo
tests/                       testes automáticos (pytest)
```

## Decisões técnicas

- **`Decimal` em vez de `float`:** dinheiro precisa de exatidão. O `float` pode errar centavos em algumas contas.
- **Limites 90 e 70:** foram escolhidos testando com os dados fictícios. Com dados reais, talvez precisem de ajuste.
- **Revisão humana:** quando a semelhança é média ou a unidade muda, o programa não decide sozinho.
- **Números diferentes impedem o casamento:** evita juntar medidas diferentes do mesmo produto.
- **Interface separada da lógica:** o `app.py` só mostra os resultados. Isso facilita trocar o Streamlit por uma API depois.
- **Erros claros:** planilha com coluna faltando, preço inválido ou código repetido gera uma mensagem em português, não uma falha do programa.

## Limitações da versão 1

- Aceita só `.xlsx` com as colunas `codigo`, `descricao`, `unidade` e `preco`.
- Foi testado apenas com dados fictícios.
- Os limites de semelhança podem precisar de ajuste com dados reais.
- Quando há dois candidatos muito parecidos, a ordem dos itens pode influenciar qual fica com qual.
- Se um produto mudou de medida, ele aparece como descontinuado mais um item novo, e não como revisão.
- Não tem login, banco de dados, histórico nem API.

## Próximos passos

- API com FastAPI.
- Banco de dados PostgreSQL com histórico das comparações.
- Interface em HTML e JavaScript consumindo a API.
- Login e separação de dados por empresa.
- Deploy.

## Autoria e uso de IA

Projeto desenvolvido por José Neto como estudo de Python aplicado (módulos, exceções, tipos e testes). Parte do código e da documentação foi feita com apoio de IA (Claude). Eu li, executei e testei o resultado, e escrevi os testes com ele.

## Aviso

Todos os dados deste repositório são fictícios e foram gerados por script. Não use dados reais de empresas sem autorização.
