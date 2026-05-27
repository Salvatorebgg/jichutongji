/* ── Statistical Analysis Module ───────────────────────── */
/* Handles: analysis execution, result rendering, chart visualization */

async function runAnalysis() {
  const config = getTestConfig(STATE.activeTestType);
  if (!config) { toast('请先选择检验方法', 'info'); return; }
  if (!STATE.columns || STATE.columns.length === 0) { toast('请先载入数据', 'warning'); return; }

  const btn = el('runAnalysisBtn');
  setLoading(btn, true);
  setStatus('正在执行统计分析...');

  try {
    const body = buildAnalysisRequest(config);
    const data = await apiPost('/api/analyze', body);

    if (data.status === 'error') {
      toast(data.message || '分析失败', 'error');
      setStatus(data.message || '分析失败', true);
      renderErrorResult(data.message);
      return;
    }

    STATE.currentResult = data.result;
    STATE.currentDiscussion = data.discussion || null;
    STATE.currentTables = data.tables || null;
    STATE.currentTableData = data.tables?.result?.rows || [];

    renderAnalysisResult(data);
    renderResultTables(data.tables);
    updateChartTab(data.result);

    const badge = el('resultBadge');
    if (badge) {
      badge.textContent = data.result.p_value == null
        ? (data.result.significant ? '性能较好' : '模型指标')
        : (data.result.significant ? 'p < 0.05' : 'p >= 0.05');
      badge.className = 'badge ' + (data.result.significant ? 'warning' : 'success');
    }

    const exportBar = el('analysisExportBar');
    if (exportBar) exportBar.style.display = 'flex';

    updateDownloadList();
    updateFlowLine(4);
    setStatus(`分析完成: ${data.result.summary || data.result.test_name}`);
    toast('统计分析完成！', 'success');
  } catch (e) {
    toast('分析失败: ' + e.message, 'error');
    setStatus('分析失败: ' + e.message, true);
  } finally {
    setLoading(btn, false);
  }
}

function buildAnalysisRequest(config) {
  const body = {
    test_type: STATE.activeTestType,
    var: el('varSelect')?.value || '',
    use_demo: !STATE.uploadId,
    dataset_name: STATE.datasetName || 'general_clinical_example',
    upload_id: STATE.uploadId || null,
    sheet_name: STATE.activeSheet || null,
  };

  if (config.requiresGroup) {
    body.group_var = el('groupVarSelect')?.value || '';
  }
  if (config.requiresPaired) {
    body.paired_var = el('pairedVarSelect')?.value || '';
  }
  if (config.supportsPostHoc) {
    body.post_hoc = STATE.postHocMethod || null;
  }
  if (config.requiresSubject) {
    body.subject_var = el('subjectVarSelect')?.value || '';
  }
  if (config.requiresTimeEvent) {
    body.time_var = el('timeVarSelect')?.value || '';
    body.event_var = el('eventVarSelect')?.value || '';
  }
  if (config.requiresCovariate) {
    body.covar = el('covarSelect')?.value || '';
  }
  if (config.requiresMultiVar) {
    const xVarsSelect = el('xVarsSelect');
    body.x_vars = xVarsSelect ? Array.from(xVarsSelect.selectedOptions || []).map(o => o.value) : [];
  }

  return body;
}

