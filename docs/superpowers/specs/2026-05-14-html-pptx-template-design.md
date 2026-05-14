# HTML-PPTX Template Skill — Design Spec

## 1. Overview

A Claude Code Skill that:
1. Takes a webpage URL, extracts its visual style (colors, fonts, spacing, layout rhythm), and saves it as a reusable PPT template.
2. Later, when a user provides content (text, images, data), the Skill generates a PPTX file matching the extracted style.
3. Supports multiple templates with arrow-key selection via `AskUserQuestion`.

### Key Decisions
- **Output format**: Custom YAML-based theme config + python-pptx for PPTX generation.
- **Web extraction**: Playwright (async) for rendering both static and SPA pages, then CSSOM extraction.
- **Template storage**: Folder-per-template under `templates/` with `meta.yaml`, `theme.yaml`, `layout.md`, `assets/`.
- **Interaction**: Claude Code `AskUserQuestion` for arrow-key selection; Skill proactively asks when template choice is ambiguous.

---

## 2. Project Structure

```
html-pptx-template/
├── skill.yaml                    # Claude Code Skill definition
├── pyproject.toml / setup.py     # Python package config
├── requirements.txt              # Dependencies
│
├── src/
│   ├── html_pptx_template/       # Main Python package
│   │   ├── __init__.py
│   │   ├── cli.py                # CLI entry: create-template, generate-ppt, list-templates
│   │   │
│   │   ├── extractor/            # Webpage style extraction
│   │   │   ├── __init__.py
│   │   │   ├── browser.py        # Playwright wrapper: launch, navigate, get computed styles
│   │   │   ├── css_parser.py     # Parse CSS rules: colors, fonts, spacing, sizes
│   │   │   ├── style_analyzer.py # Analyze & classify: primary/secondary/accent colors, heading/body fonts
│   │   │   └── screenshot.py     # Capture page/element screenshots for assets/
│   │   │
│   │   ├── templates/            # Template management
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # CRUD: create, list, load, delete templates
│   │   │   ├── index.py          # Template index scanning & discovery
│   │   │   └── schema.py         # Pydantic models: Meta, Theme, Layout
│   │   │
│   │   ├── generator/            # PPTX generation engine
│   │   │   ├── __init__.py
│   │   │   ├── engine.py         # Main orchestrator: read theme + layout + user content → PPTX
│   │   │   ├── slide_builder.py  # Build individual slides from layout definitions
│   │   │   ├── theme_applier.py  # Apply theme.yaml colors/fonts/spacing to python-pptx shapes
│   │   │   └── layout_parser.py  # Parse layout.md into slide type definitions
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── color.py          # Color utilities: hex↔rgb, color distance, palette extraction
│   │       └── validators.py     # Input validation helpers
│   │
│   └── tests/                    # Unit & integration tests
│
├── templates/                    # User template storage (gitignored, created at runtime)
│   └── (template folders)
│
└── docs/
    └── superpowers/specs/        # This design doc
```

---

## 3. Template Format Specification

Each template is a folder containing:

### 3.1 meta.yaml — Template Metadata

```yaml
id: "business-blue-20260514"      # Unique identifier
name: "商务蓝"                     # Display name
source_url: "https://example.com" # Source webpage
source_title: "Example Corp"      # Page title
source_favicon: "assets/favicon.png"
description: "深蓝色主调，适合商务汇报"
created_at: "2026-05-14T10:00:00Z"
tags: ["business", "blue", "formal", "corporate"]
version: 1
```

### 3.2 theme.yaml — Visual Style Configuration

