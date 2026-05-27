from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)


def make_t_test_independent_example() -> pd.DataFrame:
    """Two groups for independent t-test: Treatment vs Control with blood pressure reduction."""
    n = 100
    treatment = rng.normal(15.2, 6.5, n)
    control = rng.normal(8.1, 7.0, n)
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, 2 * n + 1)],
        "group": ["Treatment"] * n + ["Control"] * n,
        "sbp_reduction": np.round(np.concatenate([treatment, control]), 1),
        "age": np.round(np.concatenate([rng.normal(55, 10, n), rng.normal(57, 11, n)]), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], 2 * n),
    })
    return df


def make_t_test_paired_example() -> pd.DataFrame:
    """Paired t-test: before/after treatment measurements."""
    n = 60
    base = rng.normal(145, 15, n)
    reduction = rng.normal(12, 7, n)
    after = base - reduction
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "sbp_before": np.round(base, 1),
        "sbp_after": np.round(after, 1),
        "age": np.round(rng.normal(58, 11, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_one_sample_t_test_example() -> pd.DataFrame:
    """One-sample t-test: LDL-C reduction tested against a reference value of 0."""
    n = 90
    change = rng.normal(-0.42, 0.58, n)
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "ldl_change": np.round(change, 2),
        "age": np.round(rng.normal(57, 10, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
        "baseline_ldl": np.round(rng.normal(3.4, 0.7, n).clip(1.2, 6.5), 2),
    })
    return df


def make_normality_test_example() -> pd.DataFrame:
    """Normality test: a skewed biomarker distribution."""
    n = 160
    biomarker = rng.lognormal(mean=1.35, sigma=0.52, size=n)
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "biomarker": np.round(biomarker, 2),
        "age": np.round(rng.normal(60, 11, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
        "group": rng.choice(["Control", "Treatment"], n),
    })
    return df


def make_levene_test_example() -> pd.DataFrame:
    """Levene test: treatment groups with unequal variability."""
    groups = []
    values = []
    for group, mu, sd, n in [
        ("Control", 12.0, 2.0, 55),
        ("Low dose", 13.1, 3.7, 55),
        ("High dose", 14.0, 6.2, 55),
    ]:
        groups.extend([group] * n)
        values.extend(rng.normal(mu, sd, n))
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, len(groups) + 1)],
        "group": groups,
        "response_value": np.round(values, 2),
        "age": np.round(rng.normal(56, 12, len(groups)), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], len(groups)),
    })
    return df


def make_anova_example() -> pd.DataFrame:
    """One-way ANOVA: 4 treatment groups with different efficacy."""
    n_per = 50
    groups = []
    values = []
    # Drug A: mean ~14, Drug B: mean ~18, Drug C: mean ~10, Placebo: mean ~6
    for drug, mu, sd in [("Drug A", 14.0, 5.5), ("Drug B", 18.5, 5.0), ("Drug C", 10.2, 6.0), ("Placebo", 5.8, 5.8)]:
        groups.extend([drug] * n_per)
        values.extend(np.round(rng.normal(mu, sd, n_per), 1))
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, 4 * n_per + 1)],
        "treatment": groups,
        "efficacy_score": values,
        "age": np.round(rng.normal(56, 12, 4 * n_per), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], 4 * n_per),
        "bmi": np.round(rng.normal(24.5, 3.5, 4 * n_per).clip(16, 40), 1),
    })
    return df


