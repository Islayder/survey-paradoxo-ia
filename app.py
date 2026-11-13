"""Dashboard do survey: indicadores agregados e cálculos pré-registrados."""
from pathlib import Path
import io

import pandas as pd
import streamlit as st

from src.charts import category_chart, likert_chart, pair_heatmap, effort_chart
from src.analysis import (
    VERIFY, coexistence, construct_scores, correlations,
    effort_analysis, prepare,
)

st.set_page_config(
    page_title="Paradoxo da IA | Survey PUC Minas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Não alteramos a cor geral dos widgets com CSS: ela vem do tema oficial
# em .streamlit/config.toml. Assim o texto sempre contrasta com seu fundo.
st.markdown("""
<style>
    .block-container {max-width: 1320px; padding-top: 2.0rem;}
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DBE5EE;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 7px rgba(14, 33, 55, .045);
    }
    div[data-testid="stMetricLabel"] {color: #52637A !important;}
    div[data-testid="stMetricValue"] {color: #15283F !important;}
    h1, h2, h3 {letter-spacing: -.025em;}
    h1 {font-size: clamp(1.8rem, 2.7vw, 2.35rem) !important;}
    .eyebrow {font-weight: 750; letter-spacing: .12em; font-size: .79rem; color:#0C6E83;}
    section[data-testid="stSidebar"] .eyebrow {color: #7DD3FC;}
    div[data-testid="stTabs"] button {font-weight: 650;}
    div[data-testid="stTabs"] button p {font-weight: 650;}
</style>
""", unsafe_allow_html=True)

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


def nformat(value, digits=3) -> str:
    return "—" if pd.isna(value) else f"{value:.{digits}f}".replace(".", ",")


st.sidebar.markdown('<p class="eyebrow">PUC MINAS · 2026/2</p>', unsafe_allow_html=True)
st.sidebar.markdown("**Medição e Experimentação em Engenharia de Software**")
st.sidebar.divider()
st.sidebar.subheader("Fonte dos dados")
upload = st.sidebar.file_uploader(
    "Exportação do Google Forms", type=["xlsx", "csv"],
    help="Carregue a planilha oficial. Não envie respostas ao GitHub.",
)
local_path = Path("data/respostas.xlsx")
if upload is not None:
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
    st.info("Envie a planilha XLSX ou CSV do Google Forms pela barra lateral para visualizar os resultados.")
    st.caption("O repositório não inclui respostas de participantes.")
    st.stop()

try:
    all_data = prepare(raw)
except ValueError as err:
    st.error(f"Estrutura incompatível com o questionário oficial: {err}")
    st.stop()

st.sidebar.divider()
st.sidebar.subheader("Filtros dos participantes")
valid = all_data[all_data["valida"]].copy()
selected = {}
for key, label in {"E01": "Perfil", "E04": "Tempo de experiência", "E05": "Frequência de uso de IA"}.items():
    options = sorted(valid[key].dropna().astype(str).unique())
    selected[key] = st.sidebar.multiselect(label, options, default=options)
mask = pd.Series(True, index=valid.index)
for col, chosen in selected.items():
    mask &= valid[col].isin(chosen)
subset = valid.loc[mask].copy()
scored, meta = construct_scores(subset)

st.markdown('<p class="eyebrow">SURVEY · RESULTADOS PRELIMINARES</p>', unsafe_allow_html=True)
st.title("O paradoxo da produtividade com IA")
st.caption("Produtividade percebida, retrabalho e confiança no código gerado · Survey transversal")
if len(valid) < 50:
    st.info("Coleta em andamento: ainda não atingimos 50 respostas válidas. ")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Respostas recebidas", len(all_data), help="Total bruto, independentemente dos filtros")
k2.metric("Válidas (total)", len(valid), help="Depois das exclusões do protocolo")
k3.metric("Excluídas", len(all_data) - len(valid))
k4.metric("Amostra filtrada", len(scored), help="O filtro não modifica a auditoria global")

if scored.empty:
    st.warning("Nenhuma resposta válida atende aos filtros selecionados.")
    st.stop()

tabs = st.tabs(["Visão geral", "QP1 · Paradoxo", "QP2 · Esforço", "QP3 · Confiança", "Método e qualidade"])
with tabs[0]:
    st.subheader("Quem respondeu?")
    a, b = st.columns(2)
    with a:
        st.altair_chart(category_chart(scored, "E01"), use_container_width=True)
    with b:
        st.altair_chart(category_chart(scored, "E04"), use_container_width=True)
    st.subheader("Produtividade e retrabalho")
    st.caption("Barras Likert divergentes: discordância à esquerda e concordância à direita.")
    st.altair_chart(likert_chart(
        scored, ["P01", "P02", "P03", "R01", "R02", "R03"],
        ["P01 · Primeira versão", "P02 · Superar dificuldades", "P03 · Mais tarefas",
         "R01 · Alterações", "R02 · Esforço de correção", "R03 · Economia de tempo"],
    ), use_container_width=True)

with tabs[1]:
    st.subheader("QP1 · Produtividade percebida × retrabalho")
    st.caption("Em que medida ganhos de produtividade percebidos coexistem com retrabalho?")
    both = coexistence(scored)
    test = correlations(scored).iloc[0]
    a, b, c = st.columns(3)
    a.metric("Coexistência (P ≥ 4 e R ≥ 4)", f"{nformat(both['percent'],1)}%",
             help=f"{both['total']} de {both['n']} respostas com escores disponíveis")
    b.metric("Correlação de Spearman (ρ)", nformat(test["rho"]))
    c.metric("p ajustado (Holm)", nformat(test["p_holm"], 4))
    st.caption(f"P: {meta['P']['method']} · R: {meta['R']['method']}. Holm considera QP1 e as três análises de QP3.")
    st.altair_chart(pair_heatmap(scored), use_container_width=True)
    st.caption("Células mostram contagens agregadas para os pares de escores; não identificam participantes.")
    st.altair_chart(likert_chart(scored, ["P01", "P02", "P03", "R01", "R02", "R03"],
                                ["P01", "P02", "P03", "R01", "R02", "R03"]), use_container_width=True)

with tabs[2]:
    st.subheader("QP2 · Esforço por atividade")
    st.caption("Comparação de compreensão, correção, adaptação e integração do código gerado por IA.")
    details, global_test, posthoc = effort_analysis(scored)
    a, b, c = st.columns(3)
    a.metric("Friedman (χ²)", nformat(global_test["friedman"]))
    b.metric("p global", nformat(global_test["p"], 4))
    c.metric("Kendall W", nformat(global_test["kendall_w"]))
    st.altair_chart(effort_chart(details), use_container_width=True)
    st.dataframe(details, use_container_width=True, hide_index=True)
    st.caption(f"Friedman usa {global_test['n_pareado']} registros completos. 'Não se aplica' não equivale a zero.")
    if not posthoc.empty:
        st.markdown("**Comparações pós-hoc (Wilcoxon pareado + Holm)**")
        st.dataframe(posthoc, hide_index=True, use_container_width=True)
    elif pd.notna(global_test["p"]) and global_test["p"] >= .05:
        st.caption("Sem pós-hoc: teste global não significativo no nível α = 0,05.")

with tabs[3]:
    st.subheader("QP3 · Confiança e verificação")
    st.caption(f"Confiança: {meta['C']['method']}. Associação com três comportamentos de verificação.")
    corr = correlations(scored).iloc[1:].copy()
    st.dataframe(corr.rename(columns={"comparacao": "Relação", "rho": "Spearman ρ",
                                     "p": "p bruto", "p_holm": "p Holm"}),
                 hide_index=True, use_container_width=True)
    st.altair_chart(likert_chart(scored, ["C01", "C02", "C03"],
                                 ["C01 · Correção", "C02 · Requisitos", "C03 · Robustez"]),
                    use_container_width=True)
    st.altair_chart(likert_chart(scored, list(VERIFY), list(VERIFY.values())),
                    use_container_width=True)

with tabs[4]:
    st.subheader("Método e qualidade da amostra")
    st.markdown("**Auditoria global — motivos principais**")
    reasons = all_data["motivo"].value_counts().rename_axis("Motivo").reset_index(name="Quantidade")
    st.dataframe(reasons, hide_index=True, use_container_width=True)
    st.markdown("**Confiabilidade dos construtos (amostra filtrada)**")
    alpha_df = pd.DataFrame([{"Construto": name, "Alfa de Cronbach": m["alpha"],
                              "Indicador utilizado": m["method"]} for name, m in meta.items()])
    st.dataframe(alpha_df, hide_index=True, use_container_width=True)
    with st.expander("Critérios pré-registrados e limitações", expanded=True):
        st.markdown("""
        - População: adultos com prática de programação e uso de assistentes de IA nos últimos seis meses.
        - Exclusões: consentimento/maioridade, perfil E01–E03, AT01 ≠ 4, item obrigatório ausente/inválido.
        - E05 = zero dias nos últimos 30 dias **não** exclui; A01–A04 = “Não se aplica” é ausência legítima.
        - P/R/C são médias dos três itens se alfa ≥ 0,70; caso contrário, P03/R02/C01.
        - QP1 e QP3: Spearman bicaudal, com Holm em uma família de quatro testes.
        - QP2: Friedman, Kendall W; Wilcoxon pós-hoc, quando aplicável, com Holm separado.
        - Questão aberta: codificação manual por dois avaliadores, sem publicação do texto individual.
        """)
    st.warning("A amostra é não probabilística (conveniência e bola de neve). Não assegura representatividade "
               "e não permite interpretações causais.")
    st.caption("O painel mostra apenas agregados; a base bruta e as respostas abertas não integram o repositório.")

st.divider()
st.caption("PUC Minas · Medição e Experimentação em Engenharia de Software · Survey pré-registrado · 2026/2")