```yaml
# Color palette (extracted from CSS)
colors:
  primary: "#1E3A5F"           # Main brand color
  secondary: "#4A90D9"         # Secondary/accent
  accent: "#E67E22"            # CTA/highlight color
  background: "#FFFFFF"        # Slide background
  surface: "#F5F7FA"           # Card/container background
  text_primary: "#2C3E50"      # Main text
  text_secondary: "#7F8C8D"    # Subtitle/caption
  text_on_primary: "#FFFFFF"   # Text on primary color bg

# Typography (extracted from font-family + font-size)
fonts:
  heading:
    family: "Microsoft YaHei, sans-serif"
    sizes:
      h1: 44        # Title slide
      h2: 32        # Section header
      h3: 24        # Slide title
    weight: "bold"
    color: "text_primary"
  body:
    family: "Microsoft YaHei, sans-serif"
    size: 18
    weight: "normal"
    color: "text_primary"
  caption:
    family: "Microsoft YaHei, sans-serif"
    size: 14
    color: "text_secondary"

# Spacing & layout rhythm
spacing:
  slide_padding: [40, 40, 40, 40]   # [top, right, bottom, left] in points
  content_gap: 20                    # Gap between content blocks
  line_spacing: 1.5                  # Line spacing multiplier

# Page proportions (inferred or default)
aspect_ratio: "16:9"                # 16:9 or 4:3
slide_width: 10.0                   # Inches
slide_height: 5.625                 # Inches
```

### 3.3 layout.md — Slide Layout Definitions

Defines the available slide types for this template. Used by the generator to know what layouts exist.

```markdown
# Slide Layouts

## title
- Type: title slide
- Background: primary color with gradient
- Elements:
  - Title (h1, centered, top 40%)
  - Subtitle (body, centered, below title)
  - Footer: source URL caption

## content
- Type: content slide
- Background: background color
- Elements:
  - Header bar: primary color, height 60pt
  - Slide title (h3, left-aligned, in header bar)
  - Content area: single column, body text

## two_column
- Type: content slide
- Background: background color
- Elements:
  - Header bar: primary color
  - Slide title (h3)
  - Left column: 50% width
  - Right column: 50% width

## section_divider
- Type: section divider
- Background: secondary color
- Elements:
  - Section title (h2, centered, white text)
  - Divider line: accent color

## image_left
- Type: content slide with image
- Background: background color
- Elements:
  - Header bar
  - Left 40%: image placeholder
  - Right 60%: text content
```

### 3.4 assets/ — Extracted Assets

```
assets/
├── fullpage.png          # Full page screenshot
├── color-palette.png     # Generated color palette visualization
├── hero-section.png      # Hero area crop (if identifiable)
└── favicon.png           # Site favicon
```

---

## 4. Webpage Style Extraction Module

### 4.1 Flow

```
URL input
  → Playwright launches headless browser
  → Navigate to URL, wait for network idle
  → Capture fullpage screenshot → assets/fullpage.png
  → Execute JS to collect computed styles:
      - All unique color values (bg, text, border)
      - All font-family declarations
      - Common font sizes
      - Spacing values (padding, margin, gap)
  → Extract DOM structure hints (section count, hero detection)
  → Close browser
  → CSS analysis & classification:
      - Cluster colors into palette (primary/secondary/accent/bg/text)
      - Identify heading vs body fonts
      - Infer spacing rhythm
  → Generate theme.yaml
  → Generate layout.md (default layouts + page-structure-inspired ones)
  → Generate meta.yaml
  → Save to templates/<id>/
```

### 4.2 Color Extraction Strategy

1. **Collect** all color values from computed styles (rgb, hex, hsl).
2. **Filter** out near-duplicates using color distance (CIEDE2000, threshold < 5).
3. **Classify** by usage frequency and context:
   - Most frequent background → `background`
   - Most frequent text → `text_primary`
   - Largest solid area (non-bg) → `primary`
   - Next most prominent → `secondary`
   - High saturation, used sparingly → `accent`
   - Light gray backgrounds → `surface`
   - Lighter text → `text_secondary`
4. **Validate** contrast ratios (WCAG 2.1 AA) between text/bg pairs.

### 4.3 Font Extraction Strategy

1. Collect all `font-family` values, weighted by element count.
2. Identify heading fonts: elements `h1`-`h6` + elements with larger sizes.
3. Identify body fonts: `p`, `span`, `li` elements.
4. Map to system fonts or record as-is (python-pptx will use best-match).
5. Extract size hierarchy: largest → h1, next → h2, next → h3, modal → body.

