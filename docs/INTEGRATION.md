# 二次集成说明

## 架构概述

本平台采用 FastAPI + 原生前端 SPA 的轻量架构：

- **后端**：Python FastAPI，负责上传、读取、变量识别、统计检验、结果讨论生成、出版级图表导出、三线表/基线表生成和数据导出。
- **前端**：HTML / CSS / JavaScript，无前端框架依赖，11个JS模块。
- **统计检验**：22种常用临床统计检验方法（6大类：参数/非参数/分类资料/相关分析/生存分析/回归与判别），集中在 `app/services/stats_service.py`。
- **图形**：本地 Plotly.js v3.0.1，双通道渲染——优先使用后端 `chart_data` 结构化数据，无后端数据时回退到前端本地计算。
- **出版级导出**：`publication_chart_service.py` 基于 Matplotlib/Seaborn 生成 PNG/SVG/PDF，支持11种期刊风格主题（CNS/Nature/Lancet/NEJM/Science 等）。
- **数据链路**：先选检验方法，再加载对应示例或上传数据；分析通过 `/api/analyze` 执行，返回结果+讨论+三线表+图表数据。

## 推荐集成方式

### 方式一：独立部署

```bash
python run.py
```

默认访问：

```text
http://127.0.0.1:8765
```

主站可以用 iframe 或普通链接集成：

```html
<iframe src="http://127.0.0.1:8765" width="100%" height="860"></iframe>
<a href="http://127.0.0.1:8765" target="_blank" rel="noreferrer">打开临床基础统计分析平台</a>
```

如果默认端口被占用，可指定新端口：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8872
```

### 方式二：挂载到 FastAPI 主应用

```python
import sys
from fastapi import FastAPI

sys.path.insert(0, "/path/to/jichutongji")
from app.main import app as stats_app

main_app = FastAPI()
main_app.mount("/stats", stats_app)
```

访问：

```text
http://your-site.com/stats
```

### 方式三：只调用 API

上传文件：

```javascript
const formData = new FormData();
formData.append("file", file);

const uploadResp = await fetch("http://127.0.0.1:8765/api/upload", {
  method: "POST",
  body: formData,
});
const upload = await uploadResp.json();
```

执行统计分析：

```javascript
const analysisResp = await fetch("http://127.0.0.1:8765/api/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    test_type: "t_test_independent",
    var: "sbp",
    group_var: "group",
    upload_id: upload.upload_id,
  }),
});
const result = await analysisResp.json();
```

使用示例数据：

```javascript
const analysisResp = await fetch("http://127.0.0.1:8765/api/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    test_type: "anova",
    var: "sbp",
    group_var: "treatment",
    post_hoc: "tukey",
    use_demo: true,
    dataset_name: "anova_example",
  }),
});
const result = await analysisResp.json();
// result 包含: { status, result, discussion, tables: { result, group_stats, post_hoc } }
// result.result.chart_data 可直接用于 Plotly 图表渲染
```

生成基线特征表与描述统计表：

```javascript
// 基线特征表（Table 1）
const baselineResp = await fetch("http://127.0.0.1:8765/api/table/baseline", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    dataset_name: "general_clinical_example",
    group_var: "group",
    use_demo: true,
  }),
});
const baseline = await baselineResp.json();

// 描述统计表
const descResp = await fetch("http://127.0.0.1:8765/api/table/descriptive", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    dataset_name: "general_clinical_example",
    variables: ["age", "bmi", "sbp", "glucose"],
    use_demo: true,
  }),
});

// 缺失值统计表
const missResp = await fetch("http://127.0.0.1:8765/api/table/missing", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    dataset_name: "general_clinical_example",
    use_demo: true,
  }),
});
```

导出出版级图表：

```javascript
const chartResp = await fetch("http://127.0.0.1:8765/api/export/chart/publication", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    chart_type: "box",
    y_var: "sbp",
    x_var: "group",
    format: "png",
    title: "SBP by Group",
    style: "cns",            // cns | nature
    dataset_name: "general_clinical_example",
    use_demo: true,
  }),
});
const blob = await chartResp.blob();
```

## 关键接口

| 端点 | 用途 |
|---|---|
| `/api/upload` | 上传文件并返回预览、变量类型和摘要 |
| `/api/read-sheet` | 切换Excel工作表 |
| `/api/examples` | 获取示例数据列表 |
| `/api/examples/{name}` | 获取示例预览和变量类型 |
| `/api/examples/{name}/download` | 下载示例CSV |
| `/api/dataset/data` | 返回完整列式数据 |
| `/api/analyze` | 执行统计分析（22种检验统一入口） |
| `/api/descriptive` | 生成描述统计表 |
| `/api/chart/variables` | 获取图表推荐变量 |
| `/api/chart/data` | 准备图表渲染数据 |
| `/api/table/baseline` | 生成基线特征表 (Table 1) |
| `/api/table/descriptive` | 生成整体描述统计表 |
| `/api/table/missing` | 生成缺失值统计表 |
| `/api/export/table-csv` | 导出CSV表格 |
| `/api/export/table-excel` | 导出Excel表格 |
| `/api/export/table-html` | 导出HTML表格 |
| `/api/export/chart/publication` | 导出出版级图表 (PNG/SVG/PDF) |
| `/api/export/stat-chart/publication` | 导出统计分析结果图表 (PNG/SVG/PDF) |

## CORS 配置

默认允许任意来源调用，方便本地集成。生产环境建议限制来源：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 生产部署

### Uvicorn

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8765
```

### Gunicorn + Uvicorn Worker

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8765
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name stats.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 200M;
    }
}
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8765
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
```

## 数据和会话隔离

上传文件保存在 `data/uploads/`，文件名前缀使用UUID。生产环境建议：

- 定时清理 `data/uploads/` 和 `outputs/`。
- 在外层应用中绑定用户身份和 `upload_id`。
- 对上传大小、并发请求和分析频率做限制。
- 如需长期保存结果，使用数据库记录上传、分析参数和导出文件路径。

## 注意事项

- 前端默认加载本地 `app/static/vendor/plotly.min.js`，避免CDN失败导致图形渲染不可用。
- 统计分析通过 `/api/analyze` 统一执行，返回结果包含 `result`、`discussion`（结构化临床讨论）、`tables.result`、`tables.group_stats`、`tables.post_hoc`。
- 图表渲染优先使用 `result.chart_data`（后端结构化数据），兼容所有22种检验方法。
- CSV/TSV文件自动识别编码（UTF-8/GB18030/Latin1等），Excel支持 .xlsx/.xls 多工作表切换。
- 出版级图表通过 `/api/export/chart/publication` 导出，支持 scatter/box/bar/line/forest/survival/roc/heatmap/histogram/china_map/world_map 共11种图表类型。
- 新增统计检验方法时必须同时维护 `sample_service.py` 示例生成函数、`analysis.js` 的 `TEST_CATALOG` 配置和 `variableSelect.js` 的变量槽位定义。
