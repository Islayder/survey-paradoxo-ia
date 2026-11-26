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

O tema oficial está em `.streamlit/config.toml`: fundo branco, texto preto e barra lateral azul-clara. Os gráficos são feitos com **Altair/Vega-Lite**, sem a dependência do módulo JavaScript `PlotlyChart` que falhou na primeira implantação.

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

## Estado da coleta e condições para a defesa

A coleta oficial foi encerrada em **22/11/2026**. A exportação oficial auditada contém **60 respostas**, **50 válidas** e **10 descartadas** (7 por AT01 e 3 por E01). O grupo atual é **Islayder, Bárbara e Vinícius**; o pré-registro original, com cinco nomes, permanece imutável e a alteração administrativa consta na página de metodologia.

Os indicadores são **fixados usando a amostra completa de 50 válidas**, e **só depois** os filtros E01/E04/E05 selecionam participantes. Isso evita que o alfa de Cronbach de um subgrupo mude a definição da variável durante a defesa. Testes recalculados por segmento devem ser interpretados como **exploratórios**, em especial se o n for pequeno.

A **margem nominal para proporções**, calculada pela fórmula do enunciado com n=50, p=0,5 e nível nominal de 95%, é **±13,9 pontos percentuais**. Por ser amostragem de conveniência/bola de neve, não constitui margem de erro inferencial garantida nem representa IC dos coeficientes de Spearman.

Os resultados auditados e as conclusões da base final estão em [Resultados finais](docs/RESULTADOS_FINAIS.md).

**Ainda exigem ação humana e evidência antes da entrega:** capturas datadas da divulgação, codificação independente/consenso de OA01, autorização se necessária para a alteração de integrantes e ensaio da defesa. Consulte [guia de evidências e demonstração](docs/ENTREGA_E_EVIDENCIAS.md) e [protocolo de codificação da OA01](docs/CODIFICACAO_OA01.md).

**Importante para demonstrar:** o link público carrega a interface, mas **não traz a base oficial embutida**. Uma pessoa do grupo deve carregar o CSV/XLSX original autorizado pela barra lateral no ambiente confiável da apresentação. O arquivo bruto não deve ser adicionado ao GitHub público; não se deve inferir que o professor verá os gráficos automaticamente ao apenas abrir o link.

Este estudo não mede produtividade objetiva, não permite inferência causal e não garante representatividade.

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
  percentual e contagem em cada quadrante, `ρ` de Spearman, `p` bruto e `p` Holm, n efetivo e conclusão da significância.
  A distribuição detalhada de pares de escores continua disponível sob expansão.
- **QP2:** barras 100% empilhadas com os cinco níveis de esforço, ranking de
  respostas 4–5, medianas, Friedman, Kendall W e pós-hoc quando cabível.
- **QP3:** gráfico horizontal dos três coeficientes `ρ` na escala de −1 a +1,
  tabela de `n`, `p` bruto/ajustado e distribuições de confiança e verificação.
- **Método:** descarte auditável, alfa de Cronbach fixado antes dos filtros, plano versus execução, evidências pendentes e limitações.

Os valores apresentados com a **exportação oficial congelada em 22/11/2026** correspondem aos resultados finais desta amostra; ao carregar outro arquivo, as estimativas refletirão a fonte selecionada. A matriz da QP1
usa “abaixo do corte” para valores menores que 4 — não afirma que são respostas
negativas. Os dados individuais não são publicados no repositório.

Para verificar a versão implantada no Streamlit Community Cloud, confirme em
**Manage app → Settings → Repository / Branch** que a aplicação aponta para a
branch `feat/dashboard-streamlit-mvp` (antes do merge) ou `main` (após o merge).
Uma alteração na branch errada não é implantada naquele aplicativo.