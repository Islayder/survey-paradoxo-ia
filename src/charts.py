"""Visualizações agregadas em Altair, independentes da interface Streamlit."""

import altair as alt
import pandas as pd

# Paleta aplicada aos dados, não aos widgets. Negativos: terracota;
# neutro: cinza; positivos: verde. Contraste mantido em fundos claros.
LIKERT_COLORS = {
    "Discordo totalmente": "#B45347",
    "Discordo parcialmente": "#E3A091",
    "Neutro": "#B5C0CD",
    "Concordo parcialmente": "#78B5A6",
    "Concordo totalmente": "#237E70",
}
ACCENT = "#116F92"
TEXT = "#263B52"
GRID = "#E3EAF2"



def chart_theme(chart: alt.Chart) -> alt.Chart:
    """Estilo único para visualizações Vega-Lite, independente do tema do navegador."""
    return (
        chart.configure_view(stroke=None)
        .configure_axis(
            labelColor=TEXT, titleColor=TEXT, gridColor=GRID,
            labelFontSize=12, titleFontSize=12,
        )
        .configure_legend(labelColor=TEXT, titleColor=TEXT, labelFontSize=12)
    )


def category_chart(df: pd.DataFrame, col: str) -> alt.Chart:
    counts = df[col].fillna("Não informado").astype(str).value_counts()
    tab = counts.rename_axis("Categoria").reset_index(name="Pessoas")
    order = tab["Categoria"].tolist()
    y = alt.Y("Categoria:N", sort=order, title=None, axis=alt.Axis(labelLimit=240))
    bars = alt.Chart(tab).mark_bar(color=ACCENT, size=24, cornerRadiusEnd=5).encode(
        x=alt.X("Pessoas:Q", title="Participantes", axis=alt.Axis(tickMinStep=1)),
        y=y,
        tooltip=["Categoria:N", "Pessoas:Q"],
    )
    text = alt.Chart(tab).mark_text(align="left", dx=7, color=TEXT, fontWeight="bold").encode(
        x="Pessoas:Q", y=y, text=alt.Text("Pessoas:Q", format="d"),
    )
    return chart_theme((bars + text).properties(height=max(190, len(tab) * 45)))


def likert_chart(df: pd.DataFrame, codes: list[str], labels: list[str]) -> alt.Chart:
    """Barras 100% divergentes; divide apenas o neutro para alinhar o zero."""
    rows = []
    for code, label in zip(codes, labels):
        v = df[code + "_n"].dropna().astype(int)
        fractions = v.value_counts(normalize=True).mul(100)
        amounts = {i: float(fractions.get(i, 0)) for i in range(1, 6)}
        neutral = amounts[3] / 2
        segments = [
            ("Discordo totalmente", -amounts[1]-amounts[2]-neutral, -amounts[2]-neutral, amounts[1]),
            ("Discordo parcialmente", -amounts[2]-neutral, -neutral, amounts[2]),
            ("Neutro", -neutral, 0, amounts[3]),
            ("Neutro", 0, neutral, amounts[3]),
            ("Concordo parcialmente", neutral, neutral+amounts[4], amounts[4]),
            ("Concordo totalmente", neutral+amounts[4], neutral+amounts[4]+amounts[5], amounts[5]),
        ]
        for name, left, right, percentage in segments:
            rows.append({"Pergunta": label, "Resposta": name, "Início": left,
                         "Fim": right, "Percentual": round(percentage, 2), "n": len(v)})
    data = pd.DataFrame(rows)
    return chart_theme(alt.Chart(data).mark_bar(size=26).encode(
        x=alt.X("Início:Q", scale=alt.Scale(domain=[-100, 100]),
                title="Distribuição percentual das respostas",
                axis=alt.Axis(values=[-100, -50, 0, 50, 100],
                              labelExpr="abs(datum.value) + '%'", grid=True)),
        x2="Fim:Q",
        y=alt.Y("Pergunta:N", sort=labels, title=None,
                axis=alt.Axis(labelLimit=250, labelFontSize=12)),
        color=alt.Color("Resposta:N", sort=list(LIKERT_COLORS),
                        scale=alt.Scale(domain=list(LIKERT_COLORS), range=list(LIKERT_COLORS.values())),
                        legend=alt.Legend(title=None, orient="bottom", columns=3)),
        tooltip=["Pergunta:N", "Resposta:N", alt.Tooltip("Percentual:Q", format=".1f"),
                 alt.Tooltip("n:Q", title="Respostas")],
    ).properties(height=max(165, len(codes) * 45)))


def pair_heatmap(df: pd.DataFrame) -> alt.Chart:
    counts = pd.crosstab(df["P"], df["R"])
    cells = counts.stack().rename("Participantes").reset_index()
    cells["Produtividade"] = cells["P"].map(lambda x: f"{x:.2f}".replace(".", ","))
    cells["Retrabalho"] = cells["R"].map(lambda x: f"{x:.2f}".replace(".", ","))
    tile = alt.Chart(cells).mark_rect(cornerRadius=3).encode(
        x=alt.X("Retrabalho:N", title="Retrabalho (R)"),
        y=alt.Y("Produtividade:N", title="Produtividade (P)"),
        color=alt.Color("Participantes:Q", scale=alt.Scale(scheme="blues"),
                        legend=alt.Legend(title="Pessoas")),
        tooltip=["Produtividade:N", "Retrabalho:N", "Participantes:Q"],
    )
    labels = alt.Chart(cells).mark_text(fontSize=13).encode(
        x="Retrabalho:N", y="Produtividade:N",
        text=alt.Text("Participantes:Q", format="d"),
        color=alt.condition(alt.datum.Participantes > cells["Participantes"].max() * .55,
                            alt.value("white"), alt.value(TEXT)),
    )
    return chart_theme((tile + labels).properties(height=350))


def effort_chart(details: pd.DataFrame) -> alt.Chart:
    order = details.sort_values("% esforço 4–5", ascending=False)["Atividade"].tolist()
    b = alt.Chart(details).mark_bar(color=ACCENT, size=34, cornerRadiusEnd=5).encode(
        x=alt.X("Atividade:N", sort=order, title=None),
        y=alt.Y("% esforço 4–5:Q", scale=alt.Scale(domain=[0, 100]),
                title="Participantes com esforço alto (%)"),
        tooltip=["Atividade:N", alt.Tooltip("% esforço 4–5:Q", format=".1f"), "n:Q", "Mediana:Q"],
    )
    labels = alt.Chart(details).mark_text(dy=-10, color=TEXT, fontWeight="bold").encode(
        x=alt.X("Atividade:N", sort=order), y="% esforço 4–5:Q",
        text=alt.Text("% esforço 4–5:Q", format=".1f"),
    )
    return chart_theme((b + labels).properties(height=320))