### 4.4 Playwright Integration

```python
# src/html_pptx_template/extractor/browser.py
from playwright.async_api import async_playwright

async def extract_styles(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(url, wait_until="networkidle")
        # Capture screenshot
        await page.screenshot(path="assets/fullpage.png", full_page=True)
        # Extract computed styles via JS evaluation
        styles = await page.evaluate("""
            () => {
                // JS code to collect colors, fonts, sizes, spacing
                // Returns structured data
            }
        """)
        await browser.close()
        return styles
```

---

## 5. PPTX Generation Engine

### 5.1 Flow

```
User provides content (text/markdown/json)
  → Load selected template (theme.yaml + layout.md)
  → Parse user content into slide content list
  → For each slide:
      - Select appropriate layout from layout.md
      - Create slide in python-pptx Presentation
      - Apply theme colors, fonts, spacing
      - Fill in user content (text, images, tables)
  → Save as .pptx
```

### 5.2 Content Input Format

Users provide content in a simple markdown format:

```markdown
# 我的汇报标题
## 副标题
---
# 第一部分：市场分析
- 要点一
- 要点二
- 要点三
---
# 数据对比
| 指标 | Q1 | Q2 |
|------|----|----|
| 收入 | 100 | 150 |
| 用户 | 1k | 2k |
---
# 总结
总结文字内容
```

The generator parses `---` as slide separators and maps each slide to the best-matching layout.

### 5.3 Theme Application

```python
# src/html_pptx_template/generator/theme_applier.py
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor

def apply_text_style(run, text_config, theme):
    """Apply theme font, size, color to a text run."""
    run.font.name = text_config["family"].split(",")[0].strip()
    run.font.size = Pt(text_config["size"])
    run.font.bold = text_config.get("weight") == "bold"
    color_key = text_config["color"]
    hex_color = theme.colors[color_key]
    run.font.color.rgb = RGBColor.from_string(hex_color.lstrip("#"))
```

### 5.4 Slide Layout Selection

Heuristic mapping from content to layout:
- Starts with `#` title → `title` layout
- Starts with `#` mid-document → `section_divider` or `content`
- Contains table → `content` (table layout)
- Contains image reference → `image_left` or `image_right`
- Bullet list only → `content`
- Two bullet lists → `two_column`

---

## 6. Template Management Module

### 6.1 Template Index

`templates/` directory scanned on-demand. No persistent index file needed (rebuild on access, cached in memory).

### 6.2 Manager API

```python
class TemplateManager:
    def create(self, url: str, name: str = None) -> Template
    def list(self) -> list[TemplateMeta]           # For AskUserQuestion options
    def load(self, template_id: str) -> Template
    def delete(self, template_id: str) -> bool
    def set_default(self, template_id: str) -> bool
    def get_default(self) -> TemplateMeta | None
```

### 6.3 Default Template Storage

Default template ID stored in a config file:

```
~/.config/html-pptx-template/config.yaml
```

```yaml
default_template: "business-blue-20260514"
last_used: "tech-dark-20260515"
```

---

## 7. Skill Interaction Flow

### 7.1 Skill Definition (skill.yaml)

```yaml
name: html-pptx-template
description: Extract webpage styles into PPT templates and generate styled presentations

commands:
  create-template:
    description: Create a new PPT template from a webpage URL
    prompt: >
      Extract the visual style from {{url}} and save it as a reusable PPT template.
      Ask the user for a template name if not provided.
    arguments:
      - name: url
        required: true
      - name: name
        required: false

  generate-ppt:
    description: Generate a PPTX from user content using a template
    prompt: >
      Generate a PPTX presentation from the user's content.
      If no template is specified, check for a default template.
      If no default is set or --select flag is used, use AskUserQuestion
      to let the user choose from available templates with arrow keys.
    arguments:
      - name: content
        required: true
      - name: template
        required: false
      - name: select
        type: boolean
        default: false
        description: Force template selection prompt

  list-templates:
    description: List all available templates
    prompt: List all saved PPT templates with their metadata.

  set-default:
    description: Set the default template
    prompt: Set {{template_id}} as the default template.
    arguments:
      - name: template_id
        required: true
```

