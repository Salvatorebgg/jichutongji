/* ── Global state ─────────────────────────────────────── */
const STATE = {
  uploadId: null,
  fileName: null,
  fileType: null,
  sheetNames: [],
  activeSheet: null,
  columns: [],
  dtypes: {},
  variableTypes: {},
  rowCount: 0,
  colCount: 0,
  previewRows: [],
  summary: {},
  activeTestType: null,
  activeTestCategory: 'parametric',
  activeTab: 'analysis',
  datasetName: null,
  currentResult: null,
  currentPlotlyData: null,
  currentPlotlyLayout: null,
  currentChartData: null,
  currentTables: null,
  currentDiscussion: null,
  postHocMethod: null,
  currentTableData: null,
  currentChartResizeObserver: null,
  testWorkspaces: {},
};

/* ── Test Catalog ─────────────────────────────────────── */
const TEST_CATALOG = {
  t_test_independent: {
    id: 't_test_independent',
    name: '独立样本t检验',
    category: 'parametric',
    icon: 'T₂',
    description: "Welch's t-test — 比较两组独立样本的均值差异",
    exampleDataset: 't_test_independent_example',
    requiresGroup: true,
    requiresPaired: false,
    varType: 'continuous',
  },
  t_test_paired: {
    id: 't_test_paired',
    name: '配对样本t检验',
    category: 'parametric',
    icon: 'Tp',
    description: 'Paired t-test — 比较同一组对象前后测量的差异',
    exampleDataset: 't_test_paired_example',
    requiresGroup: false,
    requiresPaired: true,
    varType: 'continuous',
  },
  one_sample_t_test: {
    id: 'one_sample_t_test',
    name: '单样本t检验',
    category: 'parametric',
    icon: 'T1',
    description: 'One-sample t-test — 检验单个连续变量均值是否偏离参考值',
    exampleDataset: 'one_sample_t_test_example',
    requiresGroup: false,
    requiresPaired: false,
    varType: 'continuous',
  },
  normality_test: {
    id: 'normality_test',
    name: '正态性检验',
    category: 'parametric',
    icon: 'W',
    description: 'Shapiro-Wilk — 判断连续变量分布是否显著偏离正态',
    exampleDataset: 'normality_test_example',
    requiresGroup: false,
    requiresPaired: false,
    varType: 'continuous',
  },
  levene_test: {
    id: 'levene_test',
    name: '方差齐性检验',
    category: 'parametric',
    icon: 'Lv',
    description: 'Levene / Brown-Forsythe — 比较多组连续变量的方差是否齐性',
    exampleDataset: 'levene_test_example',
    requiresGroup: true,
    requiresPaired: false,
    varType: 'continuous',
  },
  anova: {
    id: 'anova',
    name: '单因素方差分析',
    category: 'parametric',
    icon: 'Fa',
    description: 'One-way ANOVA — 比较三组及以上样本的均值差异',
    exampleDataset: 'anova_example',
    requiresGroup: true,
    requiresPaired: false,
    supportsPostHoc: true,
    varType: 'continuous',
  },
  chi_square: {
    id: 'chi_square',
    name: '卡方检验',
    category: 'categorical',
    icon: 'χ²',
    description: 'Chi-square test — 分析两个分类变量间的关联性',
    exampleDataset: 'chi_square_example',
    requiresGroup: true,
    requiresPaired: false,
    varType: 'categorical',
  },
  fisher_exact: {
    id: 'fisher_exact',
    name: 'Fisher精确概率法',
    category: 'categorical',
    icon: 'Fe',
    description: "Fisher's exact test — 小样本或低频数的2x2列联表精确检验",
    exampleDataset: 'fisher_exact_example',
    requiresGroup: true,
    requiresPaired: false,
    varType: 'categorical',
  },
  mann_whitney: {
    id: 'mann_whitney',
    name: 'Mann-Whitney U检验',
    category: 'nonparametric',
    icon: 'Uw',
    description: 'Wilcoxon秩和检验 — 两组独立样本的非参数比较',
    exampleDataset: 'mann_whitney_example',
    requiresGroup: true,
    requiresPaired: false,
    varType: 'continuous',
  },
  kruskal_wallis: {
    id: 'kruskal_wallis',
    name: 'Kruskal-Wallis H检验',
    category: 'nonparametric',
    icon: 'Kw',
    description: 'Kruskal-Wallis — 多组独立样本的非参数比较',
    exampleDataset: 'kruskal_wallis_example',
    requiresGroup: true,
    requiresPaired: false,
    supportsPostHoc: true,
    varType: 'continuous',
  },
  wilcoxon_signed_rank: {
    id: 'wilcoxon_signed_rank',
    name: 'Wilcoxon符号秩检验',
    category: 'nonparametric',
    icon: 'Ws',
    description: 'Wilcoxon signed-rank — 配对样本的非参数比较',
    exampleDataset: 'wilcoxon_signed_rank_example',
    requiresGroup: false,
    requiresPaired: true,
    varType: 'continuous',
  },
  mcnemar: {
    id: 'mcnemar',
    name: 'McNemar检验',
    category: 'categorical',
    icon: 'Mb',
    description: "McNemar's test — 配对分类资料的比较",
    exampleDataset: 'mcnemar_example',
    requiresGroup: false,
    requiresPaired: true,
    varType: 'categorical',
  },
  friedman: {
    id: 'friedman',
    name: 'Friedman检验',
    category: 'nonparametric',
    icon: 'Fm',
    description: 'Friedman test — 非参数重复测量方差分析',
    exampleDataset: 'friedman_example',
    requiresGroup: true,
    requiresPaired: false,
    requiresSubject: true,
    varType: 'continuous',
  },
  repeated_measures_anova: {
    id: 'repeated_measures_anova',
    name: '重复测量方差分析',
    category: 'parametric',
    icon: 'Rm',
    description: 'RM ANOVA — 同一组对象在不同时间点的重复测量',
    exampleDataset: 'repeated_measures_example',
    requiresGroup: true,
    requiresPaired: false,
    requiresSubject: true,
    varType: 'continuous',
  },
  pearson_correlation: {
    id: 'pearson_correlation',
    name: 'Pearson相关分析',
    category: 'correlation',
    icon: 'Pr',
    description: 'Pearson r — 两连续变量的线性相关分析',
    exampleDataset: 'correlation_example',
    requiresGroup: false,
    requiresPaired: true,
    requiresPairedLabel: '变量2',
    varType: 'continuous',
  },
  spearman_correlation: {
    id: 'spearman_correlation',
    name: 'Spearman秩相关',
    category: 'correlation',
    icon: 'Sp',
    description: "Spearman's ρ — 两变量的秩相关（非参数）",
    exampleDataset: 'correlation_example',
    requiresGroup: false,
    requiresPaired: true,
    requiresPairedLabel: '变量2',
    varType: 'continuous',
  },
  log_rank: {
    id: 'log_rank',
    name: 'Log-Rank生存分析',
    category: 'survival',
    icon: 'Lr',
    description: 'Log-rank test — 两组或多组生存曲线比较',
    exampleDataset: 'survival_example',
    requiresGroup: true,
    requiresPaired: false,
    requiresTimeEvent: true,
    varType: 'continuous',
  },
  logistic_regression: {
    id: 'logistic_regression',
    name: 'Logistic回归',
    category: 'regression',
    icon: 'Lg',
    description: 'Logistic Regression — 二分类结局的回归分析',
    exampleDataset: 'logistic_regression_example',
    requiresGroup: false,
    requiresPaired: false,
    requiresMultiVar: true,
    varType: 'categorical',
  },
  linear_regression: {
    id: 'linear_regression',
    name: '多重线性回归',
    category: 'regression',
    icon: 'Ln',
    description: 'Multiple Linear Regression — 多因素线性回归',
    exampleDataset: 'linear_regression_example',
    requiresGroup: false,
    requiresPaired: false,
    requiresMultiVar: true,
    varType: 'continuous',
  },
  discriminant_analysis: {
    id: 'discriminant_analysis',
    name: '线性判别分析',
    category: 'regression',
    icon: 'LD',
    description: 'LDA — 基于多项连续指标判别分类结局，并输出判别得分图',
    exampleDataset: 'discriminant_analysis_example',
    requiresGroup: false,
    requiresPaired: false,
    requiresMultiVar: true,
    varType: 'categorical',
  },
  quadratic_discriminant_analysis: {
    id: 'quadratic_discriminant_analysis',
    name: '二次判别分析',
    category: 'regression',
    icon: 'QD',
    description: 'QDA — 允许不同类别协方差结构的判别分类模型',
    exampleDataset: 'discriminant_analysis_example',
    requiresGroup: false,
    requiresPaired: false,
    requiresMultiVar: true,
    varType: 'categorical',
  },
  ancova: {
    id: 'ancova',
    name: '协方差分析',
    category: 'parametric',
    icon: 'Ac',
    description: 'ANCOVA — 控制协变量后的组间比较',
    exampleDataset: 'ancova_example',
    requiresGroup: true,
    requiresPaired: false,
    requiresCovariate: true,
    varType: 'continuous',
  },
};

