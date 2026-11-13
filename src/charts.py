"""Gráficos agregados do survey. Apenas Altair/Vega-Lite, com tema explícito.

O tema não depende do navegador ou do tema do usuário do Streamlit.
Nenhuma visualização expõe linhas individuais da planilha.
"""
from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd

# Branco + preto e escala de azuis. A diferença entre categorias não depende
# exclusivamente da cor: há posições, eixos, rótulos e tooltips legíveis.
INK = "#000000"
PAPER = "#FFFFFF"
BLUE = "#2563EB"
BLUE_MEDIUM = "#3B82F6"
BLUE_LIGHT = "#93C5FD"
LINE = "#D9E2EC"
GRID = "#E6EDF5"

AGREE = {
    "1 · Discordo totalmente": "#C6E0FF",
    "2 · Discordo parcialmente": "#93C5FD",
    "3 · Nem concordo nem discordo": "#E2E8F0",
    "4 · Concordo parcialmente": "#60A5FA",
    "5 · Concordo totalmente": "#1D4ED8",
}
LEVEL = {
    1: "#E0F0FF", 2: "#B9D9FF", 3: "#8CBDFC", 4: "#4B92EB", 5: "#1D5CB3",
}
EFFORT = {
    1: "1 · Nenhum", 2: "2 · Pouco", 3: "3 · Moderado",
    4: "4 · Elevado", 5: "5 · Extremamente elevado",
}
FREQUENCY = {
    1: "1 · Nunca", 2: "2 · Raramente", 3: "3 · Às vezes",
    4: "4 · Frequentemente", 5: "5 · Sempre",
}


def chart_theme(chart: alt.TopLevelMixin) -> alt.TopLevelMixin:
    """Força contraste preto/branco, inclusive se a preferência de tema for escura."""
    return (
        chart.configure(background=PAPER, padding={"left": 8, "right": 15, "top": 10, "bottom": 8})
        .configure_view(fill=PAPER, stroke=LINE, strokeWidth=1)
        .configure_axis(
            labelColor=INK, titleColor=INK, domainColor="#7892A9",
            tickColor="#7892A9", gridColor=GRID, gridWidth=1,
            labelFontSize=13, titleFontSize=13,
            labelPadding=8, titlePadding=12,
        )
        .configure_legend(
            labelColor=INK, titleColor=INK, labelFontSize=12,
            titleFontSize=12, symbolSize=180,
        )
    )


def category_chart(df: pd.DataFrame, col: str, short_labels: dict[str, str] | None = None):
    """Distribuição de perfis/categorias, com contagem explícita."""
    labels = df[col].fillna("Não informado").astype(str)
    if short_labels:
        labels = labels.map(lambda s: short_labels.get(s, s))
    counts = labels.value_counts()
    tab = counts.rename_axis("Categoria").reset_index(name="Pessoas")
    order = tab["Categoria"].tolist()
    y = alt.Y("Categoria:N", sort=order, title=None, axis=alt.Axis(labelLimit=290))
    x = alt.X("Pessoas:Q", title="Participantes", axis=alt.Axis(tickMinStep=1),
              scale=alt.Scale(domainMin=0, nice=True))
    bars = alt.Chart(tab).mark_bar(color=BLUE, size=28, cornerRadiusEnd=5).encode(
        x=x, y=y, tooltip=["Categoria:N", alt.Tooltip("Pessoas:Q", title="Participantes")],
    )
    number = alt.Chart(tab).mark_text(align="left", dx=8, color=INK,
                                      fontSize=13, fontWeight="bold").encode(
        x="Pessoas:Q", y=y, text=alt.Text("Pessoas:Q", format="d"),
    )
    return chart_theme((bars + number).properties(height=max(190, len(tab) * 48)))


