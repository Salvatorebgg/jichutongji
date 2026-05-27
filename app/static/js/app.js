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

  const runBtn = el('runAnalysisBtn');
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
      STATE.activeTestCategory = this.dataset.cat;
      renderMiniTestGrid(this.dataset.cat);
    });
  });
}

// ── Mini Test Grid ────────────────────────────────────
function initTestTypeGrid() {
  const grid = el('miniTestGrid');
  if (grid) {
    grid.addEventListener('click', function(e) {
      const card = e.target.closest('.mini-test-card');
      if (!card) return;
      const testId = card.dataset.test;
      if (testId) selectTest(testId);
    });
  }
}

function renderMiniTestGrid(category) {
  const grid = el('miniTestGrid');
  if (!grid) return;
  const tests = Object.values(TEST_CATALOG).filter(t => t.category === category);
  grid.innerHTML = tests.map(test => `
    <div class="mini-test-card ${STATE.activeTestType === test.id ? 'selected' : ''}" data-test="${test.id}">
      <span class="mini-test-icon">${test.icon}</span>
      <span class="mini-test-name">${test.name}</span>
    </div>
  `).join('');
}

function selectTest(testId) {
  if (STATE.activeTestType && STATE.activeTestType !== testId) {
    saveActiveTestWorkspace();
  }

  STATE.activeTestType = testId;
  STATE.currentResult = null;
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

  qsa('.mini-test-card').forEach(c => c.classList.remove('selected'));
  const activeCard = qs(`.mini-test-card[data-test="${testId}"]`);
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
  buildVarControls();
  populateDescVarSelect();

  // Reset post-hoc select
  const postHocSelect = el('postHocSelect');
  if (postHocSelect) postHocSelect.value = '';
}

function resetResults() {
  const summaryContainer = el('resultSummary');
  if (summaryContainer) {
    const config = getTestConfig(STATE.activeTestType);
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
    if (typeof disconnectStatChartResizeObserver === 'function') disconnectStatChartResizeObserver();
    chartContainer.innerHTML = '<div class="empty-state">执行分析后可查看统计图形</div>';
  }
}

