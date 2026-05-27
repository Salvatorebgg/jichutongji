from __future__ import annotations

import pandas as pd
import numpy as np
from app.services.variable_service import classify_variables


def get_chart_variables(df: pd.DataFrame, chart_type: str) -> dict:
    """Return recommended variables for a given statistical chart type."""
    var_types = classify_variables(df)
    all_vars = {c: str(df[c].dtype) for c in df.columns}

    num_cols = var_types["continuous"]
    cat_cols = var_types["categorical"] + var_types["binary"] + var_types["group"]
    date_cols = var_types["date"]
    outcome_cols = var_types["outcome_candidate"] + var_types["binary"]

    requirements = {
        "box_violin": {"required": {"y": num_cols}, "optional": {"x": cat_cols, "color": cat_cols}},
        "bar_grouped": {"required": {"x": cat_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "scatter_regression": {"required": {"x": num_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "paired_box": {"required": {"var_1": num_cols, "var_2": num_cols}, "optional": {}},
        "paired_bar": {"required": {"var_1": cat_cols, "var_2": cat_cols}, "optional": {}},
        "histogram": {"required": {"x": num_cols}, "optional": {"color": cat_cols}},
        "repeated_measures": {"required": {"y": num_cols, "group": cat_cols}, "optional": {"subject": cat_cols}},
        "survival": {"required": {"time": num_cols, "event": cat_cols}, "optional": {"group": cat_cols}},
        "forest": {"required": {"label": cat_cols, "or": num_cols, "ci_lower": num_cols, "ci_upper": num_cols}, "optional": {}},
        "heatmap": {"required": {"x": cat_cols, "y": cat_cols, "value": num_cols}, "optional": {}},
        "correlation_heatmap": {"required": {"value_vars": num_cols}, "optional": {}},
        "scatter": {"required": {"x": num_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "bar": {"required": {"x": cat_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "line": {"required": {"x": date_cols + num_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "box": {"required": {"y": num_cols}, "optional": {"x": cat_cols, "color": cat_cols}},
        "violin": {"required": {"y": num_cols}, "optional": {"x": cat_cols, "color": cat_cols}},
        "error_bar": {"required": {"x": cat_cols, "y": num_cols}, "optional": {"color": cat_cols}},
        "roc": {"required": {"outcome": outcome_cols, "predictor": num_cols}, "optional": {}},
    }

    req = requirements.get(chart_type, {"required": {}, "optional": {}})
    return {
        "required_vars": req["required"],
        "optional_vars": req["optional"],
        "all_vars": all_vars,
        "n_total": len(df),
    }


def prepare_chart_data(df: pd.DataFrame, chart_type: str, params: dict) -> dict:
    """Prepare data for chart rendering."""
    if chart_type == "correlation_heatmap":
        value_vars = params.get("value_vars", [])
        if not value_vars:
            value_vars = list(df.select_dtypes(include=[np.number]).columns[:10])
        corr_df = df[value_vars].corr().round(3)
        return {
            "type": "correlation_heatmap",
            "data": {
                "z": corr_df.values.tolist(),
                "x": list(corr_df.columns),
                "y": list(corr_df.index),
            }
        }

    if chart_type == "missingness_heatmap":
        missing = df.isnull().astype(int)
        return {
            "type": "missingness_heatmap",
            "data": {
                "z": missing.values[:100].tolist(),
                "x": list(missing.columns),
                "y": [str(i) for i in range(min(100, len(missing)))],
            }
        }

    x_var = params.get("x_var", "")
    y_var = params.get("y_var", "")
    color_var = params.get("color_var", "")
    group_var = params.get("group_var", "")
    size_var = params.get("size_var", "")
    value_vars = params.get("value_vars", [])

    plot_data = {}
    for col in [x_var, y_var, color_var, group_var, size_var]:
        if col and col in df.columns:
            plot_data[col] = df[col].tolist()

    for v in (value_vars or []):
        if v in df.columns:
            plot_data[v] = df[v].tolist()

    return {
        "type": chart_type,
        "trace_data": [],
        "plot_data": plot_data,
        "n": len(df),
    }