function getTestConfig(testId) {
  return TEST_CATALOG[testId] || null;
}

/* ── API helpers ──────────────────────────────────────── */
async function apiPost(url, body = {}) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

function apiDownload(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || '';
  a.click();
}

/* ── DOM helpers ──────────────────────────────────────── */
function el(id) { return document.getElementById(id); }
function qs(sel, parent) { return (parent || document).querySelector(sel); }
function qsa(sel, parent) { return (parent || document).querySelectorAll(sel); }

/* ── Toast notifications ──────────────────────────────── */
function toast(msg, type = 'info') {
  const container = el('toastContainer');
  if (!container) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity 0.3s ease'; setTimeout(() => t.remove(), 300); }, 3500);
}

/* ── Loading & State ──────────────────────────────────── */
function setLoading(btn, loading) {
  if (loading) {
    btn._origText = btn.textContent;
    btn.textContent = '处理中...';
    btn.disabled = true;
    btn.style.opacity = '0.6';
  } else {
    btn.textContent = btn._origText || btn.textContent;
    btn.disabled = false;
    btn.style.opacity = '1';
  }
}

function resetDatasetState() {
  STATE.uploadId = null;
  STATE.fileName = null;
  STATE.fileType = null;
  STATE.sheetNames = [];
  STATE.activeSheet = null;
  STATE.columns = [];
  STATE.dtypes = {};
  STATE.variableTypes = {};
  STATE.rowCount = 0;
  STATE.colCount = 0;
  STATE.previewRows = [];
  STATE.summary = {};
  STATE.datasetName = null;
}

