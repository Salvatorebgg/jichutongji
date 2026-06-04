/* ── Statistical Analysis Module ───────────────────────── */
/* Integrated with Basicpicture chart system for publication-quality visualization */

/* ── Statistical Test Catalog ─────────────────────────── */
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

/* ── Statistical Analysis Execution ───────────────────── */
async function runAnalysis() {
  const config = getTestConfig(STATE.activeChartType);
  if (!config && !(STATE.activeChartType && TEST_CATALOG[STATE.activeChartType])) {
    // Not a statistical test, use chart generation
    return;
  }
  const testConfig = config || getTestConfig(STATE.activeChartType);
  if (!testConfig) return;

  if (!STATE.columns || STATE.columns.length === 0) {
    toast('请先载入数据', 'warning');
    return;
  }

  const btn = el('generateChartBtn');
  if (btn) setLoading(btn, true);
  if (typeof setStatus === 'function') setStatus('正在执行统计分析...');

  try {
    const body = buildAnalysisRequest(testConfig);
    const data = await apiPost('/api/analyze', body);

    if (data.status === 'error') {
      toast(data.message || '分析失败', 'error');
      if (typeof setStatus === 'function') setStatus(data.message || '分析失败', true);
      return;
    }

    STATE.currentStatResult = data.result;
    STATE.currentResult = data.result;  // for app.js compatibility
    STATE.currentDiscussion = data.discussion || null;
    STATE.currentTableData = data.tables?.result || null;  // full table object with columns + rows
    STATE.currentStatTables = data.tables || null;

    // Load full dataset for chart visualization
    try {
      if (typeof loadChartDataset === 'function') {
        const fullData = await loadChartDataset(testConfig);
        STATE._statChartData = fullData;
      } else {
        STATE._statChartData = null;
      }
    } catch(e) {
      STATE._statChartData = null;
    }

    // Render results in analysis tab
    renderStatResults(data);
    updateDownloadList();

    if (typeof updateFlowLine === 'function') updateFlowLine(4);
    if (typeof setStatus === 'function') setStatus(`分析完成: ${data.result.summary || data.result.test_name}`);
    toast('统计分析完成！', 'success');
  } catch (e) {
    toast('分析失败: ' + e.message, 'error');
    if (typeof setStatus === 'function') setStatus('分析失败: ' + e.message, true);
  } finally {
    if (btn) setLoading(btn, false);
  }
}

function buildAnalysisRequest(config) {
  const params = typeof collectChartParams === 'function' ? collectChartParams() : {};
  const body = {
    test_type: STATE.activeChartType,
    var: params.var || params.y_var || '',
    use_demo: !STATE.uploadId,
    dataset_name: STATE.datasetName || 'general_clinical_example',
    upload_id: STATE.uploadId || null,
    sheet_name: STATE.activeSheet || null,
  };

  if (config.requiresGroup) {
    body.group_var = params.group_var || params.x_var || '';
  }
  if (config.requiresPaired) {
    body.paired_var = params.paired_var || params.end_var || params.var2 || '';
  }
  if (config.supportsPostHoc) {
    body.post_hoc = STATE.postHocMethod || null;
  }
  if (config.requiresSubject) {
    body.subject_var = params.subject_var || '';
  }
  if (config.requiresTimeEvent) {
    body.time_var = params.time_var || params.x_var || '';
    body.event_var = params.event_var || '';
  }
  if (config.requiresCovariate) {
    body.covar = params.covar || '';
  }
  if (config.requiresMultiVar) {
    body.x_vars = params.value_vars || params.x_vars || [];
  }

  return body;
}

