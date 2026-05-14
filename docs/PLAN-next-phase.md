# html-pptx-template 下一阶段实施计划

> 基于对 4 个核心参考项目（html-ppt-skill、beautiful-html-templates、ppt-master、PPTist）的调研结果制定
> 目标：让 SKILL 具备参考项目的核心能力，同时保留从网页借鉴风格的能力

---

## 一、调研核心发现

### 1. html-ppt-skill（3,760⭐）— 主题+布局+动画三层架构
- **36 个主题**：CSS 变量覆盖（`--bg`, `--text-1/2/3`, `--accent`, `--radius`, `--shadow`, `--font-sans`）
- **31 种布局**：cover、toc、bullets、two-column、kpi-grid、chart-bar/line/pie、code、terminal、timeline、roadmap、gantt、comparison、image-grid、cta、thanks 等
- **47 种动画**：27 CSS 动画（fade-up, zoom-pop, blur-in, glitch-in 等）+ 20 Canvas 特效
- **15 个完整模板**：tech-sharing, pitch-deck, product-launch, weekly-report 等
- **Agent 映射表**：商务→pitch-deck, 技术→tokyo-night, 学术→academic-paper

### 2. beautiful-html-templates（1,194⭐）— 模板元数据+感觉匹配
- **模板元数据**：mood, occasion, tone, formality(5级), density(低/中/高), scheme(亮/暗/混合), best_for, avoid_for
- **Tone-first 匹配**：不根据行业，而根据"感觉"匹配模板
- **布局类**：.layout-cover, .layout-agenda, .layout-metrics, .layout-dashboard, .layout-split, .layout-bars, .layout-quote, .layout-timeline
- **3 候选预览**：Agent 展示 3 个不同风格选项，用户选择

### 3. ppt-master（16,308⭐）— 原生 PPTX + XML 动画
- **SVG→DrawingML**：原生形状转换，非截图
- **直接写 OOXML**：绕过 python-pptx 限制，直接操作 XML
- **20+ 入场动画**：fly, zoom, blinds, checkerboard 等
- **7 种幻灯片过渡**：fade, push, wipe, split, strips, cover, random
- **模板导入系统**：manifest.json + assets/ + svg/ 分层存储

### 4. PPTist（8,946⭐）— 统一元素数据结构
- **9 种元素类型**：Text, Image, Shape, Line, Chart, Table, Video, Audio, Latex
- **主题**：6 色板 + fontColor + fontName + backgroundColor + shadow + outline
- **幻灯片类型**：'cover' | 'contents' | 'transition' | 'content' | 'end'
- **AI 模板匹配**：按占位符数量过滤模板，内容溢出自动分页
- **字体自适应**：canvas measureText 动态调整字号

### 5. open-design（40,008⭐）— Design System Token 化
- **DESIGN.md 格式**：标准化 9 节设计系统文档
- **70+ 品牌系统**：Claude, Stripe, Linear, Notion, Apple 等
- **Token 维度**：颜色、字体、间距、圆角、阴影层级

---

## 二、能力差距分析

| 能力维度 | 当前状态 | 目标状态 | 差距 |
|---------|---------|---------|------|
| **主题系统** | 颜色+字体（5个token） | 颜色+字体+间距+圆角+阴影+动画（15+token） | 需扩展 Theme 模型 |
| **布局系统** | 9 种基础布局 | 31 种专业布局 + 15 个完整模板 | 需大幅扩展 |
| **动画系统** | 无 | 20+ 入场动画 + 7 种过渡 | 需新增模块 |
| **元素类型** | text, image, table, chart | + shape, line, video, audio | 需扩展元素体系 |
| **模板匹配** | 基于内容结构推断 | mood/tone/density 元数据匹配 | 需添加元数据层 |
| **风格提取** | 颜色+字体+截图 | + 间距系统、圆角、阴影、动画偏好 | 需丰富提取维度 |
| **输出质量** | 基础形状 | 原生 DrawingML + SVG 路径 | 需 XML 层操作 |
| **Agent UX** | 单一路径生成 | 3 候选预览 + 交互选择 | 需新增交互流程 |

