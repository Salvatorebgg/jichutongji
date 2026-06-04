from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_type: str
    sheet_names: list[str] | None = None
    row_count: int
    col_count: int
    columns: list[str]
    dtypes: dict[str, str]
    variable_types: dict[str, list[str]]
    preview: list[dict]
    missing_percent: float
    summary: dict


class AnalyzeRequest(BaseModel):
    upload_id: str | None = None
    sheet_name: str | None = None
    use_demo: bool = False
    dataset_name: str | None = None
    # Test selection
    test_type: str = ""
    # Variables
    var: str = ""           # Primary variable
    group_var: str | None = None   # Grouping variable
    paired_var: str | None = None  # Second variable for paired tests / correlation var2
    var2: str | None = None        # Second variable for correlation tests
    post_hoc: str | None = None    # Post-hoc method: tukey, bonferroni, lsd, games_howell
    var_type: str | None = None    # "continuous" or "categorical"
    variables: list[str] | None = None  # Variable list for descriptive/tables
    # Advanced test params
    subject_var: str | None = None     # Subject ID for repeated measures / Friedman
    covar: str | None = None           # Covariate for ANCOVA
    time_var: str | None = None        # Time variable for survival analysis
    event_var: str | None = None       # Event variable for survival analysis
    predictor_vars: list[str] | None = None  # Predictor variables for regression
    x_vars: list[str] | None = None    # Alternative predictor variables for regression
    # Table params
    decimal_places: int = 2
    p_digits: int = 3


class ChartRequest(BaseModel):
    upload_id: str | None = None
    sheet_name: str | None = None
    use_demo: bool = False
    dataset_name: str | None = None
    chart_type: str
    x_var: str | None = None
    y_var: str | None = None
    color_var: str | None = None
    facet_var: str | None = None
    size_var: str | None = None
    group_var: str | None = None
    time_var: str | None = None
    event_var: str | None = None
    outcome_var: str | None = None
    predictor_var: str | None = None
    province_var: str | None = None
    country_var: str | None = None
    value_vars: list[str] | None = None
    chart_theme: str = "clinicalLightTheme"
    title: str | None = None
    extra_params: dict | None = Field(default_factory=dict)


class TableRequest(BaseModel):
    upload_id: str | None = None
    sheet_name: str | None = None
    use_demo: bool = False
    dataset_name: str | None = None
    table_type: str = "baseline"
    group_var: str | None = None
    variables: list[str] | None = None
    decimal_places: int = 2
    p_digits: int = 3


class StatResult(BaseModel):
    test_type: str
    test_name: str
    statistic: float | None = None
    p_value: float | None = None
    significant: bool = False
    method: str = ""
    note: str | None = None
    summary: str = ""
    details: dict | None = Field(default_factory=dict)
    post_hoc: list[dict] | None = None
    descriptive_stats: dict | None = None
    chart_data: dict | None = None


class ExportRequest(BaseModel):
    upload_id: str | None = None
    format: str = "png"  # png, svg, csv, json
    chart_data: dict | None = None
    table_data: list[dict] | None = None
    stat_result: dict | None = None