// ── Center Panel Tabs ──────────────────────────────────
function initCenterTabs() {
  qsa('.tabs .tab').forEach(tab => {
    tab.addEventListener('click', function() {
      qsa('.tabs .tab').forEach(t => t.classList.remove('active'));
      qsa('.tab-panel').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      STATE.activeTab = this.dataset.tab;
      const target = el(`tab-${this.dataset.tab}`);
      if (target) target.classList.add('active');

      // Reload chart if switching to chart tab
      if (this.dataset.tab === 'chart' && STATE.currentPlotlyData && STATE.currentPlotlyData.length > 0) {
        setTimeout(() => renderChart(STATE.currentPlotlyData, STATE.currentPlotlyLayout), 100);
      }
      // Populate variable selector when switching to descriptive tab
      if (this.dataset.tab === 'descriptive') {
        populateDescVarSelect();
      }
    });
  });
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
  if (!STATE.activeTestType) {
    const firstCard = qs('.mini-test-card');
    if (firstCard && firstCard.dataset.test) {
      selectTest(firstCard.dataset.test);
    } else {
      toast('请先选择检验方法', 'info');
      return;
    }
  }
  const config = getTestConfig(STATE.activeTestType);
  if (!config) { toast('请先选择检验方法', 'info'); return; }

  const loadBtn = el('loadExampleBtn');
  const exampleName = config.exampleDataset || 'general_clinical_example';
  if (loadBtn) setLoading(loadBtn, true);
  try {
    await loadExampleDataset(exampleName, { silent: true });
    buildVarControls();
    populateDescVarSelect();
    updateMetricGrid();
    updatePreviewTable();
    updateDownloadList();
    updateFlowLine(2);
    updateDataMeta();
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

// ── Export Buttons ──────────────────────────────────────
function initExportButtons() {
  document.addEventListener('click', function(e) {
    const exportBtn = e.target.closest('.export-btn');
    if (exportBtn) {
      e.preventDefault();
      const fmt = exportBtn.dataset.fmt;
      if (fmt === 'excel') exportTableExcel();
      else if (fmt === 'csv') exportTableCSV();
      else if (fmt === 'html') exportTableHTML();
      else if (fmt === 'clipboard') copyTableToClipboard();
    }
    const chartExportBtn = e.target.closest('.chart-export-btn');
    if (chartExportBtn) {
      e.preventDefault();
      downloadPublicationStatChart(chartExportBtn.dataset.chartFmt || 'png');
    }
  });
}

// ── Data Meta Display ──────────────────────────────────
function updateDataMeta() {
  const meta = el('wsDataMeta');
  if (!meta) return;
  const hasData = (STATE.columns || []).length > 0;
  const config = getTestConfig(STATE.activeTestType);
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
  const config = getTestConfig(STATE.activeTestType);

  grid.innerHTML = `
    <div class="summary-card"><span>N</span><strong>${hasData ? (STATE.rowCount || '—') : '--'}</strong><small>样本</small></div>
    <div class="summary-card"><span>Vars</span><strong>${hasData ? (STATE.colCount || '—') : '--'}</strong><small>变量</small></div>
    <div class="summary-card"><span>Missing</span><strong>${hasData ? (summary.missing_percent || '—') : '--'}</strong><small>缺失%</small></div>
    <div class="summary-card"><span>Method</span><strong>${config ? config.icon : '--'}</strong><small>${config ? config.name : '—'}</small></div>
  `;
}

// ── Preview Table ──────────────────────────────────────
function updatePreviewTable() {
  const target = el('previewTable');
  if (!target) return;
  const rows = STATE.previewRows || [];
  const cols = (STATE.columns || []).slice(0, 8);

  if (!rows.length || !cols.length) {
    target.innerHTML = '<div class="empty-state small">等待数据载入</div>';
    return;
  }

  const maxRows = Math.min(rows.length, 5);
  let html = '<table class="three-line"><thead><tr>';
  cols.forEach(c => { html += `<th>${escapeHtml(String(c))}</th>`; });
  html += '</tr></thead><tbody>';
  for (let i = 0; i < maxRows; i++) {
    html += '<tr>';
    cols.forEach(c => {
      const v = rows[i][c];
      html += `<td>${v !== undefined && v !== null ? escapeHtml(String(v)) : ''}</td>`;
    });
    html += '</tr>';
  }
  if (rows.length > maxRows) html += `<caption>前 ${maxRows} 行 / 共 ${rows.length} 行</caption>`;
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

  const config = getTestConfig(STATE.activeTestType);
  if (!config) {
    list.className = 'download-list empty';
    list.textContent = '选择检验方法后可导出';
    return;
  }

  if (STATE.currentResult) {
    list.className = 'download-list';
    list.innerHTML = `
      <a class="download-link" href="#" onclick="event.preventDefault();exportTableExcel();"><span>导出 Excel</span><small>结果表格</small></a>
      <a class="download-link" href="#" onclick="event.preventDefault();exportTableCSV();"><span>导出 CSV</span><small>结果表格</small></a>
      ${STATE.currentPlotlyData ? '<a class="download-link" href="#" onclick="event.preventDefault();downloadPublicationStatChart(\'png\');"><span>导出出版级 PNG</span><small>统计图</small></a>' : ''}
      ${STATE.currentPlotlyData ? '<a class="download-link" href="#" onclick="event.preventDefault();downloadPublicationStatChart(\'svg\');"><span>导出 SVG</span><small>矢量图</small></a>' : ''}
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
    list.innerHTML = examples.slice(0, 6).map(ex => `
      <a class="download-link" href="/api/examples/${ex.name}/download" target="_blank" rel="noreferrer">
        <span>${ex.name}</span><small>${ex.col_count || '-'}列</small>
      </a>
    `).join('');
  } catch (e) {}
}

// ── Bootstrap ──────────────────────────────────────────
function bootEmptyState() {
  updateMetricGrid();
  updatePreviewTable();
  updateDatasetMeta();
  updateDownloadList();
  updateDataMeta();
}

// ── Theme Selector ──────────────────────────────────────
function initThemeSelector() {
  const sel = el('chartThemeSelect');
  if (!sel) return;
  sel.addEventListener('change', () => {
    window.ACTIVE_THEME = sel.value;
    // Re-render chart if present
    if (STATE.currentPlotlyData && STATE.currentPlotlyData.length > 0) {
      renderChart(STATE.currentPlotlyData, buildThemedLayout(STATE.currentPlotlyLayout, window.ACTIVE_THEME));
    }
  });
}

function getActiveTheme() {
  const themeName = window.ACTIVE_THEME || 'CNS';
  return CHART_THEMES[themeName] || CHART_THEMES.CNS;
}

function buildThemedLayout(baseLayout, themeName) {
  const theme = CHART_THEMES[themeName] || CHART_THEMES.CNS;
  return Object.assign({}, baseLayout, {
    font: theme.font,
    paper_bgcolor: theme.paper_bg_color,
    plot_bgcolor: theme.plot_bg_color,
  });
}
