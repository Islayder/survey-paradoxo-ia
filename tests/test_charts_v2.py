"""Testes dos gráficos agregados, escolhas de escala e paleta de alto contraste."""
import pandas as pd
import pytest

pytest.importorskip("altair")
from src.charts import (
    EFFORT, FREQUENCY, category_chart, correlation_chart, effort_chart,
    likert_chart, ordinal_chart, ordinal_data, pair_heatmap, quadrant_chart,
    quadrant_data,
)


def _sample():
    return pd.DataFrame({
        "E01": ["Estudante", "Profissional", "Estudante", "Profissional", "Estudante"],
        "P": [5., 5., 3., 3., 4.],
        "R": [5., 2., 5., 2., 4.],
        "P01_n": [5, 4, 3, 1, 4], "P02_n": [5, 3, 2, 4, 3],
        "A01_n": [1., 2., 3., 4., 5.],
        "A02_n": [None, 3., 3., 5., None],
        "V01_n": [1., 2., 3., 4., 5.],
    })


def _series():
    return pd.DataFrame({
        "comparacao": ["QP3 · Confiança × Revisão da lógica",
                       "QP3 · Confiança × Execução de testes",
                       "QP3 · Confiança × Validação dos requisitos"],
        "rho": [0.5, -0.23, 0.13],
        "p": [0.03, 0.6, 0.8], "p_holm": [0.12, 1.0, 1.0], "n": [13, 13, 13],
    })


def test_quadrants_include_zero_cells_and_only_count_valid_pairs():
    df = _sample()
    quadrants = quadrant_data(df)
    assert len(quadrants) == 4
    assert quadrants["Participantes"].sum() == 5
    assert quadrants["Porcentagem"].sum() == pytest.approx(100)
    both = quadrants.loc[quadrants["Quadrante"].eq("Ambos ≥ 4")].iloc[0]
    assert both["Participantes"] == 2
    assert both["Porcentagem"] == pytest.approx(40)
    # Separação clara entre "abaixo do corte" e "baixa produtividade".
    assert set(quadrants["Produtividade"]) == {"Produtividade ≥ 4", "Produtividade < 4"}
    assert "Contagem" in quadrants


def test_ordinal_stacking_excludes_not_applicable_per_item():
    df = _sample()
    items = ordinal_data(df, ["A01", "A02"], ["Compreensão", "Correção"], EFFORT)
    assert len(items) == 10
    for _, group in items.groupby("Atividade"):
        assert group["Percentual"].sum() == pytest.approx(100, abs=0.1)
    a02 = items[items["Atividade"].eq("Correção")]
    assert set(a02["n"]) == {3}


def test_all_chart_specs_validate_with_white_background_black_text():
    df = _sample()
    details = pd.DataFrame({
        "Atividade": ["Compreensão", "Correção"],
        "% esforço 4–5": [20., 60.], "n": [5, 3], "Mediana": [3., 4.],
    })
    charts = [
        category_chart(df, "E01"),
        likert_chart(df, ["P01", "P02"], ["P01", "P02"]),
        ordinal_chart(df, ["A01", "A02"], ["Compreensão", "Correção"], EFFORT),
        ordinal_chart(df, ["V01"], ["Revisão"], FREQUENCY),
        quadrant_chart(df),
        pair_heatmap(df),
        effort_chart(details),
        correlation_chart(_series()),
    ]
    for chart in charts:
        spec = chart.to_dict(validate=True)
        config = spec["config"]
        assert config["background"] == "#FFFFFF"
        assert config["axis"]["labelColor"] == "#000000"
        assert config["axis"]["titleColor"] == "#000000"
        assert config["legend"]["labelColor"] == "#000000"
        assert "layer" in spec or "mark" in spec