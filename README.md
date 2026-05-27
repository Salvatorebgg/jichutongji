# 临床数据统计分析一键化生成平台

**Clinical Statistics Analysis Platform — One-Click Statistical Testing**

面向临床科研数据的交互式统计分析平台。采用"先选检验方法，再载入数据，后执行分析"的 test-first 工作流，支持9种常用统计检验方法，每种方法绑定对应示例数据、默认变量映射和完整统计分析接口。

## 当前版本功能

- **检验方法优先工作流**：用户先在左侧检验方法清单中选择目标检验，再加载示例或上传数据，配置变量后执行分析。
- **9种统计检验方法**：独立样本t检验、配对t检验、单因素方差分析、卡方检验、Fisher精确概率法、Mann-Whitney U检验、Kruskal-Wallis检验、Wilcoxon符号秩检验、McNemar/McNemar-Bowker检验。
- **示例数据与检验一一对应**：每个检验配置都声明 `exampleDataset`，前端选择检验后绑定对应示例和默认变量。
- **事后两两比较**：ANOVA支持Tukey HSD、Bonferroni、LSD、Games-Howell四种事后检验方法；Kruskal-Wallis支持Bonferroni校正。
- **完整统计分析输出**：检验统计量、P值、显著性结论、效应量、描述统计、分组统计表、事后比较表。
- **Plotly统计图形**：箱线图+小提琴图、分组柱状图、配对箱线图、配对柱状图、直方图等。
- **智能变量识别**：连续变量、二分类变量、多分类变量、分组变量、日期变量、ID变量等9种类型。
- **三线表导出**：结果表格支持CSV、Excel、HTML和剪贴板复制。
- **稳健数据读取**：CSV/TSV/TXT自动识别编码（UTF-8/GB18030/Latin1等）和分隔符，支持Excel (.xlsx/.xls)多工作表。

## 统计检验方法一览

| 检验方法 | 类型 | 适用场景 |
|---|---|---|
| 独立样本t检验 | 参数检验 | 比较两组独立连续变量的均值差异 |
| 配对t检验 | 参数检验 | 比较同组干预前后或配对设计的连续变量 |
| 单因素方差分析 (ANOVA) | 参数检验 | 比较多组（≥3组）连续变量的均值差异 |
| 卡方检验 | 分类资料 | 比较两组或多组分类变量的分布差异 |
| Fisher精确概率法 | 分类资料 | 小样本或低期望频数的2×2列联表分析 |
| Mann-Whitney U检验 | 非参数检验 | 两组独立数据的非参数比较（不满足正态性） |
| Kruskal-Wallis检验 | 非参数检验 | 多组独立数据的非参数比较 |
| Wilcoxon符号秩检验 | 非参数检验 | 配对设计的非参数比较 |
| McNemar检验 | 分类资料 | 配对分类资料的比较（2×2或k×k） |

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
cd jichutongji
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 启动

```bash
python run.py
```

默认访问地址：

```text
http://127.0.0.1:8868
```

如果8868端口被占用，可以指定其他端口：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8872
```

## 推荐使用流程

1. 在左侧"检验方法"中选择统计检验方法（参数检验/非参数检验/分类资料）。
2. 点击"加载示例"快速查看本检验效果，或上传自己的CSV/Excel数据。
3. 确认分析变量、分组变量或配对变量配置。
4. 对于ANOVA或Kruskal-Wallis，可选择事后检验方法。
5. 点击"执行分析"，查看检验结果、分组统计和事后比较表。
6. 切换到"可视化"页查看统计图形。
7. 使用导出按钮导出结果为Excel/CSV/HTML。

## 核心数据流

```mermaid
flowchart LR
  A["选择检验方法"] --> B["绑定 exampleDataset"]
  B --> C["加载示例或上传数据"]
  C --> D["读取并规范化 DataFrame"]
  D --> E["变量类型识别与分类"]
  E --> F["配置分析变量与分组"]
  F --> G["POST /api/analyze"]
  G --> H["统计检验 + 描述统计 + 事后比较 + 图表数据"]
  H --> I["结果表格 + 分组统计 + 事后比较表 + Plotly图形"]
