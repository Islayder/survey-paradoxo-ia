import numpy as np
import pandas as pd
from src.analysis import (score, prepare, construct_scores, holm,
                          coexistence, effort_analysis, correlations)


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