/* ── Statistical Result Rendering ─────────────────────── */
function renderStatResults(data) {
  const r = data.result;
  const tables = data.tables || {};

  // Render summary into resultSummary
  const summaryContainer = el('resultSummary');
  if (summaryContainer) {
    let html = '';

    // Key result summary cards
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:16px;">';

    if (r.statistic != null) {
      html += `<div class="summary-card"><span>统计量</span><strong>${typeof r.statistic === 'number' ? r.statistic.toFixed(4) : r.statistic}</strong><small>${r.method || ''}</small></div>`;
    }
    if (r.p_value != null) {
      const pClass = r.significant ? 'color:var(--rose);' : 'color:var(--teal);';
      html += `<div class="summary-card"><span>P值</span><strong style="${pClass}">${formatPValueDisplay(r.p_value)}</strong><small>${r.significant ? 'p < 0.05 显著' : 'p ≥ 0.05 不显著'}</small></div>`;
    }
    html += `<div class="summary-card"><span>结论</span><strong style="font-size:14px;">${r.significant ? '有统计学意义' : (r.p_value == null ? (r.significant ? '性能较好' : '参考') : '无统计学意义')}</strong><small>${escapeHtml(r.summary || '')}</small></div>`;
    html += '</div>';

    // Details
    if (r.details) {
      html += `<div style="margin-bottom:12px;padding:10px 14px;background:rgba(0,0,0,0.02);border-radius:8px;">${renderTestDetails(r)}</div>`;
    }

    // Discussion
    if (data.discussion) {
      html += renderDiscussionBlock(data.discussion);
    }

    summaryContainer.innerHTML = html;
  }

  // Render tables into their containers
  const resultTableContainer = el('resultTableContainer');
  if (resultTableContainer) {
    resultTableContainer.innerHTML = tables.result
      ? `<h4 style="margin:0 0 6px;">结果表</h4>${renderStatThreeLineTable(tables.result)}`
      : '';
  }

  const groupContainer = el('groupStatsContainer');
  if (groupContainer) {
    groupContainer.innerHTML = tables.group_stats
      ? `<h4 style="margin:0 0 6px;">分组描述统计</h4>${renderStatThreeLineTable(tables.group_stats)}`
      : '';
  }

  const postContainer = el('postHocContainer');
  if (postContainer) {
    postContainer.innerHTML = tables.post_hoc
      ? `<h4 style="margin:0 0 6px;">事后两两比较</h4>${renderStatThreeLineTable(tables.post_hoc)}`
      : '';
  }

  // Also render chart in the chart tab using the loaded dataset
  const chartContainer = el('chartPreviewContainer');
  if (chartContainer && r.test_name) {
    renderStatChart(r, data.result || {});
  }

  // Update chart preview title to match statistical result
  const previewTitle = el('chartPreviewTitle');
  if (previewTitle && r.test_name) {
    previewTitle.textContent = `${r.test_name} — 统计图形`;
  }

  // Update badge
  const badge = el('chartPreviewBadge');
  if (badge) {
    badge.textContent = r.p_value == null
      ? (r.significant ? '性能较好' : '模型指标')
      : (r.significant ? 'p < 0.05' : 'p ≥ 0.05');
    badge.style.display = 'inline-block';
  }

  // Show export bars
  const analysisExportBar = el('analysisExportBar');
  if (analysisExportBar) analysisExportBar.style.display = 'flex';
  const chartExportBar = el('chartExportBar');
  if (chartExportBar) chartExportBar.style.display = 'flex';

  if (typeof activateWorkspaceTab === 'function') activateWorkspaceTab('analysis');
}

