"""
CNS-level publication quality chart generation service.
Uses matplotlib and seaborn with professional styling.
"""
from __future__ import annotations

import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from scipy import stats

mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'Arial', 'Helvetica', 'DejaVu Sans']
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['axes.linewidth'] = 1.2
mpl.rcParams['xtick.major.width'] = 1.2
mpl.rcParams['ytick.major.width'] = 1.2
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['ytick.major.size'] = 5
mpl.rcParams['xtick.minor.size'] = 3
mpl.rcParams['ytick.minor.size'] = 3
mpl.rcParams['legend.frameon'] = False
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

CNS_PALETTE = ['#2E6F9E', '#D95F59', '#2A9D8F', '#E9A93A', '#6F5AA7',
               '#7C8B52', '#C776A5', '#4A5568', '#8F6B43', '#5BA4CF']

NATURE_PALETTE = ['#3C5488', '#E64B35', '#00A087', '#4DBBD5', '#F39B7F',
                  '#8491B4', '#91D1C2', '#7E6148']

MAP_PALETTE = ['#F6F0F2', '#E9B44C', '#4AA3A2', '#2E6F9E', '#403B8A']

_USER_PALETTE: list[str] | None = None
_USER_MARKER_SIZE: float = 8.0
_USER_LINE_WIDTH: float = 2.5

COUNTRY_TO_ISO3 = {
    "china": "CHN", "united states": "USA", "united states of america": "USA",
    "usa": "USA", "india": "IND", "japan": "JPN", "germany": "DEU",
    "brazil": "BRA", "russia": "RUS", "russian federation": "RUS",
    "united kingdom": "GBR", "uk": "GBR", "france": "FRA", "italy": "ITA",
    "canada": "CAN", "australia": "AUS", "korea, south": "KOR",
    "south korea": "KOR", "republic of korea": "KOR", "indonesia": "IDN",
    "nigeria": "NGA", "south africa": "ZAF", "mexico": "MEX",
    "turkey": "TUR", "thailand": "THA", "vietnam": "VNM", "viet nam": "VNM",
    "egypt": "EGY", "pakistan": "PAK", "bangladesh": "BGD", "philippines": "PHL",
}


def set_publication_style(style: str = 'cns', colors: list[str] | None = None,
                          marker_size: float | None = None, line_width: float | None = None):
    global _USER_PALETTE, _USER_MARKER_SIZE, _USER_LINE_WIDTH
    if colors and len(colors) > 0:
        _USER_PALETTE = colors
        palette = colors
    else:
        _USER_PALETTE = None
        palette = NATURE_PALETTE if style == 'nature' else CNS_PALETTE
    _USER_MARKER_SIZE = marker_size if marker_size is not None else 8.0
    _USER_LINE_WIDTH = line_width if line_width is not None else 2.5
    sns.set_palette(palette)
    sns.set_style('white', {
        'axes.edgecolor': '.15', 'axes.linewidth': 1.2,
        'grid.color': '.88', 'grid.linewidth': 0.6,
    })
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'Arial', 'Helvetica', 'DejaVu Sans']
    mpl.rcParams['axes.unicode_minus'] = False


def _get_palette(style: str = 'cns') -> list[str]:
    if _USER_PALETTE and len(_USER_PALETTE) > 0:
        return _USER_PALETTE
    return NATURE_PALETTE if style == 'nature' else CNS_PALETTE


def _get_marker_size() -> float:
    return _USER_MARKER_SIZE * 7


def _get_line_width() -> float:
    return _USER_LINE_WIDTH


def _map_cmap(style: str = 'cns'):
    colors = ['#F7FBFF', '#BBD7EA', '#4F93B7', '#164A73'] if style == 'nature' else MAP_PALETTE
    return mpl.colors.LinearSegmentedColormap.from_list('cns_map', colors)


def _country_to_iso3(value: object) -> str:
    raw = str(value or '').strip()
    if len(raw) == 3 and raw.isalpha():
        return raw.upper()
    return COUNTRY_TO_ISO3.get(raw.lower(), '')


