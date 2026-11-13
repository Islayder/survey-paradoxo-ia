"""Painel interativo do survey pré-registrado da PUC Minas (2026/2)."""
from pathlib import Path
import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analysis import (
    ACTIVITY, LIKERT, VERIFY, coexistence, construct_scores, correlations,
    effort_analysis, prepare,
)

st.set_page_config(page_title="Paradoxo da IA | Survey", page_icon="▣", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stApp {background: #f7f9fc; color:#17243b;}
    section[data-testid="stSidebar"] {background: #edf2f8; border-right:1px solid #e1e7f0;}
    div[data-testid="stMetric"] {background: #fff; border:1px solid #e2e8f0; border-radius: 14px;
                                   padding: 14px 18px; box-shadow:0 1px 5px #1e32500a;}
    h1, h2, h3 {letter-spacing:-.02em; color:#1a2e4a;}
    h1 {font-size: 2.0rem !important;}
    div[data-testid="stTabs"] button {font-weight: 600;}
    .eyebrow {font-weight:700; letter-spacing:.11em; font-size:.75rem; color:#57769e;}
    .muted {color:#65758c;}
</style>
""", unsafe_allow_html=True)

COLORS = {1:"#a33f54", 2:"#dc8996", 3:"#b5bac6", 4:"#7caccb", 5:"#296293"}


def read_file(uploaded) -> pd.DataFrame:
    content = io.BytesIO(uploaded.getvalue())
    if uploaded.name.casefold().endswith(".csv"):
        for encoding in ("utf-8-sig", "latin-1"):
            try:
                content.seek(0)
                return pd.read_csv(content, encoding=encoding, sep=None, engine="python")
            except UnicodeDecodeError:
                continue
        raise ValueError("Não foi possível interpretar a codificação do CSV.")
    return pd.read_excel(content, sheet_name=0)


@st.cache_data(show_spinner=False)
def load_local(path: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=0)


def fig_style(fig, height=350):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=12,r=15,t=35,b=20),
                      font=dict(family="Arial", color="#31415a", size=12),
                      legend=dict(orientation="h",y=-.22))
    return fig


def likert_chart(df: pd.DataFrame, codes: list[str], labels: list[str]):
    """Barra divergente: discordância à esquerda, neutralidade central, concordância à direita."""
    fig = go.Figure()
    matrix = {}
    for code, label in zip(codes, labels):
        v = df[code + "_n"].dropna().astype(int)
        counts = v.value_counts(normalize=True).mul(100)
        matrix[label] = {i: float(counts.get(i, 0)) for i in range(1, 6)}
    if not matrix:
        return fig_style(fig)
    for val in (1, 2, 3, 4, 5):
        # Neutro dividido simetricamente para deixar zero no centro.
        widths = [((-1 if val <= 2 else 1) * (d[val] if val != 3 else d[val] / 2))
                  for d in matrix.values()]
        if val == 3:
            fig.add_bar(y=list(matrix), x=[-d[3]/2 for d in matrix.values()], orientation="h",
                        name="Neutro", marker_color=COLORS[3], legendgroup="3", showlegend=True,
                        hovertemplate="%{y}: %{customdata:.1f}% neutro<extra></extra>",
                        customdata=[d[3] for d in matrix.values()])
            fig.add_bar(y=list(matrix), x=[d[3]/2 for d in matrix.values()], orientation="h",
                        name="Neutro", marker_color=COLORS[3], legendgroup="3", showlegend=False,
                        hovertemplate="%{y}: %{customdata:.1f}% neutro<extra></extra>",
                        customdata=[d[3] for d in matrix.values()])
        else:
            fig.add_bar(y=list(matrix), x=widths, orientation="h", name=str(val),
                        marker_color=COLORS[val],
                        hovertemplate="%{y} · " + str(val) + ": %{customdata:.1f}%<extra></extra>",
                        customdata=[d[val] for d in matrix.values()])
    fig.update_layout(barmode="relative", xaxis=dict(title="Percentual de respostas", ticksuffix="%",
                      range=[-100, 100], zeroline=True, zerolinecolor="#60718b"),
                      yaxis=dict(autorange="reversed"))
    return fig_style(fig, 270 + 25 * len(codes))


def categorical_chart(df: pd.DataFrame, col: str, title: str):
    counts = df[col].value_counts(dropna=False).rename_axis("Categoria").reset_index(name="Pessoas")
    fig = px.bar(counts, y="Categoria", x="Pessoas", orientation="h", text="Pessoas",
                 color_discrete_sequence=["#3977a5"])
    fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
    fig.update_traces(textposition="outside")
    return fig_style(fig, 280)


def nformat(v, digits=3):
    return "—" if pd.isna(v) else f"{v:.{digits}f}".replace(".", ",")


st.sidebar.markdown("**PUC MINAS · 2026/2**")
st.sidebar.caption("Medição e Experimentação em Engenharia de Software")
st.sidebar.divider()
st.sidebar.subheader("Fonte dos dados")
upload = st.sidebar.file_uploader("Carregar exportação do Forms", type=["xlsx", "csv"],
                                  help="Arquivo mantido na sessão; não é publicado no GitHub.")
local_path = Path("data/respostas.xlsx")
if upload:
    try:
        raw = read_file(upload)
    except Exception as err:
        st.error(f"Não foi possível ler o arquivo: {err}")
        st.stop()
elif local_path.exists():
    raw = load_local(str(local_path))
else:
    st.markdown('<p class="eyebrow">PESQUISA ACADÊMICA · DASHBOARD INTERATIVO</p>', unsafe_allow_html=True)
    st.title("O paradoxo da produtividade com IA")
    st.info("Carregue a exportação XLSX ou CSV do Google Forms pela barra lateral para visualizar os indicadores."
            " Para executar localmente, coloque o arquivo em `data/respostas.xlsx` (ignorado pelo Git).")
    st.caption("Nenhum dado de participante é distribuído junto com este repositório.")
    st.stop()

try:
    all_data = prepare(raw)
except ValueError as err:
    st.error(f"Estrutura incompatível com o questionário oficial: {err}")
    st.stop()

st.sidebar.divider()
st.sidebar.subheader("Filtros dos participantes")
valid = all_data[all_data["valida"]].copy()
filter_labels = {"E01": "Perfil (E01)", "E04": "Experiência (E04)", "E05": "Uso de IA (E05)"}
selected = {}
for col, label in filter_labels.items():
    options = sorted(valid[col].dropna().astype(str).unique())
    selected[col] = st.sidebar.multiselect(label, options, default=options)
mask = pd.Series(True, index=valid.index)
for col, chosen in selected.items():
    mask &= valid[col].isin(chosen)
subset = valid.loc[mask].copy()
scored, meta = construct_scores(subset)

st.markdown('<p class="eyebrow">SURVEY · DADOS PRELIMINARES</p>', unsafe_allow_html=True)
st.title("O paradoxo da produtividade com IA")
st.caption("Produtividade percebida, retrabalho e confiança no código gerado · Coleta observacional transversal")
if len(valid) < 50:
    st.info("Resultados exploratórios: a coleta ainda não atingiu 50 respostas válidas. "
            "As inferências devem ser revisadas após o encerramento.")

k1,k2,k3,k4 = st.columns(4)
k1.metric("Respostas recebidas", len(all_data), help="Total bruto, sem filtros")
k2.metric("Válidas (total)", len(valid), help="Após TCLE, elegibilidade, AT01 e itens obrigatórios")
k3.metric("Excluídas", len(all_data)-len(valid))
k4.metric("Amostra filtrada", len(scored), help="Os filtros não alteram a auditoria global")

if len(scored) < 1:
    st.warning("Nenhuma resposta válida atende aos filtros. Altere os filtros na barra lateral.")
    st.stop()

tabs = st.tabs(["Visão geral", "QP1 · Paradoxo", "QP2 · Esforço", "QP3 · Confiança", "Método e qualidade"])
with tabs[0]:
    st.subheader("Quem respondeu?")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(categorical_chart(scored, "E01", "Perfil"), use_container_width=True)
    with b:
        st.plotly_chart(categorical_chart(scored, "E04", "Experiência"), use_container_width=True)
    st.subheader("Distribuição das respostas por construto")
    st.caption("Barras Likert divergentes de 1 (discordância total) a 5 (concordância total).")
    st.plotly_chart(likert_chart(scored, ["P01","P02","P03","R01","R02","R03"],
                  ["P01 · Primeira versão", "P02 · Superar dificuldades", "P03 · Mais tarefas",
                   "R01 · Alterações", "R02 · Esforço de correção", "R03 · Economia de tempo"]),
                    use_container_width=True)

with tabs[1]:
    st.subheader("QP1 · Produtividade percebida × retrabalho")
    st.caption("Em que medida ganhos percebidos coexistem com esforço adicional?")
    coexist = coexistence(scored)
    test = correlations(scored).iloc[0]
    a,b,c = st.columns(3)
    a.metric("Coexistência (P ≥ 4 e R ≥ 4)",
             f"{nformat(coexist['percent'],1)}%", f"{coexist['total']} de {coexist['n']} respondentes")
    b.metric("Spearman ρ", nformat(test["rho"]))
    c.metric("p ajustado (Holm)", nformat(test["p_holm"],4))
    st.caption(f"P: {meta['P']['method']} · R: {meta['R']['method']}. Holm considera QP1 e três testes QP3.")
    matrix = pd.crosstab(scored["P"], scored["R"])
    fig = px.imshow(matrix, text_auto=True, labels=dict(x="Retrabalho (R)",y="Produtividade (P)", color="Participantes"),
                    color_continuous_scale="Blues", aspect="auto")
    st.plotly_chart(fig_style(fig,430), use_container_width=True)
    st.caption("Cada célula mostra a quantidade de pessoas no par de escores observado; não são dados individuais.")
    st.plotly_chart(likert_chart(scored, ["P01","P02","P03","R01","R02","R03"],
                  ["P01", "P02", "P03", "R01", "R02", "R03"]), use_container_width=True)

with tabs[2]:
    st.subheader("QP2 · Quais atividades demandam mais esforço?")
    details, global_test, posthoc = effort_analysis(scored)
    a,b,c = st.columns(3)
    a.metric("Friedman χ²", nformat(global_test["friedman"]))
    b.metric("p global", nformat(global_test["p"],4))
    c.metric("Kendall W", nformat(global_test["kendall_w"]))
    fig = px.bar(details, x="Atividade", y="% esforço 4–5", text="% esforço 4–5",
                 color_discrete_sequence=["#296293"])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_yaxes(range=[0,105], title="% de respostas com muito/extremo esforço")
    st.plotly_chart(fig_style(fig), use_container_width=True)
    st.dataframe(details, use_container_width=True, hide_index=True)
    st.caption(f"Teste de Friedman calculado em {global_test['n_pareado']} registros completos "
               "(N/A é ausência legítima por item).")
    if not posthoc.empty:
        st.markdown("**Comparações pareadas pós-hoc (Wilcoxon + Holm)**")
        st.dataframe(posthoc, hide_index=True, use_container_width=True)
    elif pd.notna(global_test["p"]) and global_test["p"] >= .05:
        st.caption("Sem pós-hoc: teste global não significativo a α = 0,05.")

with tabs[3]:
    st.subheader("QP3 · Confiança e frequência de verificação")
    st.caption(f"Confiança (C): {meta['C']['method']}; comparação com três comportamentos independentes.")
    corr = correlations(scored).iloc[1:].copy()
    st.dataframe(corr.rename(columns={"comparacao":"Relação", "rho":"Spearman ρ", "p":"p bruto",
                                          "p_holm":"p Holm"}), hide_index=True, use_container_width=True)
    st.plotly_chart(likert_chart(scored, ["C01","C02","C03"],
                  ["C01 · Correção", "C02 · Requisitos", "C03 · Robustez"]), use_container_width=True)
    st.plotly_chart(likert_chart(scored, list(VERIFY), list(VERIFY.values())), use_container_width=True)

with tabs[4]:
    st.subheader("Qualidade, análise e pré-registro")
    st.markdown("**Auditoria global das respostas**")
    reasons = all_data["motivo"].value_counts().rename_axis("Motivo principal").reset_index(name="Quantidade")
    st.dataframe(reasons, hide_index=True, use_container_width=True)
    st.markdown("**Consistência interna (amostra filtrada)**")
    alphas = pd.DataFrame([{"Construto":n, "Alfa de Cronbach":m["alpha"],
                            "Indicador utilizado":m["method"]} for n,m in meta.items()])
    st.dataframe(alphas, hide_index=True, use_container_width=True)
    st.markdown("**Critérios previamente registrados**")
    st.markdown("""
    - Público: adultos, estudantes de TI e/ou profissionais, com prática em programação e uso de IA nos últimos 6 meses.
    - Exclusão: TCLE/maioridade, E01–E03, AT01 diferente de 4, item obrigatório ausente/inválido.
    - E05 = 0 dias nos últimos 30 dias **não** exclui; A01–A04 = “Não se aplica” é ausência legítima.
    - Escalas ordinais. P, R e C são médias somente com alfa ≥ 0,70; caso contrário, P03, R02 e C01.
    - QP1/QP3: correlações de Spearman bicaudais, ajuste de Holm em uma família de quatro testes.
    - QP2: Friedman, Kendall W; Wilcoxon pareado pós-hoc se p global < 0,05, com Holm separado.
    - Respostas abertas: categorização manual por dois avaliadores independentes; não exibimos texto bruto no painel.
    """)
    st.warning("Amostragem por conveniência e bola de neve: as porcentagens descrevem a amostra. "
               "A margem de erro nominal não assegura representatividade populacional. "
               "Não se pode concluir causalidade.")
    st.caption("Base: exportação bruta do Forms. Nenhuma linha individual ou resposta aberta é publicada. "
               "A classificação dos descartes mostra somente o primeiro motivo por registro.")

st.divider()
st.caption("PUC Minas · Medição e Experimentação em Engenharia de Software · Protocolo de survey pré-registrado · 2026/2")