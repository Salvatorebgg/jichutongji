from __future__ import annotations

import json
import csv
import io
from pathlib import Path

import pandas as pd
from app.config import OUTPUTS_DIR


def export_to_csv(table_data: list[dict], filename_prefix: str = "export") -> str:
    """Export table data to CSV file."""
    if not table_data:
        raise ValueError("No data to export")
    dest = OUTPUTS_DIR / f"{filename_prefix}.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    keys = list(table_data[0].keys())
    with open(dest, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(table_data)
    return str(dest)


def export_to_excel(table_data: list[dict], filename_prefix: str = "export") -> str:
    """Export table data to Excel file."""
    if not table_data:
        raise ValueError("No data to export")
    dest = OUTPUTS_DIR / f"{filename_prefix}.xlsx"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(table_data)
    df.to_excel(dest, index=False)
    return str(dest)


def export_to_html_table(table_data: list[dict], title: str = "") -> str:
    """Export table data as HTML string."""
    if not table_data:
        return "<p>No data to export</p>"
    keys = list(table_data[0].keys())
    html = '<table class="medical-table">\n'
    if title:
        html += f'<caption>{title}</caption>\n'
    html += '<thead><tr>\n'
    for k in keys:
        html += f'<th>{k}</th>\n'
    html += '</tr></thead>\n<tbody>\n'
    for row in table_data:
        html += '<tr>\n'
        for k in keys:
            v = row.get(k, "")
            html += f'<td>{v}</td>\n'
        html += '</tr>\n'
    html += '</tbody>\n</table>'
    return html