function renderStatThreeLineTable(tableData) {
  if (!tableData || !tableData.columns || !tableData.rows) return '';
  const { columns, rows, title } = tableData;
  let html = '<div class="compact-table-wrap"><table class="three-line">';
  if (title) html += `<caption>${escapeHtml(title)}</caption>`;
  html += '<thead><tr>';
  columns.forEach(c => { html += `<th>${escapeHtml(String(c))}</th>`; });
  html += '</tr></thead><tbody>';
  (rows || []).forEach(row => {
    html += '<tr>';
    columns.forEach(c => {
      const v = row[c] !== undefined && row[c] !== null ? row[c] : '—';
      html += `<td>${escapeHtml(String(v))}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  return html;
}

function renderDiscussionBlock(discussion) {
  if (!discussion) return '';
  let html = '<div style="margin-top:10px;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:rgba(0,0,0,0.01);">';
  if (discussion.headline) {
    html += `<div style="font-weight:700;color:var(--ink);margin-bottom:8px;">${escapeHtml(discussion.headline)}</div>`;
  }
  (discussion.sections || []).forEach(section => {
    html += '<div style="margin-bottom:8px;">';
    html += `<span style="font-weight:650;color:var(--text);">${escapeHtml(section.title || '')}</span>`;
    html += '<ul style="margin:4px 0 0;padding-left:18px;">';
    (section.items || []).forEach(item => {
      html += `<li style="font-size:12px;color:var(--muted);">${escapeHtml(item)}</li>`;
    });
    html += '</ul></div>';
  });
  html += '</div>';
  return html;
}

function renderTestDetails(r) {
  let html = '';
  const d = r.details || {};
  const tt = r.test_type;

  if (tt === 't_test_independent') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_1?.name}: n=${d.group_1?.n}, Mean=${d.group_1?.mean}, SD=${d.group_1?.std}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_2?.name}: n=${d.group_2?.n}, Mean=${d.group_2?.mean}, SD=${d.group_2?.std}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">均值差: ${d.mean_diff}, 95%CI=${(d.ci_95 || []).join(', ')}</p>`;
  } else if (tt === 't_test_paired') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">配对: ${d.n_pairs}对, 干预前: Mean=${d.mean_before}, SD=${d.std_before}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">干预后: Mean=${d.mean_after}, SD=${d.std_after}, 均值差: ${d.mean_diff} ± ${d.std_diff}</p>`;
  } else if (tt === 'one_sample_t_test') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n=${d.n}, Mean=${d.mean}, SD=${d.std}, 参考均值=${d.hypothesized_mean}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">均值差=${d.mean_diff}, 95%CI=[${(d.ci_95 || []).join(', ')}]</p>`;
  } else if (tt === 'normality_test') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n=${d.n}, W统计量=${r.statistic}, 正态性判断: ${d.normal ? '未见显著偏离' : '显著偏离'}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">偏度=${d.skewness}, 峰度=${d.kurtosis}, Median=${d.median} (${d.q1}, ${d.q3})</p>`;
  } else if (tt === 'levene_test') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">组数: ${d.n_groups}, 总样本: ${d.total_n}, 方差齐性: ${d.equal_var ? '可接受' : '不齐'}</p>`;
    if (d.group_stats) {
      for (const [g, s] of Object.entries(d.group_stats)) {
        html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${g}: n=${s.n}, SD=${s.std}, Var=${s.variance}</p>`;
      }
    }
  } else if (tt === 'anova') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">组数: ${d.n_groups}, 总样本: ${d.total_n}</p>`;
    if (d.levene_test) {
      html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">Levene检验: p=${d.levene_test.p_value} (${d.levene_test.equal_var ? '方差齐' : '方差不齐'})</p>`;
    }
    if (d.group_stats) {
      for (const [g, s] of Object.entries(d.group_stats)) {
        html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${g}: n=${s.n}, Mean=${s.mean}, SD=${s.std}</p>`;
      }
    }
  } else if (tt === 'chi_square') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">自由度: ${d.degrees_of_freedom}, 最小期望频数: ${d.min_expected}</p>`;
  } else if (tt === 'fisher_exact' && d.odds_ratio) {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">OR = ${d.odds_ratio}</p>`;
  } else if (tt === 'mann_whitney') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_1?.name}: n=${d.group_1?.n}, Median=${d.group_1?.median} (${d.group_1?.q1}, ${d.group_1?.q3})</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_2?.name}: n=${d.group_2?.n}, Median=${d.group_2?.median} (${d.group_2?.q1}, ${d.group_2?.q3})</p>`;
  } else if (tt === 'kruskal_wallis' && d.group_stats) {
    for (const [g, s] of Object.entries(d.group_stats)) {
      html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${g}: n=${s.n}, Median=${s.median} (${s.q1}, ${s.q3})</p>`;
    }
  } else if (tt === 'wilcoxon_signed_rank') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">配对: ${d.n_pairs}对, 正差: ${d.n_positive_diffs}, 负差: ${d.n_negative_diffs}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">差值中位数: ${d.median_diff}</p>`;
  } else if (tt === 'mcnemar' && d.discordant_pairs) {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">不一致对: b=${d.discordant_pairs.b}, c=${d.discordant_pairs.c}</p>`;
  } else if (tt === 'friedman' || tt === 'repeated_measures_anova') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">完整观测: ${d.n_subjects_complete}, 组数: ${d.n_groups}</p>`;
  } else if (tt === 'pearson_correlation' || tt === 'spearman_correlation') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}${d.r_squared !== undefined ? `, R² = ${d.r_squared}` : ''}</p>`;
  } else if (tt === 'log_rank') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">组别: ${(d.groups || []).join(', ')}</p>`;
  } else if (tt === 'logistic_regression') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}, 特征数: ${d.n_features}</p>`;
    if (d.odds_ratios) {
      for (const [vname, or] of Object.entries(d.odds_ratios)) {
        html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${vname}: OR = ${or}</p>`;
      }
    }
  } else if (tt === 'linear_regression') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}, R² = ${d.r_squared}</p>`;
    if (d.coefficients) {
      for (const [vname, coef] of Object.entries(d.coefficients)) {
        html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${vname}: β = ${coef}</p>`;
      }
    }
  } else if (tt === 'discriminant_analysis' || tt === 'quadratic_discriminant_analysis') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}, 类别数 = ${d.n_classes}, 预测变量数 = ${d.n_predictors}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">训练准确率 = ${d.accuracy}, 交叉验证准确率 = ${d.cv_accuracy ?? '—'}, 基线准确率 = ${d.baseline_accuracy}</p>`;
  } else if (tt === 'ancova') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}, 协变量: ${d.covariate}, R² = ${d.r2_full}</p>`;
  }
  return html;
}

/* ── Helpers ──────────────────────────────────────────── */
function formatPValueDisplay(p) {
  if (p === null || p === undefined) return '—';
  if (p < 0.0001) return '< 0.0001';
  if (p < 0.001) return '< 0.001';
  return p.toFixed(4);
}

/* ── Post-hoc Section ─────────────────────────────────── */
function updatePostHocSection() {
  // Post-hoc is now handled via chart params; migrated from old UI
}

/* ── Statistical Chart Visualization ───────────────────── */
/* Computes chart data using the Basicpicture publication-quality pipeline.
   Actual Plotly rendering is deferred to renderChart() when the chart tab becomes visible. */
function renderStatChart(result, fullResult) {
  if (!window.Plotly) return;

  // Prefer full dataset (loaded by loadChartDataset), fall back to preview rows
  let rawData = STATE._statChartData || null;
  if (!rawData || Object.keys(rawData).length === 0) {
    rawData = typeof buildDataFromState === 'function' ? buildDataFromState() : {};
  }
  const params = typeof collectChartParams === 'function' ? collectChartParams() : {};
  const varName = params.var || '';
  const groupVar = params.group_var || '';
  const pairedVar = params.paired_var || '';
  const titleText = params.title || (el('chartTitleInput') ? el('chartTitleInput').value : '') || result.test_name || '';
  const tt = result.test_type;
  const chartType = tt;

  let traces = [];
  let layout = { title: { text: titleText } };

  try {
    if (tt === 't_test_independent' && varName && groupVar && rawData[varName] && rawData[groupVar]) {
      const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
      traces = groups.map((g, i) => ({
        type: 'box', name: String(g),
        y: rawData[varName].filter((_, idx) => rawData[groupVar][idx] == g),
        meta: { colorIndex: i },
        boxmean: 'sd', boxpoints: 'outliers',
      }));
      layout.yaxis = { title: { text: varName } };
      layout.xaxis = { title: { text: groupVar } };
    }
    else if (tt === 't_test_paired' && varName && pairedVar && rawData[varName] && rawData[pairedVar]) {
      const x = rawData[varName].map(Number).filter(v => !isNaN(v));
      const y = rawData[pairedVar].map(Number).filter(v => !isNaN(v));
      const n = Math.min(x.length, y.length);
      traces = [{
        type: 'scatter', mode: 'markers',
        x: x.slice(0, n), y: y.slice(0, n),
        meta: { colorIndex: 0 },
        name: '配对数据点',
      }];
      const allVals = [...x.slice(0, n), ...y.slice(0, n)];
      const lo = Math.min(...allVals), hi = Math.max(...allVals);
      traces.push({ type: 'scatter', mode: 'lines', x: [lo, hi], y: [lo, hi],
        meta: { colorIndex: 1 }, name: 'y=x',
        line: { dash: 'dash' } });
      layout.xaxis = { title: { text: varName } };
      layout.yaxis = { title: { text: pairedVar } };
    }
    else if (tt === 'one_sample_t_test' && varName && rawData[varName]) {
      const vals = rawData[varName].map(Number).filter(v => !isNaN(v));
      traces = [{
        type: 'histogram', x: vals, nbinsx: 28,
        meta: { colorIndex: 0 },
        name: varName,
      }];
      const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
      traces.push({ type: 'scatter', mode: 'lines', x: [mean, mean], y: [0, vals.length],
        meta: { colorIndex: 1 }, name: `均值=${mean.toFixed(2)}`,
        line: { dash: 'dash' } });
      layout.xaxis = { title: { text: varName } };
      layout.yaxis = { title: { text: '频数' } };
      layout.bargap = 0.05;
    }
    else if (tt === 'normality_test' && varName && rawData[varName]) {
      const vals = rawData[varName].map(Number).filter(v => !isNaN(v)).sort((a, b) => a - b);
      const n = vals.length;
      if (n > 2) {
        const mean = vals.reduce((a, b) => a + b, 0) / n;
        const std = Math.sqrt(vals.reduce((s, v) => s + (v - mean) ** 2, 0) / (n - 1));
        const qqX = [], qqY = [];
        for (let i = 0; i < n; i++) {
          const p = (i + 0.5) / n;
          const z = _normalInv(p);
          qqX.push(mean + std * z);
          qqY.push(vals[i]);
        }
        traces = [{
          type: 'scatter', mode: 'markers',
          x: qqX, y: qqY,
          meta: { colorIndex: 0 },
          name: 'Q-Q 点',
        }];
        const lo = Math.min(...qqX, ...qqY), hi = Math.max(...qqX, ...qqY);
        traces.push({ type: 'scatter', mode: 'lines', x: [lo, hi], y: [lo, hi],
          meta: { colorIndex: 1 }, name: '参考线',
          line: { dash: 'dash' } });
        layout.xaxis = { title: { text: '理论分位数' } };
        layout.yaxis = { title: { text: '样本分位数' } };
      }
    }
    else if ((tt === 'anova' || tt === 'levene_test' || tt === 'kruskal_wallis') && varName && groupVar && rawData[varName] && rawData[groupVar]) {
      const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
      traces = groups.map((g, i) => ({
        type: 'box', name: String(g),
        y: rawData[varName].filter((_, idx) => rawData[groupVar][idx] == g),
        meta: { colorIndex: i },
        boxmean: 'sd', boxpoints: 'outliers',
      }));
      layout.yaxis = { title: { text: varName } };
      layout.xaxis = { title: { text: groupVar } };
    }
    else if ((tt === 'chi_square' || tt === 'fisher_exact') && varName && groupVar && rawData[varName] && rawData[groupVar]) {
      const rowVals = [...new Set(rawData[varName].filter(v => v !== '' && v != null))];
      const colVals = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
      traces = colVals.map((c, i) => ({
        type: 'bar', name: String(c),
        x: rowVals.map(String),
        y: rowVals.map(rv => rawData[varName].filter((_, idx) => rawData[varName][idx] == rv && rawData[groupVar][idx] == c).length),
        meta: { colorIndex: i },
      }));
      layout.barmode = 'stack';
      layout.xaxis = { title: { text: varName } };
      layout.yaxis = { title: { text: '频数' } };
    }
    else if ((tt === 'mann_whitney') && varName && groupVar && rawData[varName] && rawData[groupVar]) {
      const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
      traces = groups.map((g, i) => ({
        type: 'box', name: String(g),
        y: rawData[varName].filter((_, idx) => rawData[groupVar][idx] == g),
        meta: { colorIndex: i },
        boxmean: 'sd', boxpoints: 'outliers',
      }));
      layout.yaxis = { title: { text: varName } };
      layout.xaxis = { title: { text: groupVar } };
    }
    else if (tt === 'wilcoxon_signed_rank' && varName && pairedVar && rawData[varName] && rawData[pairedVar]) {
      const x = rawData[varName].map(Number).filter(v => !isNaN(v));
      const y = rawData[pairedVar].map(Number).filter(v => !isNaN(v));
      const n = Math.min(x.length, y.length);
      if (n > 0) {
        traces = [{
          type: 'scatter', mode: 'markers',
          x: x.slice(0, n), y: y.slice(0, n),
          meta: { colorIndex: 0 },
          name: '配对数据点',
        }];
        layout.xaxis = { title: { text: varName } };
        layout.yaxis = { title: { text: pairedVar } };
      }
    }
    else if (tt === 'mcnemar') {
      // McNemar uses categorical paired data — use backend chart_data for grouped bar chart
      const cd = result.chart_data || fullResult.chart_data || {};
      const cats = cd.categories || [];
      const c1 = cd.var_1_counts || [];
      const c2 = cd.var_2_counts || [];
      if (cats.length > 0) {
        traces = [
          {
            type: 'bar', name: cd.var_1_name || varName || '变量1',
            x: cats.map(String), y: c1,
            meta: { colorIndex: 0 },
          },
          {
            type: 'bar', name: cd.var_2_name || pairedVar || '变量2',
            x: cats.map(String), y: c2,
            meta: { colorIndex: 1 },
          },
        ];
        layout.barmode = 'group';
        layout.xaxis = { title: { text: '类别' } };
        layout.yaxis = { title: { text: '频数' } };
      }
    }
    else if ((tt === 'pearson_correlation' || tt === 'spearman_correlation') && varName && pairedVar && rawData[varName] && rawData[pairedVar]) {
      const x = rawData[varName].map(Number).filter(v => !isNaN(v));
      const y = rawData[pairedVar].map(Number).filter(v => !isNaN(v));
      const n = Math.min(x.length, y.length);
      traces = [{
        type: 'scatter', mode: 'markers',
        x: x.slice(0, n), y: y.slice(0, n),
        meta: { colorIndex: 0 },
        name: '数据点',
      }];
      if (n > 2) {
        const xs = x.slice(0, n), ys = y.slice(0, n);
        const mx = xs.reduce((a, b) => a + b, 0) / n;
        const my = ys.reduce((a, b) => a + b, 0) / n;
        let num = 0, den = 0;
        for (let i = 0; i < n; i++) { num += (xs[i] - mx) * (ys[i] - my); den += (xs[i] - mx) ** 2; }
        if (den > 0) {
          const slope = num / den, intercept = my - slope * mx;
          const xRange = [Math.min(...xs), Math.max(...xs)];
          traces.push({ type: 'scatter', mode: 'lines', x: xRange, y: xRange.map(xv => slope * xv + intercept),
            meta: { colorIndex: 1 }, name: '回归线',
            line: { dash: 'dash' } });
        }
      }
      layout.xaxis = { title: { text: varName } };
      layout.yaxis = { title: { text: pairedVar } };
    }
    else if (tt === 'log_rank') {
      const timeVar = params.time_var || '';
      const eventVar = params.event_var || '';
      if (timeVar && eventVar && rawData[timeVar] && rawData[eventVar] && groupVar && rawData[groupVar]) {
        const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
        traces = groups.map((g, gi) => {
          const times = [], probs = [];
          const groupTimes = rawData[timeVar].filter((_, idx) => rawData[groupVar][idx] == g).map(Number).filter(v => !isNaN(v)).sort((a, b) => a - b);
          const groupEvents = rawData[eventVar].filter((_, idx) => rawData[groupVar][idx] == g);
          let surv = 1.0;
          let atRisk = groupTimes.length;
          times.push(0); probs.push(1);
          for (let i = 0; i < groupTimes.length; i++) {
            const died = groupEvents[i] == 1 || groupEvents[i] == '1' || groupEvents[i] === true;
            if (died) { surv *= (atRisk - 1) / atRisk; }
            atRisk--;
            times.push(groupTimes[i]); probs.push(surv);
          }
          return { type: 'scatter', mode: 'lines', name: String(g), x: times, y: probs, meta: { colorIndex: gi } };
        });
        layout.xaxis = { title: { text: '时间' } };
        layout.yaxis = { title: { text: '生存概率' }, range: [0, 1.05] };
      }
    }
    else if (tt === 'logistic_regression' || tt === 'linear_regression' || tt === 'discriminant_analysis' || tt === 'quadratic_discriminant_analysis') {
      const d = result.details || {};
      const coefs = d.coefficients || d.odds_ratios || {};
      const names = Object.keys(coefs);
      if (names.length > 0) {
        traces = [{
          type: 'bar', name: tt === 'logistic_regression' ? 'OR' : 'β',
          x: names, y: names.map(n => Number(coefs[n]) || 0),
          marker: { color: names.map((_, i) => _statPalette()[i % _statPalette().length]) },
          meta: { colorIndex: 0 },
        }];
        layout.xaxis = { title: { text: '变量' } };
        layout.yaxis = { title: { text: tt === 'logistic_regression' ? 'OR值' : '回归系数β' } };
      }
    }
    else if (tt === 'ancova' && varName && groupVar) {
      if (rawData[varName] && rawData[groupVar]) {
        const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
        traces = groups.map((g, i) => ({
          type: 'box', name: String(g),
          y: rawData[varName].filter((_, idx) => rawData[groupVar][idx] == g),
          meta: { colorIndex: i },
          boxmean: 'sd', boxpoints: 'outliers',
        }));
        layout.yaxis = { title: { text: varName } };
        layout.xaxis = { title: { text: groupVar } };
      }
    }
    else if (tt === 'friedman' || tt === 'repeated_measures_anova') {
      if (varName && groupVar && rawData[varName] && rawData[groupVar]) {
        const groups = [...new Set(rawData[groupVar].filter(v => v !== '' && v != null))];
        traces = groups.map((g, i) => ({
          type: 'box', name: String(g),
          y: rawData[varName].filter((_, idx) => rawData[groupVar][idx] == g),
          meta: { colorIndex: i },
          boxmean: 'sd', boxpoints: 'outliers',
        }));
        layout.yaxis = { title: { text: varName } };
        layout.xaxis = { title: { text: groupVar } };
      }
    }
  } catch (e) {
    console.warn('Stat chart computation failed:', e);
  }

  // No chart data — show placeholder and clear state
  if (traces.length === 0) {
    const container = el('chartPreviewContainer');
    if (container) {
      const oldPlot = container.querySelector('.js-plotly-plot');
      if (oldPlot && window.Plotly) Plotly.purge(oldPlot);
      container.innerHTML = `<div style="width:100%;padding:24px 28px;text-align:center;">
        <h3 style="margin:0 0 12px;color:var(--ink);">${escapeHtml(result.test_name || '')}</h3>
        <p style="font-size:15px;color:var(--muted);">${escapeHtml(result.summary || '')}</p>
      </div>`;
    }
    STATE.currentPlotlyData = null;
    STATE.currentPlotlyLayout = null;
    STATE.currentChartSourceData = null;
    return;
  }

  // ── Apply Basicpicture publication-quality pipeline ──
  const theme = typeof getActiveTheme === 'function' ? getActiveTheme() : (CHART_THEMES ? CHART_THEMES[STATE.chartTheme || 'cnsTheme'] : {});
  const defaultMargin = { l: 72, r: 48, t: 72, b: 72 };

  if (typeof polishTracesForPublication === 'function') {
    traces = polishTracesForPublication(traces, theme);
  }
  if (typeof applyThemeLayout === 'function') {
    layout = applyThemeLayout(layout, theme);
  }
  layout.margin = { ...defaultMargin, ...(layout.margin || {}) };
  if (typeof polishLayoutForPublication === 'function') {
    layout = polishLayoutForPublication(layout, chartType, theme);
  }
  layout.autosize = true;
  if (layout.showlegend === undefined) {
    layout.showlegend = traces.some(t => t && t.showlegend !== false && t.name);
  }

  // Store polished chart data in STATE (defer Plotly rendering to renderChart())
  STATE.currentPlotlyData = traces;
  STATE.currentPlotlyLayout = layout;
  STATE.currentChartSourceData = rawData;
  if (typeof saveCurrentChartParams === 'function') saveCurrentChartParams(params);

  // Prepare container placeholder
  const container = el('chartPreviewContainer');
  if (container) {
    if (typeof disconnectChartResizeObserver === 'function') disconnectChartResizeObserver();
    const oldPlot = container.matches('.js-plotly-plot') ? container : container.querySelector('.js-plotly-plot');
    if (oldPlot && window.Plotly) Plotly.purge(oldPlot);
    container.innerHTML = '<div class="empty-state">图表数据已准备，切换到可视化标签查看</div>';
    container.classList.remove('js-plotly-plot');
  }
}

function _statPalette() {
  const theme = typeof getActiveTheme === 'function' ? getActiveTheme() : {};
  return (theme.colorway || ['#2E6F9E', '#D95F59', '#2A9D8F', '#E9A93A', '#6F5AA7', '#7C8B52']);
}

// Approximate inverse normal CDF (Abramowitz & Stegun)
function _normalInv(p) {
  if (p <= 0) return -4;
  if (p >= 1) return 4;
  const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104799983e2, 1.383577518672690e2, -3.066479806614716e1, 2.506628277459239e0];
  const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1];
  const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277058772e0, -2.549732539343734e0, 4.374664141464968e0, 2.938163982698783e0];
  const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996e0, 3.754408661907416e0];
  const pLow = 0.02425, pHigh = 1 - pLow;
  let q, r;
  if (p < pLow) {
    q = Math.sqrt(-2 * Math.log(p));
    return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  } else if (p <= pHigh) {
    q = p - 0.5; r = q * q;
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
  } else {
    q = Math.sqrt(-2 * Math.log(1 - p));
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  }
}

/* ── Descriptive Statistics ───────────────────────────── */
async function runDescriptive() {
  if (!STATE.columns || STATE.columns.length === 0) { toast('请先载入数据', 'warning'); return; }
  try {
    const body = {
      use_demo: !STATE.uploadId,
      dataset_name: STATE.datasetName || 'general_clinical_example',
      upload_id: STATE.uploadId || null,
    };
    const data = await apiPost('/api/descriptive', body);
    if (data.status === 'ok' && data.table) {
      const container = el('descriptiveTableContainer');
      if (container) {
        container.innerHTML = `<div style="width:100%;overflow-y:auto;padding:4px 0;">
          <h4 style="margin:0 0 10px;">描述统计结果</h4>${renderStatThreeLineTable(data.table)}</div>`;
      }
      toast('描述统计生成完成！', 'success');
      if (typeof activateWorkspaceTab === 'function') activateWorkspaceTab('descriptive');
    }
  } catch (e) {
    toast('描述统计失败: ' + e.message, 'error');
  }
}
