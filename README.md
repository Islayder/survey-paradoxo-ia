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

## Aparência e publicação no Streamlit

O tema oficial está em `.streamlit/config.toml`: fundo claro, texto escuro e barra lateral azul-marinho. Os gráficos são feitos com **Altair/Vega-Lite**, sem a dependência do módulo JavaScript `PlotlyChart` que falhou na primeira implantação.

Ao publicar uma alteração de tema, o Streamlit Cloud pode precisar de reinicialização do app. Se a tela ainda mostrar arquivos de JavaScript de uma versão anterior, use **Ctrl+Shift+R** no navegador; caso persista, reinicie o aplicativo pelo painel **Manage app**.

A branch de desenvolvimento é `feat/dashboard-streamlit-mvp`. O deploy pode apontar diretamente para ela, antes do merge na `main`.

## Organização

- `app.py`: interface, filtros, gráficos e indicadores.
- `src/analysis.py`: validação de elegibilidade, escalas, confiabilidade e testes estatísticos.
- `src/charts.py`: gráficos Altair e paleta de cores para dados agregados.
- `.streamlit/config.toml`: tema e cores de alto contraste.
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

## Navegação e visualização (versão 0.2)

O tema **Clean Blue** usa branco `#FFFFFF` como fundo, textos pretos `#000000`,
barra lateral azul gelo `#F0F7FF` e realces azuis. A configuração está em
`.streamlit/config.toml`. Os gráficos especificam explicitamente texto preto,
fundo branco, eixos e bordas; `st.altair_chart(..., theme=None)` impede que a
preferência visual do usuário substitua as configurações das visualizações.

A navegação usa um seletor de página: **somente a página escolhida é renderizada**,
reduzindo os gráficos enviados de uma vez ao navegador. Os filtros de perfil,
experiência e uso de IA começam em **Todos**, sem etiquetas extensas.

- **Visão geral:** contagens por perfil e experiência; Likert divergente de P01–P03 e R01–R03.
- **QP1:** matriz 2×2 com os cortes pré-registrados `P >= 4` e `R >= 4`,
  percentual e contagem em cada quadrante, `ρ` de Spearman e `p` Holm.
  A distribuição detalhada de pares de escores continua disponível sob expansão.
- **QP2:** barras 100% empilhadas com os cinco níveis de esforço, ranking de
  respostas 4–5, medianas, Friedman, Kendall W e pós-hoc quando cabível.
- **QP3:** gráfico horizontal dos três coeficientes `ρ` na escala de −1 a +1,
  tabela de `n`, `p` bruto/ajustado e distribuições de confiança e verificação.
- **Método:** descarte auditável, alfa de Cronbach e limitações.

Percentuais e inferências são **preliminares durante a coleta**. A matriz da QP1
usa “abaixo do corte” para valores menores que 4 — não afirma que são respostas
negativas. Os dados individuais não são publicados no repositório.

Para verificar a versão implantada no Streamlit Community Cloud, confirme em
**Manage app → Settings → Repository / Branch** que a aplicação aponta para a
branch `feat/dashboard-streamlit-mvp` (antes do merge) ou `main` (após o merge).
Uma alteração na branch errada não é implantada naquele aplicativo.