def _add_axis_arrows(ax):
    x0, x1 = ax.spines['bottom'].get_bounds()
    y0, y1 = ax.spines['left'].get_bounds()
    spine_lw = ax.spines['bottom'].get_linewidth()
    color = ax.spines['bottom'].get_edgecolor()
    fig = ax.get_figure()
    trans = ax.transData
    inv = trans.inverted()
    pts_to_px = fig.dpi / 72.0
    spine_hw_px = spine_lw * pts_to_px * 0.5
    arrow_length_px = 10.0 * pts_to_px
    arrow_half_w_px = 3.5 * pts_to_px
    overlap_px = 2.0 * pts_to_px

    # X-axis arrow
    tip_disp = trans.transform((x1, y0))
    pts_disp_x = [
        (tip_disp[0] + arrow_length_px, tip_disp[1]),
        (tip_disp[0] - overlap_px, tip_disp[1] + arrow_half_w_px),
        (tip_disp[0] - overlap_px, tip_disp[1] + spine_hw_px),
        (tip_disp[0] - overlap_px, tip_disp[1] - spine_hw_px),
        (tip_disp[0] - overlap_px, tip_disp[1] - arrow_half_w_px),
    ]
    pts_data_x = inv.transform(pts_disp_x)
    ax.fill([pts_data_x[0][0], pts_data_x[1][0], pts_data_x[2][0],
             pts_data_x[3][0], pts_data_x[4][0]],
            [pts_data_x[0][1], pts_data_x[1][1], pts_data_x[2][1],
             pts_data_x[3][1], pts_data_x[4][1]],
            facecolor=color, edgecolor='none',
            clip_on=False, zorder=100, antialiased=True)

    # Y-axis arrow
    tip_disp_y = trans.transform((x0, y1))
    pts_disp_y = [
        (tip_disp_y[0], tip_disp_y[1] + arrow_length_px),
        (tip_disp_y[0] + arrow_half_w_px, tip_disp_y[1] - overlap_px),
        (tip_disp_y[0] + spine_hw_px, tip_disp_y[1] - overlap_px),
        (tip_disp_y[0] - spine_hw_px, tip_disp_y[1] - overlap_px),
        (tip_disp_y[0] - arrow_half_w_px, tip_disp_y[1] - overlap_px),
    ]
    pts_data_y = inv.transform(pts_disp_y)
    ax.fill([pts_data_y[0][0], pts_data_y[1][0], pts_data_y[2][0],
             pts_data_y[3][0], pts_data_y[4][0]],
            [pts_data_y[0][1], pts_data_y[1][1], pts_data_y[2][1],
             pts_data_y[3][1], pts_data_y[4][1]],
            facecolor=color, edgecolor='none',
            clip_on=False, zorder=100, antialiased=True)