def likert_data(df: pd.DataFrame, codes: list[str], labels: list[str]) -> pd.DataFrame:
    """Monta barras divergentes 100%; divide neutro visualmente, sem duplicar respostas."""
    rows = []
    agree_names = list(AGREE)
    for code, label in zip(codes, labels):
        values = df[code + "_n"].dropna().astype(int)
        fractions = values.value_counts(normalize=True).mul(100)
        amounts = {i: float(fractions.get(i, 0)) for i in range(1, 6)}
        neut = amounts[3] / 2
        segments = [
            (1, -amounts[1] - amounts[2] - neut, -amounts[2] - neut),
            (2, -amounts[2] - neut, -neut),
            (3, -neut, 0), (3, 0, neut),
            (4, neut, neut + amounts[4]),
            (5, neut + amounts[4], neut + amounts[4] + amounts[5]),
        ]
        for value, left, right in segments:
            rows.append({
                "Pergunta": label, "Resposta": agree_names[value - 1],
                "Início": left, "Fim": right,
                "Percentual": round(amounts[value], 2), "n": len(values),
            })
    return pd.DataFrame(rows)


def likert_chart(df: pd.DataFrame, codes: list[str], labels: list[str]):
    data = likert_data(df, codes, labels)
    y = alt.Y("Pergunta:N", sort=labels, title=None,
              axis=alt.Axis(labelLimit=290, labelFontSize=13))
    bar = alt.Chart(data).mark_bar(size=28).encode(
        x=alt.X("Início:Q", scale=alt.Scale(domain=[-100, 100]),
                title="Discordância ← percentual de respostas → Concordância",
                axis=alt.Axis(values=[-100, -50, 0, 50, 100],
                              labelExpr="abs(datum.value) + '%'")),
        x2="Fim:Q", y=y,
        color=alt.Color("Resposta:N", sort=list(AGREE),
                        scale=alt.Scale(domain=list(AGREE), range=list(AGREE.values())),
                        legend=alt.Legend(title="Grau de concordância", orient="bottom", columns=3,
                                          labelLimit=240)),
        tooltip=["Pergunta:N", "Resposta:N", alt.Tooltip("Percentual:Q", format=".1f", title="%"),
                 alt.Tooltip("n:Q", title="Respostas válidas")],
    )
    zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color=INK, strokeWidth=1.1).encode(
        x="zero:Q"
    )
    return chart_theme((bar + zero).properties(height=max(210, len(codes) * 50)))


def ordinal_data(df: pd.DataFrame, codes: list[str], labels: list[str], levels: dict[int, str]):
    """Distribuição 100% empilhada para escalas ordinais de esforço/frequência."""
    rows = []
    for code, label in zip(codes, labels):
        values = df[code + "_n"].dropna().astype(int)
        percentages = values.value_counts(normalize=True).mul(100)
        pos = 0.0
        for i in range(1, 6):
            value = float(percentages.get(i, 0))
            rows.append({"Atividade": label, "Intensidade": levels[i], "Início": pos,
                         "Fim": pos + value, "Percentual": round(value, 2), "n": len(values)})
            pos += value
    return pd.DataFrame(rows)


def ordinal_chart(df: pd.DataFrame, codes: list[str], labels: list[str],
                  levels: dict[int, str] = EFFORT):
    data = ordinal_data(df, codes, labels, levels)
    return chart_theme(alt.Chart(data).mark_bar(size=33).encode(
        x=alt.X("Início:Q", scale=alt.Scale(domain=[0, 100]),
                title="Distribuição de respostas (%)",
                axis=alt.Axis(values=[0, 25, 50, 75, 100], labelExpr="datum.value + '%'")),
        x2="Fim:Q",
        y=alt.Y("Atividade:N", sort=labels, title=None,
                axis=alt.Axis(labelLimit=290, labelFontSize=13)),
        color=alt.Color("Intensidade:N", sort=list(levels.values()),
                        scale=alt.Scale(domain=list(levels.values()), range=list(LEVEL.values())),
                        legend=alt.Legend(title="Escala de resposta", orient="bottom", columns=3,
                                          labelLimit=220)),
        tooltip=["Atividade:N", "Intensidade:N",
                 alt.Tooltip("Percentual:Q", format=".1f", title="%"),
                 alt.Tooltip("n:Q", title="Respostas aplicáveis")],
    ).properties(height=max(230, len(codes) * 58)))