def make_chi_square_example() -> pd.DataFrame:
    """Chi-square test: treatment outcome by group."""
    n = 300
    treatment = rng.choice(["Drug X", "Drug Y", "Standard"], n, p=[0.35, 0.35, 0.3])
    # Outcome depends on treatment
    outcome = []
    for t in treatment:
        if t == "Drug X":
            outcome.append(rng.choice(["Effective", "Ineffective"], p=[0.72, 0.28]))
        elif t == "Drug Y":
            outcome.append(rng.choice(["Effective", "Ineffective"], p=[0.55, 0.45]))
        else:
            outcome.append(rng.choice(["Effective", "Ineffective"], p=[0.40, 0.60]))
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "treatment": treatment,
        "outcome": outcome,
        "age": np.round(rng.normal(55, 12, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_fisher_exact_example() -> pd.DataFrame:
    """Fisher exact test: small sample 2x2."""
    n = 40
    group = ["Treatment"] * 20 + ["Control"] * 20
    # Rare event: Treatment has higher success rate
    outcome = (
        rng.choice(["Success", "Failure"], 20, p=[0.75, 0.25]).tolist() +
        rng.choice(["Success", "Failure"], 20, p=[0.35, 0.65]).tolist()
    )
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "group": group,
        "outcome": outcome,
        "age": np.round(rng.normal(52, 13, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_mann_whitney_example() -> pd.DataFrame:
    """Mann-Whitney U test: non-normal data comparing two groups."""
    n = 120
    # Skewed distributions
    group_a = np.round(rng.lognormal(2.0, 0.5, n // 2), 1)
    group_b = np.round(rng.lognormal(2.5, 0.6, n // 2), 1)
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "group": ["Group A"] * (n // 2) + ["Group B"] * (n // 2),
        "crp_level": np.concatenate([group_a, group_b]),
        "age": np.round(rng.normal(60, 11, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_kruskal_wallis_example() -> pd.DataFrame:
    """Kruskal-Wallis test: 3+ groups non-normal data."""
    n_per = 45
    groups = []
    values = []
    for stage, loc, scale in [("Stage I", 1.5, 0.5), ("Stage II", 2.0, 0.6), ("Stage III", 2.8, 0.7), ("Stage IV", 3.5, 0.8)]:
        groups.extend([stage] * n_per)
        values.extend(np.round(rng.lognormal(loc, scale, n_per), 1))
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, 4 * n_per + 1)],
        "disease_stage": groups,
        "biomarker_level": values,
        "age": np.round(rng.normal(59, 12, 4 * n_per), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], 4 * n_per),
    })
    return df


def make_wilcoxon_signed_rank_example() -> pd.DataFrame:
    """Wilcoxon signed-rank test: paired non-normal data, pain scores before/after."""
    n = 50
    before = np.round(rng.uniform(3, 9, n), 1)
    # After treatment, pain generally decreases but not always
    change = np.round(rng.uniform(-1, 5, n), 1)
    after = np.round(before - change, 1)
    after = np.clip(after, 0, 10)
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "pain_before": before,
        "pain_after": after,
        "age": np.round(rng.normal(50, 14, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_mcnemar_example() -> pd.DataFrame:
    """McNemar test: paired categorical data, diagnostic test before/after."""
    n = 120
    # Before: standard diagnosis, After: new method diagnosis
    before_disease = rng.choice(["Positive", "Negative"], n, p=[0.45, 0.55])
    after_disease = []
    for b in before_disease:
        if b == "Positive":
            after_disease.append(rng.choice(["Positive", "Negative"], p=[0.85, 0.15]))
        else:
            after_disease.append(rng.choice(["Positive", "Negative"], p=[0.12, 0.88]))
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "diagnosis_standard": before_disease,
        "diagnosis_new": after_disease,
        "age": np.round(rng.normal(55, 13, n), 0).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
    })
    return df


def make_general_clinical_example() -> pd.DataFrame:
    """Comprehensive clinical dataset with mixed variable types."""
    n = 400
    df = pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "age": np.round(rng.normal(58, 12, n)).clip(20, 90).astype(int),
        "sex": rng.choice(["Male", "Female"], n, p=[0.48, 0.52]),
        "bmi": np.round(rng.normal(24.5, 3.8, n).clip(15, 42), 1),
        "sbp": np.round(rng.normal(128, 16, n).clip(85, 190), 0).astype(int),
        "dbp": np.round(rng.normal(78, 10, n).clip(50, 120), 0).astype(int),
        "glucose": np.round(rng.normal(5.6, 1.2, n).clip(3.0, 15.0), 2),
        "cholesterol": np.round(rng.normal(5.1, 1.1, n).clip(2.5, 9.0), 2),
        "crp": np.round(rng.lognormal(0.5, 0.8, n).clip(0.1, 50), 2),
        "group": rng.choice(["Control", "Treatment A", "Treatment B"], n),
        "outcome": rng.choice(["Improved", "Stable", "Worsened"], n, p=[0.35, 0.45, 0.20]),
        "education": rng.choice(["Primary", "Secondary", "Tertiary"], n, p=[0.3, 0.45, 0.25]),
        "smoking": rng.choice(["Never", "Former", "Current"], n, p=[0.5, 0.25, 0.25]),
    })
    # Add some missing values
    for col, rate in [("bmi", 0.05), ("glucose", 0.08), ("crp", 0.10)]:
        n_missing = max(1, int(n * rate))
        missing_idx = rng.choice(df.index.to_numpy(), size=n_missing, replace=False)
        df.loc[missing_idx, col] = np.nan
    return df


def make_friedman_example() -> pd.DataFrame:
    """Friedman test: repeated measures with non-normal data across 4 time points."""
    n = 30
    records = []
    for i in range(1, n + 1):
        base = rng.uniform(2, 7)
        trend = rng.uniform(-0.5, 0.2)
        for t, tp in enumerate(["T0_Baseline", "T1_Week4", "T2_Week8", "T3_Week12"]):
            val = base + trend * t + rng.normal(0, 0.8)
            records.append({
                "subject_id": f"S{str(i).zfill(3)}",
                "timepoint": tp,
                "pain_score": round(max(0, min(10, val)), 1),
                "age": int(np.clip(rng.normal(50, 12), 25, 80)),
                "sex": rng.choice(["Male", "Female"], 1)[0],
            })
    return pd.DataFrame(records)


def make_repeated_measures_example() -> pd.DataFrame:
    """Repeated measures ANOVA: drug efficacy across 5 time points."""
    n = 40
    records = []
    for i in range(1, n + 1):
        base = rng.normal(140, 12)
        group = rng.choice(["Drug", "Placebo"], 1)[0]
        effect = -2.5 if group == "Drug" else -0.5
        for t_idx, tp in enumerate(["Week0", "Week2", "Week4", "Week8", "Week12"]):
            noise = rng.normal(0, 5)
            val = base + effect * t_idx + noise
            records.append({
                "subject_id": f"S{str(i).zfill(3)}",
                "time": tp,
                "sbp": round(val, 1),
                "group": group,
                "age": int(np.clip(rng.normal(55, 10), 30, 78)),
                "sex": rng.choice(["Male", "Female"], 1)[0],
            })
    return pd.DataFrame(records)


def make_correlation_example() -> pd.DataFrame:
    """Pearson/Spearman correlation: clinical biomarkers with relationships."""
    n = 150
    age = rng.normal(55, 12, n).clip(25, 85)
    bmi = 18 + 0.12 * age + rng.normal(0, 3, n)
    sbp = 90 + 0.6 * age + 0.4 * bmi + rng.normal(0, 8, n)
    glucose = 4.0 + 0.02 * age + 0.06 * bmi + rng.normal(0, 0.7, n)
    cholesterol = 3.5 + 0.01 * age + 0.05 * bmi + rng.normal(0, 0.7, n)
    crp = np.exp(0.02 * bmi + 0.01 * age + rng.normal(-1, 0.5, n))
    return pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "age": np.round(age, 0).astype(int),
        "bmi": np.round(bmi.clip(16, 42), 1),
        "sbp": np.round(sbp.clip(85, 190), 0).astype(int),
        "glucose": np.round(glucose.clip(3, 12), 2),
        "cholesterol": np.round(cholesterol.clip(2.5, 8), 2),
        "crp": np.round(crp.clip(0.1, 40), 2),
        "sex": rng.choice(["Male", "Female"], n),
        "smoking": rng.choice(["Never", "Former", "Current"], n, p=[0.5, 0.25, 0.25]),
    })


def make_survival_example() -> pd.DataFrame:
    """Log-rank test: survival data for two treatment groups."""
    n = 200
    group = rng.choice(["Standard", "Experimental"], n)
    time = []
    event = []
    for g in group:
        if g == "Experimental":
            t = rng.exponential(42)
            e = 1 if rng.random() < 0.35 else 0
        else:
            t = rng.exponential(28)
            e = 1 if rng.random() < 0.55 else 0
        time.append(round(t, 1))
        event.append(e)
    return pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "survival_time": time,
        "event": event,
        "treatment": group,
        "age": np.round(rng.normal(58, 11, n)).clip(30, 85).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
        "stage": rng.choice(["I", "II", "III"], n, p=[0.3, 0.4, 0.3]),
    })


