/* ── Export / Download Module ──────────────────────────── */

async function exportTableExcel() {
  const data = buildTableExportData();
  if (!data) return;
  try {
    const res = await fetch('/api/export/table-excel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table_data: data }),
    });
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    downloadBlob(blob, 'statistics_result.xlsx');
    toast('已导出 Excel', 'success');
  } catch (e) {
    toast('导出失败: ' + e.message, 'error');
  }
}

async function exportTableCSV() {
  const data = buildTableExportData();
  if (!data) return;
  try {
    const res = await fetch('/api/export/table-csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table_data: data }),
    });
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    downloadBlob(blob, 'statistics_result.csv');
    toast('已导出 CSV', 'success');
  } catch (e) {
    toast('导出失败: ' + e.message, 'error');
  }
}

async function exportTableHTML() {
  const data = buildTableExportData();
  if (!data) return;
  try {
    const res = await fetch('/api/export/table-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table_data: data }),
    });
    if (!res.ok) throw new Error('Export failed');
    const html = await res.text();
    const blob = new Blob([html], { type: 'text/html' });
    downloadBlob(blob, 'statistics_result.html');
    toast('已导出 HTML', 'success');
  } catch (e) {
    toast('导出失败: ' + e.message, 'error');
  }
}

async function copyTableToClipboard() {
  const data = buildTableExportData();
  if (!data || data.length === 0) {
    toast('无数据可复制', 'warning');
    return;
  }
  try {
    const keys = Object.keys(data[0]);
    const lines = [
      keys.join('\t'),
      ...data.map(row => keys.map(k => row[k] ?? '').join('\t')),
    ];
    const text = lines.join('\n');
    await navigator.clipboard.writeText(text);
    toast('已复制到剪贴板', 'success');
  } catch (e) {
    toast('复制失败: ' + e.message, 'error');
  }
}

function buildTableExportData() {
  if (STATE.currentTables) {
    const sections = [];
    const pushRows = (title, table) => {
      if (!table || !Array.isArray(table.rows)) return;
      table.rows.forEach(row => sections.push({ Section: title || table.title || 'Table', ...row }));
    };
    pushRows('核心结果', STATE.currentTables.result);
    pushRows('分组描述', STATE.currentTables.group_stats);
    pushRows('事后比较', STATE.currentTables.post_hoc);
    if (STATE.currentDiscussion?.sections) {
      STATE.currentDiscussion.sections.forEach(section => {
        (section.items || []).forEach((item, index) => {
          sections.push({ Section: '结果讨论', Metric: section.title, Value: item, Interpretation: index + 1 });
        });
      });
    }
    if (sections.length > 0) return sections;
  }
  if (STATE.currentTableData && STATE.currentTableData.length > 0) {
    return STATE.currentTableData;
  }
  // Fallback: collect from displayed result
  const result = STATE.currentResult;
  if (!result) { toast('请先执行分析', 'warning'); return null; }
  // Build a simple row
  return [{
    Test: result.test_name || '',
    Method: result.method || '',
    Statistic: result.statistic ?? '—',
    PValue: formatPValueDisplay(result.p_value),
    Significant: result.significant ? 'Yes (p < 0.05)' : 'No',
  }];
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadChartPNG() {
  if (!STATE.currentPlotlyData || !STATE.currentPlotlyLayout) {
    toast('请先执行分析生成图形', 'warning');
    return;
  }
  try {
    const container = el('chartPreviewContainer');
    const plotDiv = container?.querySelector('.js-plotly-plot');
    if (!plotDiv) { toast('无图形可导出', 'warning'); return; }
    const imgData = await Plotly.toImage(plotDiv, { format: 'png', width: 1200, height: 800, scale: 2 });
    const a = document.createElement('a');
    a.href = imgData;
    a.download = 'statistics_chart.png';
    a.click();
    toast('图形已导出 PNG', 'success');
  } catch (e) {
    toast('图形导出失败: ' + e.message, 'error');
  }
}

async function downloadPublicationStatChart(format = 'png') {
  if (!STATE.currentChartData) {
    toast('请先执行分析生成图形', 'warning');
    return;
  }
  const fmt = String(format || 'png').toLowerCase();
  const payload = {
    format: fmt,
    style: normalizePublicationStyleForStats(el('chartThemeSelect')?.value || 'CNS'),
    chart_data: STATE.currentChartData,
    title: STATE.currentChartData.title || STATE.currentResult?.test_name || 'Statistical result',
  };
  try {
    toast(`正在生成出版级 ${fmt.toUpperCase()}...`, 'info');
    const res = await fetch('/api/export/stat-chart/publication', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Export failed' }));
      throw new Error(err.detail || 'Export failed');
    }
    const blob = await res.blob();
    const filename = `statistics_${safeFilename(STATE.currentChartData.chart_type || 'chart')}_publication.${fmt}`;
    downloadBlob(blob, filename);
    toast(`出版级 ${fmt.toUpperCase()} 已导出`, 'success');
  } catch (e) {
    console.error('Publication export failed:', e);
    if (fmt === 'png') {
      toast('后端出版级导出失败，改用高分辨率 Plotly PNG', 'warning');
      await downloadChartPNG();
      return;
    }
    toast('出版级图形导出失败: ' + e.message, 'error');
  }
}

function normalizePublicationStyleForStats(style) {
  const value = String(style || '').toLowerCase();
  if (value.includes('nature')) return 'nature';
  return 'cns';
}

function safeFilename(value) {
  return String(value || 'chart')
    .trim()
    .replace(/[\\/:*?"<>|]+/g, '_')
    .replace(/\s+/g, '_')
    .slice(0, 80) || 'chart';
}