---

## 三、分阶段实施计划

### Phase 1 — 主题与布局系统扩展（1-2 天）

**Task 1.1: 扩展 Theme 模型**
- 文件：`src/html_pptx_template/templates/schema.py`
- 新增 token：border_radius, shadow, line_height, letter_spacing, paragraph_spacing, animation_speed
- 参考 html-ppt-skill 的 CSS 变量命名
- **测试**：Theme 序列化/反序列化保持兼容

**Task 1.2: 丰富布局类型到 20+ 种**
- 文件：`src/html_pptx_template/generator/slide_builder.py`
- 新增布局：
  - `cover` — 全屏背景+居中标题（比 title 更 dramatic）
  - `toc` / `agenda` — 目录/议程页
  - `kpi_grid` — KPI 指标网格
  - `quote` — 引用页
  - `timeline` — 时间线
  - `comparison` — 左右对比
  - `code` — 代码展示
  - `cta` / `closing` — 行动号召/结束页
  - `split` — 非对称分割
  - `dashboard` — 仪表盘风格
- 每个布局有对应的 `_build_xxx_slide()` 方法
- **测试**：每个新布局至少一个渲染测试

**Task 1.3: 布局元数据系统**
- 文件：`src/html_pptx_template/templates/schema.py`（新增 `TemplateMetadata`）
- 每个模板存储：mood[], tone[], formality, density, scheme, best_for, avoid_for
- 文件：`src/html_pptx_template/templates/matcher.py`（新增）
- 实现 `TemplateMatcher`：根据用户内容/意图关键词匹配最佳模板
- **测试**：匹配逻辑单元测试

### Phase 2 — 动画与过渡系统（1 天）

**Task 2.1: 幻灯片过渡效果**
- 文件：`src/html_pptx_template/generator/animations.py`（新建）
- 7 种过渡：fade, push, wipe, split, strips, cover, random
- 直接写入 OOXML `<p:transition>` XML
- **测试**：生成 PPTX 后用 PowerPoint 验证过渡存在

**Task 2.2: 元素入场动画**
- 文件：`src/html_pptx_template/generator/animations.py`
- 20+ 动画：fly(in/out/up/down), zoom, blinds, checkerboard, fade, appear
- 支持触发模式：on-click, with-previous, after-previous
- 支持交错延迟（stagger）
- **测试**：XML 结构正确性测试

**Task 2.3: 动画应用接口**
- 文件：`src/html_pptx_template/generator/slide_builder.py`
- `add_animation(shape, effect, trigger, delay)` 辅助方法
- 在 `_build_xxx_slide()` 中默认应用 subtle fade-in
- **测试**：集成测试

### Phase 3 — 元素体系扩展（1 天）

**Task 3.1: Shape 元素**
- 文件：`src/html_pptx_template/generator/slide_builder.py`
- 支持：矩形、圆角矩形、椭圆、箭头、线条（含箭头端点）
- 参考 PPTist 的 `PPTShapeElement` 结构
- **测试**：形状渲染正确

**Task 3.2: 原生图表**
- 文件：`src/html_pptx_template/generator/slide_builder.py`
- 用 `python-pptx` 的 `add_chart()` 替代 placeholder
- 支持：bar, column, line, pie, area
- 数据从 markdown 表格或 `!chart:type` 解析
- **测试**：图表数据正确映射

**Task 3.3: 视频/音频占位符**
- 文件：`src/html_pptx_template/generator/slide_builder.py`
- 添加视频/音频占位符形状
- 标记为「需手动替换媒体文件」
- **测试**：占位符存在

### Phase 4 — 高级生成功能（1-2 天）

**Task 4.1: 内容溢出自动分页**
- 文件：`src/html_pptx_template/generator/engine.py`
- 当 bullets > 6 时自动拆分为多个 content 幻灯片
- 参考 PPTist 的 `getAdaptedFontsize()` 思路
- **测试**：长内容正确分页

