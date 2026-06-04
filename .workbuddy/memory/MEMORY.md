# 基础统计平台 - 项目记忆

## 项目概要
- 路径: `D:\BaiduSyncdisk\document\workdocument\task\网站搭建\临床\工具\tongjifangan\jichutongji`
- 技术栈: FastAPI + 原生 JS/HTML/CSS 前端，Plotly.js 图表
- 功能: 临床基础统计分析平台，22种统计方法，6大类（参数/非参数/分类资料/相关分析/生存分析/回归判别）
- 运行: `python run.py` (默认端口 8765)，或 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765`
- 依赖: numpy, pandas, scipy, scikit-learn, lifelines, statsmodels, fastapi, uvicorn

## 关键架构
- `app/main.py`: FastAPI 路由，所有 API 端点
- `app/services/stats_service.py`: 所有统计方法实现
- `app/services/sample_service.py`: 示例数据生成
- `app/services/variable_service.py`: 变量分类 (classify_variables)
- `app/schemas.py`: Pydantic 请求/响应模型
- `app/static/js/app.js`: 前端主逻辑 + buildVarControls()
- `app/static/js/analysis.js`: 统计分析执行与结果渲染
- `app/static/js/variableSelect.js`: 图表变量选择（buildChartVarControls）

## 已知问题与修复

### 2026-06-04: 变量类型格式不匹配导致统计方法全部报错
- **根因**: API返回 `variable_types` 为分组格式 `{continuous: [...], binary: [...], group: [...]}`,
  但 `app.js` 的 `buildVarControls()` 把它当作逐列格式 `{col_name: 'type'}` 读取
- **症状**: 所有变量下拉框为空，执行分析时 `var` 字段为空字符串，后端返回 400 错误
- **修复**: 在 `buildVarControls()` 中先将分组格式转换为 `colTypeMap` 逐列查找字典，
  再用 colTypeMap 筛选 continuousCols / categoricalCols / allNumCols；
  添加候选变量为空时回退到全部列的逻辑；
  添加 autoSelect 参数使关键变量自动选中第一个默认值

### 2026-06-04: 统计分析结果无图表可视化 + 变量选择不完善
- **问题1**: renderStatResults() 只渲染文字摘要，不生成Plotly图表
- **问题2**: date类型列（如survival_time）不纳入continuousCols，导致生存分析变量选不到
- **问题3**: McNemar的paired_var从continuousCols选，应从categoricalCols选
- **问题4**: paired_var的autoSelect总是选第一个，可能和var重复
- **修复**:
  - 新增 renderStatChart() 函数，为每种统计方法生成对应的Plotly图表
  - continuousCols 添加 date 类型支持
  - McNemar 的 paired_var 根据 varType 判断使用分类变量
  - buildSelectField() 新增 defaultVal 参数，paired_var 默认选与 var 不同的变量
  - runAnalysis() 中通过 loadChartDataset() 加载完整数据集用于图表渲染

### 2026-06-04: 数据预览只显示5行8列 + 图表可视化空白
- **问题1**: updatePreviewTable() 只显示前5行8列数据，与Basicpicture项目全量展示不一致
- **问题2**: 后端API只返回 df.head(10) 即10行预览数据
- **问题3**: 统计图表区域完全空白，Plotly图表不显示
- **修复**:
  - updatePreviewTable() 改为展示所有行和所有列，添加行号列和数据量说明
  - 后端 get_example/upload_sheet 三个端点从 `df.head(10)` 改为 `df`（全量返回）
  - renderStatChart() 中给 plotMount 设置明确 width/height/minHeight
  - 给 Plotly layout 设置 width/height/autosize:false 确保图表渲染
  - chartExportBar 在分析完成后自动显示（flex）

### 2026-06-04: 生存分析 (log_rank) 完全无结果
- **根因1**: `app/main.py:241` 中 `var` 为空字符串但 log_rank 未被加入豁免列表，始终返回 400
- **根因2**: `stats_service.py` 的 `log_rank_test()` 只处理2组比较，不计算KM曲线，chart_data无实际数据
- **根因3**: 前端 `buildStatPlotFromChartData()` 缺少 survival 图表类型处理器
- **修复**:
  - main.py 第241行豁免列表加入 `"log_rank"`
  - `log_rank_test()` 重写：支持多组pairwise比较 + KM曲线计算（优先lifelines，回退手动实现）
  - 新增 `_compute_km_curves()` 辅助函数
  - `analysis.js` 新增 `buildStatPlotFromChartData` 中 type==='survival' 分支
- **端口**: 从 8868 改为 8765（避免与 Basicpicture 冲突）
- **配色**: styles.css 同步 Basicpicture 蓝色调色板 (teal→blue)