/* ── Result Rendering ─────────────────────────────────── */
function renderAnalysisResult(data) {
  const container = el('resultSummary');
  if (!container) return;
  const r = data.result;

  if (r.error) {
    container.innerHTML = `<div class="result-note">${escapeHtml(r.error)}</div>`;
    return;
  }

  let html = '<div class="result-line">';
  html += `<span class="result-label">检验方法</span><span class="result-value">${escapeHtml(r.test_name || '')}</span>`;
  html += '</div>';

  html += '<div class="result-line">';
  html += `<span class="result-label">统计量</span><span class="result-value">${r.statistic != null ? r.statistic : '—'}</span>`;
  html += '</div>';

  html += '<div class="result-line">';
  const pClass = r.significant ? 'p-significant' : 'p-ns';
  html += `<span class="result-label">P值</span><span class="result-value ${pClass}">${formatPValueDisplay(r.p_value)}</span>`;
  html += '</div>';

  html += '<div class="result-line">';
  const conclusion = r.p_value == null
    ? (r.significant ? '模型性能高于类别基线，建议进一步验证' : '当前结果主要作为模型性能描述')
    : (r.significant ? '差异有统计学意义 (p < 0.05)' : '差异无统计学意义 (p >= 0.05)');
  html += `<span class="result-label">结论</span><span class="result-value">${conclusion}</span>`;
  html += '</div>';

  html += '<div class="result-line">';
  html += `<span class="result-label">方法</span><span class="result-value" style="font-size:12px;">${escapeHtml(r.method || '')}</span>`;
  html += '</div>';

  if (r.note) {
    html += `<div class="result-note">${escapeHtml(r.note)}</div>`;
  }

  // Show details based on test type
  if (r.details) {
    html += '<div style="margin-top:10px;">';
    html += renderTestDetails(r);
    html += '</div>';
  }

  if (data.discussion) {
    html += renderDiscussionBlock(data.discussion);
  }

  container.innerHTML = html;
}

function applyDefaultVarSelections(config) {
  const defaults = {
    t_test_independent: { varSelect: 'sbp_reduction', groupVarSelect: 'group' },
    t_test_paired: { varSelect: 'sbp_before', pairedVarSelect: 'sbp_after' },
    one_sample_t_test: { varSelect: 'ldl_change' },
    normality_test: { varSelect: 'biomarker' },
    levene_test: { varSelect: 'response_value', groupVarSelect: 'group' },
    anova: { varSelect: 'efficacy_score', groupVarSelect: 'treatment' },
    repeated_measures_anova: { varSelect: 'sbp', groupVarSelect: 'time', subjectVarSelect: 'subject_id' },
    ancova: { varSelect: 'sbp_followup', groupVarSelect: 'treatment', covarSelect: 'sbp_baseline' },
    mann_whitney: { varSelect: 'crp_level', groupVarSelect: 'group' },
    kruskal_wallis: { varSelect: 'biomarker_level', groupVarSelect: 'disease_stage' },
    wilcoxon_signed_rank: { varSelect: 'pain_before', pairedVarSelect: 'pain_after' },
    friedman: { varSelect: 'pain_score', groupVarSelect: 'timepoint', subjectVarSelect: 'subject_id' },
    chi_square: { varSelect: 'outcome', groupVarSelect: 'treatment' },
    fisher_exact: { varSelect: 'outcome', groupVarSelect: 'group' },
    mcnemar: { varSelect: 'diagnosis_standard', pairedVarSelect: 'diagnosis_new' },
    pearson_correlation: { varSelect: 'age', pairedVarSelect: 'bmi' },
    spearman_correlation: { varSelect: 'glucose', pairedVarSelect: 'crp' },
    log_rank: { varSelect: 'survival_time', groupVarSelect: 'treatment', timeVarSelect: 'survival_time', eventVarSelect: 'event' },
    logistic_regression: { varSelect: 'outcome', xVarsSelect: ['age', 'bmi', 'glucose', 'cholesterol'] },
    linear_regression: { varSelect: 'sbp', xVarsSelect: ['age', 'bmi', 'glucose', 'cholesterol'] },
    discriminant_analysis: { varSelect: 'diagnosis_group', xVarsSelect: ['age', 'bmi', 'sbp', 'glucose', 'cholesterol', 'crp'] },
    quadratic_discriminant_analysis: { varSelect: 'diagnosis_group', xVarsSelect: ['age', 'bmi', 'sbp', 'glucose', 'cholesterol', 'crp'] },
  }[config?.id] || {};

  Object.entries(defaults).forEach(([id, value]) => {
    const select = el(id);
    if (!select) return;
    if (Array.isArray(value)) {
      Array.from(select.options || []).forEach(option => {
        option.selected = value.includes(option.value);
      });
      if (!Array.from(select.selectedOptions || []).length) {
        Array.from(select.options || []).slice(0, Math.min(4, select.options.length)).forEach(option => {
          if (option.value) option.selected = true;
        });
      }
    } else if (Array.from(select.options || []).some(option => option.value === value)) {
      select.value = value;
    } else {
      const firstRealOption = Array.from(select.options || []).find(option => option.value);
      if (firstRealOption) select.value = firstRealOption.value;
    }
  });
}

