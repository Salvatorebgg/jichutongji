/* ── Chart Themes & Color Palettes ──────────────────────── */
/* Ported from Basicpicture for publication-quality charts */

const CHART_THEMES = {
  CNS: {
    name: 'CNS',
    label: 'CNS 顶刊',
    colorway: ['#2E6F9E', '#D95F59', '#2A9D8F', '#E9A93A', '#6F5AA7', '#7C8B52', '#C776A5', '#4A5568'],
    font: { family: 'Noto Sans SC, Microsoft YaHei, Arial', size: 12, color: '#2d4a54' },
    plot_bg_color: '#fafdfb',
    paper_bg_color: '#ffffff',
    grid_color: '#e0ebe7',
    axis_color: '#1a2b32',
  },
  Nature: {
    name: 'Nature',
    label: 'Nature 风格',
    colorway: ['#3C5488', '#E64B35', '#00A087', '#4DBBD5', '#F39B7F', '#8491B4', '#91D1C2', '#7E6148'],
    font: { family: 'Noto Sans SC, Arial', size: 11, color: '#2d323e' },
    plot_bg_color: '#ffffff',
    paper_bg_color: '#ffffff',
    grid_color: '#eaecef',
    axis_color: '#1f2229',
  },
  Lancet: {
    name: 'Lancet',
    label: 'Lancet 风格',
    colorway: ['#00468B', '#ED0000', '#42B540', '#0099B4', '#925E9F', '#FDAF91', '#AD002A', '#ADB6B6'],
    font: { family: 'Noto Sans SC, Arial', size: 11, color: '#333333' },
    plot_bg_color: '#ffffff',
    paper_bg_color: '#ffffff',
    grid_color: '#e8e8e8',
    axis_color: '#222222',
  },
  NEJM: {
    name: 'NEJM',
    label: 'NEJM 风格',
    colorway: ['#1A3A5C', '#C0392B', '#27AE60', '#2980B9', '#8E44AD', '#D35400', '#16A085', '#7F8C8D'],
    font: { family: 'Noto Sans SC, Georgia', size: 12, color: '#222222' },
    plot_bg_color: '#fdfdfd',
    paper_bg_color: '#ffffff',
    grid_color: '#e6e6e6',
    axis_color: '#1a1a1a',
  },
  Science: {
    name: 'Science',
    label: 'Science 风格',
    colorway: ['#0C4B8E', '#BF2F38', '#3A7D44', '#CC7A2D', '#6B4C8A', '#4B8BBE', '#E69B47', '#95A5A6'],
    font: { family: 'Noto Sans SC, Helvetica', size: 11, color: '#333333' },
    plot_bg_color: '#ffffff',
    paper_bg_color: '#ffffff',
    grid_color: '#ebebeb',
    axis_color: '#1a1a1a',
  },
  warm: {
    name: 'warm',
    label: '暖色系',
    colorway: ['#D95F59', '#E9A93A', '#F39B7F', '#D35400', '#E67E22', '#C0392B', '#F1C40F', '#E74C3C'],
    font: { family: 'Noto Sans SC, Arial', size: 12, color: '#4a3030' },
    plot_bg_color: '#fffaf8',
    paper_bg_color: '#ffffff',
    grid_color: '#f0e4de',
    axis_color: '#3d2525',
  },
  cool: {
    name: 'cool',
    label: '冷色系',
    colorway: ['#2E6F9E', '#2A9D8F', '#4DBBD5', '#5BA4CF', '#2980B9', '#16A085', '#3498DB', '#1ABC9C'],
    font: { family: 'Noto Sans SC, Arial', size: 12, color: '#2a3a4a' },
    plot_bg_color: '#f8fafc',
    paper_bg_color: '#ffffff',
    grid_color: '#dfe8ef',
    axis_color: '#1a2b3c',
  },
  pastel: {
    name: 'pastel',
    label: '柔和色',
    colorway: ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2', '#96C37D', '#F6CFE3'],
    font: { family: 'Noto Sans SC, Arial', size: 12, color: '#4a4a4a' },
    plot_bg_color: '#fdfdfb',
    paper_bg_color: '#ffffff',
    grid_color: '#eeece6',
    axis_color: '#3a3a3a',
  },
  dark_muted: {
    name: 'dark_muted',
    label: '暗色系',
    colorway: ['#4A5568', '#718096', '#A0AEC0', '#2D3748', '#553C9A', '#6B46C1', '#2B6CB0', '#276749'],
    font: { family: 'Noto Sans SC, Arial', size: 12, color: '#e2e8f0' },
    plot_bg_color: '#2d3748',
    paper_bg_color: '#1a202c',
    grid_color: '#4a5568',
    axis_color: '#cbd5e0',
  },
  mono: {
    name: 'mono',
    label: '黑白灰',
    colorway: ['#1a1a1a', '#4d4d4d', '#808080', '#b3b3b3', '#333333', '#666666', '#999999', '#cccccc'],
    font: { family: 'Noto Sans SC, Arial', size: 12, color: '#1a1a1a' },
    plot_bg_color: '#ffffff',
    paper_bg_color: '#ffffff',
    grid_color: '#e0e0e0',
    axis_color: '#1a1a1a',
  },
};

const COLOR_PALETTES = {
  tableau10: ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC'],
  set2: ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'],
  paired: ['#A6CEE3', '#1F78B4', '#B2DF8A', '#33A02C', '#FB9A99', '#E31A1C', '#FDBF6F', '#FF7F00', '#CAB2D6', '#6A3D9A'],
  dark2: ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02', '#A6761D', '#666666'],
  accent: ['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666'],
  viridis: ['#440154', '#482878', '#3E4A89', '#31688E', '#26828E', '#1F9E89', '#35B779', '#6DCD59', '#B4DE2C', '#FDE725'],
  plasma: ['#0D0887', '#46039F', '#7201A8', '#9C179E', '#BD3786', '#D8576B', '#ED7953', '#FB9F3A', '#FDCA26', '#F0F921'],
};

const ACTIVE_THEME = 'CNS';
const ACTIVE_PALETTE = 'cns';

function getActiveTheme() {
  return CHART_THEMES[ACTIVE_THEME] || CHART_THEMES.CNS;
}

function getActiveColors() {
  const theme = getActiveTheme();
  return theme.colorway;
}

function getPaletteColors(paletteName, n) {
  const source = COLOR_PALETTES[paletteName] || COLOR_PALETTES.tableau10;
  const result = [];
  for (let i = 0; i < n; i++) {
    result.push(source[i % source.length]);
  }
  return result;
}
