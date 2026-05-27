"""Smoke test for Clinical Statistics Platform core services."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from app.services.sample_service import EXAMPLE_MAKERS
from app.services.variable_service import classify_variables, summarize_dataset
from app.services.stats_service import (
    t_test_independent,
    t_test_paired,
    one_sample_t_test,
    normality_test,
    levene_variance_test,
    anova_oneway,
    chi_square_test,
    fisher_exact_test,
    mann_whitney_u_test,
    kruskal_wallis_test,
    wilcoxon_signed_rank_test,
    mcnemar_test,
    discriminant_analysis,
)
from app.services.table_service import (
    build_result_table,
    build_group_stats_table,
    build_descriptive_summary,
)
from app.services.io_service import get_example_datasets


def test_sample_generation():
    """All example datasets should generate without errors."""
    for name, fn in EXAMPLE_MAKERS.items():
        df = fn()
        for col in df.columns:
            if isinstance(df[col].dtype, pd.StringDtype) or str(df[col].dtype) == "string":
                df[col] = df[col].astype(object)
        assert len(df) > 0, f"{name}: empty dataframe"
        assert len(df.columns) > 0, f"{name}: no columns"
    print(f"  [PASS] Sample generation ({len(EXAMPLE_MAKERS)} datasets)")


def test_variable_classification():
    """Variable classification should return valid results."""
    df = pd.read_csv(ROOT / "data" / "examples" / "general_clinical_example.csv")
    types = classify_variables(df)
    summary = summarize_dataset(df, types)
    assert summary["sample_size"] > 0
    assert summary["variable_count"] > 0
    assert "continuous" in types
    assert "categorical" in types
    print("  [PASS] Variable classification")


def test_t_test_independent():
    """Independent t-test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "t_test_independent_example.csv")
    result = t_test_independent(df, "sbp_reduction", "group")
    assert result["test_type"] == "t_test_independent"
    assert result["statistic"] is not None
    assert result["p_value"] is not None
    assert "significant" in result
    print("  [PASS] Independent t-test")


def test_t_test_paired():
    """Paired t-test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "t_test_paired_example.csv")
    result = t_test_paired(df, "sbp_before", "sbp_after")
    assert result["test_type"] == "t_test_paired"
    assert result["statistic"] is not None
    assert result["p_value"] is not None
    print("  [PASS] Paired t-test")


def test_basic_diagnostics():
    """Basic one-sample and assumption diagnostics should work."""
    one_sample_df = EXAMPLE_MAKERS["one_sample_t_test_example"]()
    one_sample = one_sample_t_test(one_sample_df, "ldl_change")
    assert one_sample["test_type"] == "one_sample_t_test"
    assert one_sample["p_value"] is not None

    normal_df = EXAMPLE_MAKERS["normality_test_example"]()
    normality = normality_test(normal_df, "biomarker")
    assert normality["test_type"] == "normality_test"
    assert normality["statistic"] is not None

    levene_df = EXAMPLE_MAKERS["levene_test_example"]()
    levene = levene_variance_test(levene_df, "response_value", "group")
    assert levene["test_type"] == "levene_test"
    assert levene["p_value"] is not None
    print("  [PASS] Basic diagnostics")


def test_anova():
    """One-way ANOVA should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "anova_example.csv")
    result = anova_oneway(df, "efficacy_score", "treatment", "tukey")
    assert result["test_type"] == "anova"
    assert result["statistic"] is not None
    assert result["p_value"] is not None
    assert "post_hoc" in result
    print("  [PASS] One-way ANOVA + Tukey post-hoc")


def test_chi_square():
    """Chi-square test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "chi_square_example.csv")
    result = chi_square_test(df, "outcome", "treatment")
    assert result["test_type"] == "chi_square"
    assert result["statistic"] is not None
    print("  [PASS] Chi-square test")


def test_fisher_exact():
    """Fisher's exact test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "fisher_exact_example.csv")
    result = fisher_exact_test(df, "outcome", "group")
    assert result["test_type"] == "fisher_exact"
    print("  [PASS] Fisher's exact test")


def test_mann_whitney():
    """Mann-Whitney U test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "mann_whitney_example.csv")
    result = mann_whitney_u_test(df, "crp_level", "group")
    assert result["test_type"] == "mann_whitney"
    assert result["p_value"] is not None
    print("  [PASS] Mann-Whitney U test")


def test_kruskal_wallis():
    """Kruskal-Wallis test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "kruskal_wallis_example.csv")
    result = kruskal_wallis_test(df, "biomarker_level", "disease_stage", "bonferroni")
    assert result["test_type"] == "kruskal_wallis"
    assert result["statistic"] is not None
    print("  [PASS] Kruskal-Wallis test + Bonferroni post-hoc")


def test_wilcoxon():
    """Wilcoxon signed-rank test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "wilcoxon_signed_rank_example.csv")
    result = wilcoxon_signed_rank_test(df, "pain_before", "pain_after")
    assert result["test_type"] == "wilcoxon_signed_rank"
    assert result["p_value"] is not None
    print("  [PASS] Wilcoxon signed-rank test")


def test_mcnemar():
    """McNemar test should work."""
    df = pd.read_csv(ROOT / "data" / "examples" / "mcnemar_example.csv")
    result = mcnemar_test(df, "diagnosis_standard", "diagnosis_new")
    assert result["test_type"] == "mcnemar"
    print("  [PASS] McNemar test")


def test_discriminant_analysis():
    """LDA/QDA discriminant analysis should produce model metrics and chart data."""
    df = EXAMPLE_MAKERS["discriminant_analysis_example"]()
    predictors = ["age", "bmi", "sbp", "glucose", "cholesterol", "crp"]
    lda = discriminant_analysis(df, "diagnosis_group", predictors, method="lda")
    assert lda["test_type"] == "discriminant_analysis"
    assert lda["details"]["accuracy"] > lda["details"]["baseline_accuracy"]
    assert lda["chart_data"]["chart_type"] == "discriminant_scores"

    qda = discriminant_analysis(df, "diagnosis_group", predictors, method="qda")
    assert qda["test_type"] == "quadratic_discriminant_analysis"
    assert qda["details"]["accuracy"] > qda["details"]["baseline_accuracy"]
    print("  [PASS] Discriminant analysis")


def test_table_service():
    """Table generators should produce valid results."""
    df = pd.read_csv(ROOT / "data" / "examples" / "t_test_independent_example.csv")
    result = t_test_independent(df, "sbp_reduction", "group")
    result_table = build_result_table(result)
    assert len(result_table["rows"]) > 0
    assert len(result_table["columns"]) > 0

    group_table = build_group_stats_table(result)
    assert len(group_table["rows"]) > 0

    desc_table = build_descriptive_summary(df)
    assert len(desc_table["rows"]) > 0
    print("  [PASS] Table service")


def test_io_service():
    """Example dataset listing should work."""
    examples = get_example_datasets()
    assert len(examples) >= 10, f"Expected at least 10 examples, got {len(examples)}"
    print("  [PASS] IO service")


if __name__ == "__main__":
    print("Running smoke tests for Clinical Statistics Platform...")
    test_sample_generation()
    test_variable_classification()
    test_t_test_independent()
    test_t_test_paired()
    test_basic_diagnostics()
    test_anova()
    test_chi_square()
    test_fisher_exact()
    test_mann_whitney()
    test_kruskal_wallis()
    test_wilcoxon()
    test_mcnemar()
    test_discriminant_analysis()
    test_table_service()
    test_io_service()
    print("All smoke tests passed!")