def quadrant_data(df: pd.DataFrame) -> pd.DataFrame:
    """Grupos por limiares PRÉ-REGISTRADOS: P>=4 e R>=4; valores 3 não são 'baixos'."""
    pair = df[["P", "R"]].dropna()
    total = len(pair)
    rows = []
    for r_high, r_label in [(True, "Retrabalho ≥ 4"), (False, "Retrabalho < 4")]:
        for p_high, p_label in [(False, "Produtividade < 4"), (True, "Produtividade ≥ 4")]:
            n = int(((pair["P"] >= 4) == p_high).mul((pair["R"] >= 4) == r_high).sum())
            rows.append({
                "Produtividade": p_label, "Retrabalho": r_label, "Participantes": n,
                "Porcentagem": round(100 * n / total, 1) if total else 0.,
                "Proporção": f"{(100 * n / total):.1f}%".replace(".", ",") if total else "0,0%",
                "Contagem": f"{n} de {total}", "Quadrante": (
                    "Ambos ≥ 4" if p_high and r_high else
                    "Somente produtividade ≥ 4" if p_high else
                    "Somente retrabalho ≥ 4" if r_high else "Ambos < 4"
                ),
            })
    return pd.DataFrame(rows)


def quadrant_chart(df: pd.DataFrame):
    data = quadrant_data(df)
    prod = ["Produtividade < 4", "Produtividade ≥ 4"]
    retr = ["Retrabalho ≥ 4", "Retrabalho < 4"]
    x = alt.X("Produtividade:N", sort=prod, title=None,
              axis=alt.Axis(labelFontSize=13, labelLimit=270, labelAngle=0, orient="top",
                            labelPadding=12))
    y = alt.Y("Retrabalho:N", sort=retr, title=None,
              axis=alt.Axis(labelFontSize=13, labelLimit=210, labelPadding=12))
    color_domain = ["Ambos < 4", "Somente produtividade ≥ 4", "Somente retrabalho ≥ 4", "Ambos ≥ 4"]
    colors = ["#F0F7FF", "#C7E0FF", "#DCEBFF", "#60A5FA"]
    tiles = alt.Chart(data).mark_rect(stroke=PAPER, strokeWidth=8,
                                      cornerRadius=10).encode(
        x=x, y=y,
        color=alt.Color("Quadrante:N", scale=alt.Scale(domain=color_domain, range=colors),
                        legend=None),
        tooltip=["Produtividade:N", "Retrabalho:N", "Participantes:Q",
                 alt.Tooltip("Porcentagem:Q", title="% da amostra")],
    )
    pct = alt.Chart(data).mark_text(fontSize=27, fontWeight="bold", color=INK, dy=-14).encode(
        x=x, y=y, text="Proporção:N",
    )
    count = alt.Chart(data).mark_text(fontSize=13, color=INK, dy=18).encode(
        x=x, y=y, text="Contagem:N",
    )
    return chart_theme((tiles + pct + count).properties(height=330))


def pair_heatmap(df: pd.DataFrame):
    """Detalhe opcional: contagem agregada para pares de escores observados."""
    pair = df[["P", "R"]].dropna()
    if pair.empty:
        data = pd.DataFrame({"Produtividade": [], "Retrabalho": [], "Participantes": []})
    else:
        data = pair.groupby(["P", "R"]).size().reset_index(name="Participantes")
        data["Produtividade"] = data["P"].map(lambda v: f"{v:g}".replace(".", ","))
        data["Retrabalho"] = data["R"].map(lambda v: f"{v:g}".replace(".", ","))
    tile = alt.Chart(data).mark_rect(stroke=PAPER, strokeWidth=5).encode(
        x=alt.X("Retrabalho:N", title="Escore de retrabalho (R)"),
        y=alt.Y("Produtividade:N", title="Escore de produtividade (P)"),
        color=alt.Color("Participantes:Q", scale=alt.Scale(scheme="blues"),
                        legend=alt.Legend(title="Respostas")),
        tooltip=["Produtividade:N", "Retrabalho:N", "Participantes:Q"],
    )
    labels = alt.Chart(data).mark_text(fontSize=14, color=INK, fontWeight="bold").encode(
        x="Retrabalho:N", y="Produtividade:N", text="Participantes:Q",
    )
    return chart_theme((tile + labels).properties(height=330))