function renderDiscussionBlock(discussion) {
  if (!discussion) return '';
  let html = '<div class="result-discussion">';
  if (discussion.headline) {
    html += `<div class="discussion-headline">${escapeHtml(discussion.headline)}</div>`;
  }
  (discussion.sections || []).forEach(section => {
    html += '<section class="discussion-section">';
    html += `<h4>${escapeHtml(section.title || '')}</h4>`;
    html += '<ul>';
    (section.items || []).forEach(item => {
      html += `<li>${escapeHtml(item)}</li>`;
    });
    html += '</ul></section>';
  });
  html += '</div>';
  return html;
}

function renderTestDetails(r) {
  let html = '';
  const d = r.details;
  const tt = r.test_type;

  if (tt === 't_test_independent') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_1?.name}: n=${d.group_1?.n}, Mean=${d.group_1?.mean}, SD=${d.group_1?.std}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">${d.group_2?.name}: n=${d.group_2?.n}, Mean=${d.group_2?.mean}, SD=${d.group_2?.std}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">均值差: ${d.mean_diff}</p>`;
  } else if (tt === 't_test_paired') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">配对: ${d.n_pairs}对</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">干预前: Mean=${d.mean_before}, SD=${d.std_before}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">干预后: Mean=${d.mean_after}, SD=${d.std_after}</p>`;
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">均值差: ${d.mean_diff} ± ${d.std_diff}</p>`;
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
    if (d.coefficients && Object.keys(d.coefficients).length) {
      const items = Object.entries(d.coefficients).slice(0, 6).map(([k, v]) => `${k}: ${v}`).join('; ');
      html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">主要判别载荷: ${items}</p>`;
    }
  } else if (tt === 'ancova') {
    html += `<p style="margin:4px 0;font-size:12px;color:var(--muted);">n = ${d.n}, 协变量: ${d.covariate}, R² = ${d.r2_full}</p>`;
  }

  return html;
}

function renderResultTables(tables) {
  const resultContainer = el('resultTableContainer');
  if (resultContainer && tables.result) {
    resultContainer.innerHTML = renderThreeLineTable(tables.result);
  }

  const groupContainer = el('groupStatsContainer');
  if (groupContainer && tables.group_stats) {
    groupContainer.innerHTML = `<h4 style="margin:10px 0 6px;">分组描述统计</h4>` + renderThreeLineTable(tables.group_stats);
  } else if (groupContainer) {
    groupContainer.innerHTML = '';
  }

  const postContainer = el('postHocContainer');
  if (postContainer && tables.post_hoc) {
    postContainer.innerHTML = `<h4 style="margin:10px 0 6px;">事后两两比较</h4>` + renderThreeLineTable(tables.post_hoc);
  } else if (postContainer) {
    postContainer.innerHTML = '';
  }
}

function renderErrorResult(message) {
  const container = el('resultSummary');
  if (container) {
    container.innerHTML = `<div class="result-note">分析错误: ${escapeHtml(message)}</div>`;
  }
}