**Task 4.2: 模板骨架 + 数据注入模式**
- 文件：`src/html_pptx_template/generator/template_injector.py`（新建）
- 参考 docxtemplater 的模板语法
- 支持 PPTX 模板导入：`{title}`, `{body}`, `{image}` 占位符
- 用户提供 PPTX 骨架 + JSON 数据 → 生成完整 PPTX
- **测试**：占位符替换正确

**Task 4.3: SVG 路径支持**
- 文件：`src/html_pptx_template/generator/drawingml.py`（新建）
- 参考 ppt-master 的 SVG→DrawingML 转换
- 支持简单 SVG path 转换为 PPTX 自定义形状
- **测试**：SVG 正确渲染

### Phase 5 — 风格提取增强（1 天）

**Task 5.1: 丰富提取维度**
- 文件：`src/html_pptx_template/extractor/browser.py`
- 新增提取：border-radius, box-shadow, letter-spacing, line-height, animation-duration
- 通过 computed style 采样获取
- **测试**：提取值合理

**Task 5.2: DESIGN.md 生成**
- 文件：`src/html_pptx_template/templates/design_md_generator.py`（新建）
- 参考 open-design 的 DESIGN.md 9 节格式
- 从提取数据自动生成标准化设计文档
- **测试**：文档格式正确

**Task 5.3: 品牌系统匹配**
- 文件：`src/html_pptx_template/extractor/brand_matcher.py`（新建）
- 内置 20+ 知名品牌配色库
- URL 匹配到品牌后应用该品牌的完整 Design System
- **测试**：知名品牌正确匹配

### Phase 6 — Agent UX 改进（1 天）

**Task 6.1: 3 候选预览流程**
- 文件：`skill.yaml`（更新 prompts）
- Agent 根据内容 mood 推荐 3 个不同风格模板
- 用 `AskUserQuestion` 让用户选择
- **测试**：交互流程正确

**Task 6.2: 交互式选项选择**
- 文件：`skill.yaml`
- 实现用户用方向键选择选项（AskUserQuestion 多选）
- 支持：主题选择、布局选择、动画开关
- **测试**：选项渲染正确

**Task 6.3: HTML 预览生成**
- 文件：`src/html_pptx_template/generator/html_preview.py`（新建）
- 生成每页幻灯片的 HTML 预览（用于 Agent 展示给用户）
- 参考 reveal.js 的 CSS 主题结构
- **测试**：预览与 PPTX 一致

---

## 四、技术决策备忘

### 关键架构决策
1. **保留 python-pptx 作为基础**：不全面替换，而是在其基础上扩展 XML 操作能力
2. **新建 `drawingml.py` 模块**：封装直接写入 OOXML 的能力，用于动画、复杂形状
3. **Theme 模型向后兼容**：新增字段有默认值，旧模板仍可加载
4. **布局采用「注册表」模式**：新增布局只需在 `slide_builder.py` 注册 `_build_xxx` 方法 + 在 `engine.py` 注册 fallback

### 优先级调整原则
- 如果用户主要用「网页风格提取」→ Phase 5 优先
- 如果用户主要用「内容生成质量」→ Phase 1+2 优先
- 如果用户主要用「交互体验」→ Phase 6 优先

---

## 五、当前代码基线

**已通过测试**：134 个测试全部通过
**已有能力**：
- 9 种基础布局（title, content, section_divider, two_column, image_left, image_full, table, chart, image_gallery）
- 智能自动布局推断
- 从 URL 提取颜色/字体/截图
- VisualAnalyzer 解析 visual_analysis.md
- 多网站风格泛化验证（Studio Namma, Stripe, Linear）

**已知限制**：
- 图表是 placeholder 而非原生图表
- 无动画/过渡
- 无形状/线条元素
- 布局类型较少
- 无模板元数据匹配

---

*计划制定时间: 2026-05-14*
*调研来源: html-ppt-skill, beautiful-html-templates, ppt-master, PPTist, open-design*
