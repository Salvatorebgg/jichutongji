from __future__ import annotations

import pandas as pd
import numpy as np
from app.services.stats_service import calc_descriptive, format_p_value, _test_normality


def build_result_table(result: dict) -> dict:
    """Convert a statistical test result into a display table format."""
    if "error" in result:
        return {"columns": ["Error"], "rows": [{"Error": result["error"]}], "title": "Analysis Error"}

    details = result.get("details") or {}
    rows = [
        {"Metric": "检验方法", "Value": result.get("test_name", ""), "Interpretation": result.get("method", "")},
        {"Metric": "统计量", "Value": _display_value(result.get("statistic")), "Interpretation": _statistic_label(result)},
        {
            "Metric": "P 值",
            "Value": format_p_value(result.get("p_value")),
            "Interpretation": _p_value_interpretation(result),
        },
    ]

    sample_size = _sample_size_from_details(result)
    if sample_size:
        rows.append({"Metric": "有效样本量", "Value": sample_size, "Interpretation": "用于本次检验的完整观测数"})

    effect_summary = _effect_summary(result)
    if effect_summary:
        rows.append({"Metric": "效应摘要", "Value": effect_summary["value"], "Interpretation": effect_summary["interpretation"]})

    if result.get("post_hoc"):
        sig_pairs = [row for row in result["post_hoc"] if row.get("significant")]
        rows.append({
            "Metric": "事后比较",
            "Value": f"{len(sig_pairs)} / {len(result['post_hoc'])} 个比较显著",
            "Interpretation": "多组比较需结合校正后 P 值解释",
        })

    if details.get("levene_test"):
        lev = details["levene_test"]
        rows.append({
            "Metric": "方差齐性",
            "Value": f"Levene P = {format_p_value(lev.get('p_value'))}",
            "Interpretation": "方差齐性可接受" if lev.get("equal_var") else "提示方差不齐，建议谨慎解释",
        })

    if result.get("note"):
        rows.append({"Metric": "方法备注", "Value": result["note"], "Interpretation": "请在报告中说明"})

    columns = ["Metric", "Value", "Interpretation"]
    return {"columns": columns, "rows": rows, "title": result.get("test_name", "Statistical Test Result")}


