/* ── Main Application Entry ─────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  initTestCategoryTabs();
  initTestTypeGrid();
  initCenterTabs();
  initFileInputs();
  initExportButtons();
  initPostHocSelect();
  initThemeSelector();
  loadExampleList();

  const runBtn = el('generateChartBtn');
  if (runBtn) runBtn.addEventListener('click', runAnalysis);

  const descBtn = el('runDescriptiveBtn');
  if (descBtn) descBtn.addEventListener('click', runDescriptive);

  renderMiniTestGrid('parametric');
  bootEmptyState();
});

// ── Test Category Tabs ────────────────────────────────
function initTestCategoryTabs() {
  qsa('#testCatTabs .cat-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      qsa('#testCatTabs .cat-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      STATE.activeChartCategory = this.dataset.cat;
      renderMiniTestGrid(this.dataset.cat);
    });
  });
}

// ── Mini Test Grid ────────────────────────────────────
function initTestTypeGrid() {
  const grid = el('miniTestGrid');
  if (grid) {
    grid.addEventListener('click', function(e) {
      const card = e.target.closest('.mini-chart-card');
      if (!card) return;
      const testId = card.dataset.test;
      if (testId) selectTest(testId);
    });
  }
}

function renderMiniTestGrid(category) {
  const grid = el('miniTestGrid');
  if (!grid) return;
  if (typeof TEST_CATALOG === 'undefined') return;
  const tests = Object.values(TEST_CATALOG).filter(t => t.category === category);
  grid.innerHTML = tests.map(test => `
    <div class="mini-chart-card ${STATE.activeChartType === test.id ? 'selected' : ''}" data-test="${test.id}">
      <span class="mini-chart-icon">${escapeHtml(test.icon)}</span>
      <span class="mini-chart-name">${escapeHtml(test.name)}</span>
    </div>
  `).join('');
}

function selectTest(testId) {
  if (STATE.activeChartType && STATE.activeChartType !== testId) {
    saveActiveTestWorkspace();
  }

  STATE.activeChartType = testId;
  STATE.currentResult = null;
  STATE.currentStatResult = null;
  STATE.currentStatChartData = null;
  STATE.currentPlotlyData = null;
  STATE.currentPlotlyLayout = null;
  STATE.currentChartData = null;
  STATE.currentTables = null;
  STATE.currentDiscussion = null;
  STATE.currentTableData = null;
  STATE.postHocMethod = null;
  loadTestWorkspace(testId);

  const config = getTestConfig(testId);
  if (config && !STATE.uploadId && !STATE.datasetName) {
    STATE.datasetName = config.exampleDataset;
  }

  qsa('.mini-chart-card').forEach(c => c.classList.remove('selected'));
  const activeCard = qs(`.mini-chart-card[data-test="${testId}"]`);
  if (activeCard) activeCard.classList.add('selected');

  const label = el('selectedTestLabel');
  if (label) label.textContent = config ? config.name : '请选择';

  const analysisTitle = el('analysisTitle');
  if (analysisTitle) analysisTitle.textContent = config ? config.name + ' — 分析结果' : '分析结果';

  const resultBadge = el('resultBadge');
  if (resultBadge) { resultBadge.textContent = config ? config.description || '' : ''; resultBadge.className = 'badge'; }

  updateFlowLine(1);
  resetResults();
  updateMetricGrid();
  updatePreviewTable();
  updateDownloadList();
  updatePostHocSection();
  updateDataMeta();
  renderDataPanel();
  buildVarControls();
  renderAppearanceControls();
  populateDescVarSelect();

  // Reset post-hoc select
  const postHocSelect = el('postHocSelect');
  if (postHocSelect) postHocSelect.value = '';
}

function resetResults() {
  STATE.currentStatResult = null;
  STATE.currentStatChartData = null;
  const summaryContainer = el('resultSummary');
  if (summaryContainer) {
    const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;
    summaryContainer.innerHTML = `<div class="empty-state">${config ? `已选择「${config.name}」，载入数据后点击执行分析` : '请在左侧选择检验方法'}</div>`;
  }
  const resultContainer = el('resultTableContainer');
  if (resultContainer) resultContainer.innerHTML = '';
  const groupContainer = el('groupStatsContainer');
  if (groupContainer) groupContainer.innerHTML = '';
  const postContainer = el('postHocContainer');
  if (postContainer) postContainer.innerHTML = '';
  const exportBar = el('analysisExportBar');
  if (exportBar) exportBar.style.display = 'none';
  const chartExportBar = el('chartExportBar');
  if (chartExportBar) chartExportBar.style.display = 'none';

  const chartContainer = el('chartPreviewContainer');
  if (chartContainer) {
    const oldPlot = chartContainer.querySelector('.js-plotly-plot');
    if (oldPlot && window.Plotly) Plotly.purge(oldPlot);
    chartContainer.innerHTML = '<div class="empty-state">执行分析后可查看统计图形</div>';
  }
}

// ── Center Panel Tabs ──────────────────────────────────
function initCenterTabs() {
  qsa('.workspace-tabs .tab').forEach(tab => {
    tab.addEventListener('click', function() {
      activateWorkspaceTab(this.dataset.tab);
    });
  });
}

function activateWorkspaceTab(tabName) {
  qsa('.workspace-tabs .tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
  qsa('.tab-panel').forEach(p => p.classList.remove('active'));
  const target = el(`tab-${tabName}`);
  if (target) target.classList.add('active');
  STATE.activeTab = tabName;

  // Reload chart if switching to chart tab
  if (tabName === 'chart' && STATE.currentPlotlyData && STATE.currentPlotlyData.length > 0) {
    setTimeout(() => renderChart(STATE.currentPlotlyData, STATE.currentPlotlyLayout), 100);
  }
  // Populate variable selector when switching to descriptive tab
  if (tabName === 'descriptive') {
    populateDescVarSelect();
  }
}

// ── File Inputs ────────────────────────────────────────
function initFileInputs() {
  const fileInput = el('wsFileInput');
  const uploadBtn = el('uploadDataBtn');

  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
  }
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0], { fromChart: true });
        fileInput.value = '';
      }
    });
  }

  const loadBtn = el('loadExampleBtn');
  if (loadBtn) {
    loadBtn.addEventListener('click', () => doLoadExample());
  }
}

async function doLoadExample() {
  if (!STATE.activeChartType) {
    const firstCard = qs('.mini-chart-card');
    if (firstCard && firstCard.dataset.test) {
      selectTest(firstCard.dataset.test);
    } else {
      toast('请先选择检验方法', 'info');
      return;
    }
  }
  const config = getTestConfig(STATE.activeChartType);
  if (!config) { toast('请先选择检验方法', 'info'); return; }

  const loadBtn = el('loadExampleBtn');
  const exampleName = config.exampleDataset || 'general_clinical_example';
  if (loadBtn) setLoading(loadBtn, true);
  try {
    await loadExampleDataset(exampleName, { silent: true });
    buildVarControls();
    renderAppearanceControls();
    populateDescVarSelect();
    updateMetricGrid();
    updatePreviewTable();
    updateDownloadList();
    updateFlowLine(2);
    updateDataMeta();
    renderDataPanel();
    setStatus('数据已载入');
    toast(`已加载「${config.name}」示例数据`, 'success');
  } catch(e) {
    toast('加载示例失败: ' + e.message, 'error');
  } finally {
    if (loadBtn) setLoading(loadBtn, false);
  }
}

// ── Post Hoc Select ────────────────────────────────────
function initPostHocSelect() {
  const sel = el('postHocSelect');
  if (!sel) return;
  sel.addEventListener('change', () => {
    STATE.postHocMethod = sel.value || null;
  });
}

function updatePostHocSection() {
  const section = el('postHocSection');
  if (!section) return;
  const config = getTestConfig(STATE.activeChartType);
  if (config && config.supportsPostHoc) {
    section.hidden = false;
  } else {
    section.hidden = true;
  }
}

// ── Export Buttons ──────────────────────────────────────
function initExportButtons() {
  document.addEventListener('click', function(e) {
    // Analysis export buttons
    const exportBtn = e.target.closest('#analysisExportBar .export-btn');
    if (exportBtn) {
      e.preventDefault();
      const fmt = exportBtn.dataset.fmt;
      if (fmt === 'excel') exportTableExcel();
      else if (fmt === 'csv') exportTableCSV();
      else if (fmt === 'html') exportTableHTML();
      else if (fmt === 'clipboard') copyTableToClipboard();
      return;
    }

    // Chart download toggle
    const downloadToggle = e.target.closest('#chartDownloadBtn');
    if (downloadToggle) {
      e.preventDefault();
      toggleChartDownloadMenu();
      return;
    }

    // Chart download option
    const chartExportBtn = e.target.closest('#chartDownloadMenu .download-option');
    if (chartExportBtn) {
      e.preventDefault();
      const fmt = chartExportBtn.dataset.fmt;
      closeChartDownloadMenu();
      if (['png', 'svg', 'tiff', 'pdf'].includes(fmt)) downloadChartImage(fmt);
      return;
    }

    // Close download menu when clicking outside
    if (!e.target.closest('#chartExportBar')) {
      closeChartDownloadMenu();
    }
  });
}

function toggleChartDownloadMenu() {
  const menu = el('chartDownloadMenu');
  const btn = el('chartDownloadBtn');
  if (!menu || !btn) return;
  const willOpen = menu.hidden;
  menu.hidden = !willOpen;
  btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
}

function closeChartDownloadMenu() {
  const menu = el('chartDownloadMenu');
  const btn = el('chartDownloadBtn');
  if (!menu || !btn) return;
  menu.hidden = true;
  btn.setAttribute('aria-expanded', 'false');
}

// ── Theme Selector ──────────────────────────────────────
function initThemeSelector() {
  const sel = el('chartThemeSelect');
  if (sel) {
    sel.value = STATE.chartTheme || 'cnsTheme';
    sel.addEventListener('change', () => {
      STATE.chartTheme = sel.value;
      STATE.userColors = null;
      renderAppearanceControls();
      toast('主题: ' + (typeof CHART_THEMES !== 'undefined' && CHART_THEMES[sel.value]?.name || sel.value), 'info');
      refreshCurrentVisualization();
    });
  }

  const titleInput = el('chartTitleInput');
  if (titleInput && !titleInput.dataset.boundStatTitleRefresh) {
    titleInput.dataset.boundStatTitleRefresh = 'true';
    let titleTimer = null;
    titleInput.addEventListener('input', () => {
      window.clearTimeout(titleTimer);
      titleTimer = window.setTimeout(() => refreshCurrentVisualization(), 220);
    });
  }
}

function refreshCurrentVisualization() {
  if (typeof rerenderCurrentStatChart === 'function' && rerenderCurrentStatChart()) {
    return true;
  }
  if (STATE.currentPlotlyData && STATE.currentPlotlyData.length > 0) {
    if (STATE.activeTab === 'chart') {
      renderChart(STATE.currentPlotlyData, STATE.currentPlotlyLayout);
    }
    return true;
  }
  return false;
}

function buildThemedLayout(baseLayout, themeName) {
  const theme = (typeof CHART_THEMES !== 'undefined' && CHART_THEMES[themeName]) ? CHART_THEMES[themeName] : null;
  if (!theme || !baseLayout) return baseLayout || {};
  return Object.assign({}, baseLayout, {
    font: theme.font || baseLayout.font,
    paper_bgcolor: theme.paper_bgcolor || baseLayout.paper_bgcolor,
    plot_bgcolor: theme.plot_bgcolor || baseLayout.plot_bgcolor,
  });
}

// ── Data Meta Display ──────────────────────────────────
function updateDataMeta() {
  const meta = el('wsDataMeta');
  if (!meta) return;
  const hasData = (STATE.columns || []).length > 0;
  const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;
  meta.textContent = hasData
    ? `${STATE.rowCount || 0} 行 · ${STATE.colCount || 0} 列 · ${STATE.uploadId ? STATE.fileName : (STATE.datasetName || '示例')}`
    : (config ? `推荐示例：${config.exampleDataset || ''}` : '请先选择检验方法');
}

// ── Flow Line ──────────────────────────────────────────
function updateFlowLine(activeIndex) {
  qsa('.flow-line span').forEach((span, i) => {
    span.classList.toggle('is-active', i < activeIndex);
  });
}

// ── Status Stack ───────────────────────────────────────
function setStatus(msg, isError) {
  const stack = el('statusStack');
  if (!stack) return;
  const div = document.createElement('div');
  div.className = `status-item active${isError ? ' error' : ''}`;
  div.textContent = msg;
  stack.appendChild(div);
  while (stack.children.length > 4) stack.removeChild(stack.firstChild);
}

// ── Metric Grid ────────────────────────────────────────
function updateMetricGrid() {
  const grid = el('metricGrid');
  if (!grid) return;
  const hasData = (STATE.columns || []).length > 0;
  const summary = STATE.summary || {};
  const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;

  grid.innerHTML = `
    <div class="summary-card"><span>N</span><strong>${hasData ? (STATE.rowCount || '—') : '--'}</strong><small>样本</small></div>
    <div class="summary-card"><span>Vars</span><strong>${hasData ? (STATE.colCount || '—') : '--'}</strong><small>变量</small></div>
    <div class="summary-card"><span>Missing</span><strong>${hasData ? (summary.missing_percent || '—') : '--'}</strong><small>缺失%</small></div>
    <div class="summary-card"><span>Method</span><strong>${config ? config.icon : '--'}</strong><small>${config ? config.name : '—'}</small></div>
  `;
}

// ── Preview Table (three-line table standard) ──────────
function updatePreviewTable() {
  const target = el('previewTable');
  if (!target) return;
  const rows = STATE.previewRows || [];
  const cols = STATE.columns || [];

  if (!rows.length || !cols.length) {
    target.innerHTML = '<div class="empty-state small">等待数据载入</div>';
    return;
  }

  // Three-line table matching Basicpicture standard
  let html = '<table class="three-line"><thead><tr>';
  cols.forEach(c => { html += `<th>${escapeHtml(String(c))}</th>`; });
  html += '</tr></thead><tbody>';
  for (let i = 0; i < rows.length; i++) {
    html += '<tr>';
    cols.forEach(c => {
      const v = rows[i][c];
      html += `<td>${v !== undefined && v !== null ? escapeHtml(String(v)) : ''}</td>`;
    });
    html += '</tr>';
  }
  const totalRows = STATE.rowCount || rows.length;
  if (totalRows > rows.length) html += `<caption>显示前 ${rows.length} 行 / 共 ${totalRows} 行</caption>`;
  html += '</tbody></table>';
  target.innerHTML = html;
}

// ── Dataset Meta ───────────────────────────────────────
function updateDatasetMeta() {
  const meta = el('datasetMeta');
  if (!meta) return;
  const hasData = (STATE.columns || []).length > 0;
  meta.textContent = hasData
    ? `${STATE.fileName || STATE.datasetName || '已载入'} · ${STATE.rowCount || 0} 行 × ${STATE.colCount || 0} 列`
    : '未载入数据';
}

// ── Download List ──────────────────────────────────────
function updateDownloadList() {
  const list = el('downloadList');
  if (!list) return;

  const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;
  if (!config) {
    list.className = 'download-list empty';
    list.innerHTML = '选择检验方法后可导出';
    return;
  }

  if (STATE.currentResult) {
    list.className = 'download-list';
    const chartLinks = STATE.currentPlotlyData ? `
      <a class="download-link" href="#" onclick="event.preventDefault();downloadChartImage('png');"><span>导出 PNG 图</span><small>高清位图</small></a>
      <a class="download-link" href="#" onclick="event.preventDefault();downloadChartImage('svg');"><span>导出 SVG 图</span><small>矢量图</small></a>
      <a class="download-link" href="#" onclick="event.preventDefault();downloadChartImage('tiff');"><span>导出 TIFF 图</span><small>期刊位图</small></a>
      <a class="download-link" href="#" onclick="event.preventDefault();downloadChartImage('pdf');"><span>导出 PDF 图</span><small>当前预览版式</small></a>
    ` : '';
    list.innerHTML = `
      <a class="download-link" href="#" onclick="event.preventDefault();exportTableExcel();"><span>导出 Excel</span><small>结果表格</small></a>
      <a class="download-link" href="#" onclick="event.preventDefault();exportTableCSV();"><span>导出 CSV</span><small>结果表格</small></a>
      ${chartLinks}
    `;
  } else {
    const exampleName = config.exampleDataset || 'general_clinical_example';
    list.className = 'download-list';
    list.innerHTML = `<a class="download-link" href="/api/examples/${exampleName}/download" target="_blank" rel="noreferrer"><span>下载示例 CSV</span><small>${exampleName}.csv</small></a>`;
  }
}

// ── Example List ───────────────────────────────────────
async function loadExampleList() {
  try {
    const examples = await apiGet('/api/examples');
    const list = el('exampleList');
    if (!list) return;
    const sorted = Array.isArray(examples)
      ? examples.slice().sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
      : [];
    list.innerHTML = sorted.map(ex => `
      <a class="download-link" href="/api/examples/${ex.name}/download" target="_blank" rel="noreferrer">
        <span>${escapeHtml(ex.name)}</span><small>${ex.row_count || '-'}行</small>
      </a>
    `).join('');
  } catch (e) {}
}

// ── Build Analysis Variable Controls ────────────────────
function buildVarControls() {
  const container = el('varControls');
  if (!container) return;

  const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;
  if (!config || !STATE.columns || STATE.columns.length === 0) {
    container.innerHTML = '<div class="empty-state small">请先选择检验方法并载入数据</div>';
    return;
  }

  const defaults = typeof getTestDefaultParams === 'function' ? getTestDefaultParams(STATE.activeChartType) : {};
  const cols = STATE.columns || [];
  // Convert grouped variableTypes {continuous: [...], binary: [...], ...}
  // to per-column lookup {colName: 'continuous', ...}
  const groupedVT = STATE.variableTypes || {};
  const colTypeMap = {};
  for (const [typeName, typeCols] of Object.entries(groupedVT)) {
    if (Array.isArray(typeCols)) {
      typeCols.forEach(c => { colTypeMap[c] = typeName; });
    }
  }
  const continuousCols = cols.filter(c => colTypeMap[c] === 'continuous' || colTypeMap[c] === 'numeric' || colTypeMap[c] === 'date');
  const categoricalCols = cols.filter(c => colTypeMap[c] === 'categorical' || colTypeMap[c] === 'binary' || colTypeMap[c] === 'group' || colTypeMap[c] === 'outcome_candidate');
  const allNumCols = cols.filter(c => {
    const t = colTypeMap[c];
    return t === 'continuous' || t === 'numeric' || t === 'binary' || t === 'date';
  });
  const pickDefault = (values, candidates) => {
    const wanted = (Array.isArray(values) ? values : [values]).filter(Boolean).map(String);
    return (candidates || []).find(c => wanted.includes(String(c))) || '';
  };

  let html = '';

  // Main variable — fallback to all columns if no typed candidates
  const varLabel = config.varType === 'categorical' ? '分类变量' : '连续变量';
  let varCandidates = config.varType === 'categorical' ? categoricalCols : continuousCols;
  if (varCandidates.length === 0) varCandidates = cols;
  const mainDefault = pickDefault([defaults.var, defaults.y_var], varCandidates);
  html += buildSelectField('var', varLabel, varCandidates, '选择分析变量', true, mainDefault);

  // Group variable
  if (config.requiresGroup) {
    let groupCandidates = categoricalCols;
    if (groupCandidates.length === 0) groupCandidates = cols;
    const groupDefault = pickDefault([defaults.group_var, defaults.x_var], groupCandidates);
    html += buildSelectField('group_var', '分组变量', groupCandidates, '选择分组变量（如治疗组/对照组）', true, groupDefault);
  }

  // Paired / second variable
  if (config.requiresPaired) {
    const pairedLabel = config.requiresPairedLabel || '配对变量';
    // For categorical tests (McNemar), paired var should be categorical/binary
    let pairedCandidates = config.varType === 'categorical' ? categoricalCols : continuousCols;
    if (pairedCandidates.length === 0) pairedCandidates = cols;
    // Default to second candidate (different from var) for paired variable
    const pairedDefault = pickDefault(defaults.paired_var, pairedCandidates)
      || pairedCandidates.find(c => c !== (mainDefault || varCandidates[0])) || pairedCandidates[0];
    html += buildSelectField('paired_var', pairedLabel, pairedCandidates, '选择配对或第二个变量', true, pairedDefault);
  }

  // Subject variable
  if (config.requiresSubject) {
    let subjectCandidates = cols.filter(c => colTypeMap[c] === 'id' || colTypeMap[c] === 'binary');
    if (subjectCandidates.length === 0) subjectCandidates = cols;
    const subjectDefault = pickDefault(defaults.subject_var, subjectCandidates);
    html += buildSelectField('subject_var', '受试者ID', subjectCandidates, '选择受试者/患者标识变量', true, subjectDefault);
  }

  // Time + Event for survival
  if (config.requiresTimeEvent) {
    let timeCandidates = continuousCols;
    if (timeCandidates.length === 0) timeCandidates = cols;
    const timeDefault = pickDefault(defaults.time_var, timeCandidates);
    html += buildSelectField('time_var', '时间变量', timeCandidates, '选择生存时间变量', true, timeDefault);
    let eventCandidates = categoricalCols;
    if (eventCandidates.length === 0) eventCandidates = cols;
    const eventDefault = pickDefault(defaults.event_var, eventCandidates);
    html += buildSelectField('event_var', '事件变量', eventCandidates, '选择事件状态变量（0/1）', true, eventDefault);
  }

  // Covariate for ANCOVA
  if (config.requiresCovariate) {
    let covarCandidates = continuousCols;
    if (covarCandidates.length === 0) covarCandidates = cols;
    const covarDefault = pickDefault(defaults.covar, covarCandidates);
    html += buildSelectField('covar', '协变量', covarCandidates, '选择需要控制的协变量', true, covarDefault);
  }

  // Multi-variable for regression/discriminant
  if (config.requiresMultiVar) {
    let multiCandidates = allNumCols;
    if (multiCandidates.length === 0) multiCandidates = cols;
    let selectedValues = Array.isArray(defaults.value_vars)
      ? defaults.value_vars.filter(v => multiCandidates.some(c => String(c) === String(v)))
      : [];
    if (selectedValues.length === 0) {
      selectedValues = multiCandidates
        .filter(c => String(c) !== String(mainDefault || ''))
        .slice(0, Math.min(6, multiCandidates.length));
    }
    html += '<div class="field-row">';
    html += '<label>预测变量（可多选）</label>';
    html += `<select id="chartVar_value_vars" class="chart-var-select" multiple size="5">`;
    multiCandidates.forEach(c => {
      const selected = selectedValues.some(v => String(v) === String(c)) ? ' selected' : '';
      html += `<option value="${escapeHtml(c)}"${selected}>${escapeHtml(c)}</option>`;
    });
    html += '</select>';
    html += '<small>按住 Ctrl/Cmd 多选</small>';
    html += '</div>';
  }

  container.innerHTML = html || '<div class="empty-state small">请选择变量</div>';
}

function buildSelectField(id, label, candidates, placeholder, autoSelect, defaultVal) {
  // Use chartVar_ prefix so collectChartParams() can read values
  const elementId = `chartVar_${id}`;
  if (!candidates || candidates.length === 0) {
    return `<div class="field-row"><label>${escapeHtml(label)}</label><select id="${elementId}" class="chart-var-select"><option value="">无可选变量</option></select></div>`;
  }
  let html = '<div class="field-row">';
  html += `<label for="${elementId}">${escapeHtml(label)}</label>`;
  html += `<select id="${elementId}" class="chart-var-select">`;
  html += `<option value="">${escapeHtml(placeholder || '请选择')}</option>`;
  candidates.forEach((c, i) => {
    const isSelected = defaultVal ? (c === defaultVal) : (autoSelect && i === 0);
    const selected = isSelected ? ' selected' : '';
    html += `<option value="${escapeHtml(c)}"${selected}>${escapeHtml(c)}</option>`;
  });
  html += '</select></div>';
  return html;
}

// ── Descriptive Stats Variable Selector ──────────────────
function populateDescVarSelect() {
  const sel = el('descVarSelect');
  if (!sel) return;
  const cols = STATE.columns || [];
  if (!cols.length) {
    sel.innerHTML = '<option value="">请先载入数据</option>';
    return;
  }
  sel.innerHTML = cols.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
}

// ── Render Chart (publication-quality re-render) ────────
// Data is assumed to be already polished from renderStatChart() or generateChart()
function renderChart(plotlyData, plotlyLayout) {
  const container = el('chartPreviewContainer');
  if (!container || !window.Plotly || !plotlyData || !plotlyData.length) return;

  const chartType = STATE.activeChartType || 'box';
  const theme = typeof getActiveTheme === 'function' ? getActiveTheme() : (CHART_THEMES ? CHART_THEMES[STATE.chartTheme || 'cnsTheme'] : {});
  const themeKeys = ['bgColor', 'plotBgColor', 'ink', 'fontFamily', 'axisLineColor', 'gridColor',
                     'legendFontSize', 'tickFontSize', 'axisFontSize', 'titleFontSize', 'titleColor'];

  // Light theme refresh only — traces are already polished, only update colors/fonts from theme
  let traces = plotlyData;
  let layout = { ...plotlyLayout };

  // Apply theme-specific visual properties to layout
  if (theme) {
    layout.paper_bgcolor = theme.bgColor || layout.paper_bgcolor || '#ffffff';
    layout.plot_bgcolor = theme.plotBgColor || layout.plot_bgcolor || '#ffffff';
    if (theme.ink && layout.font) layout.font = { ...layout.font, color: theme.ink };
    if (theme.fontFamily && layout.font) layout.font = { ...layout.font, family: theme.fontFamily };
  }

  // Clean up and create plot mount
  if (typeof disconnectChartResizeObserver === 'function') disconnectChartResizeObserver();
  const oldPlot = container.matches('.js-plotly-plot') ? container : container.querySelector('.js-plotly-plot');
  if (oldPlot && window.Plotly) Plotly.purge(oldPlot);
  container.classList.remove('js-plotly-plot');
  container.innerHTML = '';

  const plotMount = document.createElement('div');
  plotMount.className = 'chart-plot';
  container.appendChild(plotMount);

  // Compute size
  const useFitFunc = typeof fitChartPlotToFrame === 'function';
  let frameSize;
  if (useFitFunc) {
    frameSize = fitChartPlotToFrame(plotMount, chartType);
  } else {
    const previewStyle = getComputedStyle(container);
    const padX = parseFloat(previewStyle.paddingLeft || 0) + parseFloat(previewStyle.paddingRight || 0);
    const padY = parseFloat(previewStyle.paddingTop || 0) + parseFloat(previewStyle.paddingBottom || 0);
    const w = Math.max(560, Math.floor((container.clientWidth || 900) - padX));
    const h = Math.max(480, Math.floor((container.clientHeight || 680) - padY), Math.floor(window.innerHeight * 0.5));
    frameSize = { width: w, height: h };
    plotMount.style.width = w + 'px';
    plotMount.style.height = h + 'px';
    plotMount.style.minHeight = h + 'px';
  }
  layout.width = frameSize.width;
  layout.height = frameSize.height;
  layout.autosize = false;

  Plotly.newPlot(plotMount, traces, layout, {
    responsive: true,
    displaylogo: false,
    displayModeBar: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'sendDataToCloud'],
    toImageButtonOptions: {
      format: 'png', height: 1440, width: 2160, scale: 2,
      filename: (chartType || 'chart') + '_' + Date.now(),
    },
  });

  if (typeof syncCurrentPlotlyLayoutFromDom === 'function') syncCurrentPlotlyLayoutFromDom(plotMount);
  if (typeof installChartResizeObserver === 'function') installChartResizeObserver(plotMount, chartType);

  const chartExportBar = el('chartExportBar');
  if (chartExportBar) chartExportBar.style.display = 'flex';
}

// ── Workspace Persistence Helpers ────────────────────────
function saveActiveTestWorkspace() {
  if (!STATE.activeChartType) return;
  if (!STATE._testWorkspaces) STATE._testWorkspaces = {};
  STATE._testWorkspaces[STATE.activeChartType] = {
    var: el('chartVar_var')?.value || '',
    group_var: el('chartVar_group_var')?.value || '',
    paired_var: el('chartVar_paired_var')?.value || '',
    subject_var: el('chartVar_subject_var')?.value || '',
    time_var: el('chartVar_time_var')?.value || '',
    event_var: el('chartVar_event_var')?.value || '',
    covar: el('chartVar_covar')?.value || '',
    value_vars: [...(el('chartVar_value_vars')?.selectedOptions || [])].map(o => o.value),
  };
}

function loadTestWorkspace(testId) {
  if (!STATE._testWorkspaces || !STATE._testWorkspaces[testId]) return;
  const saved = STATE._testWorkspaces[testId];
  // Values will be restored when buildVarControls is called after this
  setTimeout(() => {
    if (saved.var && el('chartVar_var')) el('chartVar_var').value = saved.var;
    if (saved.group_var && el('chartVar_group_var')) el('chartVar_group_var').value = saved.group_var;
    if (saved.paired_var && el('chartVar_paired_var')) el('chartVar_paired_var').value = saved.paired_var;
    if (saved.subject_var && el('chartVar_subject_var')) el('chartVar_subject_var').value = saved.subject_var;
    if (saved.time_var && el('chartVar_time_var')) el('chartVar_time_var').value = saved.time_var;
    if (saved.event_var && el('chartVar_event_var')) el('chartVar_event_var').value = saved.event_var;
    if (saved.covar && el('chartVar_covar')) el('chartVar_covar').value = saved.covar;
    if (saved.value_vars && el('chartVar_value_vars')) {
      [...el('chartVar_value_vars').options].forEach(o => {
        o.selected = saved.value_vars.includes(o.value);
      });
    }
  }, 50);
}

// ── Appearance Controls ──────────────────────────────────
function renderAppearanceControls() {
  const container = el('appearanceControls');
  if (!container) return;

  const theme = (typeof CHART_THEMES !== 'undefined' && typeof getActiveTheme === 'function')
    ? getActiveTheme() : null;
  const palette = (theme && theme.colorway)
    ? theme.colorway
    : ['#2E6F9E', '#D95F59', '#2A9D8F', '#E9A93A', '#6F5AA7', '#7C8B52'];
  const numColors = 4;

  let html = '';

  // Color swatches
  html += '<div class="appearance-section">';
  html += '<label class="appearance-label">配色方案</label>';
  html += '<div class="color-picker-row" id="colorPickerRow">';
  if (STATE.userColors) {
    STATE.userColors = STATE.userColors.slice(0, numColors);
  }
  for (let i = 0; i < numColors; i++) {
    const currentColor = (STATE.userColors && STATE.userColors[i]) || palette[i % palette.length];
    html += `<input type="color" class="color-swatch" data-idx="${i}" value="${currentColor}" title="颜色 ${i + 1}" aria-label="颜色 ${i + 1}">`;
  }
  html += '<button class="color-reset-btn" id="resetColorsBtn" title="重置为主题默认色">重置</button>';
  html += '</div></div>';

  // Marker size slider
  const markerSize = STATE.markerSize || 8;
  html += `<div class="appearance-section">
    <label class="appearance-label">点/标记大小</label>
    <div class="slider-row">
      <input type="range" id="markerSizeInput" min="3" max="20" value="${markerSize}" class="app-slider">
      <span class="slider-val" id="markerSizeVal">${markerSize}</span>
    </div>
  </div>`;

  // Line width slider
  const lineWidth = STATE.lineWidth || 2.5;
  html += `<div class="appearance-section">
    <label class="appearance-label">线条宽度</label>
    <div class="slider-row">
      <input type="range" id="lineWidthInput" min="0.5" max="8" step="0.5" value="${lineWidth}" class="app-slider">
      <span class="slider-val" id="lineWidthVal">${lineWidth}</span>
    </div>
  </div>`;

  // Opacity slider
  const opacity = STATE.markerOpacity != null ? STATE.markerOpacity : 0.88;
  html += `<div class="appearance-section opacity-section">
    <label class="appearance-label">透明度</label>
    <div class="slider-row">
      <input type="range" id="markerOpacityInput" min="0.1" max="1" step="0.05" value="${opacity}" class="app-slider">
      <span class="slider-val" id="markerOpacityVal">${opacity}</span>
    </div>
  </div>`;

  container.innerHTML = html;

  // Bind color pickers
  qsa('.color-swatch', container).forEach(input => {
    input.addEventListener('input', (e) => {
      if (!STATE.userColors) STATE.userColors = [...palette.slice(0, numColors)];
      STATE.userColors[Number(e.target.dataset.idx)] = e.target.value;
    });
    input.addEventListener('change', () => {
      refreshCurrentVisualization();
    });
  });

  const resetBtn = el('resetColorsBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      STATE.userColors = null;
      renderAppearanceControls();
      refreshCurrentVisualization();
    });
  }

  // Bind sliders
  const markerSlider = el('markerSizeInput');
  if (markerSlider) {
    markerSlider.addEventListener('input', () => {
      STATE.markerSize = Number(markerSlider.value);
      const valSpan = el('markerSizeVal');
      if (valSpan) valSpan.textContent = markerSlider.value;
    });
    markerSlider.addEventListener('change', () => {
      refreshCurrentVisualization();
    });
  }

  const lineSlider = el('lineWidthInput');
  if (lineSlider) {
    lineSlider.addEventListener('input', () => {
      STATE.lineWidth = Number(lineSlider.value);
      const valSpan = el('lineWidthVal');
      if (valSpan) valSpan.textContent = lineSlider.value;
    });
    lineSlider.addEventListener('change', () => {
      refreshCurrentVisualization();
    });
  }

  const opacitySlider = el('markerOpacityInput');
  if (opacitySlider) {
    opacitySlider.addEventListener('input', () => {
      STATE.markerOpacity = Number(opacitySlider.value);
      const valSpan = el('markerOpacityVal');
      if (valSpan) valSpan.textContent = opacitySlider.value;
    });
    opacitySlider.addEventListener('change', () => {
      refreshCurrentVisualization();
    });
  }
}

// ── Data Panel Rendering ───────────────────────────────
function renderDataPanel() {
  const hasData = (STATE.columns || []).length > 0;
  const config = typeof getTestConfig === 'function' ? getTestConfig(STATE.activeChartType) : null;

  const meta = el('wsDataMeta');
  if (meta) {
    meta.textContent = hasData
      ? `${STATE.rowCount || 0} 行 · ${STATE.colCount || 0} 列 · ${STATE.uploadId ? STATE.fileName : (STATE.datasetName || '示例')}`
      : (config ? `推荐示例：${config.exampleDataset || 'general_clinical_example'}` : '请先选择检验方法');
  }
}

// ── Bootstrap ──────────────────────────────────────────
function bootEmptyState() {
  updateMetricGrid();
  updatePreviewTable();
  updateDatasetMeta();
  updateDownloadList();
  updateDataMeta();
}

// ── Utilities ──────────────────────────────────────────
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
