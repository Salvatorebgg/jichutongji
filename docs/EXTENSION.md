# 后续扩展说明

本文档说明如何在当前版本中添加新的统计检验方法、新示例数据和新导出格式。

## 添加新的统计检验方法

### 1. 在后端实现检验函数

在 `app/services/stats_service.py` 中添加函数：

```python
def new_test(df: pd.DataFrame, var: str, group_var: str) -> dict:
    """New statistical test implementation."""
    groups = df[group_var].dropna().unique()
    ...
    return {
        "test_type": "new_test",
        "test_name": "新检验方法",
        "statistic": float(stat),
        "p_value": float(p),
        "significant": p < 0.05,
        "method": "Method description",
        "note": "",
        "summary": "结论文字",
        "details": {...},
        "descriptive_stats": {...},
        "chart_data": {...},
    }
```

关键约定：返回字典必须包含 `test_type`、`test_name`、`statistic`、`p_value`、`significant`、`method`、`summary`、`details`、`descriptive_stats`、`chart_data` 字段。

### 2. 注册到路由

在 `app/main.py` 的 `run_analysis()` 中添加分支：

```python
elif test_type == "new_test":
    if not group_var or group_var not in df.columns:
        raise HTTPException(status_code=400, detail="New test requires a group variable")
    result = new_test(df, var, group_var)
```

### 3. 创建示例数据

在 `app/services/sample_service.py` 中添加：

```python
def make_new_test_example() -> pd.DataFrame:
    n = 100
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "outcome": rng.normal(0, 1, n),
        "group": rng.choice(["Control", "Treatment"], n),
    })
```

注册到 `EXAMPLE_MAKERS`：

```python
EXAMPLE_MAKERS = {
    ...
    "new_test_example": make_new_test_example,
}
```

### 4. 添加前端配置

在 `app/static/js/utils.js` 的 `TEST_CATALOG` 中添加：

```javascript
new_test: {
  id: "new_test",
  name: "新检验方法",
  category: "parametric",  // parametric | nonparametric | categorical
  icon: "NT",
  description: "新检验方法的简要说明",
  exampleDataset: "new_test_example",
  requiresGroup: true,
  requiresPaired: false,
  supportsPostHoc: false,
  varType: "continuous",  // continuous | categorical
},
```

### 5. 添加默认变量映射

在 `app/static/js/variableSelect.js` 的 `TEST_DEFAULT_VARS` 中添加：

```javascript
new_test: { var: 'outcome', group_var: 'group' },
```

## 添加新的示例数据集

1. 在 `app/services/sample_service.py` 中添加生成函数。
2. 注册到 `EXAMPLE_MAKERS`。
3. 重启应用，CSV文件会自动生成到 `data/examples/`。

修改已有示例生成逻辑后，需要删除旧的CSV文件让应用重新生成，或直接替换CSV文件。

## 添加新的事后检验方法

### 1. 在 `stats_service.py` 中实现

```python
def _post_hoc_new_method(groups: dict, alpha: float = 0.05) -> list[dict]:
    comparisons = []
    group_names = list(groups.keys())
    for i in range(len(group_names)):
        for j in range(i + 1, len(group_names)):
            ...
            comparisons.append({
                "comparison": f"{g1} vs {g2}",
                "statistic": ...,
                "p_value": ...,
                "significant": ...,
                "method": "New Method",
            })
    return comparisons
```

### 2. 添加到前端下拉选项

在 `app/static/index.html` 的 `#postHocSelect` 中添加：

```html
<option value="new_method">New Method</option>
```

### 3. 在分析路由中处理

在 `app/main.py` 中传递 `post_hoc` 参数给对应的检验函数。

## 添加新的导出格式

### 1. 在 `export_service.py` 中添加

```python
def export_to_format(data: list[dict], filename: str) -> Path:
    dest = OUTPUTS_DIR / f"{filename}.ext"
    # 导出逻辑
    return dest
```

### 2. 添加 FastAPI 路由

在 `app/main.py` 中添加：

```python
@app.post("/api/export/table-format")
def export_table_format(req: ExportRequest) -> FileResponse:
    data = req.table_data or []
    dest = export_to_format(data, "statistics_export")
    return FileResponse(dest, media_type="...", filename="statistics_export.ext")
```

### 3. 添加前端导出按钮

在 `app/static/index.html` 的导出工具栏中添加按钮，在 `app/static/js/download.js` 中添加对应的导出函数。

## 添加新数据格式

编辑 `app/services/io_service.py`：

1. 在 `SUPPORTED_EXTENSIONS` 中添加后缀。
2. 在 `read_file()` 中添加读取逻辑。
3. 返回前确保DataFrame已规范化。

## 验证命令

每次新增检验方法或接口后建议运行：

```bash
python tests\smoke.py
python -m compileall app
```

也可以启动临时端口验证新接口：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8872
```

```bash
curl -X POST http://127.0.0.1:8872/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"test_type\":\"t_test_independent\",\"var\":\"sbp\",\"group_var\":\"group\",\"use_demo\":true,\"dataset_name\":\"t_test_independent_example\"}"
```