def _save_figure(fig: plt.Figure) -> tuple[bytes, bytes, bytes]:
    png_buf = io.BytesIO()
    fig.savefig(png_buf, format='png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    png_buf.seek(0)
    png_bytes = png_buf.read()

    svg_buf = io.BytesIO()
    fig.savefig(svg_buf, format='svg', bbox_inches='tight', facecolor='white',
               edgecolor='none')
    svg_buf.seek(0)
    svg_bytes = svg_buf.read()

    pdf_buf = io.BytesIO()
    fig.savefig(pdf_buf, format='pdf', bbox_inches='tight', facecolor='white',
               edgecolor='none')
    pdf_buf.seek(0)
    pdf_bytes = pdf_buf.read()

    plt.close(fig)
    return png_bytes, svg_bytes, pdf_bytes


# ═══ Chart Generators ═══════════════════════════════════════

def generate_scatter_plot(
    df: pd.DataFrame, x_var: str, y_var: str,
    color_var: str | None = None, title: str = '',
    style: str = 'cns', figsize: tuple[float, float] = (6.5, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    ms = _get_marker_size()
    fig, ax = plt.subplots(figsize=figsize)

    if color_var and color_var in df.columns:
        groups = df[color_var].unique()
        for i, group in enumerate(groups):
            mask = df[color_var] == group
            ax.scatter(df.loc[mask, x_var], df.loc[mask, y_var],
                       label=str(group), color=palette[i % len(palette)],
                       s=ms, alpha=0.72, edgecolors='white', linewidths=0.4)
        ax.legend(frameon=False, loc='best', fontsize=10,
                  handletextpad=0.8, markerscale=0.9)
    else:
        ax.scatter(df[x_var], df[y_var], color=palette[0],
                   s=ms, alpha=0.72, edgecolors='white', linewidths=0.4)

    ax.set_xlabel(x_var, fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel(y_var, fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_box_plot(
    df: pd.DataFrame, y_var: str, x_var: str | None = None,
    color_var: str | None = None, title: str = '',
    style: str = 'cns', figsize: tuple[float, float] = (7.5, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    sns.violinplot(data=df, x=x_var, y=y_var, hue=color_var,
                   palette=palette, ax=ax, inner=None, alpha=0.25,
                   linewidth=0, cut=0)
    sns.boxplot(data=df, x=x_var, y=y_var, hue=color_var,
                palette=palette, ax=ax, width=0.28,
                boxprops=dict(alpha=0.82, linewidth=1.4, zorder=2),
                whiskerprops=dict(linewidth=1.4),
                capprops=dict(linewidth=1.4),
                medianprops=dict(color='#1a1a1a', linewidth=2.2),
                flierprops=dict(marker='o', markersize=3.5, alpha=0.45))

    if x_var:
        sns.stripplot(data=df, x=x_var, y=y_var, hue=color_var,
                      palette=palette, ax=ax, size=3, alpha=0.35,
                      dodge=True, jitter=0.18, zorder=1)

    ax.set_xlabel(x_var if x_var else '', fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel(y_var, fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        n_groups = len(set(labels))
        ax.legend(handles[:n_groups], labels[:n_groups],
                  frameon=False, loc='best', fontsize=10)

    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_bar_plot(
    df: pd.DataFrame, x_var: str, y_var: str,
    color_var: str | None = None, title: str = '',
    style: str = 'cns', figsize: tuple[float, float] = (8, 5.5),
    show_error: bool = True,
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    if color_var and color_var in df.columns:
        grouped = df.groupby([x_var, color_var])[y_var].agg(['mean', 'sem']).reset_index()
        x_labels = grouped[x_var].unique()
        colors_unique = grouped[color_var].unique()
        width = 0.8 / len(colors_unique)
        x_pos = np.arange(len(x_labels))
        for i, color_val in enumerate(colors_unique):
            subset = grouped[grouped[color_var] == color_val]
            offset = (i - len(colors_unique) / 2 + 0.5) * width
            ax.bar(x_pos + offset, subset['mean'], width,
                   label=str(color_val), color=palette[i % len(palette)],
                   alpha=0.88, edgecolor='white', linewidth=0.8)
            if show_error:
                ax.errorbar(x_pos + offset, subset['mean'],
                            yerr=subset['sem'], fmt='none',
                            ecolor='#333', elinewidth=1.4,
                            capsize=4, capthick=1.4)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=35, ha='right', fontsize=10)
        ax.legend(frameon=False, loc='best', fontsize=10)
    else:
        grouped = df.groupby(x_var)[y_var].agg(['mean', 'sem']).reset_index()
        ax.bar(range(len(grouped)), grouped['mean'], color=palette,
               alpha=0.88, edgecolor='white', linewidth=0.8, width=0.65)
        if show_error:
            ax.errorbar(range(len(grouped)), grouped['mean'],
                        yerr=grouped['sem'], fmt='none',
                        ecolor='#333', elinewidth=1.4, capsize=4, capthick=1.4)
        ax.set_xticks(range(len(grouped)))
        ax.set_xticklabels(grouped[x_var], rotation=35, ha='right', fontsize=10)

    ax.set_xlabel(x_var, fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel(y_var, fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_line_plot(
    df: pd.DataFrame, x_var: str, y_var: str,
    color_var: str | None = None, title: str = '',
    style: str = 'cns', figsize: tuple[float, float] = (7, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    lw = _get_line_width()
    fig, ax = plt.subplots(figsize=figsize)

    if color_var and color_var in df.columns:
        for i, (name, grp) in enumerate(df.groupby(color_var)):
            grp_sorted = grp.sort_values(x_var)
            ax.plot(grp_sorted[x_var], grp_sorted[y_var],
                    color=palette[i % len(palette)], linewidth=lw,
                    marker='o', markersize=5, label=str(name),
                    markeredgecolor='white', markeredgewidth=0.5)
        ax.legend(frameon=False, loc='best', fontsize=10)
    else:
        df_sorted = df.sort_values(x_var)
        ax.plot(df_sorted[x_var], df_sorted[y_var],
                color=palette[0], linewidth=lw,
                marker='o', markersize=5, markeredgecolor='white',
                markeredgewidth=0.5)

    ax.set_xlabel(x_var, fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel(y_var, fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_forest_plot(
    df: pd.DataFrame, label_var: str, or_var: str,
    ci_lower_var: str, ci_upper_var: str,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] = (7, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    labels = df[label_var].values
    or_vals = df[or_var].values
    ci_l = df[ci_lower_var].values
    ci_u = df[ci_upper_var].values
    y_positions = range(len(labels) - 1, -1, -1)

    for i, (y, or_val, lo, hi) in enumerate(zip(y_positions, or_vals, ci_l, ci_u)):
        color = palette[1] if or_val < 1 else palette[0]
        ax.errorbar(or_val, y, xerr=[[or_val - lo], [hi - or_val]],
                    fmt='o', color=color, ecolor='#555',
                    elinewidth=1.5, capsize=4, capthick=1.5,
                    markersize=9, markeredgecolor='white',
                    markeredgewidth=0.6)

    ax.axvline(x=1, color='#999', linewidth=1, linestyle='--', alpha=0.7)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Odds Ratio (95% CI)', fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    ax.set_xscale('log')
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_survival_plot(
    df: pd.DataFrame, time_var: str, event_var: str,
    group_var: str | None = None, title: str = '',
    style: str = 'cns', figsize: tuple[float, float] = (7, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    if group_var and group_var in df.columns:
        df_groups = df.groupby(group_var)
    else:
        df_groups = [('All', df)]

    for i, (name, group_df) in enumerate(df_groups):
        times = group_df[time_var].values
        events = group_df[event_var].values
        sorted_idx = np.argsort(times)
        times_sorted = times[sorted_idx]
        events_sorted = events[sorted_idx]
        n = len(times_sorted)
        surv = 1.0
        steps_t = [0]
        steps_s = [1.0]
        at_risk = n
        for t, e in zip(times_sorted, events_sorted):
            if e == 1 and at_risk > 0:
                surv *= (1 - 1 / at_risk)
            at_risk -= 1
            steps_t.append(t)
            steps_s.append(max(0, surv))
        label = str(name) if group_var else 'Survival'
        ax.step(steps_t, steps_s, where='post',
                color=palette[i % len(palette)], linewidth=_get_line_width(),
                label=label)

    ax.set_xlabel(time_var, fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel('Survival Probability', fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylim(0, 1.05)
    if group_var and group_var in df.columns:
        ax.legend(frameon=False, loc='lower left', fontsize=10)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_roc_plot(
    df: pd.DataFrame, outcome_var: str, predictor_var: str,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] = (6, 5.5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    outcome = df[outcome_var].values
    predictor = df[predictor_var].values
    order = np.argsort(predictor)[::-1]
    outcome_sorted = outcome[order]
    n_pos = np.sum(outcome_sorted == 1)
    n_neg = np.sum(outcome_sorted == 0)

    if n_pos == 0 or n_neg == 0:
        ax.text(0.5, 0.5, 'Insufficient data for ROC', ha='center', va='center',
                transform=ax.transAxes, fontsize=13)
    else:
        tp, fp = 0, 0
        tpr, fpr = [0], [0]
        for o in outcome_sorted:
            if o == 1:
                tp += 1
            else:
                fp += 1
            tpr.append(tp / n_pos)
            fpr.append(fp / n_neg)
        tpr.append(1)
        fpr.append(1)
        _trapz = getattr(np, 'trapezoid', None) or np.trapz
        auc = _trapz(tpr, fpr)
        ax.plot(fpr, tpr, color=palette[0], linewidth=_get_line_width(),
                label=f'ROC (AUC = {auc:.3f})')
        ax.plot([0, 1], [0, 1], '--', color='#999', linewidth=1.2, label='Random')
        ax.fill_between(fpr, tpr, alpha=0.12, color=palette[0])
        ax.legend(frameon=False, loc='lower right', fontsize=10)

    ax.set_xlabel('1 - Specificity (FPR)', fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel('Sensitivity (TPR)', fontsize=13, fontweight='medium', labelpad=8)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_heatmap(
    df: pd.DataFrame, value_vars: list[str] | None = None,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] | None = None,
    correlation: bool = True,
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)

    if value_vars:
        data = df[value_vars]
    else:
        data = df.select_dtypes(include=[np.number])
    matrix = data.corr() if correlation else data
    n = len(matrix.columns)

    if figsize is None:
        base = max(8, n * 0.35)
        figsize = (base + 1.5, base)

    if correlation:
        vmin, vmax = -1, 1
        cmap = sns.diverging_palette(240, 15, s=85, l=45, as_cmap=True)
        fmt = '.2f'
    else:
        vmin, vmax = None, None
        cmap = sns.color_palette("mako", as_cmap=True)
        fmt = '.1f'

    fig, ax = plt.subplots(figsize=figsize)
    show_annot = n <= 35
    annot_size = max(5, min(10, 260 // max(n, 1)))

    sns.heatmap(
        matrix, annot=show_annot, fmt=fmt, cmap=cmap,
        vmin=vmin, vmax=vmax, center=0 if correlation else None,
        square=True, linewidths=0.3, linecolor='white',
        cbar_kws={
            'shrink': 0.85, 'aspect': 35, 'pad': 0.02,
            'label': 'Correlation (r)' if correlation else 'Value',
        },
        ax=ax, annot_kws={'fontsize': annot_size, 'color': 'auto'},
    )

    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    tick_size = max(7, min(11, 400 // max(n, 1)))
    ax.tick_params(labelsize=tick_size)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    plt.setp(ax.get_yticklabels(), rotation=0)
    for _, spine in ax.spines.items():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_color('#cccccc')
    plt.tight_layout()
    return _save_figure(fig)


def generate_histogram(
    df: pd.DataFrame, x_var: str, color_var: str | None = None,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] = (7, 5),
) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)

    if color_var and color_var in df.columns:
        for i, (name, grp) in enumerate(df.groupby(color_var)):
            ax.hist(grp[x_var].dropna(), bins=25, alpha=0.45,
                    color=palette[i % len(palette)], label=str(name),
                    edgecolor='white', linewidth=0.6, density=True)
        ax.legend(frameon=False, loc='best', fontsize=10)
    else:
        ax.hist(df[x_var].dropna(), bins=28, alpha=0.75,
                color=palette[0], edgecolor='white',
                linewidth=0.6, density=True)

    ax.set_xlabel(x_var, fontsize=13, fontweight='medium', labelpad=8)
    ax.set_ylabel('Density', fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)


def generate_china_map(
    df: pd.DataFrame, province_var: str, value_var: str,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] = (8.8, 7.2),
) -> tuple[bytes, bytes, bytes]:
    from pathlib import Path
    geojson_path = Path(__file__).parent.parent / 'static' / 'china_provinces.geojson'
    if not geojson_path.exists():
        return _china_map_fallback(df, province_var, value_var, title, style, figsize)

    try:
        import geopandas as gpd
    except ImportError:
        return _china_map_fallback(df, province_var, value_var, title, style, figsize)

    set_publication_style(style)
    cmap = _map_cmap(style)
    china = gpd.read_file(geojson_path)
    if china.crs is None:
        china = china.set_crs('EPSG:4326')

    province_vals = {}
    for _, row in df.iterrows():
        key = str(row[province_var]).lower().strip()
        cn_to_en = {
            '北京': 'beijing', '上海': 'shanghai', '广东': 'guangdong',
            '浙江': 'zhejiang', '江苏': 'jiangsu', '山东': 'shandong',
            '河南': 'henan', '河北': 'hebei', '四川': 'sichuan',
            '湖北': 'hubei', '湖南': 'hunan', '福建': 'fujian',
            '江西': 'jiangxi', '安徽': 'anhui', '山西': 'shanxi',
            '陕西': 'shaanxi', '甘肃': 'gansu', '辽宁': 'liaoning',
            '吉林': 'jilin', '黑龙江': 'heilongjiang', '云南': 'yunnan',
            '贵州': 'guizhou', '广西': 'guangxi', '海南': 'hainan',
            '天津': 'tianjin', '重庆': 'chongqing', '新疆': 'xinjiang',
            '西藏': 'xizang', '内蒙古': 'inner mongol',
            '宁夏': 'ningxia', '青海': 'qinghai', '台湾': 'taiwan',
            '香港': 'hong kong', '澳门': 'macau',
            'tibet': 'xizang', 'nei menggu': 'inner mongol',
            'inner mongolia': 'inner mongol',
        }
        mapped_key = cn_to_en.get(key, key)
        province_vals[mapped_key] = row[value_var]

    china['value'] = china['id'].map(province_vals)
    fig, ax = plt.subplots(figsize=figsize)
    china.plot(ax=ax, color='#F3F1EF', edgecolor='#CBD5DA', linewidth=0.42)
    china.dropna(subset=['value']).plot(
        column='value', ax=ax, cmap=cmap,
        edgecolor='white', linewidth=0.58,
    )

    finite_vals = china['value'].dropna()
    if not finite_vals.empty:
        norm = mpl.colors.Normalize(vmin=float(finite_vals.min()), vmax=float(finite_vals.max()))
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.032, pad=0.018)
        cbar.set_label(value_var, fontsize=10, labelpad=8)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(labelsize=8, length=3, width=0.8)

    for _, row in china.iterrows():
        centroid = row.geometry.representative_point()
        cn_name = row.get('name_cn', row['name_en'])
        ax.annotate(cn_name, (centroid.x, centroid.y),
                    ha='center', va='center', fontsize=6.2,
                    color='#263238', fontweight='medium')

    ax.set_aspect('equal')
    ax.set_xlim(72, 136.5)
    ax.set_ylim(16, 54.8)
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=18)
    plt.tight_layout()
    return _save_figure(fig)


def generate_world_map(
    df: pd.DataFrame, country_var: str, value_var: str,
    title: str = '', style: str = 'cns',
    figsize: tuple[float, float] = (10.5, 5.8),
) -> tuple[bytes, bytes, bytes]:
    from pathlib import Path
    geojson_path = Path(__file__).parent.parent / 'static' / 'world_countries.geojson'
    if not geojson_path.exists():
        return generate_bar_plot(df, country_var, value_var, None, title, style, figsize)

    try:
        import geopandas as gpd
    except ImportError:
        return generate_bar_plot(df, country_var, value_var, None, title, style, figsize)

    set_publication_style(style)
    cmap = _map_cmap(style)
    world = gpd.read_file(geojson_path)
    if world.crs is None:
        world = world.set_crs('EPSG:4326')

    country_vals: dict[str, float] = {}
    country_names: dict[str, str] = {}
    for _, row in df.iterrows():
        iso = _country_to_iso3(row[country_var])
        if not iso:
            continue
        value = pd.to_numeric(row[value_var], errors='coerce')
        if pd.notna(value):
            country_vals[iso] = float(value)
            country_names[iso] = str(row[country_var])

    world['value'] = world['ISO_A3'].map(country_vals)
    fig, ax = plt.subplots(figsize=figsize)
    world.plot(ax=ax, color='#F1F4F2', edgecolor='#D7DEE3', linewidth=0.28)
    world.dropna(subset=['value']).plot(
        column='value', ax=ax, cmap=cmap,
        edgecolor='white', linewidth=0.36,
    )

    finite_vals = world['value'].dropna()
    if not finite_vals.empty:
        norm = mpl.colors.Normalize(vmin=float(finite_vals.min()), vmax=float(finite_vals.max()))
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.026, pad=0.012)
        cbar.set_label(value_var, fontsize=10, labelpad=8)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(labelsize=8, length=3, width=0.8)

    labelled = (
        world.dropna(subset=['value'])
        .sort_values('value', ascending=False)
        .head(12)
    )
    for _, row in labelled.iterrows():
        x = row.get('LABEL_X')
        y = row.get('LABEL_Y')
        if pd.isna(x) or pd.isna(y):
            point = row.geometry.representative_point()
            x, y = point.x, point.y
        label = country_names.get(row['ISO_A3'], row.get('NAME_EN', row.get('NAME', row['ISO_A3'])))
        ax.annotate(f"{label}\n{row['value']:.1f}", (x, y),
                    ha='center', va='center', fontsize=6.5, color='#263238')

    ax.set_xlim(-180, 180)
    ax.set_ylim(-58, 84)
    ax.set_aspect('equal')
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=16)
    plt.tight_layout()
    return _save_figure(fig)


def generate_statistical_chart(
    chart_data: dict,
    title: str = '',
    style: str = 'cns',
    figsize: tuple[float, float] = (7.6, 5.6),
) -> tuple[bytes, bytes, bytes]:
    """Generate a publication-quality image from statistical result chart_data."""
    chart_type = chart_data.get("chart_type", "")
    title = title or chart_data.get("title", "") or "Statistical result"

    if chart_type == "box_violin":
        return _generate_stat_box_violin(chart_data, title, style, figsize)
    if chart_type == "paired_box":
        return _generate_stat_paired_box(chart_data, title, style, figsize)
    if chart_type in {"bar_grouped", "paired_bar"}:
        return _generate_stat_bar(chart_data, title, style, figsize)
    if chart_type == "scatter_regression":
        return _generate_stat_scatter(chart_data, title, style, figsize)
    if chart_type == "discriminant_scores":
        return _generate_stat_discriminant_scores(chart_data, title, style, figsize)
    if chart_type == "histogram":
        return _generate_stat_histogram(chart_data, title, style, figsize)
    if chart_type == "repeated_measures":
        return _generate_stat_repeated_measures(chart_data, title, style, figsize)

    return _generate_stat_fallback(chart_data, title, style, figsize)


def _generate_stat_box_violin(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    rows = []
    for trace in chart_data.get("traces", []):
        group = trace.get("name", "Group")
        for value in _clean_values(trace.get("values", [])):
            rows.append({"Group": str(group), "Value": value})
    df_plot = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=figsize)
    if df_plot.empty:
        ax.text(0.5, 0.5, "No plottable data", ha="center", va="center", transform=ax.transAxes)
    else:
        group_palette = _palette_for_categories(df_plot["Group"], palette)
        sns.violinplot(data=df_plot, x="Group", y="Value", hue="Group", palette=group_palette,
                       legend=False, inner=None, cut=0, linewidth=0, ax=ax)
        sns.boxplot(
            data=df_plot, x="Group", y="Value", hue="Group", palette=group_palette, legend=False,
            width=0.28, ax=ax,
            boxprops={"alpha": 0.86, "linewidth": 1.3},
            whiskerprops={"linewidth": 1.2},
            capprops={"linewidth": 1.2},
            medianprops={"color": "#111827", "linewidth": 2},
            flierprops={"marker": "o", "markersize": 3, "alpha": 0.35},
        )
        sns.stripplot(data=df_plot, x="Group", y="Value", hue="Group", palette=group_palette,
                      legend=False, size=3.2, alpha=0.42, jitter=0.18, ax=ax)
        ax.set_xlabel(chart_data.get("x_label", "Group"), fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel(chart_data.get("y_label", "Value"), fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_paired_box(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    a = _clean_values(chart_data.get("var_1_values", []))
    b = _clean_values(chart_data.get("var_2_values", []))
    n = min(len(a), len(b))
    groups = [str(chart_data.get("var_1_name", "Before")), str(chart_data.get("var_2_name", "After"))]
    long_df = pd.DataFrame({
        "Group": [groups[0]] * n + [groups[1]] * n,
        "Value": a[:n] + b[:n],
    })
    fig, ax = plt.subplots(figsize=figsize)
    if long_df.empty:
        ax.text(0.5, 0.5, "No paired data", ha="center", va="center", transform=ax.transAxes)
    else:
        group_palette = _palette_for_categories(long_df["Group"], palette)
        sns.violinplot(data=long_df, x="Group", y="Value", hue="Group", palette=group_palette,
                       legend=False, inner=None, cut=0, linewidth=0, ax=ax)
        sns.boxplot(data=long_df, x="Group", y="Value", hue="Group", palette=group_palette,
                    legend=False, width=0.25, ax=ax,
                    medianprops={"color": "#111827", "linewidth": 2})
        max_lines = min(n, 120)
        for i in range(max_lines):
            ax.plot([0, 1], [a[i], b[i]], color="#64748B", alpha=0.16, linewidth=0.8, zorder=0)
        ax.scatter(np.zeros(max_lines), a[:max_lines], color=palette[0], s=18, alpha=0.58, edgecolors="white", linewidths=0.4)
        ax.scatter(np.ones(max_lines), b[:max_lines], color=palette[1 % len(palette)], s=18, alpha=0.58, edgecolors="white", linewidths=0.4)
        ax.set_xlabel("", fontsize=13)
        ax.set_ylabel("Value", fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_bar(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    if chart_data.get("chart_type") == "paired_bar":
        series = [
            {"name": chart_data.get("var_1_name", "Var 1"), "values": chart_data.get("var_1_counts", [])},
            {"name": chart_data.get("var_2_name", "Var 2"), "values": chart_data.get("var_2_counts", [])},
        ]
        categories = chart_data.get("categories", [])
    else:
        series = chart_data.get("series", [])
        categories = chart_data.get("categories", [])

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(categories))
    if not categories or not series:
        ax.text(0.5, 0.5, "No categorical data", ha="center", va="center", transform=ax.transAxes)
    else:
        width = 0.78 / max(len(series), 1)
        for i, row in enumerate(series):
            values = [float(v) if pd.notna(v) else 0 for v in row.get("values", [])]
            offset = (i - (len(series) - 1) / 2) * width
            bars = ax.bar(
                x + offset, values, width=width, label=str(row.get("name", f"Series {i + 1}")),
                color=palette[i % len(palette)], alpha=0.9, edgecolor="white", linewidth=0.8,
            )
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:g}", ha="center",
                        va="bottom", fontsize=8, color="#334155")
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in categories], rotation=25, ha="right")
        if len(series) > 1:
            ax.legend(frameon=False, fontsize=10, ncol=min(3, len(series)))
        ax.set_xlabel(chart_data.get("x_label", ""), fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel(chart_data.get("y_label", "Count"), fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_scatter(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    x = _clean_values(chart_data.get("x_values", []))
    y = _clean_values(chart_data.get("y_values", []))
    n = min(len(x), len(y))
    x = x[:n]
    y = y[:n]
    fig, ax = plt.subplots(figsize=figsize)
    if n < 2:
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.scatter(x, y, color=palette[0], s=_get_marker_size(), alpha=0.72, edgecolors="white", linewidths=0.45)
        slope, intercept = np.polyfit(x, y, 1)
        xs = np.linspace(min(x), max(x), 100)
        ax.plot(xs, slope * xs + intercept, color=palette[1 % len(palette)], linewidth=_get_line_width())
        if chart_data.get("r") is not None:
            ax.text(0.03, 0.96, f"r = {chart_data.get('r')}, p = {chart_data.get('p_value')}",
                    transform=ax.transAxes, ha="left", va="top", fontsize=10,
                    bbox={"boxstyle": "round,pad=0.28", "fc": "white", "ec": "#E2E8F0", "lw": 0.8})
        ax.set_xlabel(chart_data.get("x_var", "X"), fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel(chart_data.get("y_var", "Y"), fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_discriminant_scores(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    x = _clean_values(chart_data.get("x_values", []))
    y = _clean_values(chart_data.get("y_values", []))
    labels = [str(v) for v in chart_data.get("labels", [])]
    n = min(len(x), len(y), len(labels))
    fig, ax = plt.subplots(figsize=figsize)
    if n < 2:
        ax.text(0.5, 0.5, "Insufficient discriminant scores", ha="center", va="center", transform=ax.transAxes)
    else:
        plot_df = pd.DataFrame({"x": x[:n], "y": y[:n], "Class": labels[:n]})
        for i, (class_name, group_df) in enumerate(plot_df.groupby("Class", sort=False)):
            ax.scatter(
                group_df["x"], group_df["y"],
                label=str(class_name),
                color=palette[i % len(palette)],
                s=_get_marker_size(),
                alpha=0.76,
                edgecolors="white",
                linewidths=0.5,
            )
            if len(group_df) >= 3:
                center_x = float(group_df["x"].mean())
                center_y = float(group_df["y"].mean())
                ax.scatter(
                    [center_x], [center_y],
                    color=palette[i % len(palette)],
                    s=_get_marker_size() * 1.35,
                    marker="X",
                    edgecolors="#111827",
                    linewidths=0.6,
                    zorder=4,
                )
        ax.axhline(0, color="#CBD5E1", linewidth=0.9, linestyle="--", zorder=0)
        ax.axvline(0, color="#CBD5E1", linewidth=0.9, linestyle="--", zorder=0)
        ax.legend(frameon=False, fontsize=10, loc="best")
        ax.set_xlabel(chart_data.get("x_label", "LD1"), fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel(chart_data.get("y_label", "LD2"), fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_histogram(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    values = _clean_values((chart_data.get("traces") or [{}])[0].get("values", []))
    fig, ax = plt.subplots(figsize=figsize)
    if not values:
        ax.text(0.5, 0.5, "No numeric data", ha="center", va="center", transform=ax.transAxes)
    else:
        sns.histplot(values, bins=28, kde=True, color=palette[0], edgecolor="white", linewidth=0.6, alpha=0.78, ax=ax)
        ax.set_xlabel(chart_data.get("x_label", ""), fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel("Count", fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_repeated_measures(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    groups = [str(g) for g in chart_data.get("groups", [])]
    values = chart_data.get("values", {})
    fig, ax = plt.subplots(figsize=figsize)
    if not groups or not values:
        ax.text(0.5, 0.5, "No repeated-measures data", ha="center", va="center", transform=ax.transAxes)
    else:
        matrix = []
        for group in groups:
            matrix.append(_clean_values(values.get(group, [])))
        n = min(len(row) for row in matrix if row)
        for i in range(min(n, 80)):
            y = [row[i] for row in matrix]
            ax.plot(groups, y, color="#94A3B8", linewidth=0.8, alpha=0.24)
        means = [float(np.mean(row[:n])) if n else np.nan for row in matrix]
        ax.plot(groups, means, color=palette[0], linewidth=3, marker="o", markersize=6,
                markeredgecolor="white", markeredgewidth=0.8, label="Mean")
        ax.legend(frameon=False, fontsize=10)
        ax.set_xlabel("Time / condition", fontsize=13, fontweight="medium", labelpad=8)
        ax.set_ylabel("Value", fontsize=13, fontweight="medium", labelpad=8)
    _finish_stat_axis(ax, title)
    return _save_figure(fig)


def _generate_stat_fallback(chart_data: dict, title: str, style: str, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    fig, ax = plt.subplots(figsize=figsize)
    ax.text(
        0.5, 0.55,
        f"{chart_data.get('chart_type', 'chart')} can be exported from Plotly preview.",
        ha="center", va="center", transform=ax.transAxes, fontsize=12,
    )
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", pad=18)
    return _save_figure(fig)


def _finish_stat_axis(ax, title: str) -> None:
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    try:
        _add_axis_arrows(ax)
    except Exception:
        pass
    plt.tight_layout()


def _clean_values(values) -> list[float]:
    result = []
    for value in values or []:
        numeric = pd.to_numeric(value, errors="coerce")
        if pd.notna(numeric):
            result.append(float(numeric))
    return result


def _palette_for_categories(values, palette: list[str]) -> dict[str, str]:
    categories = [str(v) for v in pd.Series(values).dropna().unique().tolist()]
    return {category: palette[i % len(palette)] for i, category in enumerate(categories)}


def _china_map_fallback(df, province_var, value_var, title, style, figsize) -> tuple[bytes, bytes, bytes]:
    set_publication_style(style)
    palette = _get_palette(style)
    fig, ax = plt.subplots(figsize=figsize)
    df_sorted = df.sort_values(value_var, ascending=True)
    ax.barh(range(len(df_sorted)), df_sorted[value_var],
            color=palette[0], alpha=0.85, edgecolor='white',
            linewidth=0.6, height=0.7)
    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted[province_var], fontsize=9)
    ax.set_xlabel(value_var, fontsize=13, fontweight='medium', labelpad=8)
    if title:
        ax.set_title(title + ' (by province)', fontsize=15, fontweight='bold', pad=18)
    ax.tick_params(labelsize=10)
    sns.despine(ax=ax, trim=True)
    _add_axis_arrows(ax)
    plt.tight_layout()
    return _save_figure(fig)
