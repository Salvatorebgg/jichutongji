/* ── Variable Select Module ────────────────────────────────── */
/* Extracted variable control logic for the clinical statistics platform. */

const TEST_DEFAULT_VARS = {
  t_test_independent: { var: 'sbp_reduction', group_var: 'group' },
  t_test_paired: { var: 'sbp_before', paired_var: 'sbp_after' },
  one_sample_t_test: { var: 'ldl_change' },
  normality_test: { var: 'biomarker' },
  levene_test: { var: 'response_value', group_var: 'group' },
  anova: { var: 'efficacy_score', group_var: 'treatment' },
  chi_square: { var: 'outcome', group_var: 'treatment' },
  fisher_exact: { var: 'outcome', group_var: 'group' },
  mann_whitney: { var: 'crp_level', group_var: 'group' },
  kruskal_wallis: { var: 'biomarker_level', group_var: 'disease_stage' },
  wilcoxon_signed_rank: { var: 'pain_before', paired_var: 'pain_after' },
  mcnemar: { var: 'diagnosis_standard', paired_var: 'diagnosis_new' },
  friedman: { var: 'pain_score', group_var: 'timepoint', subject_var: 'subject_id' },
  repeated_measures_anova: { var: 'sbp', group_var: 'time', subject_var: 'subject_id' },
  pearson_correlation: { var: 'sbp', paired_var: 'bmi' },
  spearman_correlation: { var: 'crp', paired_var: 'bmi' },
  log_rank: { var: 'survival_time', group_var: 'treatment', time_var: 'survival_time', event_var: 'event' },
  logistic_regression: { var: 'outcome' },
  linear_regression: { var: 'sbp' },
  discriminant_analysis: { var: 'diagnosis_group', x_vars: ['age', 'bmi', 'sbp', 'glucose', 'cholesterol', 'crp'] },
  quadratic_discriminant_analysis: { var: 'diagnosis_group', x_vars: ['age', 'bmi', 'sbp', 'glucose', 'cholesterol', 'crp'] },
  ancova: { var: 'sbp_followup', group_var: 'treatment', covar: 'sbp_baseline' },
};

function getDefaultVars(testType) {
  return TEST_DEFAULT_VARS[testType] || {};
}

function uniqueList(items) {
  return [...new Set((items || []).filter(Boolean))];
}