def effort_chart(details: pd.DataFrame):
    """Ranking complementar: fração 4 e 5, além do panorama 1 a 5."""
    safe = details.copy()
    safe["Rótulo"] = safe["% esforço 4–5"].map(
        lambda x: f"{x:.1f}%".replace(".", ",") if pd.notna(x) else "—"
    )
    order = safe.sort_values("% esforço 4–5", ascending=False)["Atividade"].tolist()
    y = alt.Y("Atividade:N", sort=order, title=None,
              axis=alt.Axis(labelLimit=280, labelFontSize=13))
    bars = alt.Chart(safe).mark_bar(color=BLUE, size=30, cornerRadiusEnd=5).encode(
        x=alt.X("% esforço 4–5:Q", scale=alt.Scale(domain=[0, 100]),
                title="Respostas 4 ou 5 (%)",
                axis=alt.Axis(values=[0, 25, 50, 75, 100], labelExpr="datum.value + '%'")),
        y=y,
        tooltip=["Atividade:N", alt.Tooltip("% esforço 4–5:Q", format=".1f"),
                 "n:Q", "Mediana:Q"],
    )
    text = alt.Chart(safe).mark_text(color=INK, align="left", dx=8,
                                      fontSize=13, fontWeight="bold").encode(
        x="% esforço 4–5:Q", y=y, text="Rótulo:N",
    )
    return chart_theme((bars + text).properties(height=260))


def correlation_chart(correlations: pd.DataFrame):
    """Coeficientes Spearman da QP3, apresentados em escala fixa [-1,1]."""
    labels = {
        "QP3 · Confiança × Revisão da lógica": "Revisar a lógica",
        "QP3 · Confiança × Execução de testes": "Executar testes",
        "QP3 · Confiança × Validação dos requisitos": "Validar requisitos",
    }
    values = correlations.copy()
    values["Comportamento"] = values["comparacao"].map(labels).fillna(values["comparacao"])
    values["Zero"] = 0.0
    values["ρ"] = values["rho"].map(
        lambda x: f"{x:+.2f}".replace(".", ",") if pd.notna(x) else "Não calculável"
    )
    order = list(labels.values())
    y = alt.Y("Comportamento:N", sort=order, title=None,
              axis=alt.Axis(labelLimit=230, labelFontSize=13))
    x = alt.X("rho:Q", scale=alt.Scale(domain=[-1, 1]),
              title="Correlação de Spearman (ρ)",
              axis=alt.Axis(values=[-1, -.5, 0, .5, 1]))
    guide = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color=INK, strokeWidth=1.5).encode(
        x=alt.X("zero:Q", scale=alt.Scale(domain=[-1, 1]))
    )
    segments = alt.Chart(values).mark_rule(color=BLUE_LIGHT, strokeWidth=5).encode(
        x=alt.X("Zero:Q", scale=alt.Scale(domain=[-1, 1])), x2="rho:Q", y=y,
    )
    dots = alt.Chart(values).mark_circle(color=BLUE, size=165).encode(
        x=x, y=y,
        tooltip=["Comportamento:N", alt.Tooltip("rho:Q", title="ρ", format=".3f"),
                 alt.Tooltip("p:Q", title="p bruto", format=".4f"),
                 alt.Tooltip("p_holm:Q", title="p Holm", format=".4f"),
                 alt.Tooltip("n:Q", title="n efetivo")],
    )
    return chart_theme((guide + segments + dots).properties(height=255))