def _display_value(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _statistic_label(result: dict) -> str:
    mapping = {
        "t_test_independent": "t 值",
        "t_test_paired": "t 值",
        "one_sample_t_test": "t 值",
        "normality_test": "W 值",
        "levene_test": "Levene W 值",
        "anova": "F 值",
        "chi_square": "χ² 值",
        "fisher_exact": "OR 或近似统计量",
        "mann_whitney": "U 值",
        "kruskal_wallis": "H 值",
        "wilcoxon_signed_rank": "W 值",
        "mcnemar": "χ² 或精确概率",
        "friedman": "χ² 值",
        "repeated_measures_anova": "F 值",
        "pearson_correlation": "r 值",
        "spearman_correlation": "ρ 值",
        "log_rank": "χ² 值",
        "linear_regression": "R²",
        "logistic_regression": "模型准确率",
        "discriminant_analysis": "交叉验证准确率",
        "quadratic_discriminant_analysis": "交叉验证准确率",
        "ancova": "F 值",
    }
    return mapping.get(result.get("test_type"), "统计量")


def _p_value_interpretation(result: dict) -> str:
    if result.get("p_value") is None:
        return "该方法当前返回模型性能指标，不提供传统 P 值"
    if result.get("test_type") == "normality_test":
        return "提示偏离正态" if result.get("significant") else "未发现显著偏离正态"
    if result.get("test_type") == "levene_test":
        return "提示方差不齐" if result.get("significant") else "方差齐性可接受"
    return "差异/关联具有统计学意义" if result.get("significant") else "未达到 0.05 显著性水平"


def _sample_size_from_details(result: dict) -> str:
    details = result.get("details") or {}
    if details.get("total_n") is not None:
        return str(details["total_n"])
    if details.get("n") is not None:
        return str(details["n"])
    if details.get("n_pairs") is not None:
        return f"{details['n_pairs']} 对"
    if details.get("n_subjects_complete") is not None:
        return f"{details['n_subjects_complete']} 个完整个体"
    g1 = details.get("group_1") or {}
    g2 = details.get("group_2") or {}
    if g1.get("n") is not None and g2.get("n") is not None:
        return f"{g1['n']} + {g2['n']}"
    return ""


def _effect_summary(result: dict) -> dict | None:
    details = result.get("details") or {}
    test_type = result.get("test_type")
    if details.get("mean_diff") is not None:
        return {"value": _display_value(details["mean_diff"]), "interpretation": "均值差；方向取决于当前分组顺序"}
    if details.get("median_diff") is not None:
        return {"value": _display_value(details["median_diff"]), "interpretation": "配对差值中位数"}
    if details.get("odds_ratio") is not None:
        return {"value": f"OR = {_display_value(details['odds_ratio'])}", "interpretation": "优势比；大于 1 表示第一类结局优势更高"}
    if details.get("r_squared") is not None:
        return {"value": f"R² = {_display_value(details['r_squared'])}", "interpretation": "解释度估计"}
    if test_type in {"pearson_correlation", "spearman_correlation"} and result.get("statistic") is not None:
        return {"value": _display_value(result["statistic"]), "interpretation": "相关系数；绝对值越大相关越强"}
    if test_type in {"discriminant_analysis", "quadratic_discriminant_analysis"}:
        acc = details.get("cv_accuracy") if details.get("cv_accuracy") is not None else details.get("accuracy")
        baseline = details.get("baseline_accuracy")
        if acc is not None:
            return {
                "value": f"Accuracy = {_display_value(acc)}; baseline = {_display_value(baseline)}",
                "interpretation": "判别性能；应优先参考交叉验证或外部验证结果",
            }
    if test_type == "normality_test":
        return {"value": f"偏度 = {_display_value(details.get('skewness'))}; 峰度 = {_display_value(details.get('kurtosis'))}", "interpretation": "分布形态诊断"}
    if test_type == "levene_test":
        return {"value": "方差齐性可接受" if details.get("equal_var") else "方差不齐", "interpretation": "影响后续均值比较方法选择"}
    return None


def build_group_stats_table(result: dict) -> dict | None:
    """Extract group descriptive statistics from result."""
    details = result.get("details") or {}
    confusion = details.get("confusion_matrix")
    if confusion:
        cols = ["Actual \\ Predicted"] + [str(c) for c in confusion.get("cols", [])]
        rows = []
        for row_name, row_values in zip(confusion.get("rows", []), confusion.get("data", [])):
            row = {"Actual \\ Predicted": str(row_name)}
            for col_name, value in zip(confusion.get("cols", []), row_values):
                row[str(col_name)] = int(value)
            rows.append(row)
        return {"columns": cols, "rows": rows, "title": "判别分析混淆矩阵（训练集）"}

    desc = result.get("descriptive_stats")
    if not desc:
        return None

    group_stats = desc.get("group_stats")
    if not group_stats:
        return None

    cols = ["Group", "N", "Missing", "Mean", "SD", "Median", "Q1", "Q3", "Min", "Max", "Distribution / Top categories"]
    rows = []
    for g_name, g_stat in group_stats.items():
        if g_stat.get("type") == "continuous":
            rows.append({
                "Group": g_name,
                "N": g_stat.get("n", "—"),
                "Missing": g_stat.get("missing", "—"),
                "Mean": g_stat.get("mean", "—"),
                "SD": g_stat.get("std", "—"),
                "Median": g_stat.get("median", "—"),
                "Q1": g_stat.get("q1", "—"),
                "Q3": g_stat.get("q3", "—"),
                "Min": g_stat.get("min", "—"),
                "Max": g_stat.get("max", "—"),
                "Distribution / Top categories": "近似正态" if g_stat.get("is_normal") else "偏态/未通过正态性",
            })
        else:
            # Categorical
            top_cats = g_stat.get("top_categories", [])
            cat_str = "; ".join([f"{c['name']}: {c['count']} ({c['pct']}%)" for c in top_cats[:5]])
            rows.append({
                "Group": g_name,
                "N": g_stat.get("n", "—"),
                "Missing": g_stat.get("missing", "—"),
                "Mean": "—",
                "SD": "—",
                "Median": "—",
                "Q1": "—",
                "Q3": "—",
                "Min": "—",
                "Max": "—",
                "Distribution / Top categories": cat_str,
            })

    return {"columns": cols, "rows": rows, "title": f"Descriptive Statistics by Group: {desc.get('variable', '')}"}


def build_post_hoc_table(result: dict) -> dict | None:
    """Extract post-hoc comparison results."""
    post_hoc = result.get("post_hoc")
    if not post_hoc:
        return None

    rows = []
    for ph in post_hoc:
        if "error" in ph:
            rows.append({"Comparison": ph.get("comparison", ""), "Result": ph["error"]})
        else:
            row = {
                "Comparison": ph.get("comparison", ""),
                "Mean Diff": ph.get("mean_diff", "—"),
                "P value (adj)": format_p_value(ph.get("p_value_adj") or ph.get("p_value")),
                "Significant": "Yes" if ph.get("significant") else "No",
                "Method": ph.get("method", ""),
            }
            if ph.get("ci_lower") is not None:
                row["95% CI"] = f"[{ph['ci_lower']}, {ph['ci_upper']}]"
            rows.append(row)

    # Determine columns from first valid row
    cols = list(rows[0].keys()) if rows else ["Comparison", "Result"]
    return {"columns": cols, "rows": rows, "title": f"Post-hoc Comparisons ({post_hoc[0].get('method', '') if post_hoc else ''})"}


def build_descriptive_summary(df: pd.DataFrame, variables: list[str] | None = None) -> dict:
    """Build a comprehensive descriptive statistics summary table."""
    if variables is None:
        variables = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not variables:
        variables = [c for c in df.columns]

    rows = []
    for var in variables:
        desc = calc_descriptive(pd.DataFrame({var: df[var]}), var)
        if desc["type"] == "continuous":
            rows.append({
                "Variable": var,
                "N": desc["n"],
                "Missing": desc["missing"],
                "Mean": desc["mean"],
                "SD": desc["std"],
                "Median": desc["median"],
                "Q1": desc["q1"],
                "Q3": desc["q3"],
                "Min": desc["min"],
                "Max": desc["max"],
                "Skewness": desc["skewness"],
                "Normal": "Yes" if desc["is_normal"] else "No",
            })
        else:
            top_cats = desc.get("top_categories", [])
            cat_str = "; ".join([f"{c['name']}: {c['count']} ({c['pct']}%)" for c in top_cats[:5]])
            rows.append({
                "Variable": var,
                "N": desc["n"],
                "Missing": desc["missing"],
                "Mean": cat_str,
                "SD": "—",
                "Median": "—",
                "Q1": "—",
                "Q3": "—",
                "Min": "—",
                "Max": "—",
                "Skewness": "—",
                "Normal": "—",
            })

    cols = ["Variable", "N", "Missing", "Mean", "SD", "Median", "Q1", "Q3", "Min", "Max", "Skewness", "Normal"]
    return {"columns": cols, "rows": rows, "title": "Descriptive Statistics Summary"}


# ═══ Three-line Tables (Publication Standard) ═══════════════════

def build_baseline_table(
    df: pd.DataFrame,
    group_var: str,
    variables: list[str] | None = None,
    decimal_places: int = 2,
    p_digits: int = 3,
) -> dict:
    """Generate standard Table 1 (baseline characteristics by group)."""
    if variables is None:
        variables = [c for c in df.columns if c != group_var]

    groups = sorted(df[group_var].dropna().unique().tolist())
    rows = []

    for var in variables:
        if var == group_var:
            continue
        series = df[var].dropna()
        is_num = pd.api.types.is_numeric_dtype(series)

        row = {"Variable": var, "Type": "continuous" if is_num else "categorical"}
        total_n = len(series)

        if is_num:
            is_normal = _test_normality(series)
            if is_normal:
                row["Total"] = f"{series.mean():.{decimal_places}f} ± {series.std():.{decimal_places}f}"
            else:
                q1, med, q3 = series.quantile([0.25, 0.5, 0.75])
                row["Total"] = f"{med:.{decimal_places}f} ({q1:.{decimal_places}f}, {q3:.{decimal_places}f})"

            for g in groups:
                g_series = df.loc[df[group_var] == g, var].dropna()
                if len(g_series) > 0:
                    if is_normal:
                        row[str(g)] = f"{g_series.mean():.{decimal_places}f} ± {g_series.std():.{decimal_places}f}"
                    else:
                        q1g, medg, q3g = g_series.quantile([0.25, 0.5, 0.75])
                        row[str(g)] = f"{medg:.{decimal_places}f} ({q1g:.{decimal_places}f}, {q3g:.{decimal_places}f})"
                else:
                    row[str(g)] = "—"
        else:
            counts = series.value_counts()
            pcts = series.value_counts(normalize=True) * 100
            top_cats = counts.head(10)
            parts = []
            for cat, cnt in top_cats.items():
                pct = pcts.get(cat, 0)
                parts.append(f"{cat}: {cnt} ({pct:.1f}%)")
            row["Total"] = "; ".join(parts)

            for g in groups:
                g_series = df.loc[df[group_var] == g, var].dropna()
                if len(g_series) > 0:
                    g_counts = g_series.value_counts()
                    g_pcts = g_series.value_counts(normalize=True) * 100
                    g_parts = []
                    for cat, cnt in g_counts.head(10).items():
                        g_parts.append(f"{cat}: {cnt} ({g_pcts.get(cat, 0):.1f}%)")
                    row[str(g)] = "; ".join(g_parts)
                else:
                    row[str(g)] = "—"

        from app.services.stats_service import calc_group_comparison
        comp = calc_group_comparison(df, var, group_var)
        row["P value"] = format_p_value(comp["p_value"], p_digits)
        row["Method"] = comp["method"]
        rows.append(row)

    cols = ["Variable", "Type", "Total"] + [str(g) for g in groups] + ["P value", "Method"]
    return {"columns": cols, "rows": rows, "groups": groups, "group_var": group_var, "n_total": len(df)}


def build_descriptive_table(
    df: pd.DataFrame,
    variables: list[str] | None = None,
    decimal_places: int = 2,
) -> dict:
    """Generate overall descriptive statistics table."""
    if variables is None:
        variables = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    rows = []
    for var in variables:
        series = df[var].dropna()
        if not pd.api.types.is_numeric_dtype(series):
            continue
        is_normal = _test_normality(series)
        rows.append({
            "Variable": var,
            "N": len(series),
            "Missing": int(df[var].isnull().sum()),
            "Mean": round(float(series.mean()), decimal_places),
            "SD": round(float(series.std()), decimal_places),
            "Median": round(float(series.median()), decimal_places),
            "Q1": round(float(series.quantile(0.25)), decimal_places),
            "Q3": round(float(series.quantile(0.75)), decimal_places),
            "Min": round(float(series.min()), decimal_places),
            "Max": round(float(series.max()), decimal_places),
            "Distribution": "Normal" if is_normal else "Skewed",
            "Skewness": round(float(series.skew()), decimal_places),
        })

    cols = ["Variable", "N", "Missing", "Mean", "SD", "Median", "Q1", "Q3", "Min", "Max", "Distribution", "Skewness"]
    return {"columns": cols, "rows": rows, "n_total": len(df)}


def build_missing_table(df: pd.DataFrame) -> dict:
    """Generate missing value statistics table."""
    rows = []
    for col in df.columns:
        missing = int(df[col].isnull().sum())
        complete = len(df) - missing
        rows.append({
            "Variable": col,
            "Complete (n)": complete,
            "Missing (n)": missing,
            "Complete (%)": round(complete / len(df) * 100, 2),
            "Missing (%)": round(missing / len(df) * 100, 2),
            "Type": str(df[col].dtype),
        })
    rows.sort(key=lambda r: r["Missing (n)"], reverse=True)
    cols = ["Variable", "Complete (n)", "Missing (n)", "Complete (%)", "Missing (%)", "Type"]
    return {"columns": cols, "rows": rows, "n_total": len(df)}
