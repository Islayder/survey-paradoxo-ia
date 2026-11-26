import numpy as np
import pandas as pd
from src.analysis import (score, prepare, construct_scores, holm,
                          coexistence, effort_analysis, correlations, score_filtered_with_global_alpha)


def sample(n=5):
    row = {"Carimbo de data/hora": "2026-11-13", "TCLE — Termo": "Declaro ter pelo menos 18 anos e concordo",
           "E01 — Perfil": "Sou estudante de um curso de TI.", "E02 — Prática": "Sim", "E03 — IA": "Sim",
           "E04 — Experiência": "De 1 a menos de 3 anos", "E05 — Frequência": "0 dias"}
    for code in ["P01","P02","P03","R01","R02","R03","A01","A02","A03","A04",
                 "C01","C02","C03","V01","V02","V03"]:
        row[code+" — Pergunta"] = "4 — Concordo parcialmente"
    row["AT01 — Atenção"] = "4 — Concordo parcialmente"
    row["OA01 — Contexto"] = ""
    return pd.DataFrame([row] * n)


def test_score():
    assert score("4 — Concordo parcialmente") == 4
    assert np.isnan(score("Não se aplica"))
    assert np.isnan(score("opção inválida"))


def test_eligibility_and_attention():
    df = sample(3)
    df.loc[1, "E01 — Perfil"] = "Nenhuma das alternativas."
    df.loc[2, "AT01 — Atenção"] = "5 — Concordo totalmente"
    out = prepare(df)
    assert out["motivo"].tolist() == ["Válida", "E01: fora da população", "AT01: falha na atenção"]


def test_zero_days_not_excluded_and_na_activity():
    df = sample(1)
    df.loc[0, "A01 — Pergunta"] = "Não se aplica"
    out = prepare(df)
    assert out.loc[0, "valida"]
    assert np.isnan(out.loc[0, "A01_n"])


def test_holm_monotonic():
    assert np.allclose(holm([.04,.01,.02,np.nan])[:3], [.04,.03,.04])


def test_fallback_if_alpha_undefined():
    df = prepare(sample(5))
    scored, meta = construct_scores(df)
    assert meta["P"]["method"] == "Indicador alternativo P03"
    assert scored["P"].eq(4).all()
    assert coexistence(scored)["total"] == 5
    assert len(correlations(scored)) == 4
    detail, global_test, posthoc = effort_analysis(scored)
    assert len(detail) == 4
    assert np.isnan(global_test["p"])


def test_filter_keeps_construct_definition_from_full_sample():
    """Um segmento não pode trocar o fallback P03 pela média de P01–P03."""
    raw = sample(10)
    triplets = (
        [(i, i, min(5, i + 1)) for i in range(1, 6)] +
        [(i, 6 - i, 6 - i) for i in range(1, 6)]
    )
    for idx, (p01, p02, p03) in enumerate(triplets):
        for code, value in [("P01", p01), ("P02", p02), ("P03", p03)]:
            raw.loc[idx, code + " — Pergunta"] = f"{value} — Resposta"
    valid = prepare(raw)
    mask = pd.Series([True] * 5 + [False] * 5, index=valid.index)
    selected, meta = score_filtered_with_global_alpha(valid, mask)
    separately_scored, subgroup_meta = construct_scores(valid.loc[mask])

    assert meta["P"]["alpha"] < 0.70
    assert not meta["P"]["composite"]
    assert subgroup_meta["P"]["alpha"] >= 0.70
    assert subgroup_meta["P"]["composite"]
    assert selected["P"].tolist() == [2., 3., 4., 5., 5.]  # P03 fixo
    assert not np.allclose(selected["P"], separately_scored["P"].to_numpy())
    assert len(selected) == 5


def test_nominal_margin_reference_50():
    """Verifica a fórmula do enunciado para a amostra completa."""
    import math
    e_pp = 100 * 1.96 * math.sqrt(0.5 * (1 - 0.5) / 50)
    assert round(e_pp, 1) == 13.9


def test_holm_not_confused_with_effect_size():
    # Holm pode chegar a 1 mesmo quando o rho estimado não é zero.
    assert holm([.2604, .40, .60, .80])[0] == 1.0



def test_dashboard_source_compiles_and_uses_global_alpha():
    """Evita regressões silenciosas no app, que não é importado nos testes unitários."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    app_source = (root / "app.py").read_text(encoding="utf-8")
    chart_source = (root / "src" / "charts.py").read_text(encoding="utf-8")
    compile(app_source, str(root / "app.py"), "exec")
    compile(chart_source, str(root / "src" / "charts.py"), "exec")
    assert "score_filtered_with_global_alpha(valid, mask)" in app_source
    assert "p bruto · Spearman" in app_source
    assert "Margem de erro nominal" in app_source
    assert "R03 · Redução da economia de tempo" in app_source
