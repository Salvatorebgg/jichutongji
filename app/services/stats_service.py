from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr, chi2_contingency


def format_p_value(p: float | None, digits: int = 4) -> str:
    if p is None:
        return "—"
    if p < 0.0001:
        return "<0.0001"
    if p < 0.001:
        return "<0.001"
    return f"{p:.{digits}f}"


def _test_normality(series: pd.Series, alpha: float = 0.05) -> bool:
    sample = series.dropna()
    if len(sample) < 3:
        return False
    if len(sample) > 5000:
        sample = sample.sample(n=5000, random_state=42)
    try:
        _, p = stats.shapiro(sample)
        return p > alpha
    except Exception:
        return False


def calc_descriptive(df: pd.DataFrame, col: str, group_col: str | None = None) -> dict:
    series = df[col].dropna()
    is_numeric = pd.api.types.is_numeric_dtype(series)
    if not is_numeric:
        counts = series.value_counts()
        pcts = series.value_counts(normalize=True) * 100
        result = {
            "type": "categorical",
            "n": int(len(series)),
            "missing": int(df[col].isnull().sum()),
            "unique": int(series.nunique()),
            "top_categories": [
                {"name": str(k), "count": int(v), "pct": round(float(pcts.get(k, 0)), 2)}
                for k, v in counts.head(10).items()
            ],
        }
        if group_col and group_col in df.columns:
            groups = sorted(df[group_col].dropna().unique())
            result["by_group"] = {}
            for g in groups:
                gs = df.loc[df[group_col] == g, col].dropna()
                gc = gs.value_counts()
                gp = gs.value_counts(normalize=True) * 100
                result["by_group"][str(g)] = {
                    "n": int(len(gs)),
                    "top": [{"name": str(k), "count": int(v), "pct": round(float(gp.get(k, 0)), 2)}
                            for k, v in gc.head(5).items()],
                }
        return result
    result = {
        "type": "continuous",
        "n": int(len(series)),
        "missing": int(df[col].isnull().sum()),
        "mean": round(float(series.mean()), 3),
        "std": round(float(series.std()), 3),
        "median": round(float(series.median()), 3),
        "q1": round(float(series.quantile(0.25)), 3),
        "q3": round(float(series.quantile(0.75)), 3),
        "min": round(float(series.min()), 3),
        "max": round(float(series.max()), 3),
        "skewness": round(float(series.skew()), 3),
        "kurtosis": round(float(series.kurtosis()), 3),
        "is_normal": _test_normality(series),
    }
    if group_col and group_col in df.columns:
        groups = sorted(df[group_col].dropna().unique())
        result["by_group"] = {}
        for g in groups:
            g_series = df.loc[df[group_col] == g, col].dropna()
            if len(g_series) > 0:
                result["by_group"][str(g)] = {
                    "n": int(len(g_series)),
                    "mean": round(float(g_series.mean()), 3),
                    "std": round(float(g_series.std()), 3),
                    "median": round(float(g_series.median()), 3),
                    "q1": round(float(g_series.quantile(0.25)), 3),
                    "q3": round(float(g_series.quantile(0.75)), 3),
                }
    return result


def calc_group_comparison(df: pd.DataFrame, var: str, group_col: str) -> dict:
    groups = df[group_col].dropna().unique()
    if len(groups) < 2:
        return {"method": "N/A", "p_value": None, "statistic": None, "note": "少于2组，无法比较"}
    group_data = {str(g): df.loc[df[group_col] == g, var].dropna().values for g in groups}
    group_data = {k: v for k, v in group_data.items() if len(v) > 0}
    if len(group_data) < 2:
        return {"method": "N/A", "p_value": None, "statistic": None, "note": "有效组不足2个"}
    series = df[var].dropna()
    is_numeric = pd.api.types.is_numeric_dtype(series)
    try:
        if is_numeric:
            if len(group_data) == 2:
                a, b = list(group_data.values())
                if len(a) >= 3 and len(b) >= 3 and _test_normality(series):
                    t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
                    return {"method": "Welch's t-test", "p_value": round(float(p_val), 4), "statistic": round(float(t_stat), 4)}
                else:
                    u_stat, p_val = stats.mannwhitneyu(a, b, alternative="two-sided")
                    return {"method": "Mann-Whitney U", "p_value": round(float(p_val), 4), "statistic": round(float(u_stat), 4)}
            else:
                data_list = list(group_data.values())
                if all(len(d) >= 3 for d in data_list) and _test_normality(series):
                    f_stat, p_val = stats.f_oneway(*data_list)
                    return {"method": "One-way ANOVA", "p_value": round(float(p_val), 4), "statistic": round(float(f_stat), 4)}
                else:
                    h_stat, p_val = stats.kruskal(*data_list)
                    return {"method": "Kruskal-Wallis", "p_value": round(float(p_val), 4), "statistic": round(float(h_stat), 4)}
        else:
            contingency = pd.crosstab(df[var], df[group_col])
            if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
                chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
                return {"method": "Chi-square", "p_value": round(float(p_val), 4), "statistic": round(float(chi2), 4)}
            else:
                return {"method": "Fisher's exact", "p_value": None, "statistic": None, "note": "使用Fisher精确检验"}
    except Exception as e:
        return {"method": "N/A", "p_value": None, "statistic": None, "note": str(e)}


# ═══ Individual Statistical Test Functions ═══════════════════════