function getWorkspaceStateFromCurrent() {
  return {
    uploadId: STATE.uploadId,
    fileName: STATE.fileName,
    fileType: STATE.fileType,
    sheetNames: [...(STATE.sheetNames || [])],
    activeSheet: STATE.activeSheet,
    columns: [...(STATE.columns || [])],
    dtypes: { ...(STATE.dtypes || {}) },
    variableTypes: { ...(STATE.variableTypes || {}) },
    rowCount: STATE.rowCount || 0,
    colCount: STATE.colCount || 0,
    previewRows: [...(STATE.previewRows || [])],
    summary: { ...(STATE.summary || {}) },
    datasetName: STATE.datasetName || null,
  };
}

function saveActiveTestWorkspace() {
  if (!STATE.activeTestType) return;
  STATE.testWorkspaces[STATE.activeTestType] = getWorkspaceStateFromCurrent();
}

function loadTestWorkspace(testId) {
  const workspace = STATE.testWorkspaces[testId];
  if (!workspace) {
    resetDatasetState();
    return;
  }
  STATE.uploadId = workspace.uploadId || null;
  STATE.fileName = workspace.fileName || null;
  STATE.fileType = workspace.fileType || null;
  STATE.sheetNames = [...(workspace.sheetNames || [])];
  STATE.activeSheet = workspace.activeSheet || null;
  STATE.columns = [...(workspace.columns || [])];
  STATE.dtypes = { ...(workspace.dtypes || {}) };
  STATE.variableTypes = { ...(workspace.variableTypes || {}) };
  STATE.rowCount = workspace.rowCount || 0;
  STATE.colCount = workspace.colCount || 0;
  STATE.previewRows = [...(workspace.previewRows || [])];
  STATE.summary = { ...(workspace.summary || {}) };
  STATE.datasetName = workspace.datasetName || null;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