def make_logistic_regression_example() -> pd.DataFrame:
    """Logistic regression: binary outcome with multiple predictors."""
    n = 300
    age = rng.normal(58, 12, n).clip(25, 85)
    bmi = 18 + 0.12 * age + rng.normal(0, 3, n)
    sbp = 90 + 0.6 * age + 0.4 * bmi + rng.normal(0, 8, n)
    glucose = 4.0 + 0.02 * age + 0.06 * bmi + rng.normal(0, 0.7, n)
    cholesterol = 3.5 + 0.01 * age + 0.05 * bmi + rng.normal(0, 0.7, n)
    logit = -10 + 0.03 * age + 0.05 * sbp + 0.2 * glucose + 0.15 * cholesterol
    prob = 1 / (1 + np.exp(-logit))
    outcome = (rng.random(n) < prob).astype(int)
    return pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "age": np.round(age, 0).astype(int),
        "bmi": np.round(bmi.clip(16, 42), 1),
        "sbp": np.round(sbp.clip(85, 190), 0).astype(int),
        "glucose": np.round(glucose.clip(3, 12), 2),
        "cholesterol": np.round(cholesterol.clip(2.5, 8), 2),
        "outcome": outcome,
        "sex": rng.choice(["Male", "Female"], n),
    })


def make_linear_regression_example() -> pd.DataFrame:
    """Linear regression: continuous outcome with multiple predictors."""
    n = 200
    age = rng.normal(55, 12, n).clip(25, 85)
    bmi = 18 + 0.12 * age + rng.normal(0, 3, n)
    sbp = 90 + 0.6 * age + 0.4 * bmi + rng.normal(0, 8, n)
    glucose = 4.0 + 0.02 * age + 0.06 * bmi + rng.normal(0, 0.7, n)
    cholesterol = 3.5 + 0.01 * age + 0.05 * bmi + rng.normal(0, 0.7, n)
    return pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "age": np.round(age, 0).astype(int),
        "bmi": np.round(bmi.clip(16, 42), 1),
        "sbp": np.round(sbp.clip(85, 190), 0).astype(int),
        "glucose": np.round(glucose.clip(3, 12), 2),
        "cholesterol": np.round(cholesterol.clip(2.5, 8), 2),
        "sex": rng.choice(["Male", "Female"], n),
        "group": rng.choice(["Control", "Treatment"], n),
    })