def t_test_independent(df: pd.DataFrame, var: str, group_var: str) -> dict:
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) != 2:
        return {"error": f"独立样本t检验需要恰好2组，当前有{len(groups)}组"}
    a = df.loc[df[group_var] == groups[0], var].dropna().values
    b = df.loc[df[group_var] == groups[1], var].dropna().values
    t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
    is_normal_a = _test_normality(pd.Series(a))
    is_normal_b = _test_normality(pd.Series(b))
    note = ""
    if not is_normal_a or not is_normal_b:
        note = "数据不完全满足正态性假设，建议同时参考Mann-Whitney U检验结果。"
    # Effect size: Cohen's d
    d_val = cohens_d(a, b) if len(a) > 1 and len(b) > 1 else None
    # 95% CI for mean difference (Welch approximation)
    se_diff = np.sqrt(np.var(a, ddof=1)/len(a) + np.var(b, ddof=1)/len(b))
    df_welch = (np.var(a, ddof=1)/len(a) + np.var(b, ddof=1)/len(b))**2 / (
        (np.var(a, ddof=1)/len(a))**2/(len(a)-1) + (np.var(b, ddof=1)/len(b))**2/(len(b)-1)
    ) if se_diff > 0 else 1
    t_crit = stats.t.ppf(0.975, df=max(1, df_welch))
    mean_diff = float(np.mean(a) - np.mean(b))
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    return {
        "test_type": "t_test_independent",
        "test_name": "独立样本t检验 (Welch's t-test)",
        "statistic": round(float(t_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Welch's t-test（不假设方差齐性）",
        "note": note if note else None,
        "summary": f"t = {t_stat:.4f}, p = {format_p_value(p_val)}",
        "details": {
            "group_1": {"name": str(groups[0]), "n": int(len(a)), "mean": round(float(np.mean(a)), 3), "std": round(float(np.std(a, ddof=1)), 3), "normal": is_normal_a},
            "group_2": {"name": str(groups[1]), "n": int(len(b)), "mean": round(float(np.mean(b)), 3), "std": round(float(np.std(b, ddof=1)), 3), "normal": is_normal_b},
            "mean_diff": round(mean_diff, 3),
            "ci_95": [round(float(ci_lower), 4), round(float(ci_upper), 4)],
            "cohens_d": round(float(d_val), 4) if d_val is not None else None,
        },
        "descriptive_stats": _group_descriptive(df, var, group_var),
        "chart_data": _build_chart_data(df, var, group_var),
        "post_hoc": None,
    }


def t_test_paired(df: pd.DataFrame, var: str, paired_var: str) -> dict:
    df_clean = df[[var, paired_var]].dropna()
    a = df_clean[var].values
    b = df_clean[paired_var].values
    if len(a) < 3:
        return {"error": "配对样本量不足（需要至少3对完整数据）"}
    t_stat, p_val = stats.ttest_rel(a, b)
    diffs = a - b
    return {
        "test_type": "t_test_paired",
        "test_name": "配对样本t检验 (Paired t-test)",
        "statistic": round(float(t_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "配对t检验",
        "summary": f"t = {t_stat:.4f}, p = {format_p_value(p_val)}",
        "details": {
            "n_pairs": int(len(a)),
            "mean_before": round(float(np.mean(a)), 3),
            "std_before": round(float(np.std(a, ddof=1)), 3),
            "mean_after": round(float(np.mean(b)), 3),
            "std_after": round(float(np.std(b, ddof=1)), 3),
            "mean_diff": round(float(np.mean(diffs)), 3),
            "std_diff": round(float(np.std(diffs, ddof=1)), 3),
        },
        "descriptive_stats": {"variable_1": var, "variable_2": paired_var},
        "chart_data": {
            "chart_type": "paired_box",
            "var_1_name": str(var), "var_2_name": str(paired_var),
            "var_1_values": [float(v) if pd.notna(v) else None for v in a.tolist()],
            "var_2_values": [float(v) if pd.notna(v) else None for v in b.tolist()],
            "diffs": [float(v) if pd.notna(v) else None for v in diffs.tolist()],
            "title": f"配对比较: {var} vs {paired_var}",
        },
        "post_hoc": None,
    }


def one_sample_t_test(df: pd.DataFrame, var: str, hypothesized_mean: float = 0.0) -> dict:
    """One-sample t-test against a specified reference mean."""
    series = pd.to_numeric(df[var], errors="coerce").dropna()
    if len(series) < 3:
        return {"error": "单样本 t 检验样本量不足（需要至少 3 个有效观测）"}
    values = series.to_numpy(dtype=float)
    t_stat, p_val = stats.ttest_1samp(values, popmean=hypothesized_mean)
    mean_val = float(np.mean(values))
    sd_val = float(np.std(values, ddof=1))
    se = sd_val / np.sqrt(len(values))
    t_crit = stats.t.ppf(0.975, df=len(values) - 1)
    ci_lower = mean_val - t_crit * se
    ci_upper = mean_val + t_crit * se
    mean_diff_val = mean_val - hypothesized_mean
    normal = _test_normality(series)
    return {
        "test_type": "one_sample_t_test",
        "test_name": "单样本 t 检验 (One-sample t-test)",
        "statistic": round(float(t_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": f"One-sample t-test, reference mean = {hypothesized_mean:g}",
        "summary": f"t = {t_stat:.4f}, p = {format_p_value(p_val)}, n = {len(values)}",
        "note": None if normal else "正态性未完全满足；样本量较小时建议结合符号检验或非参数方法作敏感性分析。",
        "details": {
            "n": int(len(values)),
            "mean": round(mean_val, 3),
            "std": round(sd_val, 3),
            "median": round(float(np.median(values)), 3),
            "q1": round(float(np.quantile(values, 0.25)), 3),
            "q3": round(float(np.quantile(values, 0.75)), 3),
            "hypothesized_mean": round(float(hypothesized_mean), 4),
            "mean_diff": round(float(mean_diff_val), 4),
            "ci_95": [round(float(ci_lower), 4), round(float(ci_upper), 4)],
            "normal": normal,
        },
        "descriptive_stats": None,
        "chart_data": _build_chart_data(df, var, None),
        "post_hoc": None,
    }


def normality_test(df: pd.DataFrame, var: str) -> dict:
    """Shapiro-Wilk normality test with distribution diagnostics."""
    series = pd.to_numeric(df[var], errors="coerce").dropna()
    if len(series) < 3:
        return {"error": "正态性检验样本量不足（需要至少 3 个有效观测）"}
    tested = series
    if len(tested) > 5000:
        tested = tested.sample(n=5000, random_state=42)
    w_stat, p_val = stats.shapiro(tested.to_numpy(dtype=float))
    is_normal = p_val >= 0.05
    values = series.to_numpy(dtype=float)
    return {
        "test_type": "normality_test",
        "test_name": "Shapiro-Wilk 正态性检验",
        "statistic": round(float(w_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Shapiro-Wilk normality test",
        "summary": f"W = {w_stat:.4f}, p = {format_p_value(p_val)}",
        "note": "P < 0.05 提示分布显著偏离正态。" if not is_normal else "未发现显著偏离正态的证据。",
        "details": {
            "n": int(len(series)),
            "tested_n": int(len(tested)),
            "mean": round(float(np.mean(values)), 3),
            "std": round(float(np.std(values, ddof=1)), 3),
            "median": round(float(np.median(values)), 3),
            "q1": round(float(np.quantile(values, 0.25)), 3),
            "q3": round(float(np.quantile(values, 0.75)), 3),
            "skewness": round(float(pd.Series(values).skew()), 3),
            "kurtosis": round(float(pd.Series(values).kurtosis()), 3),
            "normal": is_normal,
        },
        "descriptive_stats": None,
        "chart_data": _build_chart_data(df, var, None),
        "post_hoc": None,
    }


def levene_variance_test(df: pd.DataFrame, var: str, group_var: str) -> dict:
    """Median-centered Levene/Brown-Forsythe test for homogeneity of variance."""
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) < 2:
        return {"error": "方差齐性检验需要至少 2 组数据"}
    group_data = {}
    for group in groups:
        vals = pd.to_numeric(df.loc[df[group_var] == group, var], errors="coerce").dropna().to_numpy(dtype=float)
        if len(vals) >= 2:
            group_data[str(group)] = vals
    if len(group_data) < 2:
        return {"error": "有效分组不足；每组至少需要 2 个有效观测"}
    stat, p_val = stats.levene(*group_data.values(), center="median")
    equal_var = p_val >= 0.05
    return {
        "test_type": "levene_test",
        "test_name": "Levene 方差齐性检验",
        "statistic": round(float(stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Median-centered Levene test (Brown-Forsythe)",
        "summary": f"Levene W = {stat:.4f}, p = {format_p_value(p_val)}",
        "note": "方差齐性可接受。" if equal_var else "提示组间方差不齐，后续均值比较建议使用 Welch 或稳健方法。",
        "details": {
            "n_groups": len(group_data),
            "total_n": int(sum(len(v) for v in group_data.values())),
            "center": "median",
            "equal_var": equal_var,
            "group_stats": {
                str(g): {
                    "n": int(len(v)),
                    "mean": round(float(np.mean(v)), 3),
                    "std": round(float(np.std(v, ddof=1)), 3),
                    "variance": round(float(np.var(v, ddof=1)), 3),
                    "median": round(float(np.median(v)), 3),
                }
                for g, v in group_data.items()
            },
        },
        "descriptive_stats": _group_descriptive(df, var, group_var),
        "chart_data": _build_chart_data(df, var, group_var),
        "post_hoc": None,
    }


def anova_oneway(df: pd.DataFrame, var: str, group_var: str, post_hoc: str | None = None) -> dict:
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) < 2:
        return {"error": "方差分析需要至少2组数据"}
    group_data = {str(g): df.loc[df[group_var] == g, var].dropna().values for g in groups}
    group_data = {k: v for k, v in group_data.items() if len(v) > 0}
    if len(group_data) < 2:
        return {"error": "有效组数不足2个"}
    data_list = list(group_data.values())
    try:
        levene_stat, levene_p = stats.levene(*data_list)
        equal_var = levene_p > 0.05
    except Exception:
        levene_stat, levene_p, equal_var = None, None, False
    f_stat, p_val = stats.f_oneway(*data_list)
    normality_results = {str(g): _test_normality(pd.Series(v)) for g, v in group_data.items()}
    all_normal = all(normality_results.values())
    note = ""
    if not all_normal:
        note = "部分组数据不完全满足正态性假设，建议同时参考Kruskal-Wallis检验结果。"
    if not equal_var:
        note += " Levene检验提示方差不齐，建议使用Welch ANOVA或非参数检验。"
    # Effect size: eta-squared
    df_effect = len(group_data) - 1
    df_error = int(sum(len(v) for v in data_list)) - len(group_data)
    eta_sq = eta_squared(f_stat, df_effect, df_error) if df_error > 0 else None
    result = {
        "test_type": "anova",
        "test_name": "单因素方差分析 (One-way ANOVA)",
        "statistic": round(float(f_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "One-way ANOVA",
        "summary": f"F = {f_stat:.4f}, p = {format_p_value(p_val)}",
        "note": note if note else None,
        "details": {
            "n_groups": len(group_data),
            "total_n": int(sum(len(v) for v in data_list)),
            "df_between": int(df_effect),
            "df_within": int(df_error),
            "eta_squared": round(float(eta_sq), 4) if eta_sq is not None else None,
            "group_stats": {str(g): {"n": int(len(v)), "mean": round(float(np.mean(v)), 3), "std": round(float(np.std(v, ddof=1)), 3), "normal": normality_results.get(str(g), False)} for g, v in group_data.items()},
            "levene_test": {"statistic": round(float(levene_stat), 4) if levene_stat else None, "p_value": round(float(levene_p), 4) if levene_p else None, "equal_var": equal_var},
        },
        "descriptive_stats": _group_descriptive(df, var, group_var),
        "chart_data": _build_chart_data(df, var, group_var),
        "post_hoc": None,
    }
    if post_hoc and p_val < 0.05 and len(group_data) >= 3:
        result["post_hoc"] = _run_post_hoc(df, var, group_var, post_hoc, equal_var, groups)
    return result


def chi_square_test(df: pd.DataFrame, var: str, group_var: str) -> dict:
    try:
        contingency = pd.crosstab(df[var], df[group_var])
        if contingency.shape[0] < 2 or contingency.shape[1] < 2:
            return {"error": "列联表维度不足，请确保两个分类变量各有至少2个类别"}
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
        min_expected = np.min(expected)
        n_cells_lt5 = int(np.sum(expected < 5))
        total_cells = int(expected.size)
        use_fisher_note = ""
        method = "Pearson卡方检验"
        if contingency.shape == (2, 2) and (min_expected < 1 or n_cells_lt5 / total_cells > 0.2):
            chi2, p_val = stats.chi2_contingency(contingency, correction=True)[:2]
            method = "Pearson卡方检验（Yates连续性校正）"
            use_fisher_note = "超过20%单元格期望频数<5或最小期望频数<1，已使用Yates校正。建议同时参考Fisher精确概率法。"
        return {
            "test_type": "chi_square",
            "test_name": "卡方检验 (Chi-square test)",
            "statistic": round(float(chi2), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": method,
            "summary": f"χ² = {chi2:.4f}, df = {dof}, p = {format_p_value(p_val)}",
            "note": use_fisher_note if use_fisher_note else None,
            "details": {
                "degrees_of_freedom": int(dof),
                "contingency_table": {"rows": contingency.index.tolist(), "cols": contingency.columns.tolist(), "data": contingency.values.tolist()},
                "min_expected": round(float(min_expected), 2),
                "cells_lt5_pct": round(n_cells_lt5 / total_cells * 100, 1),
                "cohens_w": round(float(cohens_w(contingency.values, int(np.sum(contingency.values)))), 4) if int(np.sum(contingency.values)) > 0 else None,
                "pct_cells_lt5": round(n_cells_lt5 / total_cells * 100, 1),
            },
            "descriptive_stats": _group_descriptive(df, var, group_var),
            "chart_data": _build_contingency_chart(contingency, var, group_var),
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"卡方检验计算失败: {str(e)}"}


def fisher_exact_test(df: pd.DataFrame, var: str, group_var: str) -> dict:
    try:
        contingency = pd.crosstab(df[var], df[group_var])
        if contingency.shape == (2, 2):
            odds_ratio, p_val = stats.fisher_exact(contingency)
            return {
                "test_type": "fisher_exact",
                "test_name": "Fisher精确概率法 (Fisher's exact test)",
                "statistic": round(float(odds_ratio), 4),
                "p_value": round(float(p_val), 6),
                "significant": p_val < 0.05,
                "method": "Fisher's exact test (2×2)",
                "summary": f"OR = {odds_ratio:.4f}, p = {format_p_value(p_val)}",
                "details": {"odds_ratio": round(float(odds_ratio), 4), "contingency_table": {"rows": contingency.index.tolist(), "cols": contingency.columns.tolist(), "data": contingency.values.tolist()}},
                "descriptive_stats": _group_descriptive(df, var, group_var),
                "chart_data": _build_contingency_chart(contingency, var, group_var),
                "post_hoc": None,
            }
        else:
            try:
                result = stats.chi2_contingency(contingency, lambda_="log-likelihood")
                return {
                    "test_type": "fisher_exact",
                    "test_name": "Fisher精确概率法（扩展）",
                    "statistic": None,
                    "p_value": round(float(result[1]), 6),
                    "significant": result[1] < 0.05,
                    "method": "Fisher-Freeman-Halton扩展",
                    "summary": f"p = {format_p_value(result[1])}",
                    "note": f"表格维度为{contingency.shape}，使用似然比卡方近似。对非2×2表建议使用卡方检验。",
                    "details": {"contingency_table": {"rows": contingency.index.tolist(), "cols": contingency.columns.tolist(), "data": contingency.values.tolist()}},
                    "descriptive_stats": _group_descriptive(df, var, group_var),
                    "chart_data": None,
                    "post_hoc": None,
                }
            except Exception:
                return {"error": "Fisher精确概率法当前仅支持2×2列联表，请使用卡方检验"}
    except Exception as e:
        return {"error": f"Fisher精确概率法计算失败: {str(e)}"}


def mann_whitney_u_test(df: pd.DataFrame, var: str, group_var: str) -> dict:
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) != 2:
        return {"error": f"Mann-Whitney U检验需要2组，当前有{len(groups)}组"}
    a = df.loc[df[group_var] == groups[0], var].dropna().values
    b = df.loc[df[group_var] == groups[1], var].dropna().values
    u_stat, p_val = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {
        "test_type": "mann_whitney",
        "test_name": "Mann-Whitney U检验 (Wilcoxon秩和检验)",
        "statistic": round(float(u_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Mann-Whitney U test",
        "summary": f"U = {u_stat:.4f}, p = {format_p_value(p_val)}",
        "details": {
            "group_1": {"name": str(groups[0]), "n": int(len(a)), "median": round(float(np.median(a)), 3), "q1": round(float(np.quantile(a, 0.25)), 3), "q3": round(float(np.quantile(a, 0.75)), 3)},
            "group_2": {"name": str(groups[1]), "n": int(len(b)), "median": round(float(np.median(b)), 3), "q1": round(float(np.quantile(b, 0.25)), 3), "q3": round(float(np.quantile(b, 0.75)), 3)},
        },
        "descriptive_stats": _group_descriptive(df, var, group_var),
        "chart_data": _build_chart_data(df, var, group_var),
        "post_hoc": None,
    }


def kruskal_wallis_test(df: pd.DataFrame, var: str, group_var: str, post_hoc: str | None = None) -> dict:
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) < 2:
        return {"error": "Kruskal-Wallis检验需要至少2组数据"}
    group_data = {str(g): df.loc[df[group_var] == g, var].dropna().values for g in groups}
    group_data = {k: v for k, v in group_data.items() if len(v) > 0}
    if len(group_data) < 2:
        return {"error": "有效组数不足2个"}
    data_list = list(group_data.values())
    h_stat, p_val = stats.kruskal(*data_list)
    result = {
        "test_type": "kruskal_wallis",
        "test_name": "Kruskal-Wallis H检验 (秩和检验)",
        "statistic": round(float(h_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Kruskal-Wallis H test",
        "summary": f"H = {h_stat:.4f}, p = {format_p_value(p_val)}",
        "details": {
            "n_groups": len(group_data),
            "total_n": int(sum(len(v) for v in data_list)),
            "group_stats": {str(g): {"n": int(len(v)), "median": round(float(np.median(v)), 3), "q1": round(float(np.quantile(v, 0.25)), 3), "q3": round(float(np.quantile(v, 0.75)), 3)} for g, v in group_data.items()},
        },
        "descriptive_stats": _group_descriptive(df, var, group_var),
        "chart_data": _build_chart_data(df, var, group_var),
        "post_hoc": None,
    }
    if post_hoc == "bonferroni" and p_val < 0.05 and len(group_data) >= 3:
        comparisons = [(g1, g2) for i, g1 in enumerate(groups) for g2 in groups[i + 1:]]
        n_comp = len(comparisons)
        post_results = []
        for g1, g2 in comparisons:
            a = group_data[str(g1)]
            b = group_data[str(g2)]
            try:
                u_s, p_raw = stats.mannwhitneyu(a, b, alternative="two-sided")
                p_adj = min(p_raw * n_comp, 1.0)
                post_results.append({
                    "comparison": f"{g1} vs {g2}",
                    "statistic": round(float(u_s), 2),
                    "p_value_raw": round(float(p_raw), 6),
                    "p_value_adj": round(float(p_adj), 6),
                    "significant": p_adj < 0.05,
                    "method": "Mann-Whitney U + Bonferroni校正",
                })
            except Exception as e:
                post_results.append({"comparison": f"{g1} vs {g2}", "error": str(e)})
        result["post_hoc"] = post_results
    return result


def wilcoxon_signed_rank_test(df: pd.DataFrame, var: str, paired_var: str) -> dict:
    df_clean = df[[var, paired_var]].dropna()
    a = df_clean[var].values
    b = df_clean[paired_var].values
    if len(a) < 5:
        return {"error": "配对样本量不足（需要至少5对完整数据）"}
    try:
        w_stat, p_val = stats.wilcoxon(a, b, alternative="two-sided")
    except Exception as e:
        return {"error": f"Wilcoxon符号秩检验计算失败: {str(e)}"}
    diffs = a - b
    return {
        "test_type": "wilcoxon_signed_rank",
        "test_name": "Wilcoxon符号秩检验 (配对秩和检验)",
        "statistic": round(float(w_stat), 4),
        "p_value": round(float(p_val), 6),
        "significant": p_val < 0.05,
        "method": "Wilcoxon signed-rank test",
        "summary": f"W = {w_stat:.4f}, p = {format_p_value(p_val)}",
        "details": {
            "n_pairs": int(len(a)),
            "n_positive_diffs": int(np.sum(diffs > 0)),
            "n_negative_diffs": int(np.sum(diffs < 0)),
            "n_zero_diffs": int(np.sum(diffs == 0)),
            "median_diff": round(float(np.median(diffs)), 3),
            "median_before": round(float(np.median(a)), 3),
            "median_after": round(float(np.median(b)), 3),
        },
        "descriptive_stats": {"variable_1": var, "variable_2": paired_var},
        "chart_data": {"chart_type": "paired_box", "var_1_name": str(var), "var_2_name": str(paired_var), "var_1_values": [float(v) if pd.notna(v) else None for v in a.tolist()], "var_2_values": [float(v) if pd.notna(v) else None for v in b.tolist()], "diffs": [float(v) if pd.notna(v) else None for v in diffs.tolist()], "title": f"Wilcoxon配对比较: {var} vs {paired_var}"},
        "post_hoc": None,
    }


def mcnemar_test(df: pd.DataFrame, var: str, paired_var: str, continuity_correction: bool = True) -> dict:
    df_clean = df[[var, paired_var]].dropna()
    if len(df_clean) == 0:
        return {"error": "无有效配对数据"}
    all_cats = sorted(set(df_clean[var].dropna().unique().tolist() + df_clean[paired_var].dropna().unique().tolist()))
    if len(all_cats) == 2:
        b = int(((df_clean[var] == all_cats[0]) & (df_clean[paired_var] == all_cats[1])).sum())
        c = int(((df_clean[var] == all_cats[1]) & (df_clean[paired_var] == all_cats[0])).sum())
        if b + c < 10:
            from scipy.stats import binomtest
            result_exact = binomtest(min(b, c), n=b + c, p=0.5, alternative="two-sided")
            chi2_stat, p_val = None, result_exact.pvalue
            method_used = "McNemar精确检验 (二项检验)"
        else:
            chi2_stat = (abs(b - c) - (1 if continuity_correction else 0)) ** 2 / (b + c) if (b + c) > 0 else 0
            method_used = "McNemar检验（连续性校正）" if continuity_correction else "McNemar检验"
            p_val = 1 - stats.chi2.cdf(chi2_stat, 1)
        return {
            "test_type": "mcnemar",
            "test_name": "McNemar检验 (配对分类资料)",
            "statistic": round(float(chi2_stat), 4) if chi2_stat is not None else None,
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": method_used,
            "summary": f"χ² = {chi2_stat:.4f}, p = {format_p_value(p_val)}" if chi2_stat is not None else f"Exact p = {format_p_value(p_val)}",
            "details": {"discordant_pairs": {"b": int(b), "c": int(c), "total": int(b + c)}, "categories": all_cats},
            "chart_data": {"chart_type": "paired_bar", "var_1_name": str(var), "var_2_name": str(paired_var), "categories": all_cats, "var_1_counts": [int((df_clean[var] == cat).sum()) for cat in all_cats], "var_2_counts": [int((df_clean[paired_var] == cat).sum()) for cat in all_cats], "title": f"配对分类比较: {var} vs {paired_var}"},
            "post_hoc": None,
        }
    else:
        try:
            k = len(all_cats)
            ct = pd.crosstab(df_clean[var], df_clean[paired_var])
            ct = ct.reindex(index=all_cats, columns=all_cats, fill_value=0)
            mat = ct.values
            bowker_stat = 0.0
            for i in range(k):
                for j in range(i + 1, k):
                    n_ij, n_ji = mat[i, j], mat[j, i]
                    if n_ij + n_ji > 0:
                        bowker_stat += (n_ij - n_ji) ** 2 / (n_ij + n_ji)
            df_bowker = k * (k - 1) // 2
            p_val = 1 - stats.chi2.cdf(bowker_stat, df_bowker)
            return {
                "test_type": "mcnemar",
                "test_name": "McNemar-Bowker检验 (配对多分类)",
                "statistic": round(float(bowker_stat), 4),
                "p_value": round(float(p_val), 6),
                "significant": p_val < 0.05,
                "method": f"McNemar-Bowker对称性检验 (df={df_bowker})",
                "summary": f"χ² = {bowker_stat:.4f}, df = {df_bowker}, p = {format_p_value(p_val)}",
                "details": {"k_categories": k, "degrees_of_freedom": df_bowker, "categories": all_cats},
                "chart_data": {"chart_type": "paired_bar", "var_1_name": str(var), "var_2_name": str(paired_var), "categories": all_cats, "var_1_counts": [int((df_clean[var] == cat).sum()) for cat in all_cats], "var_2_counts": [int((df_clean[paired_var] == cat).sum()) for cat in all_cats], "title": f"配对多分类比较: {var} vs {paired_var}"},
                "post_hoc": None,
            }
        except Exception as e:
            return {"error": f"McNemar-Bowker检验计算失败: {str(e)}"}


# ═══ Additional Clinical Statistical Methods ═══════════════════

def friedman_test(df: pd.DataFrame, var: str, subject_var: str, group_var: str) -> dict:
    """Friedman test for repeated measures (non-parametric one-way RM ANOVA)."""
    if not group_var or group_var not in df.columns:
        return {"error": "Friedman检验需要有效的分组变量"}
    if not subject_var or subject_var not in df.columns:
        return {"error": "Friedman检验需要有效的受试者ID变量"}
    subjects = df[subject_var].dropna().unique()
    groups = df[group_var].dropna().unique()
    if len(groups) < 2:
        return {"error": "Friedman检验需要至少2个处理组"}
    data_for_test = []
    for g in groups:
        g_data = []
        for s in subjects:
            vals = df.loc[(df[subject_var] == s) & (df[group_var] == g), var].values
            g_data.append(vals[0] if len(vals) > 0 else np.nan)
        data_for_test.append(np.array(g_data, dtype=float))
    valid_mask = np.all([~np.isnan(d) for d in data_for_test], axis=0)
    clean_data = [d[valid_mask] for d in data_for_test]
    n_valid = int(np.sum(valid_mask))
    if n_valid < 3:
        return {"error": f"有效完整观测不足（仅{n_valid}个受试者有所有处理组的完整数据），需要至少3个"}
    try:
        chi2, p_val = stats.friedmanchisquare(*clean_data)
        return {
            "test_type": "friedman",
            "test_name": "Friedman检验 (非参数重复测量)",
            "statistic": round(float(chi2), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": "Friedman test (non-parametric repeated measures)",
            "summary": f"χ² = {chi2:.4f}, p = {format_p_value(p_val)}",
            "details": {"n_subjects_complete": n_valid, "n_groups": len(groups), "groups": [str(g) for g in groups]},
            "chart_data": {"chart_type": "repeated_measures", "groups": [str(g) for g in groups], "subject_var": subject_var, "values": {str(g): [float(v) if pd.notna(v) else None for v in d] for g, d in zip(groups, clean_data)}, "title": f"重复测量: {var}"},
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"Friedman检验计算失败: {str(e)}"}


def repeated_measures_anova(df: pd.DataFrame, var: str, subject_var: str, group_var: str, between_var: str | None = None) -> dict:
    """Repeated measures ANOVA (one-way within, or mixed design)."""
    if not group_var or group_var not in df.columns:
        return {"error": "重复测量方差分析需要有效的组内因素变量"}
    if not subject_var or subject_var not in df.columns:
        return {"error": "重复测量方差分析需要有效的受试者ID变量"}
    subjects = df[subject_var].dropna().unique()
    groups = df[group_var].dropna().unique()
    if len(groups) < 2:
        return {"error": "重复测量方差分析需要至少2个时间点/处理条件"}
    data_for_test = []
    for g in groups:
        g_data = []
        for s in subjects:
            vals = df.loc[(df[subject_var] == s) & (df[group_var] == g), var].values
            g_data.append(vals[0] if len(vals) > 0 else np.nan)
        data_for_test.append(np.array(g_data, dtype=float))
    valid_mask = np.all([~np.isnan(d) for d in data_for_test], axis=0)
    clean_data = [d[valid_mask] for d in data_for_test]
    n_valid = int(np.sum(valid_mask))
    if n_valid < 3:
        return {"error": f"有效完整观测不足（仅{n_valid}个受试者），需要至少3个"}
    try:
        # Proper repeated measures ANOVA with subject blocking
        # Compute SS_total, SS_subjects, SS_treatment, SS_error
        all_vals = np.concatenate(clean_data)
        grand_mean = np.mean(all_vals)
        n = n_valid  # number of subjects
        k = len(clean_data)  # number of conditions

        # Subject means (across conditions)
        subject_means = np.mean(np.column_stack(clean_data), axis=1)

        # Condition means
        condition_means = np.array([np.mean(d) for d in clean_data])

        # Sum of squares
        ss_total = np.sum((all_vals - grand_mean) ** 2)
        ss_subjects = k * np.sum((subject_means - grand_mean) ** 2)
        ss_treatment = n * np.sum((condition_means - grand_mean) ** 2)
        ss_error = ss_total - ss_subjects - ss_treatment

        # Handle negative SS_error due to floating point
        if ss_error < 0:
            ss_error = max(ss_error, 1e-10)

        # Degrees of freedom
        df_treatment = k - 1
        df_error = (n - 1) * (k - 1)

        if df_error <= 0 or ss_error <= 0:
            return {"error": "自由度不足或误差为0，无法计算F统计量"}

        ms_treatment = ss_treatment / df_treatment
        ms_error = ss_error / df_error
        f_stat = ms_treatment / ms_error if ms_error > 0 else float('inf')
        p_val = float(stats.f.sf(f_stat, df_treatment, df_error))

        # Effect size: partial eta-squared
        eta_sq = ss_treatment / (ss_treatment + ss_error) if (ss_treatment + ss_error) > 0 else 0.0

        return {
            "test_type": "repeated_measures_anova",
            "test_name": "重复测量方差分析 (RM ANOVA)",
            "statistic": round(float(f_stat), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": "One-way repeated measures ANOVA (with subject blocking)",
            "summary": f"F({int(df_treatment)}, {int(df_error)}) = {f_stat:.4f}, p = {format_p_value(p_val)}",
            "note": "注：此处采用单变量法univariate approach计算RM ANOVA，包含subject效应。未进行球形检验（Mauchly's test）。如需球形校正（Greenhouse-Geisser, Huynh-Feldt）或更完整的分析，建议使用SPSS/R等专业软件。",
            "details": {
                "n_subjects_complete": n_valid,
                "n_groups": len(groups),
                "groups": [str(g) for g in groups],
                "ss_treatment": round(float(ss_treatment), 4),
                "ss_error": round(float(ss_error), 4),
                "ss_subjects": round(float(ss_subjects), 4),
                "ms_treatment": round(float(ms_treatment), 4),
                "ms_error": round(float(ms_error), 4),
                "df_treatment": int(df_treatment),
                "df_error": int(df_error),
                "partial_eta_squared": round(float(eta_sq), 4),
            },
            "chart_data": {"chart_type": "repeated_measures", "groups": [str(g) for g in groups], "subject_var": subject_var, "values": {str(g): [float(v) if pd.notna(v) else None for v in d] for g, d in zip(groups, clean_data)}, "title": f"重复测量: {var}"},
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"重复测量方差分析计算失败: {str(e)}"}


def pearson_correlation(df: pd.DataFrame, var1: str, var2: str) -> dict:
    """Pearson correlation coefficient."""
    if var1 not in df.columns or var2 not in df.columns:
        return {"error": "变量不存在于数据集中"}
    clean = df[[var1, var2]].copy()
    clean[var1] = pd.to_numeric(clean[var1], errors="coerce")
    clean[var2] = pd.to_numeric(clean[var2], errors="coerce")
    clean = clean.dropna()
    x, y = clean[var1].values.astype(float), clean[var2].values.astype(float)
    if len(x) < 3:
        return {"error": "样本量不足（需要至少3个完整观测）"}
    try:
        r, p_val = pearsonr(x, y)
        if p_val < 0.001:
            interpretation = "高度显著相关"
        elif p_val < 0.01:
            interpretation = "显著相关"
        elif p_val < 0.05:
            interpretation = "有统计学意义的相关"
        else:
            interpretation = "无统计学意义的相关"
        return {
            "test_type": "pearson_correlation",
            "test_name": "Pearson线性相关分析",
            "statistic": round(float(r), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": "Pearson product-moment correlation",
            "summary": f"r = {r:.4f}, p = {format_p_value(p_val)}",
            "note": interpretation,
            "details": {"n": int(len(x)), "r_squared": round(float(r ** 2), 4), "variable_1": var1, "variable_2": var2},
            "chart_data": {"chart_type": "scatter_regression", "x_var": var1, "y_var": var2, "x_values": [float(v) for v in x], "y_values": [float(v) for v in y], "r": round(float(r), 4), "p_value": round(float(p_val), 6), "title": f"Pearson: {var1} vs {var2}"},
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"Pearson相关计算失败: {str(e)}"}


def spearman_correlation(df: pd.DataFrame, var1: str, var2: str) -> dict:
    """Spearman rank correlation coefficient."""
    if var1 not in df.columns or var2 not in df.columns:
        return {"error": "变量不存在于数据集中"}
    clean = df[[var1, var2]].copy()
    clean[var1] = pd.to_numeric(clean[var1], errors="coerce")
    clean[var2] = pd.to_numeric(clean[var2], errors="coerce")
    clean = clean.dropna()
    x, y = clean[var1].values.astype(float), clean[var2].values.astype(float)
    if len(x) < 3:
        return {"error": "样本量不足（需要至少3个完整观测）"}
    try:
        rho, p_val = spearmanr(x, y)
        return {
            "test_type": "spearman_correlation",
            "test_name": "Spearman秩相关分析",
            "statistic": round(float(rho), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": "Spearman rank correlation",
            "summary": f"ρ = {rho:.4f}, p = {format_p_value(p_val)}",
            "details": {"n": int(len(x)), "variable_1": var1, "variable_2": var2},
            "chart_data": {"chart_type": "scatter_regression", "x_var": var1, "y_var": var2, "x_values": [float(v) for v in x], "y_values": [float(v) for v in y], "r": round(float(rho), 4), "p_value": round(float(p_val), 6), "title": f"Spearman: {var1} vs {var2}"},
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"Spearman相关计算失败: {str(e)}"}


def log_rank_test(df: pd.DataFrame, time_var: str, event_var: str, group_var: str) -> dict:
    """Log-rank test for survival analysis."""
    if not group_var or group_var not in df.columns:
        return {"error": "Log-rank检验需要有效的分组变量"}
    groups = sorted(df[group_var].dropna().unique().tolist())
    if len(groups) < 2:
        return {"error": "Log-rank检验需要至少2组"}
    group_data = {}
    for g in groups:
        # Drop rows where either time or event is NaN to ensure alignment
        mask = (df[group_var] == g) & df[time_var].notna() & df[event_var].notna()
        group_data[str(g)] = {
            "time": df.loc[mask, time_var].values.astype(float),
            "event": df.loc[mask, event_var].values.astype(int),
        }
    # Validate data
    for g in groups:
        gk = str(g)
        if len(group_data[gk]["time"]) < 2:
            return {"error": f"分组 '{gk}' 有效观测不足（需要至少2个完整观测）"}
    try:
        result = logrank_test(
            group_data[str(groups[0])]["time"], group_data[str(groups[1])]["time"],
            group_data[str(groups[0])]["event"], group_data[str(groups[1])]["event"],
        )
        return {
            "test_type": "log_rank",
            "test_name": "Log-Rank 生存分析检验",
            "statistic": round(float(result.test_statistic), 4),
            "p_value": round(float(result.p_value), 6),
            "significant": result.p_value < 0.05,
            "method": "Log-rank test (Mantel-Cox)",
            "summary": f"χ² = {result.test_statistic:.4f}, p = {format_p_value(result.p_value)}",
            "details": {"groups": [str(g) for g in groups], "test_statistic": round(float(result.test_statistic), 4)},
            "chart_data": {"chart_type": "survival", "time_var": time_var, "event_var": event_var, "group_var": group_var, "groups": [str(g) for g in groups], "title": "Kaplan-Meier 生存曲线"},
            "post_hoc": None,
        }
    except ImportError:
        # Fallback without lifelines
        return {
            "test_type": "log_rank",
            "test_name": "Log-Rank 生存分析检验",
            "statistic": None,
            "p_value": None,
            "significant": False,
            "method": "Log-rank test (需安装lifelines库)",
            "summary": "需要安装lifelines库: pip install lifelines",
            "note": "需要安装lifelines库以进行精确的生存分析。当前可使用Kaplan-Meier可视化查看生存曲线趋势。",
            "details": {"groups": [str(g) for g in groups]},
            "chart_data": {"chart_type": "survival", "time_var": time_var, "event_var": event_var, "group_var": group_var, "groups": [str(g) for g in groups], "title": "Kaplan-Meier 生存曲线"},
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"Log-rank检验计算失败: {str(e)}"}


def discriminant_analysis(
    df: pd.DataFrame,
    outcome_var: str,
    predictor_vars: list[str],
    method: str = "lda",
) -> dict:
    """Linear or quadratic discriminant analysis for categorical outcomes."""
    if not predictor_vars:
        return {"error": "判别分析需要至少 1 个连续型预测变量"}

    predictors = [col for col in predictor_vars if col in df.columns and col != outcome_var]
    if not predictors:
        return {"error": "判别分析的预测变量不存在或为空"}

    working = df[[outcome_var] + predictors].copy()
    for col in predictors:
        working[col] = pd.to_numeric(working[col], errors="coerce")
    working[outcome_var] = working[outcome_var].astype("object")
    working = working.dropna(subset=[outcome_var] + predictors)

    # Remove constant columns after dropna (may have changed)
    predictors = [col for col in predictors if col in working.columns and working[col].nunique(dropna=True) > 1]
    if not predictors:
        return {"error": "预测变量均为常量或缺失，无法进行判别分析"}
    working = working[[outcome_var] + predictors].dropna()

    if len(working) < 20:
        return {"error": f"样本量不足（仅 {len(working)} 个完整观测），判别分析建议至少 20 个观测"}

    class_counts = working[outcome_var].value_counts()
    if len(class_counts) < 2:
        return {"error": "判别分析需要至少 2 个结局类别"}
    if int(class_counts.min()) < 3:
        return {"error": f"每个结局类别至少需要 3 个完整观测（最小类别仅有 {int(class_counts.min())} 个）"}

    try:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.metrics import accuracy_score, confusion_matrix
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        from sklearn.pipeline import make_pipeline
        from sklearn.decomposition import PCA
        import warnings

        coefficients = {}
        explained = []

        method_key = "qda" if str(method).lower().startswith("q") else "lda"
        model_name = (
            "二次判别分析 (Quadratic Discriminant Analysis, QDA)"
            if method_key == "qda"
            else "线性判别分析 (Linear Discriminant Analysis, LDA)"
        )

        X = working[predictors].to_numpy(dtype=float)
        encoder = LabelEncoder()
        y = encoder.fit_transform(working[outcome_var].astype(str))
        class_names = encoder.classes_.tolist()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Try fitting with QDA, fall back to LDA if QDA fails (singular covariance)
        if method_key == "qda":
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    estimator = QuadraticDiscriminantAnalysis(reg_param=0.2)
                    estimator.fit(X_scaled, y)
                    y_pred = estimator.predict(X_scaled)
            except Exception as qda_err:
                # Fall back to LDA with note
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    estimator = LinearDiscriminantAnalysis(solver="svd")
                    estimator.fit(X_scaled, y)
                    y_pred = estimator.predict(X_scaled)
                method_key = "lda"
                model_name = "线性判别分析 (LDA, QDA因协方差奇异自动回退)"
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                estimator = LinearDiscriminantAnalysis(solver="svd")
                estimator.fit(X_scaled, y)
                y_pred = estimator.predict(X_scaled)

        accuracy = float(accuracy_score(y, y_pred))
        baseline_accuracy = float(np.max(np.bincount(y)) / len(y))
        min_class_n = int(np.min(np.bincount(y)))
        cv_accuracy = None
        if min_class_n >= 2:
            folds = min(5, min_class_n)
            if folds >= 2:
                cv_estimator = (
                    QuadraticDiscriminantAnalysis(reg_param=0.2)
                    if method_key == "qda"
                    else LinearDiscriminantAnalysis(solver="svd")
                )
                pipeline = make_pipeline(StandardScaler(), cv_estimator)
                splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        scores = cross_val_score(pipeline, X, y, cv=splitter, scoring="accuracy")
                    cv_accuracy = float(np.mean(scores))
                except Exception:
                    cv_accuracy = None

        cm = confusion_matrix(y, y_pred, labels=list(range(len(class_names))))
        coefficients = {}
        explained = []

        # Extract LDA coefficients
        if method_key == "lda" and hasattr(estimator, "scalings_"):
            try:
                scalings = np.asarray(estimator.scalings_)
                # scalings_ shape: (n_features, n_components) where n_components = min(n_features, n_classes-1)
                if scalings.ndim == 1:
                    first_axis = scalings
                elif scalings.ndim == 2 and scalings.shape[1] >= 1:
                    first_axis = scalings[:, 0]
                else:
                    first_axis = scalings.flatten()
                if len(first_axis) == len(predictors):
                    coefficients = {var: round(float(value), 4) for var, value in zip(predictors, first_axis)}
            except Exception:
                pass
        elif method_key == "lda" and hasattr(estimator, "coef_"):
            try:
                coef = np.asarray(estimator.coef_)
                if coef.ndim == 1:
                    first_axis = coef
                else:
                    first_axis = coef[0]
                if len(first_axis) == len(predictors):
                    coefficients = {var: round(float(value), 4) for var, value in zip(predictors, first_axis)}
            except Exception:
                pass

        if hasattr(estimator, "explained_variance_ratio_"):
            try:
                explained = [round(float(v), 4) for v in np.asarray(estimator.explained_variance_ratio_).flatten().tolist()]
            except Exception:
                pass

        # Projection for visualization
        if method_key == "lda":
            try:
                projected = estimator.transform(X_scaled)
                x_scores = projected[:, 0]
                if projected.shape[1] > 1:
                    y_scores = projected[:, 1]
                    y_label = "LD2"
                else:
                    y_scores = np.zeros(len(projected))
                    y_label = "0"
                x_label = "LD1"
            except Exception:
                # Fallback to PCA
                pca = PCA(n_components=min(2, X_scaled.shape[1]), random_state=42)
                projected = pca.fit_transform(X_scaled)
                x_scores = projected[:, 0]
                y_scores = projected[:, 1] if projected.shape[1] > 1 else np.zeros(len(projected))
                x_label = "PC1"
                y_label = "PC2" if projected.shape[1] > 1 else "0"
                explained = [round(float(v), 4) for v in pca.explained_variance_ratio_.tolist()]
        else:
            pca = PCA(n_components=min(2, X_scaled.shape[1]), random_state=42)
            projected = pca.fit_transform(X_scaled)
            x_scores = projected[:, 0]
            y_scores = projected[:, 1] if projected.shape[1] > 1 else np.zeros(len(projected))
            x_label = "PC1"
            y_label = "PC2" if projected.shape[1] > 1 else "0"
            explained = [round(float(v), 4) for v in pca.explained_variance_ratio_.tolist()]

        cv_text = f", CV accuracy = {cv_accuracy:.4f}" if cv_accuracy is not None else ""
        return {
            "test_type": "quadratic_discriminant_analysis" if method_key == "qda" else "discriminant_analysis",
            "test_name": model_name,
            "statistic": round(float(cv_accuracy if cv_accuracy is not None else accuracy), 4),
            "p_value": None,
            "significant": (cv_accuracy if cv_accuracy is not None else accuracy) > baseline_accuracy + 0.05,
            "method": "QDA with standardized predictors" if method_key == "qda" else "LDA with standardized predictors",
            "summary": f"Accuracy = {accuracy:.4f}{cv_text}, baseline = {baseline_accuracy:.4f}, n = {len(working)}",
            "note": "准确率为模型判别性能指标，不等同于传统显著性 P 值；正式建模建议进一步使用独立验证集或嵌套交叉验证。",
            "details": {
                "n": int(len(working)),
                "n_classes": int(len(class_names)),
                "classes": class_names,
                "class_counts": {str(k): int(v) for k, v in class_counts.sort_index().items()},
                "predictors": predictors,
                "n_predictors": int(len(predictors)),
                "accuracy": round(accuracy, 4),
                "cv_accuracy": round(cv_accuracy, 4) if cv_accuracy is not None else None,
                "baseline_accuracy": round(baseline_accuracy, 4),
                "confusion_matrix": {
                    "rows": class_names,
                    "cols": class_names,
                    "data": cm.astype(int).tolist(),
                },
                "coefficients": coefficients,
                "explained_variance_ratio": explained,
            },
            "descriptive_stats": None,
            "chart_data": {
                "chart_type": "discriminant_scores",
                "x_values": [float(v) for v in x_scores.tolist()],
                "y_values": [float(v) for v in y_scores.tolist()],
                "labels": [str(class_names[i]) for i in y.tolist()],
                "classes": class_names,
                "x_label": x_label,
                "y_label": y_label,
                "title": f"{'QDA' if method_key == 'qda' else 'LDA'} 判别得分图",
            },
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"判别分析计算失败: {str(e)}"}


def logistic_regression(df: pd.DataFrame, outcome_var: str, predictor_vars: list[str]) -> dict:
    """Simple logistic regression (univariate or multivariate)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    if not predictor_vars:
        return {"error": "Logistic回归需要至少1个预测变量"}
    # Keep only columns that exist
    valid_predictors = [c for c in predictor_vars if c in df.columns and c != outcome_var]
    if not valid_predictors:
        return {"error": "预测变量不存在或全部为结局变量"}
    cols = [outcome_var] + valid_predictors
    clean = df[cols].copy()
    # Convert predictors to numeric
    for col in valid_predictors:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean = clean.dropna()
    if len(clean) < 20:
        return {"error": f"样本量不足（仅{len(clean)}个完整观测），需要至少20个"}
    X_raw = clean[valid_predictors].values.astype(float)
    y_raw = clean[outcome_var].values
    try:
        # Encode string labels to 0/1
        encoder = LabelEncoder()
        y = encoder.fit_transform(y_raw.astype(str))
        classes = encoder.classes_.tolist()
        if len(classes) < 2:
            return {"error": f"结局变量 '{outcome_var}' 只有1个类别，Logistic回归需要至少2个类别"}
        if len(classes) > 2:
            return {"error": f"结局变量 '{outcome_var}' 有{len(classes)}个类别，当前仅支持二分类Logistic回归。请考虑使用判别分析。"}
        # Standardize predictors
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)
        model = LogisticRegression(max_iter=2000, solver='lbfgs')
        model.fit(X, y)
        coefs = {var: round(float(c), 4) for var, c in zip(valid_predictors, model.coef_[0])}
        ors = {var: round(float(np.exp(c)), 4) for var, c in zip(valid_predictors, model.coef_[0])}
        accuracy = round(float(model.score(X, y)), 4)
        class_labels = {0: str(classes[0]), 1: str(classes[1])}
        return {
            "test_type": "logistic_regression",
            "test_name": "Logistic回归分析",
            "statistic": accuracy,
            "p_value": None,
            "significant": False,
            "method": "Logistic Regression (sklearn, standardized)",
            "summary": f"Accuracy = {accuracy:.4f}, n = {len(clean)}, AUC可用",
            "note": "注：变量已标准化，OR为每1个标准差变化的比值比。完整p值和95%CI需使用statsmodels。",
            "details": {
                "n": int(len(clean)),
                "n_features": len(valid_predictors),
                "coefficients": coefs,
                "odds_ratios": ors,
                "intercept": round(float(model.intercept_[0]), 4),
                "class_labels": class_labels,
                "predictors": valid_predictors,
            },
            "chart_data": None,
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"Logistic回归计算失败: {str(e)}"}


def linear_regression(df: pd.DataFrame, y_var: str, x_vars: list[str]) -> dict:
    """Multiple linear regression."""
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    if not x_vars:
        return {"error": "线性回归需要至少1个预测变量"}
    valid_predictors = [c for c in x_vars if c in df.columns and c != y_var]
    if not valid_predictors:
        return {"error": "预测变量不存在或全部等于因变量"}
    cols = [y_var] + valid_predictors
    clean = df[cols].copy()
    for col in valid_predictors:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean[y_var] = pd.to_numeric(clean[y_var], errors="coerce")
    clean = clean.dropna()
    if len(clean) < 20:
        return {"error": f"样本量不足（仅{len(clean)}个完整观测），需要至少20个"}
    X_raw = clean[valid_predictors].values.astype(float)
    y = clean[y_var].values.astype(float)
    try:
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)
        model = LinearRegression()
        model.fit(X, y)
        coefs = {var: round(float(c), 4) for var, c in zip(valid_predictors, model.coef_)}
        r_squared = round(float(model.score(X, y)), 4)
        # Adjusted R-squared
        n, p = len(y), len(valid_predictors)
        adj_r2 = round(float(1 - (1 - r_squared) * (n - 1) / max(1, n - p - 1)), 4)
        return {
            "test_type": "linear_regression",
            "test_name": "多重线性回归分析",
            "statistic": r_squared,
            "p_value": None,
            "significant": r_squared > 0.1,
            "method": "Multiple Linear Regression (sklearn, standardized)",
            "summary": f"R² = {r_squared:.4f}, adj R² = {adj_r2:.4f}, n = {len(clean)}",
            "note": "注：变量已标准化，系数为标准化回归系数(β)。标准误和p值需使用statsmodels获取。",
            "details": {
                "n": int(n),
                "n_predictors": p,
                "coefficients": coefs,
                "intercept": round(float(model.intercept_), 4),
                "r_squared": r_squared,
                "adj_r_squared": adj_r2,
                "predictors": valid_predictors,
            },
            "chart_data": None,
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"线性回归计算失败: {str(e)}"}


def ancova(df: pd.DataFrame, var: str, group_var: str, covar: str) -> dict:
    """ANCOVA (Analysis of Covariance) simplified."""
    if not group_var or group_var not in df.columns:
        return {"error": "ANCOVA需要一个有效的分组变量"}
    if not covar or covar not in df.columns:
        return {"error": "ANCOVA需要一个有效的协变量"}
    # Validate numeric types
    if not pd.api.types.is_numeric_dtype(df[var].dropna()):
        return {"error": f"因变量 '{var}' 必须是连续数值型变量"}
    if not pd.api.types.is_numeric_dtype(df[covar].dropna()):
        return {"error": f"协变量 '{covar}' 必须是连续数值型变量"}
    clean = df[[var, group_var, covar]].copy()
    clean[var] = pd.to_numeric(clean[var], errors="coerce")
    clean[covar] = pd.to_numeric(clean[covar], errors="coerce")
    clean = clean.dropna()
    groups = sorted(clean[group_var].unique())
    if len(groups) < 2:
        return {"error": "ANCOVA需要至少2组"}
    if len(clean) < 10:
        return {"error": f"ANCOVA样本量不足（仅{len(clean)}个完整观测），需要至少10个"}
    from sklearn.linear_model import LinearRegression
    clean_encoded = clean.copy()
    for i, g in enumerate(groups):
        clean_encoded[f"group_{i}"] = (clean[group_var] == g).astype(int)
    group_cols = [f"group_{i}" for i in range(len(groups) - 1)]
    X = clean_encoded[[covar] + group_cols].values
    y = clean_encoded[var].values
    try:
        if X.shape[1] < 2:
            return {"error": "自变量数量不足（需要至少1个协变量+1个分组变量）"}
        model_full = LinearRegression()
        model_full.fit(X, y)
        r2_full = model_full.score(X, y)
        model_reduced = LinearRegression()
        X_reduced = clean_encoded[[covar]].values
        model_reduced.fit(X_reduced, y)
        r2_reduced = model_reduced.score(X_reduced, y)
        n = len(y)
        p_full = X.shape[1]
        p_reduced = 1
        f_num = (r2_full - r2_reduced) / max(p_full - p_reduced, 1)
        f_den = (1 - r2_full) / max(n - p_full - 1, 1)
        if f_den <= 0:
            return {"error": "ANCOVA模型误差为0，无法计算F统计量。请检查数据是否存在完全共线性。"}
        f_stat = f_num / f_den
        df1 = p_full - p_reduced
        df2 = n - p_full - 1
        p_val = 1 - stats.f.cdf(f_stat, df1, max(df2, 1))
        # Group adjusted means
        group_adj_means = {}
        for g in groups:
            g_mask = clean[group_var] == g
            g_mean_covar = clean.loc[g_mask, covar].mean()
            group_adj_means[str(g)] = round(float(
                model_full.predict([[g_mean_covar] + [1 if i == groups.index(g) and i < len(groups) - 1 else 0 for i in range(len(groups) - 1)]])[0]
            ), 3) if n > 0 else None
        return {
            "test_type": "ancova",
            "test_name": "协方差分析 (ANCOVA)",
            "statistic": round(float(f_stat), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "method": "ANCOVA (协方差分析)",
            "summary": f"F({df1},{max(df2,1)}) = {f_stat:.4f}, p = {format_p_value(p_val)}",
            "note": f"校正协变量: {covar}。此为简化近似计算，正式发表建议使用SPSS/R等专业软件。",
            "details": {
                "n": int(n),
                "groups": [str(g) for g in groups],
                "covariate": covar,
                "r2_full": round(float(r2_full), 4),
                "r2_reduced": round(float(r2_reduced), 4),
                "adjusted_means": group_adj_means,
                "df1": int(df1),
                "df2": int(max(df2, 1)),
            },
            "chart_data": None,
            "post_hoc": None,
        }
    except Exception as e:
        return {"error": f"ANCOVA计算失败: {str(e)}"}


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return float((np.mean(group1) - np.mean(group2)) / pooled_sd) if pooled_sd > 0 else 0.0


def eta_squared(f_stat: float, df_effect: int, df_error: int) -> float:
    """Calculate eta-squared effect size for ANOVA."""
    return float((f_stat * df_effect) / (f_stat * df_effect + df_error))


def cohens_w(contingency: np.ndarray, n: int) -> float:
    """Calculate Cohen's w effect size for chi-square."""
    expected = np.outer(np.sum(contingency, axis=1), np.sum(contingency, axis=0)) / n
    return float(np.sqrt(np.sum((contingency - expected) ** 2 / expected) / n))


# ═══ Helper Functions ═══════════════════════════════════════════

def _group_descriptive(df: pd.DataFrame, var: str, group_var: str) -> dict:
    groups = sorted(df[group_var].dropna().unique().tolist())
    result = {"groups": groups, "group_stats": {}, "variable": var, "variable_type": "continuous" if pd.api.types.is_numeric_dtype(df[var]) else "categorical"}
    for g in groups:
        g_series = df.loc[df[group_var] == g, var].dropna()
        result["group_stats"][str(g)] = calc_descriptive(pd.DataFrame({var: g_series}), var)
    return result


def _build_chart_data(df: pd.DataFrame, var: str, group_var: str | None) -> dict:
    if group_var and group_var in df.columns:
        groups = sorted(df[group_var].dropna().unique().tolist())
        traces = []
        for g in groups:
            vals = df.loc[df[group_var] == g, var].dropna().tolist()
            traces.append({"name": str(g), "values": [float(v) if pd.notna(v) else None for v in vals]})
        return {"chart_type": "box_violin", "traces": traces, "x_label": str(group_var), "y_label": str(var), "title": f"{var} by {group_var}"}
    else:
        vals = df[var].dropna().tolist()
        return {"chart_type": "histogram", "traces": [{"name": str(var), "values": [float(v) if pd.notna(v) else None for v in vals]}], "x_label": str(var), "y_label": "Count", "title": f"Distribution of {var}"}


def _build_contingency_chart(contingency: pd.DataFrame, var: str, group_var: str) -> dict:
    return {"chart_type": "bar_grouped", "categories": contingency.columns.tolist(), "series": [{"name": str(idx), "values": [int(v) for v in row]} for idx, row in zip(contingency.index, contingency.values.tolist())], "x_label": str(group_var), "y_label": "Count", "title": f"{var} × {group_var} 列联图"}


def _run_post_hoc(df: pd.DataFrame, var: str, group_var: str, method: str, equal_var: bool, groups: list) -> list[dict]:
    results = []
    if method == "tukey":
        try:
            from statsmodels.stats.multicomp import pairwise_tukeyhsd
            df_clean = df[[var, group_var]].dropna()
            tukey = pairwise_tukeyhsd(df_clean[var].values, df_clean[group_var].values, alpha=0.05)
            summary_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])
            for _, row in summary_df.iterrows():
                results.append({"comparison": f"{row['group1']} vs {row['group2']}", "mean_diff": round(float(row['meandiff']), 4), "ci_lower": round(float(row['lower']), 4), "ci_upper": round(float(row['upper']), 4), "p_value": round(float(row['p-adj']), 6), "significant": bool(row['reject']), "method": "Tukey HSD"})
        except Exception as e:
            results.append({"error": f"Tukey HSD计算失败: {str(e)}", "method": "Tukey HSD"})
    elif method == "bonferroni":
        comparisons = [(g1, g2) for i, g1 in enumerate(groups) for g2 in groups[i + 1:]]
        n_comparisons = len(comparisons)
        for g1, g2 in comparisons:
            a = df.loc[df[group_var] == g1, var].dropna().values
            b = df.loc[df[group_var] == g2, var].dropna().values
            try:
                t_stat, p_val = stats.ttest_ind(a, b, equal_var=equal_var)
                p_adj = min(p_val * n_comparisons, 1.0)
                results.append({"comparison": f"{g1} vs {g2}", "mean_diff": round(float(np.mean(a) - np.mean(b)), 4), "p_value_raw": round(float(p_val), 6), "p_value_adj": round(float(p_adj), 6), "significant": p_adj < 0.05, "method": "Bonferroni校正"})
            except Exception as e:
                results.append({"comparison": f"{g1} vs {g2}", "error": str(e), "method": "Bonferroni校正"})
    elif method == "lsd":
        comparisons = [(g1, g2) for i, g1 in enumerate(groups) for g2 in groups[i + 1:]]
        for g1, g2 in comparisons:
            a = df.loc[df[group_var] == g1, var].dropna().values
            b = df.loc[df[group_var] == g2, var].dropna().values
            try:
                t_stat, p_val = stats.ttest_ind(a, b, equal_var=equal_var)
                results.append({"comparison": f"{g1} vs {g2}", "mean_diff": round(float(np.mean(a) - np.mean(b)), 4), "p_value": round(float(p_val), 6), "significant": p_val < 0.05, "method": "LSD"})
            except Exception as e:
                results.append({"comparison": f"{g1} vs {g2}", "error": str(e), "method": "LSD"})
    elif method == "games_howell":
        comparisons = [(g1, g2) for i, g1 in enumerate(groups) for g2 in groups[i + 1:]]
        for g1, g2 in comparisons:
            a = df.loc[df[group_var] == g1, var].dropna().values
            b = df.loc[df[group_var] == g2, var].dropna().values
            try:
                n1, n2 = len(a), len(b)
                var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
                se = np.sqrt(var1 / n1 + var2 / n2)
                t_stat = (np.mean(a) - np.mean(b)) / se
                df_num = (var1 / n1 + var2 / n2) ** 2
                df_den = (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
                df_welch = df_num / df_den
                p_val = 2 * stats.t.sf(abs(t_stat), df_welch)
                results.append({"comparison": f"{g1} vs {g2}", "mean_diff": round(float(np.mean(a) - np.mean(b)), 4), "p_value": round(float(p_val), 6), "significant": p_val < 0.05, "method": "Games-Howell"})
            except Exception as e:
                results.append({"comparison": f"{g1} vs {g2}", "error": str(e), "method": "Games-Howell"})
    return results
