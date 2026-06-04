from __future__ import annotations

from typing import Any

from app.services.stats_service import format_p_value


def build_result_discussion(result: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a structured, clinically oriented interpretation for a test result."""
    context = context or {}
    if not result or result.get("error"):
        message = result.get("error", "分析未能完成。") if result else "分析未能完成。"
        return {
            "headline": "分析未完成",
            "sections": [
                {
                    "title": "需要处理的问题",
                    "items": [message, "请检查变量类型、分组数、缺失值和样本量后重新运行分析。"],
                }
            ],
            "plain_text": message,
        }

    test_type = result.get("test_type", "")
    p_value = result.get("p_value")
    p_text = format_p_value(p_value)
    significant = bool(result.get("significant"))
    chart_data = result.get("chart_data") or {}
    primary = context.get("var") or context.get("primary") or _first_nonempty(
        result.get("details", {}).get("variable_1"),
        chart_data.get("y_label"),
        chart_data.get("y_var"),
        "目标变量",
    )
    group_var = context.get("group_var") or chart_data.get("x_label")
    method = result.get("method") or result.get("test_name") or "统计检验"

    headline = _headline(result, p_text, significant)
    if p_value is None:
        statistical_items = [
            f"本次使用 {method}，核心指标为 {_format_value(result.get('statistic'))}。",
            "该方法当前输出模型性能或诊断指标，不提供传统显著性 P 值。",
        ]
    else:
        statistical_items = [
            f"本次使用 {method}，统计量为 {_format_value(result.get('statistic'))}，P 值为 {p_text}。",
            "结果达到预设的 0.05 显著性水平。" if significant else "结果未达到预设的 0.05 显著性水平。",
        ]

    effect_items = _effect_items(test_type, result, primary, group_var)
    method_items = _method_items(test_type, result)
    report_items = _report_items(test_type, result, primary, group_var, significant)

    if result.get("note"):
        method_items.append(str(result["note"]))

    sections = [
        {"title": "统计结论", "items": statistical_items},
        {"title": "效应与临床含义", "items": effect_items},
        {"title": "方法学检查", "items": method_items},
        {"title": "报告建议", "items": report_items},
    ]

    plain_text = "\n".join(
        [headline]
        + [f"{section['title']}：" + "；".join(section["items"]) for section in sections]
    )
    return {"headline": headline, "sections": sections, "plain_text": plain_text}


def _headline(result: dict[str, Any], p_text: str, significant: bool) -> str:
    test_name = result.get("test_name") or "统计检验"
    if result.get("p_value") is None:
        return f"{test_name} 已完成，主要结果为 {result.get('summary', '模型性能指标')}。"
    if significant:
        return f"{test_name} 提示差异/关联具有统计学意义（P = {p_text}）。"
    return f"{test_name} 未发现达到 0.05 水平的统计学差异/关联（P = {p_text}）。"


def _effect_items(test_type: str, result: dict[str, Any], primary: str, group_var: str | None) -> list[str]:
    details = result.get("details") or {}
    items: list[str] = []

    if test_type == "t_test_independent":
        g1, g2 = details.get("group_1", {}), details.get("group_2", {})
        items.append(
            f"{g1.get('name', '组1')} 均值为 {_format_value(g1.get('mean'))}，"
            f"{g2.get('name', '组2')} 均值为 {_format_value(g2.get('mean'))}，"
            f"均值差为 {_format_value(details.get('mean_diff'))}。"
        )
        items.append(_direction_text(details.get("mean_diff"), primary))
    elif test_type in {"t_test_paired", "wilcoxon_signed_rank"}:
        items.append(
            f"共纳入 {_format_value(details.get('n_pairs'))} 对完整配对观测，"
            f"配对差值为 {_format_value(details.get('mean_diff', details.get('median_diff')))}。"
        )
        items.append("配对设计的解释重点应放在个体内变化，而不是两组独立样本差异。")
    elif test_type == "one_sample_t_test":
        items.append(
            f"样本均值为 {_format_value(details.get('mean'))}，参考均值为 {_format_value(details.get('hypothesized_mean'))}，"
            f"均值差为 {_format_value(details.get('mean_diff'))}。"
        )
        if details.get("ci_95"):
            items.append(f"均值差 95%CI 为 [{_format_value(details['ci_95'][0])}, {_format_value(details['ci_95'][1])}]。")
    elif test_type == "normality_test":
        items.append(
            f"样本量为 {_format_value(details.get('n'))}，偏度为 {_format_value(details.get('skewness'))}，"
            f"峰度为 {_format_value(details.get('kurtosis'))}。"
        )
        items.append("P < 0.05 时更支持分布偏离正态；样本量较大时轻微偏离也可能显著。")
    elif test_type == "levene_test":
        items.append(
            f"共比较 {_format_value(details.get('n_groups'))} 组，"
            f"总样本量为 {_format_value(details.get('total_n'))}。"
        )
        items.append("若方差不齐，后续均值比较优先考虑 Welch t 检验、Welch ANOVA 或稳健/非参数方法。")
    elif test_type == "anova":
        items.append(
            f"共比较 {_format_value(details.get('n_groups'))} 组，"
            f"总样本量为 {_format_value(details.get('total_n'))}。"
        )
        if result.get("post_hoc"):
            sig_pairs = [p for p in result["post_hoc"] if p.get("significant")]
            items.append(f"事后比较中有 {len(sig_pairs)} 个两两比较达到显著水平。")
        else:
            items.append("若总体检验显著，建议进一步查看事后两两比较定位差异来源。")
    elif test_type in {"mann_whitney", "kruskal_wallis"}:
        if details.get("group_stats"):
            items.append("各组以中位数和四分位数描述，更适合偏态或等级资料。")
        else:
            g1, g2 = details.get("group_1", {}), details.get("group_2", {})
            items.append(
                f"{g1.get('name', '组1')} 中位数为 {_format_value(g1.get('median'))}，"
                f"{g2.get('name', '组2')} 中位数为 {_format_value(g2.get('median'))}。"
            )
    elif test_type in {"chi_square", "fisher_exact", "mcnemar"}:
        if details.get("odds_ratio") is not None:
            items.append(f"优势比 OR = {_format_value(details.get('odds_ratio'))}，可作为效应方向和强度的补充。")
        elif details.get("discordant_pairs"):
            dp = details["discordant_pairs"]
            items.append(f"不一致配对数 b = {dp.get('b')}，c = {dp.get('c')}，检验主要由这两类转换贡献。")
        else:
            items.append("分类资料结果应同时查看列联表中的实际频数和比例，避免只根据 P 值下结论。")
    elif test_type in {"pearson_correlation", "spearman_correlation"}:
        r = result.get("statistic")
        items.append(f"相关系数为 {_format_value(r)}，可解释为 {_correlation_strength(r)}。")
        if details.get("r_squared") is not None:
            items.append(f"R² = {_format_value(details.get('r_squared'))}，表示线性解释度的粗略比例。")
    elif test_type in {"linear_regression", "logistic_regression", "ancova"}:
        items.append("模型结果用于估计变量关系，建议结合系数方向、效应量、置信区间和临床先验解释。")
        if details.get("coefficients"):
            items.append("主要系数：" + "；".join(f"{k}={v}" for k, v in list(details["coefficients"].items())[:6]))
        if details.get("odds_ratios"):
            items.append("主要 OR：" + "；".join(f"{k}={v}" for k, v in list(details["odds_ratios"].items())[:6]))
    elif test_type in {"discriminant_analysis", "quadratic_discriminant_analysis"}:
        items.append(
            f"训练准确率为 {_format_value(details.get('accuracy'))}，"
            f"交叉验证准确率为 {_format_value(details.get('cv_accuracy'))}，"
            f"类别基线准确率为 {_format_value(details.get('baseline_accuracy'))}。"
        )
        if details.get("coefficients"):
            items.append("主要判别载荷：" + "；".join(f"{k}={v}" for k, v in list(details["coefficients"].items())[:6]))
        items.append("判别得分图可用于查看类别之间是否形成清晰分离，以及是否存在重叠样本或异常样本。")
    elif test_type == "log_rank":
        items.append("生存资料需结合 Kaplan-Meier 曲线形态、中位生存时间和风险表综合解释。")
    else:
        items.append(f"请结合 {primary} 的描述统计、分组分布和研究设计判断统计差异是否具有实际意义。")

    return [item for item in items if item]


def _method_items(test_type: str, result: dict[str, Any]) -> list[str]:
    details = result.get("details") or {}
    items: list[str] = []

    if test_type in {"t_test_independent", "anova"}:
        if test_type == "t_test_independent":
            normals = [details.get("group_1", {}).get("normal"), details.get("group_2", {}).get("normal")]
            items.append("正态性检查：" + ("各组基本通过。" if all(normals) else "至少一组未通过或样本量不足，建议同步参考非参数检验。"))
        if details.get("levene_test"):
            lev = details["levene_test"]
            items.append(
                f"Levene 方差齐性检验 P = {_format_value(lev.get('p_value'))}，"
                + ("方差齐性可接受。" if lev.get("equal_var") else "提示方差不齐，需谨慎解释。")
            )
    elif test_type in {"chi_square", "fisher_exact"}:
        if details.get("min_expected") is not None:
            items.append(
                f"最小期望频数为 {_format_value(details.get('min_expected'))}，"
                f"期望频数小于 5 的单元格约 {details.get('pct_cells_lt5', '—')}%。"
            )
        items.append("当样本量较小或期望频数偏低时，Fisher 精确检验通常比普通卡方检验更稳健。")
    elif test_type in {"mann_whitney", "kruskal_wallis", "wilcoxon_signed_rank", "friedman"}:
        items.append("非参数检验对正态性要求较低，但检验的是秩分布差异，不能简单等同于均值差异。")
    elif test_type == "one_sample_t_test":
        items.append("单样本 t 检验要求观测彼此独立，且均值差的抽样分布近似正态。")
    elif test_type == "normality_test":
        items.append("正态性检验应结合直方图、Q-Q 图、偏度/峰度和研究场景判断，不能只依赖 P 值。")
    elif test_type == "levene_test":
        items.append("本实现采用中位数中心的 Levene/Brown-Forsythe 检验，对偏态资料比均值中心版本更稳健。")
    elif test_type in {"linear_regression", "logistic_regression", "ancova"}:
        items.append("建议进一步检查模型残差、共线性、异常值和样本量/事件数是否满足建模要求。")
    elif test_type in {"discriminant_analysis", "quadratic_discriminant_analysis"}:
        items.append("判别分析假定预测变量能稳定区分类别；LDA 还隐含各类别协方差结构相近的前提。")
        items.append("当前准确率来自训练集和交叉验证，正式报告应优先使用独立验证集或外部验证集。")
    else:
        items.append("请确认变量编码、缺失值处理和研究设计与所选统计方法一致。")

    return items


def _report_items(
    test_type: str,
    result: dict[str, Any],
    primary: str,
    group_var: str | None,
    significant: bool,
) -> list[str]:
    p_text = format_p_value(result.get("p_value"))
    stat = _format_value(result.get("statistic"))
    first_item = (
        f"报告时建议写明检验方法、模型指标、样本量，并同时呈现 {primary} 的描述统计。"
        if result.get("p_value") is None
        else f"报告时建议写明检验方法、统计量、P 值、样本量，并同时呈现 {primary} 的描述统计。"
    )
    items = [first_item]
    if result.get("p_value") is None:
        items.append(f"可写作：{result.get('test_name', '统计检验')}，核心指标 = {stat}；{result.get('summary', '')}")
    else:
        items.append(f"可写作：{result.get('test_name', '统计检验')}，统计量 = {stat}，P = {p_text}。")
    if group_var:
        items.append(f"表格中应保留按 {group_var} 分组的 N、中心趋势、离散程度和缺失情况。")
    if not significant:
        items.append("未显著并不等于两组完全相同，应结合置信区间、样本量和最小临床重要差异讨论把握度。")
    if test_type in {"anova", "kruskal_wallis"}:
        items.append("多组比较时，正文应区分总体检验结果和事后比较结果，避免把总体 P 值当作任意两组差异。")
    if test_type in {"discriminant_analysis", "quadratic_discriminant_analysis"}:
        items.append("判别分析报告建议同时列出类别样本量、预测变量、准确率/交叉验证准确率、混淆矩阵和判别得分图。")
    if test_type in {"normality_test", "levene_test"}:
        items.append("该检验更适合作为方法选择依据，建议在正式结果中与主要分析方法一起呈现。")
    return items


def _direction_text(diff: Any, variable: str) -> str:
    try:
        value = float(diff)
    except (TypeError, ValueError):
        return f"{variable} 的效应方向需结合分组编码解释。"
    if value > 0:
        return f"按当前分组顺序，第一组 {variable} 平均水平更高。"
    if value < 0:
        return f"按当前分组顺序，第二组 {variable} 平均水平更高。"
    return f"{variable} 的两组均值几乎相同。"


def _correlation_strength(value: Any) -> str:
    try:
        r = abs(float(value))
    except (TypeError, ValueError):
        return "相关强度无法判断"
    if r < 0.1:
        return "极弱相关"
    if r < 0.3:
        return "弱相关"
    if r < 0.5:
        return "中等相关"
    if r < 0.7:
        return "较强相关"
    return "强相关"


def _first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _format_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)
