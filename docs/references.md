# 参考项目汇总（用于改进 html-pptx-template）

> 本文档由调研 Agent 整理，供开发 Agent 读取后针对性改进项目。
> 所有项目按「参考价值优先级」排序，每个项目标注了：Star 数、核心借鉴点、具体要看的文件/目录。

---

## S 级 — 直接对标竞品，架构/功能参考

### 1. open-design — 40,008⭐
**链接**: https://github.com/nexu-io/open-design

**定位**: Claude Design 的开源替代品，71 个品牌级 Design System，支持 slides/PPTX/MP4 导出

**我们要借鉴什么**:
- **Design System Token 化方式**: 颜色、字体、间距、圆角、阴影如何结构化定义，让 agent 能自动匹配
- **Skill 定义结构**: 19 个 Skill 如何组织，每个 Skill 的 `skill.yaml` / `CLAUDE.md` 写法
- **沙盒预览机制**: HTML 预览如何做到安全隔离
- **多格式导出**: HTML → PDF/PPTX/MP4 的导出链设计

**具体要看哪些文件**:
```
skills/                    # Skill 定义目录，看每个 skill 的入口文件
design-systems/            # 71 个 Design System 的定义结构
core/                      # 核心引擎，看 Design System 如何被解析和应用
export/                    # 导出模块，看 PPTX 导出实现
```

**对我们项目的直接启发**:
- 当前 `create-template` 只提取颜色和字体，可以参考它的方式把「间距系统、圆角、阴影层级」也 token 化
- 它的 Design System 是预设的 71 个，我们是「从任意 URL 动态提取」，可以学习它的 token 结构来丰富提取维度

---

### 2. html-ppt-skill — 3,760⭐
**链接**: https://github.com/lewislulu/html-ppt-skill

**定位**: HTML PPT Studio — Agent Skill，24 主题、31 布局、20+ 动画

**我们要借鉴什么**:
- **主题系统**: 24 个主题如何定义和切换
- **布局体系**: 31 种 slide 布局的分类和实现
- **动画系统**: 20+ 动画效果如何在 HTML slide 中实现
- **Skill 调用流程**: 用户如何通过自然语言触发，agent 如何选择主题和布局

**具体要看哪些文件**:
```
skills/                    # Skill YAML 定义
src/themes/                # 24 个主题的定义（CSS/JSON/配置）
src/layouts/               # 31 种布局的实现
src/animations/            # 动画效果库
CLAUDE.md                  # Skill 入口 prompt 设计
```

**对我们项目的直接启发**:
- 它的「主题 + 布局 + 动画」三层架构可以直接借鉴
- 我们的模板系统目前只有「颜色+字体」，可以扩展为「主题（颜色+字体+间距+装饰）+ 布局（slide 结构）」两层
- 学习它的布局命名和分类方式，丰富我们的 fallback layout 体系

---

## A 级 — 技术实现参考（特定模块）

### 3. beautiful-html-templates — 1,194⭐
**链接**: https://github.com/zarazhangrui/beautiful-html-templates

**定位**: 专为 coding agent 设计的 HTML slide 模板库，agent 自动选择合适模板生成 deck

**我们要借鉴什么**:
- **模板分类体系**: 模板如何按场景分类（cover / title / content / section / closing 等）
- **Agent 选择逻辑**: prompt 中如何让 agent 根据内容自动匹配合适模板
- **HTML 模板结构**: 每个模板是独立的 HTML/CSS 文件还是组件化结构
- **模板元数据**: 每个模板如何描述自己的适用场景（如 "适合科技风、适合数据展示"）

**具体要看哪些文件**:
```
templates/                 # 所有 HTML 模板文件
README.md                  # 模板分类和使用方式
CLAUDE.md / skill.yaml     # Agent 如何被引导选择模板
```

**对我们项目的直接启发**:
- 我们目前的 layout 系统（title, content, two_column, image_left 等）可以学习它的分类方式扩展
- 模板元数据（适用场景标签）可以添加到我们的 template JSON 中，让 agent 更智能地推荐

---

### 4. visual-explainer — 8,238⭐
**链接**: https://github.com/nicobailon/visual-explainer