def make_ancova_example() -> pd.DataFrame:
    """ANCOVA: treatment effect adjusted for baseline."""
    n = 150
    group = rng.choice(["Drug A", "Drug B", "Placebo"], n)
    baseline = rng.normal(135, 15, n).clip(100, 180)
    effect = {"Drug A": -12, "Drug B": -8, "Placebo": -2}
    followup = []
    for g, bl in zip(group, baseline):
        fu = bl + effect[g] + rng.normal(0, 6)
        followup.append(round(fu, 1))
    return pd.DataFrame({
        "patient_id": [f"P{str(i).zfill(4)}" for i in range(1, n + 1)],
        "treatment": group,
        "sbp_baseline": np.round(baseline, 1),
        "sbp_followup": followup,
        "age": np.round(rng.normal(56, 11, n)).clip(30, 80).astype(int),
        "sex": rng.choice(["Male", "Female"], n),
        "bmi": np.round(rng.normal(24.5, 3.5, n).clip(17, 38), 1),
    })


def make_discriminant_analysis_example() -> pd.DataFrame:
    """Discriminant analysis: clinical classes separated by multivariate markers."""
    n_per = 75
    rows = []
    profiles = [
        ("Low risk", 50, 23.2, 118, 5.0, 4.5, 1.1),
        ("Metabolic risk", 59, 27.0, 136, 6.4, 5.5, 2.6),
        ("Inflammatory risk", 62, 25.4, 130, 5.8, 5.2, 6.8),
    ]
    for label, age_mu, bmi_mu, sbp_mu, glu_mu, chol_mu, crp_mu in profiles:
        age = rng.normal(age_mu, 7.5, n_per).clip(25, 86)
        bmi = rng.normal(bmi_mu, 2.4, n_per).clip(16, 42)
        sbp = rng.normal(sbp_mu, 9.5, n_per).clip(90, 190)
        glucose = rng.normal(glu_mu, 0.55, n_per).clip(3.2, 12)
        cholesterol = rng.normal(chol_mu, 0.55, n_per).clip(2.5, 8.5)
        crp = rng.lognormal(np.log(crp_mu), 0.32, n_per).clip(0.1, 35)
        for values in zip(age, bmi, sbp, glucose, cholesterol, crp):
            rows.append({
                "diagnosis_group": label,
                "age": int(round(values[0])),
                "bmi": round(float(values[1]), 1),
                "sbp": int(round(values[2])),
                "glucose": round(float(values[3]), 2),
                "cholesterol": round(float(values[4]), 2),
                "crp": round(float(values[5]), 2),
                "sex": rng.choice(["Male", "Female"], 1)[0],
            })
    df = pd.DataFrame(rows)
    df.insert(0, "patient_id", [f"P{str(i).zfill(4)}" for i in range(1, len(df) + 1)])
    return df


EXAMPLE_MAKERS = {
    "one_sample_t_test_example": make_one_sample_t_test_example,
    "normality_test_example": make_normality_test_example,
    "levene_test_example": make_levene_test_example,
    "t_test_independent_example": make_t_test_independent_example,
    "t_test_paired_example": make_t_test_paired_example,
    "anova_example": make_anova_example,
    "chi_square_example": make_chi_square_example,
    "fisher_exact_example": make_fisher_exact_example,
    "mann_whitney_example": make_mann_whitney_example,
    "kruskal_wallis_example": make_kruskal_wallis_example,
    "wilcoxon_signed_rank_example": make_wilcoxon_signed_rank_example,
    "mcnemar_example": make_mcnemar_example,
    "friedman_example": make_friedman_example,
    "repeated_measures_example": make_repeated_measures_example,
    "correlation_example": make_correlation_example,
    "survival_example": make_survival_example,
    "logistic_regression_example": make_logistic_regression_example,
    "linear_regression_example": make_linear_regression_example,
    "ancova_example": make_ancova_example,
    "discriminant_analysis_example": make_discriminant_analysis_example,
    "general_clinical_example": make_general_clinical_example,
}