function renderThreeLineTable(tableData) {
  if (!tableData || !tableData.columns || !tableData.rows) return '';
  const { columns, rows, title } = tableData;
  let html = '<div class="compact-table-wrap"><table class="three-line">';
  if (title) html += `<caption>${escapeHtml(title)}</caption>`;
  html += '<thead><tr>';
  columns.forEach(c => { html += `<th>${escapeHtml(String(c))}</th>`; });
  html += '</tr></thead><tbody>';
  rows.forEach(row => {
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

/* ── Variable Controls ─────────────────────────────────── */
function buildVarControls() {
  const container = el('varControls');
  if (!container) return;

  const config = getTestConfig(STATE.activeTestType);
  if (!config) {
    container.innerHTML = '<div class="empty-state small">请先选择检验方法并载入数据</div>';
    return;
  }

  const cols = STATE.columns || [];
  const varTypes = STATE.variableTypes || {};
  const continuousCols = varTypes.continuous || cols.filter(c => /int|float/i.test(String(STATE.dtypes[c] || '')));
  const categoricalCols = [...(varTypes.categorical || []), ...(varTypes.binary || [])];
  const binaryCols = varTypes.binary || [];
  const groupCandidates = [...new Set([...(varTypes.group || []), ...binaryCols, ...categoricalCols].filter(Boolean))];
  const categoricalCandidates = [...new Set([...categoricalCols, ...(varTypes.group || []), ...binaryCols].filter(Boolean))];

  let html = '';

  // Main variable selector
  html += '<div class="form-group">';
  const varLabel = config.varType === 'categorical' ? '结局变量（分类）' : '指标变量（连续）';
  html += `<label class="form-label">${varLabel} <span style="color:var(--rose);">*</span></label>`;
  html += '<select id="varSelect" class="analysis-var-select">';
  html += '<option value="">— 请选择 —</option>';
  const varCandidates = config.varType === 'categorical' ? categoricalCandidates : continuousCols;
  varCandidates.forEach(c => { html += `<option value="${c}">${c}</option>`; });
  html += '</select>';
  html += '</div>';

  // Group variable
  if (config.requiresGroup) {
    html += '<div class="form-group">';
    html += '<label class="form-label">分组变量 <span style="color:var(--rose);">*</span></label>';
    html += '<select id="groupVarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    groupCandidates.forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '</div>';
  }

  // Paired variable
  if (config.requiresPaired) {
    const pairedLabel = config.requiresPairedLabel || (config.varType === 'categorical' ? '配对变量（变量2）' : '配对变量（干预后）');
    html += '<div class="form-group">';
    html += `<label class="form-label">${pairedLabel} <span style="color:var(--rose);">*</span></label>`;
    html += '<select id="pairedVarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    const pairedCandidates = config.varType === 'categorical' ? categoricalCandidates : continuousCols;
    pairedCandidates.forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '</div>';
  }

  // Subject variable (Friedman, RM ANOVA)
  if (config.requiresSubject) {
    html += '<div class="form-group">';
    html += '<label class="form-label">受试者ID <span style="color:var(--rose);">*</span></label>';
    html += '<select id="subjectVarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    const subjectCandidates = cols.filter(c => /subject|patient|id/i.test(c));
    (subjectCandidates.length ? subjectCandidates : cols).forEach(c => {
      html += `<option value="${c}">${c}</option>`;
    });
    html += '</select>';
    html += '</div>';
  }

  // Time + Event (Log-rank)
  if (config.requiresTimeEvent) {
    html += '<div class="form-group">';
    html += '<label class="form-label">时间变量 <span style="color:var(--rose);">*</span></label>';
    html += '<select id="timeVarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    continuousCols.forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '</div>';
    html += '<div class="form-group">';
    html += '<label class="form-label">事件变量（0/1） <span style="color:var(--rose);">*</span></label>';
    html += '<select id="eventVarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    [...binaryCols, ...categoricalCols].forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '</div>';
  }

  // Covariate (ANCOVA)
  if (config.requiresCovariate) {
    html += '<div class="form-group">';
    html += '<label class="form-label">协变量 <span style="color:var(--rose);">*</span></label>';
    html += '<select id="covarSelect" class="analysis-var-select">';
    html += '<option value="">— 请选择 —</option>';
    continuousCols.forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '</div>';
  }

  // Multi variable select (regression)
  if (config.requiresMultiVar) {
    html += '<div class="form-group">';
    html += '<label class="form-label">自变量（可多选） <span style="color:var(--rose);">*</span></label>';
    html += '<select id="xVarsSelect" class="analysis-var-select" multiple size="5" style="min-height:100px;">';
    continuousCols.forEach(c => { html += `<option value="${c}">${c}</option>`; });
    html += '</select>';
    html += '<span class="form-hint">按住Ctrl/Cmd键多选</span>';
    html += '</div>';
  }

  container.innerHTML = html;
  applyDefaultVarSelections(config);
}

/* ── Post Hoc Section ─────────────────────────────────── */
function updatePostHocSection() {
  const section = el('postHocSection');
  if (!section) return;
  const config = getTestConfig(STATE.activeTestType);
  section.hidden = !(config && config.supportsPostHoc);
}

/* ── Descriptive Statistics ───────────────────────────── */
async function runDescriptive() {
  if (!STATE.columns || STATE.columns.length === 0) { toast('请先载入数据', 'warning'); return; }
  const btn = el('runDescriptiveBtn');
  setLoading(btn, true);
  try {
    const descSelect = el('descVarSelect');
    const selectedVars = descSelect && descSelect.selectedOptions
      ? Array.from(descSelect.selectedOptions).map(o => o.value)
      : [];
    const body = {
      use_demo: !STATE.uploadId,
      dataset_name: STATE.datasetName || 'general_clinical_example',
      upload_id: STATE.uploadId || null,
      variables: selectedVars.length > 0 ? selectedVars : null,
      test_type: '',
      var: '',
    };
    const data = await apiPost('/api/descriptive', body);
    if (data.status === 'ok' && data.table) {
      const container = el('descriptiveTableContainer');
      if (container) { container.innerHTML = renderThreeLineTable(data.table); }
      toast('描述统计生成完成！', 'success');
    }
  } catch (e) {
    toast('描述统计失败: ' + e.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

function populateDescVarSelect() {
  const select = el('descVarSelect');
  if (!select) return;
  const cols = STATE.columns || [];
  select.innerHTML = cols.map(c => `<option value="${c}">${c}</option>`).join('');
}

/* ── Chart / Visualization ────────────────────────────── */
function updateChartTab(result) {
  const config = getTestConfig(STATE.activeTestType);
  const chartData = result?.chart_data;
  const container = el('chartPreviewContainer');
  const exportBar = el('chartExportBar');
  if (!container) return;

  if (!chartData || !chartData.chart_type) {
    STATE.currentChartData = null;
    if (exportBar) exportBar.style.display = 'none';
    container.innerHTML = '<div class="empty-state">此检验暂无统计图形</div>';
    return;
  }

  try {
    STATE.currentChartData = chartData;
    const theme = getActiveTheme();
    const colors = getActiveColors();
    const chartConfig = getStatChartConfig(chartData.chart_type);

    let traces, layout;
    if (chartConfig) {
      traces = chartConfig.buildTraces(chartData, colors);
      layout = Object.assign({
        font: theme.font,
        paper_bgcolor: theme.paper_bg_color,
        plot_bgcolor: theme.plot_bg_color,
        margin: { l: 60, r: 20, t: 50, b: 60 },
      }, chartConfig.buildLayout(chartData, theme));
    } else {
      // Fallback for simple chart types
      traces = buildFallbackTraces(chartData, colors);
      layout = buildFallbackLayout(chartData, theme);
    }

    // Apply 3-line aesthetics to axes
    if (layout.xaxis) {
      layout.xaxis.linecolor = theme.axis_color;
      layout.xaxis.linewidth = 1.2;
      layout.xaxis.showline = true;
      layout.xaxis.mirror = false;
    }
    if (layout.yaxis) {
      layout.yaxis.linecolor = theme.axis_color;
      layout.yaxis.linewidth = 1.2;
      layout.yaxis.showline = true;
      layout.yaxis.mirror = false;
    }

    traces = polishStatTracesForPublication(traces, theme);
    layout = polishStatLayoutForPublication(layout, chartData.chart_type, theme);
    STATE.currentPlotlyData = traces;
    STATE.currentPlotlyLayout = layout;
    renderChart(traces, layout);
    if (exportBar) exportBar.style.display = 'flex';
  } catch (e) {
    console.error('Chart render error:', e);
    if (exportBar) exportBar.style.display = 'none';
    container.innerHTML = '<div class="empty-state">图形渲染失败</div>';
  }
}

function polishStatTracesForPublication(traces, theme) {
  const palette = theme.colorway || ['#2E6F9E', '#D95F59', '#2A9D8F', '#E9A93A'];
  const markerLine = '#ffffff';
  return (traces || []).map((trace, i) => {
    const t = { ...trace };
    const color = palette[i % palette.length];
    if (t.type === 'scatter') {
      const mode = String(t.mode || '');
      if (mode.includes('lines')) {
        t.line = { ...(t.line || {}), color: t.line?.color || color, width: Math.max(t.line?.width || 0, 2.6), shape: t.line?.shape || 'spline' };
      }
      if (mode.includes('markers') || !mode) {
        t.marker = { ...(t.marker || {}), color: t.marker?.color || color, size: t.marker?.size || 8.5, opacity: t.marker?.opacity ?? 0.78, line: { color: markerLine, width: 0.8 } };
      }
    }
    if (t.type === 'bar') {
      t.marker = { ...(t.marker || {}), color: t.marker?.color || color, opacity: t.marker?.opacity ?? 0.88, line: { color: markerLine, width: 0.8 } };
      t.textposition = t.textposition || 'outside';
      t.cliponaxis = false;
    }
    if (t.type === 'box') {
      t.line = { ...(t.line || {}), color, width: 1.6 };
      t.fillcolor = t.fillcolor || hexToRgba(color, 0.2);
      t.marker = { ...(t.marker || {}), color, size: 4, opacity: 0.55, line: { color: markerLine, width: 0.4 } };
      t.boxmean = t.boxmean ?? 'sd';
      t.boxpoints = t.boxpoints ?? 'outliers';
      t.jitter = t.jitter ?? 0.28;
    }
    if (t.type === 'histogram') {
      t.marker = { ...(t.marker || {}), color, opacity: 0.78, line: { color: markerLine, width: 0.6 } };
      t.nbinsx = t.nbinsx || 28;
    }
    return t;
  });
}

function polishStatLayoutForPublication(layout, chartType, theme) {
  const l = { ...(layout || {}) };
  const ink = theme.axis_color || theme.font?.color || '#1F2937';
  const family = theme.font?.family || 'Noto Sans SC, Microsoft YaHei, Arial';
  const axisColor = theme.axis_color || '#26313D';
  l.paper_bgcolor = theme.paper_bg_color || '#ffffff';
  l.plot_bgcolor = theme.plot_bg_color || '#ffffff';
  l.font = { family, size: 12, color: ink };
  l.hoverlabel = { bgcolor: '#ffffff', bordercolor: '#D7DEE8', font: { family, color: ink, size: 11 }, ...(l.hoverlabel || {}) };
  l.legend = {
    orientation: 'h',
    x: 0,
    y: -0.18,
    xanchor: 'left',
    yanchor: 'top',
    bgcolor: 'rgba(255,255,255,0)',
    borderwidth: 0,
    font: { family, size: 11, color: ink },
    ...(l.legend || {}),
  };
  l.title = normalizeStatChartTitle(l.title, family, ink);
  if (!l.xaxis) l.xaxis = {};
  if (!l.yaxis) l.yaxis = {};
  ['xaxis', 'yaxis'].forEach((axisKey) => {
    const prev = l[axisKey] || {};
    const isY = axisKey === 'yaxis';
    l[axisKey] = {
      ...prev,
      showline: false,
      linewidth: 0,
      mirror: false,
      ticks: 'outside',
      ticklen: 4,
      tickwidth: 1,
      tickcolor: axisColor,
      zeroline: false,
      showgrid: isY,
      gridcolor: theme.grid_color || 'rgba(31,41,55,0.08)',
      gridwidth: 0.6,
      automargin: true,
      tickfont: { family, size: 11, color: ink },
      title: normalizeAxisTitle(prev.title, family, ink),
    };
  });
  l.margin = { l: 76, r: 34, t: 74, b: 82, ...(l.margin || {}) };
  if (!['survival'].includes(chartType)) {
    l.shapes = [
      ...(Array.isArray(l.shapes) ? l.shapes : []),
      { type: 'line', xref: 'x domain', yref: 'y domain', x0: 0, y0: 0, x1: 1, y1: 0, line: { color: axisColor, width: 1.45 }, layer: 'above' },
      { type: 'line', xref: 'x domain', yref: 'y domain', x0: 0, y0: 0, x1: 0, y1: 1, line: { color: axisColor, width: 1.45 }, layer: 'above' },
    ];
    l.annotations = [
      { x: 1.02, y: 0, xref: 'x domain', yref: 'y domain', ax: 0.97, ay: 0, axref: 'x domain', ayref: 'y domain', showarrow: true, arrowhead: 3, arrowsize: 1.15, arrowwidth: 1.45, arrowcolor: axisColor, text: '' },
      { x: 0, y: 1.03, xref: 'x domain', yref: 'y domain', ax: 0, ay: 0.97, axref: 'x domain', ayref: 'y domain', showarrow: true, arrowhead: 3, arrowsize: 1.15, arrowwidth: 1.45, arrowcolor: axisColor, text: '' },
      ...(Array.isArray(l.annotations) ? l.annotations : []),
    ];
  }
  return l;
}

function normalizeStatChartTitle(title, family, ink) {
  const titleObj = typeof title === 'string' ? { text: title } : (title || { text: '' });
  return {
    ...titleObj,
    x: titleObj.x ?? 0.02,
    y: titleObj.y ?? 0.97,
    xanchor: titleObj.xanchor || 'left',
    yanchor: titleObj.yanchor || 'top',
    font: { family, size: titleObj.font?.size || 17, color: titleObj.font?.color || ink },
  };
}

function normalizeAxisTitle(title, family, ink) {
  const titleObj = typeof title === 'string' ? { text: title } : (title || {});
  return { ...titleObj, font: { family, size: 13, color: ink }, standoff: 10 };
}

function buildFallbackTraces(chartData, colors) {
  const ct = chartData.chart_type;
  if (ct === 'box_violin') {
    return (chartData.traces || []).map((t, i) => ({
      type: 'box', name: t.name, y: t.values || [],
      marker: { color: colors[i % colors.length] },
      fillcolor: hexToRgba(colors[i % colors.length], 0.15),
      boxmean: 'sd', showlegend: true,
    }));
  }
  if (ct === 'bar_grouped') {
    return (chartData.series || []).map((s, i) => ({
      type: 'bar', name: s.name, x: chartData.categories, y: s.values,
      marker: { color: colors[i % colors.length], opacity: 0.85 },
    }));
  }
  if (ct === 'paired_box') {
    return [
      { type: 'box', name: chartData.var_1_name, y: chartData.var_1_values, marker: { color: colors[0] }, fillcolor: hexToRgba(colors[0], 0.15) },
      { type: 'box', name: chartData.var_2_name, y: chartData.var_2_values, marker: { color: colors[1] }, fillcolor: hexToRgba(colors[1], 0.15) },
    ];
  }
  if (ct === 'paired_bar') {
    return [
      { type: 'bar', name: chartData.var_1_name, x: chartData.categories, y: chartData.var_1_counts, marker: { color: colors[0], opacity: 0.85 } },
      { type: 'bar', name: chartData.var_2_name, x: chartData.categories, y: chartData.var_2_counts, marker: { color: colors[1], opacity: 0.85 } },
    ];
  }
  if (ct === 'scatter_regression') {
    return [{
      type: 'scatter', mode: 'markers',
      x: chartData.x_values, y: chartData.y_values,
      marker: { color: colors[0], size: 8, opacity: 0.65 },
      name: 'Data',
    }];
  }
  if (ct === 'histogram') {
    return [{
      type: 'histogram', x: chartData.traces?.[0]?.values || [],
      marker: { color: colors[0], opacity: 0.75 }, nbinsx: 25,
    }];
  }
  return [{ type: 'scatter', mode: 'markers', x: [], y: [] }];
}

function buildFallbackLayout(chartData, theme) {
  return {
    font: theme.font,
    paper_bgcolor: theme.paper_bg_color,
    plot_bgcolor: theme.plot_bg_color,
    margin: { l: 60, r: 20, t: 50, b: 60 },
    title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
    xaxis: { title: { text: chartData.x_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
    yaxis: { title: { text: chartData.y_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
  };
}

function renderChart(traces, layout) {
  const container = el('chartPreviewContainer');
  if (!container) return;
  if (typeof Plotly === 'undefined') {
    container.innerHTML = '<div class="empty-state">Plotly.js 未加载</div>';
    return;
  }
  const oldPlot = container.querySelector('.js-plotly-plot');
  if (oldPlot) Plotly.purge(oldPlot);
  container.innerHTML = '';
  const plotDiv = document.createElement('div');
  plotDiv.className = 'chart-plot';
  container.appendChild(plotDiv);
  const chartType = STATE.currentChartData?.chart_type || 'stat_chart';
  const size = fitStatChartPlotToFrame(plotDiv, chartType);
  const finalLayout = { ...(layout || {}), width: size.width, height: size.height, autosize: false };
  STATE.currentPlotlyLayout = finalLayout;
  Plotly.newPlot(plotDiv, traces, finalLayout, {
    responsive: true,
    displayModeBar: true,
    toImageButtonOptions: { format: 'png', filename: 'statistical_chart', width: 1600, height: 1050, scale: 2 },
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'sendDataToCloud'],
    displaylogo: false,
  }).then(() => {
    installStatChartResizeObserver(plotDiv, chartType);
  });
}

function disconnectStatChartResizeObserver() {
  if (STATE.currentChartResizeObserver) {
    STATE.currentChartResizeObserver.disconnect();
    STATE.currentChartResizeObserver = null;
  }
}

function getStatChartFrameSize(plotMount, chartType) {
  const preview = el('chartPreviewContainer') || plotMount.parentElement;
  const width = Math.max(520, Math.floor(preview?.clientWidth || 900));
  const denseTypes = ['bar_grouped', 'paired_bar', 'repeated_measures'];
  const minHeight = denseTypes.includes(chartType) ? 620 : 560;
  const height = Math.max(minHeight, Math.floor(preview?.clientHeight || minHeight));
  return { width, height };
}

function fitStatChartPlotToFrame(plotMount, chartType) {
  const size = getStatChartFrameSize(plotMount, chartType);
  plotMount.style.width = '100%';
  plotMount.style.height = `${size.height}px`;
  plotMount.style.minHeight = `${size.height}px`;
  return size;
}

function installStatChartResizeObserver(plotMount, chartType) {
  disconnectStatChartResizeObserver();
  if (!window.ResizeObserver) return;
  let resizeFrame = null;
  const observer = new ResizeObserver(() => {
    if (resizeFrame) cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
      const size = fitStatChartPlotToFrame(plotMount, chartType);
      if (window.Plotly && plotMount.isConnected) {
        Plotly.relayout(plotMount, { width: size.width, height: size.height, autosize: false });
      }
    });
  });
  observer.observe(plotMount.parentElement || plotMount);
  STATE.currentChartResizeObserver = observer;
}

/* ── Helpers ──────────────────────────────────────────── */
function formatPValueDisplay(p) {
  if (p === null || p === undefined) return '—';
  if (p < 0.0001) return '< 0.0001';
  if (p < 0.001) return '< 0.001';
  return p.toFixed(4);
}
