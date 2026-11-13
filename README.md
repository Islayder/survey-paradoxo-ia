# Survey — O paradoxo da produtividade com IA

Dashboard interativo para a **Parte 2 — Resultados** da disciplina de **Medição e Experimentação em Engenharia de Software (PUC Minas, 2026/2)**. A pesquisa investiga produtividade percebida, retrabalho e confiança no código gerado por assistentes de IA.

## Rodar localmente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

No painel, envie a exportação `.xlsx` ou `.csv` obtida em **Google Forms → Respostas → Planilha vinculada → Arquivo → Fazer download**. Alternativamente, para desenvolvimento local, salve a exportação como `data/respostas.xlsx`: o Git ignora esse diretório.

**Não suba respostas individuais ao GitHub.** O repositório é público; nem arquivos antigos devem conter os dados. O app só apresenta resultados agregados e não renderiza as respostas abertas. O arquivo carregado fica na sessão do Streamlit, mas o servidor que hospeda o painel ainda processa esses dados; use um ambiente confiável e configure controle de acesso antes de hospedar uma versão pública ligada à planilha oficial.

## Organização

- `app.py`: interface, filtros, gráficos e indicadores.
- `src/analysis.py`: validação de elegibilidade, escalas, confiabilidade e testes estatísticos.
- `tests/test_analysis.py`: testes automatizados com dados artificiais **somente no código de testes**, não usados como resultados.
- `data/`: espaço local para exportações reais, ignorado pelo Git.

## Questões de pesquisa

1. **QP1:** Ganhos de produtividade percebidos coexistem com retrabalho? Proporção P ≥ 4 e R ≥ 4 e Spearman.
2. **QP2:** Que atividades demandam mais esforço? Descrição, Friedman, Kendall W e pós-hoc Wilcoxon/Holm quando aplicável.
3. **QP3:** Confiança está associada à verificação do código? Três correlações de Spearman/Holm.

A correção de Holm é aplicada conjuntamente às quatro correlações de QP1 e QP3. Os construtos P/R/C são médias dos três itens **somente se** alfa de Cronbach ≥ 0,70; em caso contrário usam-se os representantes P03/R02/C01 definidos antes da coleta. "Não se aplica" é ausente legítimo nos itens de esforço; E05 igual a zero **não** invalida resposta. Cada registro recebe um único motivo principal de exclusão, seguindo precedência documentada no código.

## Estado e próximos passos

**Versão inicial (MVP):** permite analisar uma exportação real e substituir o arquivo sem modificar código. Os resultados na fase de coleta são **preliminares**. Antes da defesa, precisamos: auditar a extração final e os descartes, fazer codificação independente das respostas abertas, documentar eventuais desvios, decidir o controle de acesso à fonte para hospedagem e ensaiar a apresentação de dez minutos.

Este estudo utiliza amostragem não probabilística por conveniência/bola de neve; não há inferência causal nem representatividade garantida.