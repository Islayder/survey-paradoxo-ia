"""Garante que as visualizações não dependem de módulos Plotly ou dados individuais."""
import pandas as pd
import pytest
pytest.importorskip("altair")
from src.charts import category_chart, effort_chart, likert_chart, pair_heatmap


def test_altair_charts_compile():
    df = pd.DataFrame({
        "E01": ["Estudante", "Profissional", "Estudante"],
        "P": [3, 4, 5], "R": [2, 4, 3],
        "P01_n": [1, 3, 5], "P02_n": [2, 4, 5],
    })
    efforts = pd.DataFrame({
        "Atividade": ["Compreensão", "Correção"],
        "% esforço 4–5": [25., 75.], "n": [3, 3], "Mediana": [2., 4.],
    })
    for chart in [
        category_chart(df, "E01"),
        likert_chart(df, ["P01", "P02"], ["Rapidez", "Dificuldade"]),
        pair_heatmap(df),
        effort_chart(efforts),
    ]:
        spec = chart.to_dict(validate=True)
        assert "config" in spec
        assert "layer" in spec or "mark" in spec


def test_likert_chart_is_divergent_and_aggregated():
    df = pd.DataFrame({"P01_n": [1, 1, 3, 4, 5]})
    chart = likert_chart(df, ["P01"], ["Produtividade"])
    spec = chart.to_dict(validate=True)
    cells = spec.get("data", {}).get("values", [])
    if not cells:
        # Altair pode manter os valores nos datasets na especificação serializada.
        cells = next(iter(spec.get("datasets", {}).values()))
    assert len(cells) == 6
    assert any(row["Início"] < 0 for row in cells)
    assert any(row["Fim"] > 0 for row in cells)
    assert set(cells[0]) == {"Pergunta", "Resposta", "Início", "Fim", "Percentual", "n"}