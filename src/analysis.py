"""Regras pre-registradas do survey. Nenhuma resposta individual e publicada."""
from __future__ import annotations

from itertools import combinations
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

CODES = ["E01", "E02", "E03", "E04", "E05", "P01", "P02", "P03",
         "R01", "R02", "R03", "A01", "A02", "A03", "A04",
         "C01", "C02", "C03", "V01", "V02", "V03", "AT01", "OA01"]
NUMERIC = [x for x in CODES if x[0] in "PRACV" or x == "AT01"]
REQUIRED = [x for x in CODES if x != "OA01"]
LIKERT = {"P": ["P01", "P02", "P03"], "R": ["R01", "R02", "R03"],
          "C": ["C01", "C02", "C03"]}
FALLBACK = {"P": "P03", "R": "R02", "C": "C01"}
ACTIVITY = {"A01": "Compreensão", "A02": "Correção de defeitos",
            "A03": "Adaptação", "A04": "Integração"}
VERIFY = {"V01": "Revisão da lógica", "V02": "Execução de testes",
          "V03": "Validação dos requisitos"}


def identify_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Converte títulos verbosos do Google Forms nos IDs do protocolo."""
    rename: dict[str, str] = {}
    for c in df.columns:
        label = str(c).strip()
        if label.startswith("TCLE"):
            rename[c] = "TCLE"
        elif label.lower().startswith("carimbo") or label.lower() == "timestamp":
            rename[c] = "timestamp"
        else:
            match = re.match(r"^(E0[1-5]|P0[1-3]|R0[1-3]|A0[1-4]|C0[1-3]|V0[1-3]|AT01|OA01)(?:\b|\s*[—-])", label)
            if match:
                rename[c] = match.group(1)
    result = df.rename(columns=rename).copy()
    mandatory = ["timestamp", "TCLE"] + REQUIRED
    missing = [c for c in mandatory if c not in result.columns]
    if missing:
        raise ValueError("Colunas obrigatórias não encontradas: " + ", ".join(missing))
    if result.columns.duplicated().any():
        raise ValueError("A planilha contém identificadores de pergunta duplicados.")
    return result


def score(value: Any) -> float:
    """Respostas '4 — Concordo parcialmente' viram 4; N/A permanece ausente."""
    if pd.isna(value) or str(value).strip() == "":
        return np.nan
    text = str(value).strip()
    if "não se aplica" in text.casefold() or "nao se aplica" in text.casefold():
        return np.nan
    match = re.match(r"^([1-5])(?:\s*[—–-]|\s*$)", text)
    return float(match.group(1)) if match else np.nan


def _yes(value: Any) -> bool:
    return str(value).strip().casefold() == "sim"


def exclusion_reason(row: pd.Series) -> str:
    consent = str(row["TCLE"]).casefold()
    if not ("18 anos" in consent and "concordo" in consent):
        return "Consentimento/maioridade"
    if "nenhuma" in str(row["E01"]).casefold() or pd.isna(row["E01"]):
        return "E01: fora da população"
    if not _yes(row["E02"]):
        return "E02: sem prática de programação"
    if not _yes(row["E03"]):
        return "E03: não usou IA nos últimos 6 meses"
    if score(row["AT01"]) != 4:
        return "AT01: falha na atenção"
    for code in REQUIRED:
        val = row[code]
        if pd.isna(val) or str(val).strip() == "":
            return "Item obrigatório ausente"
        if code in NUMERIC and code[:1] != "A" and pd.isna(score(val)):
            return "Item obrigatório inválido"
        if code in ACTIVITY and pd.isna(score(val)) and "não se aplica" not in str(val).casefold():
            return "Item obrigatório inválido"
    return "Válida"


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    out = identify_columns(raw)
    out["motivo"] = out.apply(exclusion_reason, axis=1)
    out["valida"] = out["motivo"].eq("Válida")
    for key in NUMERIC:
        out[key + "_n"] = out[key].map(score)
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    return out


def cronbach_alpha(df: pd.DataFrame, codes: list[str]) -> float:
    values = df[[c + "_n" for c in codes]].dropna()
    if len(values) < 3:
        return np.nan
    k = len(codes)
    total_var = values.sum(axis=1).var(ddof=1)
    if total_var <= 0 or pd.isna(total_var):
        return np.nan
    return float(k / (k - 1) * (1 - values.var(ddof=1).sum() / total_var))


def construct_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    out = df.copy()
    meta: dict[str, dict[str, Any]] = {}
    for name, codes in LIKERT.items():
        alpha = cronbach_alpha(out, codes)
        use_mean = bool(np.isfinite(alpha) and alpha >= .7)
        col = [c + "_n" for c in codes]
        out[name] = out[col].mean(axis=1) if use_mean else out[FALLBACK[name] + "_n"]
        meta[name] = {"alpha": alpha, "method": "Média dos três itens" if use_mean else
                      f"Indicador alternativo {FALLBACK[name]}", "composite": use_mean}
    return out, meta


def holm(pvalues: list[float]) -> list[float]:
    """Ajuste step-down de Holm, ignorando testes não calculáveis."""
    result = [np.nan] * len(pvalues)
    valid = sorted([i for i, p in enumerate(pvalues) if np.isfinite(p)], key=lambda i: pvalues[i])
    largest = 0.
    for rank, i in enumerate(valid):
        largest = max(largest, (len(valid) - rank) * pvalues[i])
        result[i] = min(1., largest)
    return result


def spearman_pair(df: pd.DataFrame, x: str, y: str, label: str) -> dict[str, Any]:
    pair = df[[x, y]].dropna()
    output = {"comparacao": label, "n": len(pair), "rho": np.nan, "p": np.nan}
    if len(pair) < 4 or any(pair[c].nunique() < 2 for c in [x, y]):
        return output
    res = stats.spearmanr(pair[x], pair[y])
    output.update(rho=float(res.statistic), p=float(res.pvalue))
    return output


def correlations(df: pd.DataFrame) -> pd.DataFrame:
    tests = [spearman_pair(df, "P", "R", "QP1 · Produtividade × retrabalho")]
    tests += [spearman_pair(df, "C", x + "_n", f"QP3 · Confiança × {label}") for x, label in VERIFY.items()]
    adj = holm([t["p"] for t in tests])
    for item, val in zip(tests, adj):
        item["p_holm"] = val
    return pd.DataFrame(tests)


def effort_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    items = list(ACTIVITY)
    details = []
    for code, label in ACTIVITY.items():
        v = df[code + "_n"].dropna()
        details.append({"Atividade": label, "n": len(v), "Mediana": float(v.median()) if len(v) else np.nan,
                        "% esforço 4–5": float((v >= 4).mean() * 100) if len(v) else np.nan})
    complete = df[[c + "_n" for c in items]].dropna()
    summary: dict[str, Any] = {"n_pareado": len(complete), "friedman": np.nan, "p": np.nan,
                               "kendall_w": np.nan}
    posthoc = []
    if len(complete) >= 4 and not complete.eq(complete.iloc[:, 0], axis=0).all().all():
        try:
            result = stats.friedmanchisquare(*[complete[c + "_n"] for c in items])
            if np.isfinite(result.pvalue):
                summary.update(friedman=float(result.statistic), p=float(result.pvalue),
                               kendall_w=float(result.statistic / (len(complete) * (len(items) - 1))))
        except ValueError:
            pass
    if np.isfinite(summary["p"]) and summary["p"] < .05:
        for a, b in combinations(items, 2):
            diff = complete[a + "_n"] - complete[b + "_n"]
            nonzero = int((diff != 0).sum())
            test = {"Par": ACTIVITY[a] + " × " + ACTIVITY[b], "n": nonzero,
                    "Diferença mediana": float(diff.median()), "p": np.nan, "r": np.nan}
            if nonzero >= 2:
                res = stats.wilcoxon(complete[a + "_n"], complete[b + "_n"], zero_method="wilcox",
                                     method="approx", correction=False)
                test["p"] = float(res.pvalue)
                z = getattr(res, "zstatistic", np.nan)
                test["r"] = float(abs(z) / np.sqrt(nonzero)) if np.isfinite(z) else np.nan
            posthoc.append(test)
        adjusted = holm([r["p"] for r in posthoc])
        for row, p in zip(posthoc, adjusted):
            row["p_holm"] = p
    return pd.DataFrame(details), summary, pd.DataFrame(posthoc)


def coexistence(df: pd.DataFrame) -> dict[str, Any]:
    both = df[["P", "R"]].dropna()
    matches = (both["P"] >= 4) & (both["R"] >= 4)
    return {"n": len(both), "total": int(matches.sum()),
            "percent": float(100 * matches.mean()) if len(both) else np.nan}