**定位**: Agent Skill，生成丰富的 HTML slide decks，用于图表、diff review、plan audit

**我们要借鉴什么**:
- **Agent Skill 定义方式**: `skill.yaml` 的结构，commands 如何定义
- **Slide deck 生成 prompt**: 如何将非 PPT 内容（如代码 diff、数据表格）转化为 slide 结构
- **HTML 输出格式**: 生成的 HTML deck 结构，如何用 CSS 保证跨设备一致性

**具体要看哪些文件**:
```
skill.yaml                 # Skill 定义
src/                       # 核心生成逻辑
*.md                       # prompt 模板
```

**对我们项目的直接启发**:
- 它的 prompt 设计可能更成熟，可以参考来优化我们的 `generate-ppt` 命令 prompt
- 学习它如何将「结构化数据」转化为「slide 内容」的逻辑

---

### 5. ppt-master — 16,308⭐
**链接**: https://github.com/hugohe3/ppt-master

**定位**: AI 生成原生可编辑 PPTX（非图片），保留 PowerPoint 原生形状和动画

**我们要借鉴什么**:
- **原生 PPTX 生成**: 如何用 python-pptx / PptxGenJS 生成「真正的 PPTX 形状」而不是截图/图片
- **动画系统**: 如何在生成的 PPTX 中保留原生动画
- **版式自动匹配**: AI 如何决定每页用什么版式（title slide / content / chart / image）

**具体要看哪些文件**:
```
src/pptx_generator.py      # PPTX 生成核心（推测文件名）
src/layout_matcher.py      # 版式匹配逻辑（推测文件名）
templates/                 # PPTX 版式模板
```

**对我们项目的直接启发**:
- 我们目前生成的 PPTX 是否已经是「原生形状」？如果不是，这是提升质量的关键
- 学习它的版式自动匹配逻辑，改进我们的 `_create_fallback_layout`

---

### 6. PPTist — 8,946⭐
**链接**: https://github.com/pipipi-pikachu/PPTist

**定位**: 在线复刻 PowerPoint，Vue3 + TS，支持 AI 生成 PPT

**我们要借鉴什么**:
- **Slide 元素系统**: 文本框、图片、图表、表格、形状等如何抽象为统一的数据结构
- **主题系统**: 颜色主题、字体主题如何全局切换
- **布局预设**: 内置的 slide 布局有哪些，数据结构如何定义
- **画布渲染**: HTML 如何精确还原 PPT 的排版效果

**具体要看哪些文件**:
```
src/views/components/element/    # 所有 slide 元素组件
src/types/                       # TypeScript 类型定义（slide 数据结构）
src/configs/                     # 主题配置
src/store/                       # 状态管理，看主题/布局切换逻辑
src/hooks/                       # 业务逻辑 hook
```

**对我们项目的直接启发**:
- PPTist 的 `Slide` 数据结构和我们的 `content` 结构对比，看能否借鉴更丰富的元素类型
- 它的主题切换机制（全局 CSS 变量 or JSON token）可以参考

---

## B 级 — 底层技术参考

### 7. reveal.js — 71,205⭐
**链接**: https://github.com/hakimel/reveal.js

**定位**: HTML 演示框架之王

**我们要借鉴什么**:
- **主题 CSS 结构**: `css/theme/` 下的主题文件，看颜色、字体、背景如何参数化
- **Slide Section 结构**: `<section>` 如何组织，data 属性如何控制布局
- **背景系统**: 渐变、图片、视频背景如何配置

**具体要看哪些文件**:
```
css/theme/                 # 所有主题 CSS 文件
css/theme/template/        # 主题模板（变量定义）
dist/reveal.css            # 核心样式
index.html                 # 示例 slide 结构
```

**对我们项目的直接启发**:
- 它的 CSS 变量命名（`--r-background-color`、`--r-main-font` 等）可以作为我们模板 CSS 的命名参考
- Slide section 的 data 属性（`data-background`、`data-transition`）可以启发我们扩展模板配置

---

### 8. docxtemplater — 3,568⭐
**链接**: https://github.com/open-xml-templating/docxtemplater

**定位**: 模板引擎 — 先做 .pptx 模板，再注入 JSON 数据生成