### 7.2 generate-ppt Decision Flow

```
User calls generate-ppt
  → Parse arguments
  → If template_id provided:
      → Use that template
  → Else, check for default template:
      → If default exists AND --select is False:
          → Use default template (inform user which one is being used)
      → Else:
          → Scan templates/ directory
          → If 0 templates: error, suggest create-template
          → If 1 template: use it
          → If 2+ templates: AskUserQuestion with arrow-key list
              → User selects with ↑↓ + Enter
              → Proceed with selected template
  → Parse user content (markdown → slide list)
  → Load template (theme.yaml + layout.md)
  → Generate PPTX
  → Save to output path (default: current working directory)
  → Report success with file path
```

### 7.3 AskUserQuestion Integration

```python
# In the Skill flow, when template selection is needed:
# (This is pseudocode for how the Skill would invoke AskUserQuestion)

templates = manager.list()  # Returns list of Meta objects
options = [
    {"label": f"{t.name} — {t.description}", "value": t.id}
    for t in templates
]
# Claude Code AskUserQuestion renders options with arrow-key navigation
selected = ask_user_question(
    question="请选择PPT模板：",
    options=options
)
template = manager.load(selected)
```

---

## 8. Dependencies

### 8.1 Python Packages (requirements.txt)

```
# Web extraction
playwright>=1.40.0
beautifulsoup4>=4.12.0

# PPTX generation
python-pptx>=0.6.23

# Data validation & config
pydantic>=2.0.0
pyyaml>=6.0

# Color science
colour-science>=0.4.3

# Utilities
aiohttp>=3.9.0
Pillow>=10.0.0
```

### 8.2 System Dependencies

- Python 3.10+
- Playwright browsers: `playwright install chromium`

---

## 9. Usage Examples

### 9.1 Create Template

```bash
# CLI
html-pptx create-template https://stripe.com --name "Stripe Style"

# Claude Code Skill
/create-template https://stripe.com
# → Template "stripe-style-20260514" created from stripe.com
# → Extracted: primary=#635BFF, secondary=#0A2540, accent=#00D4AA
```

### 9.2 Generate PPT (with default template)

```bash
# CLI
html-pptx generate-ppt my-content.md --output presentation.pptx

# Claude Code Skill
/generate-ppt
# (paste markdown content)
# → Using default template "business-blue-20260514"
# → Generated: presentation.pptx (12 slides)
```

### 9.3 Generate PPT (with template selection)

```bash
# CLI
html-pptx generate-ppt my-content.md --select

# Claude Code Skill
/generate-ppt --select
# → ? 请选择PPT模板 (Use arrow keys)
# → ❯ 商务蓝 — 来自 example.com
# →   极简白 — 来自 minimal.com
# →   科技黑 — 来自 tech.com
```

### 9.4 List Templates

```bash
# CLI
html-pptx list-templates

# Output:
# ┌──────┬────────────────────┬────────────────────┐
# │ Name │ Source             │ Created            │
# ├──────┼────────────────────┼────────────────────┤
# │ 商务蓝│ example.com        │ 2026-05-14         │
# │ 极简白│ minimal.com        │ 2026-05-13         │
# └──────┴────────────────────┴────────────────────┘
```

---

## 10. Error Handling

| Error Scenario | Handling |
|---|---|
| URL unreachable | Retry 3x with backoff, then error with suggestion |
| Page blocks scraping | Fallback to static requests (limited extraction) |
| No colors found | Error with raw CSS dump for debugging |
| No templates exist | Prompt user to run create-template first |
| python-pptx shape overflow | Auto-scale font or split to next slide |
| Invalid user markdown | Parse error with line number hint |

---

## 11. Future Extensions (Out of Scope for v1)

- Template sharing/import (download templates from a registry)
- Animation style extraction and application
- Chart generation from data
- Multi-language font detection and matching
- Template preview generation (thumbnail slide deck)
