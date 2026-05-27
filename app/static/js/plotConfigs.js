/* ── Statistical Chart Catalog ─────────────────────────── */
/* Chart configurations with buildTraces/buildLayout pattern */

const STAT_CHART_CATALOG = {
  box_violin: {
    name: '箱线图',
    description: '分组箱线图，展示中位数、四分位数、离群值',
    buildTraces(chartData, colors) {
      const traces = chartData.traces || [];
      return traces.map((t, i) => ({
        type: 'box',
        name: t.name || `Group ${i + 1}`,
        y: t.values || [],
        marker: { color: colors[i % colors.length] },
        line: { width: 1.5 },
        fillcolor: hexToRgba(colors[i % colors.length], 0.15),
        boxmean: 'sd',
        boxpoints: 'outliers',
        jitter: 0.3,
        showlegend: traces.length > 1,
      }));
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.x_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        yaxis: { title: { text: chartData.y_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        boxmode: 'group',
      };
    },
  },

  bar_grouped: {
    name: '分组柱状图',
    description: '分组柱状图，适合分类变量频率可视化',
    buildTraces(chartData, colors) {
      const categories = chartData.categories || [];
      return (chartData.series || []).map((s, i) => ({
        type: 'bar',
        name: s.name || '',
        x: categories,
        y: s.values || [],
        marker: { color: colors[i % colors.length], opacity: 0.85 },
      }));
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.x_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        yaxis: { title: { text: chartData.y_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        barmode: 'group',
      };
    },
  },

  paired_box: {
    name: '配对箱线图',
    description: '配对比较箱线图，适合配对t检验和秩和检验',
    buildTraces(chartData, colors) {
      return [
        {
          type: 'box',
          name: chartData.var_1_name || 'Before',
          y: chartData.var_1_values || [],
          marker: { color: colors[0] },
          fillcolor: hexToRgba(colors[0], 0.15),
          boxmean: 'sd',
        },
        {
          type: 'box',
          name: chartData.var_2_name || 'After',
          y: chartData.var_2_values || [],
          marker: { color: colors[1] },
          fillcolor: hexToRgba(colors[1], 0.15),
          boxmean: 'sd',
        },
      ];
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || 'Paired Comparison', font: { size: 15, color: theme.font.color } },
        yaxis: { title: { text: 'Value', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        boxmode: 'group',
      };
    },
  },

  paired_bar: {
    name: '配对条形图',
    description: '配对分类比较条形图',
    buildTraces(chartData, colors) {
      return [
        {
          type: 'bar',
          name: chartData.var_1_name || 'Var 1',
          x: chartData.categories || [],
          y: chartData.var_1_counts || [],
          marker: { color: colors[0], opacity: 0.85 },
        },
        {
          type: 'bar',
          name: chartData.var_2_name || 'Var 2',
          x: chartData.categories || [],
          y: chartData.var_2_counts || [],
          marker: { color: colors[1], opacity: 0.85 },
        },
      ];
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        yaxis: { title: { text: 'Count', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        barmode: 'group',
      };
    },
  },

  scatter_regression: {
    name: '散点+回归线',
    description: '散点图带回归趋势线，适合相关分析',
    buildTraces(chartData, colors) {
      const traces = [{
        type: 'scatter',
        mode: 'markers',
        name: 'Data',
        x: chartData.x_values || [],
        y: chartData.y_values || [],
        marker: { color: colors[0], size: 8, opacity: 0.65 },
      }];
      // Add regression line if we have data
      if (chartData.x_values && chartData.x_values.length > 1) {
        const x = chartData.x_values.filter(v => v != null);
        const y = chartData.y_values.filter(v => v != null);
        if (x.length > 1 && y.length > 1) {
          const n = Math.min(x.length, y.length);
          const fitX = x.slice(0, n);
          const fitY = y.slice(0, n);
          const m = fitX.reduce((s, v, i) => s + v * fitY[i], 0) / n - (fitX.reduce((a, b) => a + b, 0) / n) * (fitY.reduce((a, b) => a + b, 0) / n);
          const mx2 = fitX.reduce((s, v) => s + v * v, 0) / n - (fitX.reduce((a, b) => a + b, 0) / n) ** 2;
          const slope = mx2 !== 0 ? m / mx2 : 0;
          const inter = fitY.reduce((a, b) => a + b, 0) / n - slope * fitX.reduce((a, b) => a + b, 0) / n;
          const xSorted = [...fitX].sort((a, b) => a - b);
          traces.push({
            type: 'scatter',
            mode: 'lines',
            name: `r = ${chartData.r || '--'}`,
            x: [xSorted[0], xSorted[xSorted.length - 1]],
            y: [inter + slope * xSorted[0], inter + slope * xSorted[xSorted.length - 1]],
            line: { color: colors[1] || '#D95F59', width: 2, dash: 'solid' },
          });
        }
      }
      return traces;
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.x_var || 'X', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        yaxis: { title: { text: chartData.y_var || 'Y', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
      };
    },
  },

  discriminant_scores: {
    name: '判别得分图',
    description: '按分类结局展示 LDA/QDA 得分空间中的样本分布',
    buildTraces(chartData, colors) {
      const labels = chartData.labels || [];
      const classes = chartData.classes?.length ? chartData.classes : [...new Set(labels)];
      const x = chartData.x_values || [];
      const y = chartData.y_values || [];
      return classes.map((className, i) => {
        const idx = labels
          .map((label, rowIndex) => String(label) === String(className) ? rowIndex : -1)
          .filter(rowIndex => rowIndex >= 0);
        return {
          type: 'scatter',
          mode: 'markers',
          name: String(className),
          x: idx.map(rowIndex => x[rowIndex]),
          y: idx.map(rowIndex => y[rowIndex]),
          marker: {
            color: colors[i % colors.length],
            size: 9,
            opacity: 0.78,
            line: { color: '#ffffff', width: 0.8 },
          },
        };
      });
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || 'Discriminant scores', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.x_label || 'LD1', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: true, zerolinecolor: '#CBD5E1' },
        yaxis: { title: { text: chartData.y_label || 'LD2', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: true, zerolinecolor: '#CBD5E1' },
      };
    },
  },

  repeated_measures: {
    name: '重复测量图',
    description: '重复测量折线图，展示个体趋势',
    buildTraces(chartData, colors) {
      const groups = chartData.groups || [];
      const values = chartData.values || {};
      // Individual lines
      const traces = [];
      const nSubj = (values[groups[0]] || []).length;
      for (let i = 0; i < Math.min(nSubj, 30); i++) {
        const yVals = groups.map(g => (values[g] || [])[i]);
        traces.push({
          type: 'scatter',
          mode: 'lines+markers',
          name: `S${i + 1}`,
          x: groups,
          y: yVals,
          line: { color: 'rgba(128,128,128,0.25)', width: 0.8 },
          marker: { size: 3, opacity: 0.3 },
          showlegend: false,
        });
      }
      // Mean line
      const means = groups.map(g => {
        const vals = (values[g] || []).filter(v => v != null);
        return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
      });
      traces.push({
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Mean',
        x: groups,
        y: means,
        line: { color: colors[0], width: 2.5 },
        marker: { size: 8, color: colors[0] },
        showlegend: true,
      });
      return traces;
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: 'Time Point', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        yaxis: { title: { text: 'Value', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
      };
    },
  },

  survival: {
    name: '生存曲线',
    description: 'Kaplan-Meier 生存曲线',
    buildTraces(chartData, colors) {
      // Survival curves need to be computed server-side; show placeholder
      return [{
        type: 'scatter',
        mode: 'lines',
        name: 'Survival',
        x: [0],
        y: [1],
        line: { color: colors[0], width: 2 },
      }];
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || 'Kaplan-Meier Survival', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.time_var || 'Time', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false, range: [0, null] },
        yaxis: { title: { text: 'Survival Probability', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false, range: [0, 1.05] },
      };
    },
  },

  histogram: {
    name: '直方图',
    description: '数据分布直方图',
    buildTraces(chartData, colors) {
      return [{
        type: 'histogram',
        name: chartData.traces?.[0]?.name || '',
        x: chartData.traces?.[0]?.values || [],
        marker: { color: colors[0], opacity: 0.75 },
        nbinsx: 25,
      }];
    },
    buildLayout(chartData, theme) {
      return {
        title: { text: chartData.title || '', font: { size: 15, color: theme.font.color } },
        xaxis: { title: { text: chartData.x_label || '', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
        yaxis: { title: { text: 'Count', font: { size: 12 } }, gridcolor: theme.grid_color, zeroline: false },
      };
    },
  },
};

function hexToRgba(hex, alpha) {
  if (!hex || hex.length < 7) return `rgba(13,115,119,${alpha})`;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function getStatChartConfig(chartType) {
  return STAT_CHART_CATALOG[chartType] || null;
}