```

## 检验与示例数据映射

| 检验方法 | 示例数据集 |
|---|---|
| 独立样本t检验 | `t_test_independent_example` |
| 配对t检验 | `t_test_paired_example` |
| 单因素方差分析 | `anova_example` |
| 卡方检验 | `chi_square_example` |
| Fisher精确概率法 | `fisher_exact_example` |
| Mann-Whitney U检验 | `mann_whitney_example` |
| Kruskal-Wallis检验 | `kruskal_wallis_example` |
| Wilcoxon符号秩检验 | `wilcoxon_signed_rank_example` |
| McNemar检验 | `mcnemar_example` |

## 项目结构

```text
jichutongji/
├── README.md
├── requirements.txt
├── pyproject.toml
├── run.py
├── app/
│   ├── main.py                  # FastAPI 路由和应用入口
│   ├── config.py                # 路径和运行目录配置
│   ├── schemas.py               # Pydantic 请求模型
│   ├── services/
│   │   ├── io_service.py        # 上传、示例、编码/分隔符识别、数据读取
│   │   ├── variable_service.py  # 变量类型识别和数据摘要
│   │   ├── stats_service.py     # 9种统计检验核心函数
│   │   ├── table_service.py     # 结果表格、分组统计、事后比较表
│   │   ├── sample_service.py    # 10个示例数据集生成函数
│   │   └── export_service.py    # CSV/Excel/HTML 表格导出
│   └── static/
│       ├── index.html
│       ├── vendor/
│       │   └── plotly.min.js
│       ├── css/
│       │   ├── theme.css
│       │   ├── layout.css
│       │   ├── components.css
│       │   └── tables.css
│       └── js/
│           ├── utils.js         # STATE、TEST_CATALOG、API helpers
│           ├── upload.js        # 文件上传和数据加载
│           ├── analysis.js      # 统计分析执行和结果渲染
│           ├── download.js      # 结果导出
│           ├── variableSelect.js
│           ├── dataPreview.js
│           ├── tableGenerator.js
│           └── app.js           # 主入口、事件绑定、标签页
├── data/
│   ├── examples/
│   └── uploads/
├── outputs/
├── docs/
│   ├── INTEGRATION.md
│   └── EXTENSION.md
└── tests/
    └── smoke.py
```

## API 概览

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/health` | GET | 健康检查 |
| `/api/upload` | POST | 上传数据文件并返回预览、变量识别和摘要 |
| `/api/read-sheet` | POST | 读取Excel指定工作表 |
| `/api/examples` | GET | 列出示例数据集 |
| `/api/examples/{name}` | GET | 获取示例数据预览和变量识别 |
| `/api/examples/{name}/download` | GET | 下载单个示例CSV |
| `/api/dataset/data` | POST | 返回完整列式数据 |
| `/api/analyze` | POST | 执行统计分析 |
| `/api/descriptive` | POST | 生成描述统计表 |
| `/api/export/table-csv` | POST | 导出表格CSV |
| `/api/export/table-excel` | POST | 导出表格Excel |
| `/api/export/table-html` | POST | 导出表格HTML |

### 统计分析请求示例

```bash
curl -X POST http://127.0.0.1:8868/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "t_test_independent",
    "var": "sbp",
    "group_var": "group",
    "use_demo": true,
    "dataset_name": "t_test_independent_example"
  }'
```

返回核心结构：

```json
{
  "status": "ok",
  "result": {
    "test_type": "t_test_independent",
    "test_name": "独立样本t检验",
    "statistic": -2.34,
    "p_value": 0.0203,
    "significant": true,
    "method": "Welch's t-test",
    "summary": "两组差异有统计学意义",
    "details": {},
    "descriptive_stats": {},
    "chart_data": {}
  },
  "tables": {
    "result": { "columns": [], "rows": [] },
    "group_stats": { "columns": [], "rows": [] },
    "post_hoc": null
  }
}
```

## 开发与验证

```bash
python tests\smoke.py
python -m compileall app
```

## 集成与扩展

- 二次集成说明：[docs/INTEGRATION.md](docs/INTEGRATION.md)
- 添加新检验方法、新示例：[docs/EXTENSION.md](docs/EXTENSION.md)

## 许可证

MIT License
