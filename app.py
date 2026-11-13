"""Dashboard interativo do survey pré-registrado — PUC Minas 2026/2.

Visualizações são agregadas; testes e filtros preservam o protocolo da Parte 1.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import (
    ACTIVITY, VERIFY, coexistence, construct_scores, correlations,
    effort_analysis, prepare,
)
from src.charts import (
    EFFORT, FREQUENCY, category_chart, correlation_chart, effort_chart,
    likert_chart, ordinal_chart, pair_heatmap, quadrant_chart,
)

st.set_page_config(
    page_title="Survey · Produtividade com IA | PUC Minas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Padrão visual deliberado: branco = preto, azul claro como apoio.
# O tema nativo controla widgets. CSS trata bordas/contrastes sem mudar
# dimensões ou esconder componentes do Streamlit.
st.markdown("""
<style>
:root {color-scheme: light;}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}
.block-container {max-width: 1320px; padding-top: 2.0rem; padding-bottom: 3rem;}
[data-testid="stMain"] h1, [data-testid="stMain"] h2,
[data-testid="stMain"] h3, [data-testid="stMain"] p,
[data-testid="stMain"] label, [data-testid="stMain"] .stCaption {
    color: #000000 !important;
}
h1, h2, h3 {letter-spacing: -.025em;}
h1 {font-size: clamp(1.8rem, 2.6vw, 2.35rem) !important;}
.eyebrow {font-weight: 750; letter-spacing: .09em; font-size: .81rem; color:#1D4ED8;}
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 16px 20px;
    box-shadow: 0 2px 7px rgba(30,64,120,.035);
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color: #000000 !important;
    opacity: 1 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: #D9E2EC;
}
[data-testid="stSidebar"] {
    background: #F0F7FF !important;
    border-right: 1px solid #BFDBFE !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
    color: #000000 !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-color: #93B6E0 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#000000 !important;}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border-color: #B9D9FF !important;
}
[data-testid="stMain"] [data-baseweb="tab"] {color:#000000 !important;}
[data-testid="stMain"] [aria-selected="true"] {color:#1D4ED8 !important;}
[data-testid="stMain"] [data-testid="stAlert"] {border:1px solid #BFDBFE;}
[data-testid="stMain"] [data-testid="stAlert"] * {color:#000000 !important;}
</style>
""", unsafe_allow_html=True)


PROFILE_SHORT = {
    "Sou estudante de TI e trabalho com desenvolvimento de software.": "Estudante e profissional",
    "Sou estudante de um curso de TI.": "Estudante de TI",
    "Trabalho profissionalmente com desenvolvimento de software.": "Profissional de software",
}
EXPERIENCE_ORDER = [
    "Menos de 1 ano", "De 1 a menos de 3 anos", "De 3 a menos de 5 anos",
    "De 5 a menos de 10 anos", "10 anos ou mais",
]
USE_ORDER = ["0 dias", "1 a 3 dias", "4 a 7 dias", "8 a 15 dias", "16 a 30 dias"]
PAGE_NAMES = ["Visão geral", "QP1 · Paradoxo", "QP2 · Esforço", "QP3 · Confiança", "Método e qualidade"]


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


def ordered_options(available: list[str], order: list[str]) -> list[str]:
    return [x for x in order if x in available] + sorted(x for x in available if x not in order)


def single_filter(key: str, label: str, values: pd.Series,
                  order: list[str] | None = None,
                  format_map: dict[str, str] | None = None) -> str | None:
    available = values.dropna().astype(str).unique().tolist()
    options = ordered_options(available, order) if order else sorted(available)
    selected = st.sidebar.selectbox(
        label, ["Todos"] + options, index=0, key=f"filter_{key}",
        format_func=lambda s: (format_map or {}).get(s, s),
    )
    return None if selected == "Todos" else selected


def show_chart(chart, caption: str | None = None):
    # theme=None impede que cores claras de fontes do tema Streamlit sobrescrevam os eixos.
    st.altair_chart(chart, use_container_width=True, theme=None)
    if caption:
        st.caption(caption)


def section_heading(title: str, subtitle: str):
    st.subheader(title)
    st.caption(subtitle)


st.sidebar.markdown('<p class="eyebrow">PUC MINAS · 2026/2</p>', unsafe_allow_html=True)
st.sidebar.markdown("**Medição e Experimentação em Engenharia de Software**")
st.sidebar.divider()
st.sidebar.markdown("**Fonte dos dados**")
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
    st.info("Envie o XLSX ou CSV do Google Forms pela barra lateral para visualizar os resultados.")
    st.caption("Este repositório não inclui respostas de participantes.")
    st.stop()

try:
    all_data = prepare(raw)
except ValueError as err:
    st.error(f"Estrutura incompatível com o questionário oficial: {err}")
    st.stop()

valid = all_data.loc[all_data["valida"]].copy()
st.sidebar.divider()
st.sidebar.markdown("**Filtros dos participantes**")
selected = {
    "E01": single_filter("E01", "Perfil", valid["E01"], format_map=PROFILE_SHORT),
    "E04": single_filter("E04", "Experiência em programação", valid["E04"], order=EXPERIENCE_ORDER),
    "E05": single_filter("E05", "Frequência de uso de IA", valid["E05"], order=USE_ORDER),
}
mask = pd.Series(True, index=valid.index)
for key, value in selected.items():
    if value is not None:
        mask &= valid[key].astype(str).eq(value)
subset = valid.loc[mask].copy()
scored, meta = construct_scores(subset)

st.markdown('<p class="eyebrow">SURVEY · RESULTADOS PRELIMINARES</p>', unsafe_allow_html=True)
st.title("O paradoxo da produtividade com IA")
st.caption("Produtividade percebida, retrabalho e confiança no código gerado por IA")
if len(valid) < 50:
    st.info("Coleta em andamento: as análises são exploratórias até o encerramento e a auditoria final da amostra.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Respostas recebidas", len(all_data), help="Base bruta, independentemente dos filtros")
k2.metric("Respostas válidas", len(valid), help="Conforme critérios do protocolo")
k3.metric("Descartadas", len(all_data) - len(valid))
k4.metric("Amostra filtrada", len(scored), help="Participantes válidos após aplicar os filtros")
st.progress(min(len(valid) / 50, 1.0), text=f"Meta da coleta: {len(valid)} de 50 respostas válidas")

st.divider()
page = st.segmented_control("Navegação", options=PAGE_NAMES, default=PAGE_NAMES[0],
                            selection_mode="single", label_visibility="collapsed")
if scored.empty:
    st.warning("Nenhuma resposta válida corresponde aos filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

if page == "Visão geral":
    section_heading("Quem respondeu?", "Distribuição das pessoas elegíveis na amostra selecionada.")
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown("**Perfil dos participantes**")
            show_chart(category_chart(scored, "E01", short_labels=PROFILE_SHORT))
    with b:
        with st.container(border=True):
            st.markdown("**Experiência em programação**")
            show_chart(category_chart(scored, "E04"))
    section_heading("Respostas aos itens de produtividade e retrabalho",
                    "Barras Likert divergentes: discordância à esquerda; concordância à direita. Escala de 1 a 5.")
    with st.container(border=True):
        st.markdown("**Produtividade percebida (P01–P03)**")
        show_chart(likert_chart(scored, ["P01", "P02", "P03"],
                                ["P01 · Primeira versão", "P02 · Superar dificuldades", "P03 · Mais tarefas"]))
    with st.container(border=True):
        st.markdown("**Retrabalho percebido (R01–R03)**")
        show_chart(likert_chart(scored, ["R01", "R02", "R03"],
                                ["R01 · Modificar código", "R02 · Esforço de correção", "R03 · Economia de tempo"]))

elif page == "QP1 · Paradoxo":
    section_heading("QP1 · Produtividade percebida × retrabalho",
                    "Ganhos percebidos de produtividade coexistem com esforço de retrabalho?")
    both = coexistence(scored)
    test = correlations(scored).iloc[0]
    a, b, c = st.columns(3)
    a.metric("Coexistência (P ≥ 4 e R ≥ 4)", f"{nformat(both['percent'], 1)}%",
             help=f"{both['total']} de {both['n']} respondentes com indicadores disponíveis")
    b.metric("Spearman (ρ)", nformat(test["rho"]))
    c.metric("p ajustado por Holm", nformat(test["p_holm"], 4))
    with st.container(border=True):
        st.markdown("**Matriz de coexistência**")
        st.caption("Cada célula apresenta o percentual e a contagem de pessoas. Limiar ≥ 4 conforme pré-registro.")
        show_chart(quadrant_chart(scored))
        st.caption(f"Produtividade: {meta['P']['method']} · Retrabalho: {meta['R']['method']}. "
                   "Valores abaixo de 4 incluem respostas neutras; não significam necessariamente avaliação negativa.")
    with st.expander("Distribuição conjunta detalhada dos escores"):
        st.caption("Contagem de pares de escores observados, sem dados de identificação individual.")
        show_chart(pair_heatmap(scored))
    st.caption("O ajuste de Holm considera esta correlação e as três correlações da QP3. "
               "Associação observada não implica causalidade.")

elif page == "QP2 · Esforço":
    section_heading("QP2 · Quais atividades exigem maior esforço?",
                    "Compreensão, correção, adaptação e integração do código gerado por IA.")
    details, global_test, posthoc = effort_analysis(scored)
    a, b, c = st.columns(3)
    a.metric("Friedman (χ²)", nformat(global_test["friedman"]))
    b.metric("p global", nformat(global_test["p"], 4))
    c.metric("Kendall W", nformat(global_test["kendall_w"]))
    with st.container(border=True):
        st.markdown("**Distribuição completa do esforço por atividade**")
        show_chart(ordinal_chart(scored, list(ACTIVITY), list(ACTIVITY.values()), levels=EFFORT),
                   "Percentuais calculados somente sobre respostas aplicáveis em cada item. "
                   "'Não se aplica' não conta como esforço zero.")
    with st.container(border=True):
        st.markdown("**Ranking de esforço elevado (categorias 4 e 5)**")
        show_chart(effort_chart(details))
        st.dataframe(details, hide_index=True, use_container_width=True)
    st.caption(f"Friedman utiliza {global_test['n_pareado']} pessoas com os quatro itens respondidos. "
               "Os valores são ordinais; mediana e distribuição são prioritárias.")
    if not posthoc.empty:
        with st.container(border=True):
            st.markdown("**Comparações pareadas pós-hoc: Wilcoxon + Holm**")
            st.dataframe(posthoc, hide_index=True, use_container_width=True)
    elif pd.notna(global_test["p"]) and global_test["p"] >= .05:
        st.caption("Pós-hoc não realizado: teste global não significativo a α = 0,05.")

elif page == "QP3 · Confiança":
    section_heading("QP3 · Confiança e verificação do código gerado por IA",
                    "Como a confiança se associa à revisão, à execução de testes e à validação de requisitos?")
    tests = correlations(scored).iloc[1:].copy()
    with st.container(border=True):
        st.markdown("**Associação entre confiança e comportamentos de verificação**")
        show_chart(correlation_chart(tests),
                   "ρ varia de −1 a +1. Valores negativos indicam associação inversa; "
                   "valores positivos, associação direta.")
        summary = tests.rename(columns={
            "comparacao": "Associação", "n": "n efetivo", "rho": "Spearman ρ",
            "p": "p bruto", "p_holm": "p Holm",
        })
        st.dataframe(summary, hide_index=True, use_container_width=True,
                     column_config={
                         "Spearman ρ": st.column_config.NumberColumn(format="%.3f"),
                         "p bruto": st.column_config.NumberColumn(format="%.4f"),
                         "p Holm": st.column_config.NumberColumn(format="%.4f"),
                     })
    st.caption(f"Confiança (C): {meta['C']['method']}. Correção de Holm feita em família única "
               "com a correlação da QP1.")
    with st.container(border=True):
        st.markdown("**Distribuição das respostas de confiança**")
        show_chart(likert_chart(scored, ["C01", "C02", "C03"],
                                ["C01 · Correção funcional", "C02 · Atendimento aos requisitos",
                                 "C03 · Robustez"]))
    with st.container(border=True):
        st.markdown("**Distribuição das frequências de verificação**")
        show_chart(ordinal_chart(scored, list(VERIFY), list(VERIFY.values()), levels=FREQUENCY))

else:
    section_heading("Método e qualidade da pesquisa",
                    "Rastreabilidade entre o pré-registro, a preparação da amostra e os testes executados.")
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown("**Auditoria global das respostas**")
            reasons = all_data["motivo"].value_counts().rename_axis("Motivo principal").reset_index(name="Quantidade")
            st.dataframe(reasons, hide_index=True, use_container_width=True)
            st.caption("Cada resposta descartada possui exatamente um motivo principal.")
    with b:
        with st.container(border=True):
            st.markdown("**Consistência interna dos construtos**")
            alpha_data = pd.DataFrame([
                {"Construto": {"P": "Produtividade", "R": "Retrabalho", "C": "Confiança"}[k],
                 "Alfa de Cronbach": v["alpha"], "Indicador aplicado": v["method"]}
                for k, v in meta.items()
            ])
            st.dataframe(alpha_data, hide_index=True, use_container_width=True,
                         column_config={
                             "Alfa de Cronbach": st.column_config.NumberColumn(format="%.3f")})
            st.caption("Com alfa < 0,70, é usado o indicador alternativo definido antes da coleta.")
    with st.expander("Critérios de seleção, testes e limitações", expanded=True):
        st.markdown("""
        - Participantes adultos, estudantes de TI ou profissionais, com programação prática e uso de IA nos últimos seis meses.
        - Exclusões: consentimento/maioridade, perfil E01–E03, AT01 diferente de 4 e respostas obrigatórias inválidas.
        - E05 = zero dias nos últimos 30 dias **não** exclui. A01–A04 = “Não se aplica” é ausência legítima por item.
        - Produtividade, retrabalho e confiança usam médias de três itens somente com alfa de Cronbach ≥ 0,70; senão P03/R02/C01.
        - QP1 e QP3: Spearman bicaudal; correção de Holm em quatro comparações.
        - QP2: Friedman e Kendall W; Wilcoxon pareado/Holm como pós-hoc condicionado ao resultado global.
        - A questão aberta exige codificação manual por duas pessoas, sem publicar os textos individuais.
        """)
    st.warning("Amostragem não probabilística (conveniência/bola de neve). "
               "Resultados descrevem esta amostra; não garantem representatividade nem permitem inferir causalidade.")
    st.caption("Dados brutos e respostas abertas não são incorporados ao repositório. "
               "Alterações em relação ao protocolo devem ser registradas na entrega final.")

st.divider()
st.caption("PUC Minas · Medição e Experimentação em Engenharia de Software · Survey pré-registrado · 2026/2")