**我们要借鉴什么**:
- **模板语法**: PPTX 模板中如何标记可替换位置（如 `{company_name}`）
- **数据注入架构**: JSON 数据如何映射到模板中的各个占位符
- **条件渲染**: 根据数据有无决定是否显示某些 slide 或元素

**具体要看哪些文件**:
```
src/                       # 核心解析和渲染逻辑
docs/                      # 文档，看模板语法设计
```

**对我们项目的直接启发**:
- 我们目前是从零生成 PPTX，可以参考「模板+数据注入」模式来优化：先有一个基础 PPTX 模板骨架，再注入提取的颜色/字体/内容
- 这样生成的 PPTX 质量会比纯代码构建更高

---

### 9. PptxGenJS — 5,315⭐
**链接**: https://github.com/gitbrent/PptxGenJS

**定位**: JS 端最成熟的 PPTX 生成库

**我们要借鉴什么**:
- **Slide Masters**: 母版系统如何定义（https://gitbrent.github.io/PptxGenJS/docs/masters/）
- **图表 API**: 如何在 PPTX 中插入原生图表（bar/line/pie）
- **表格/图片/形状**: 各种元素的 API 设计

**具体要看哪些文件**:
```
demos/                     # 示例代码
docs/                      # API 文档
src/                       # 源码
```

**对我们项目的直接启发**:
- 如果我们用 JS/Node 重写部分逻辑，可以直接用这个库
- 它的 Master Slide 概念可以借鉴到我们的模板系统中

---

### 10. decktape — 2,376⭐
**链接**: https://github.com/astefanutti/decktape

**定位**: 将 HTML 演示导出为 PDF/PPTX

**我们要借鉴什么**:
- **HTML → PPTX 转换**: 如何将 HTML/CSS 渲染结果转换为 PPTX 格式
- **Puppeteer/Playwright 集成**: 如何用 headless browser 渲染 HTML 后导出

**对我们项目的直接启发**:
- 如果我们想支持「先渲染精美 HTML preview，再转为 PPTX」，这是关键参考

---

## 优先级总结（开发 Agent 阅读建议）

### Phase 1 — 立即参考（对现有功能直接提升）
| 优先级 | 项目 | 改进点 |
|--------|------|--------|
| P0 | **html-ppt-skill** | 扩展主题系统（颜色+字体+间距+动画），丰富布局类型 |
| P0 | **beautiful-html-templates** | 模板分类体系和 agent 自动选择逻辑 |
| P1 | **ppt-master** | 原生 PPTX 形状生成（非截图），版式自动匹配 |
| P1 | **PPTist** | Slide 元素数据结构，主题切换机制 |

### Phase 2 — 中期参考（架构级改进）
| 优先级 | 项目 | 改进点 |
|--------|------|--------|
| P2 | **open-design** | Design System token 化，丰富风格提取维度 |
| P2 | **docxtemplater** | 引入「模板骨架+数据注入」模式 |
| P2 | **visual-explainer** | Agent Skill prompt 设计优化 |

### Phase 3 — 长期参考（技术储备）
| 优先级 | 项目 | 改进点 |
|--------|------|--------|
| P3 | **reveal.js** | CSS 主题系统，slide 结构定义 |
| P3 | **PptxGenJS** | 如果用 JS 重写生成层的 API 设计 |
| P3 | **decktape** | HTML → PPTX 转换方案 |

---

## 快速启动命令（开发 Agent 使用）

```bash
# 克隆所有 S/A 级参考项目到本地
cd ~/reference-repos
git clone https://github.com/nexu-io/open-design.git
git clone https://github.com/lewislulu/html-ppt-skill.git
git clone https://github.com/zarazhangrui/beautiful-html-templates.git
git clone https://github.com/nicobailon/visual-explainer.git
git clone https://github.com/hugohe3/ppt-master.git
git clone https://github.com/pipipi-pikachu/PPTist.git

# B 级项目（可选）
git clone https://github.com/hakimel/reveal.js.git
git clone https://github.com/open-xml-templating/docxtemplater.git
git clone https://github.com/gitbrent/PptxGenJS.git
```

---

*文档更新时间: 2026-05-14*
*调研 Agent: Claude*
*目标项目: html-pptx-template*
