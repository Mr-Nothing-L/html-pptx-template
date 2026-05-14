"""CLI entry point for html-pptx-template."""

import asyncio
from pathlib import Path

import click

from html_pptx_template.extractor.browser import BrowserExtractor
from html_pptx_template.extractor.css_parser import CSSParser
from html_pptx_template.extractor.style_analyzer import StyleAnalyzer
from html_pptx_template.generator.engine import GeneratorEngine
from html_pptx_template.templates.manager import TemplateManager


@click.group()
@click.option("--templates-dir", type=click.Path(), default=None)
@click.pass_context
def cli(ctx, templates_dir):
    """HTML-PPTX Template CLI - extract webpage styles into reusable PPT templates."""
    ctx.ensure_object(dict)

    if templates_dir is None:
        templates_dir = Path.cwd() / "templates"
    else:
        templates_dir = Path(templates_dir)

    ctx.obj["templates_dir"] = templates_dir


@cli.command()
@click.argument("url")
@click.option("--name", "-n", default=None)
@click.option("--no-screenshots", is_flag=True, help="Skip screenshot capture")
@click.pass_context
def create_template(ctx, url, name, no_screenshots):
    """Create template from URL. Captures screenshots for visual analysis."""
    templates_dir = ctx.obj["templates_dir"]
    manager = TemplateManager(templates_dir)

    # 1. Extract styles via BrowserExtractor (async)
    extractor = BrowserExtractor()
    screenshot_dir = None if no_screenshots else str(templates_dir / "_temp_screenshots")
    raw_styles = asyncio.run(extractor.extract_styles(url, screenshot_dir=screenshot_dir))

    screenshots = raw_styles.pop("screenshots", [])

    # 2. Parse via CSSParser
    parser = CSSParser()
    parsed = parser.parse(raw_styles)

    # If name not provided, use page title
    if name is None:
        name = parsed.get("page_title", "Untitled")
        if not name.strip():
            name = "Untitled"

    # 3. Analyze via StyleAnalyzer
    analyzer = StyleAnalyzer()
    theme = analyzer.build_theme(parsed)

    # 4. Create template via TemplateManager
    template = manager.create(url=url, name=name, theme=theme, screenshots=screenshots)

    # 5. Move screenshots to template assets directory
    template_assets = templates_dir / template.meta.id / "assets"
    if screenshots and not no_screenshots:
        for screenshot_path in screenshots:
            src = Path(screenshot_path)
            if src.exists():
                dst = template_assets / src.name
                import shutil
                shutil.move(str(src), str(dst))
        # Clean up temp directory if empty
        temp_dir = Path(screenshot_dir)
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
        # Update screenshot paths to relative
        click.echo(f"  Screenshots: {len(screenshots)} captured")
        for s in screenshots:
            click.echo(f"    - assets/{Path(s).name}")

    # 6. Output template info
    click.echo(f"Template created:")
    click.echo(f"  ID: {template.meta.id}")
    click.echo(f"  Name: {template.meta.name}")
    click.echo(f"  Primary color: {template.theme.colors.primary}")
    click.echo(f"  Font: {template.theme.fonts.heading.family}")
    click.echo(f"  Assets dir: {template_assets}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review screenshots in {template_assets}")
    click.echo(f"  2. Fill in visual_analysis.md for richer style understanding")
    click.echo(f"  3. Use generate-ppt to create presentations with this template")


@cli.command("list-templates")
@click.pass_context
def list_templates(ctx):
    """List all templates in table format."""
    templates_dir = ctx.obj["templates_dir"]
    manager = TemplateManager(templates_dir)

    templates = manager.list()

    if not templates:
        click.echo("No templates found.")
        return

    # Output: Name | Source | Created
    click.echo(f"{'Name':<30} {'Source':<40} {'Created'}")
    click.echo("-" * 100)
    for t in templates:
        source = t.source_url[:38] if len(t.source_url) > 38 else t.source_url
        created = t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "N/A"
        click.echo(f"{t.name:<30} {source:<40} {created}")


@cli.command()
@click.argument("content_file", type=click.File("r", encoding="utf-8"))
@click.option("--template", "-t", default=None)
@click.option("--output", "-o", default="presentation.pptx")
@click.option("--select", is_flag=True)
@click.pass_context
def generate_ppt(ctx, content_file, template, output, select):
    """Generate PPTX from markdown content file."""
    templates_dir = ctx.obj["templates_dir"]
    manager = TemplateManager(templates_dir)

    # Template selection logic:
    template_id = None

    # 1. If --template specified, use it
    if template:
        template_id = template
    # 2. Else if not --select, use default template (if set)
    elif not select:
        default = manager.get_default()
        if default is not None:
            template_id = default.id

    # 3. If still no template_id, check available templates
    if template_id is None:
        all_templates = manager.list()

        # 3.1 If 0 templates: error
        if len(all_templates) == 0:
            click.echo("Error: No templates available. Create one first with create-template.", err=True)
            ctx.exit(1)

        # 4. If 1 template: use it
        if len(all_templates) == 1:
            template_id = all_templates[0].id
        # 5. Else (2+ templates): print list, exit with code 1
        else:
            click.echo("Multiple templates available. Please specify one with --template:", err=True)
            for t in all_templates:
                click.echo(f"  - {t.name} ({t.id})", err=True)
            ctx.exit(1)

    # Load the template
    loaded_template = manager.load(template_id)
    if loaded_template is None:
        click.echo(f"Error: Template '{template_id}' not found.", err=True)
        ctx.exit(1)

    # Parse content and generate PPTX
    content = content_file.read()
    engine = GeneratorEngine()
    slides_data = engine.parse_content(content)
    assets_dir = templates_dir / template_id / "assets"
    engine.generate(loaded_template, slides_data, output, assets_dir=assets_dir)

    click.echo(f"Generated {len(slides_data)} slide(s) -> {output}")


@cli.command()
@click.argument("template_id")
@click.pass_context
def set_default(ctx, template_id):
    """Set default template."""
    templates_dir = ctx.obj["templates_dir"]
    manager = TemplateManager(templates_dir)

    result = manager.set_default(template_id)
    if result:
        click.echo(f"Default template set to: {template_id}")
    else:
        click.echo(f"Error: Template '{template_id}' does not exist.", err=True)
        ctx.exit(1)


# main() entry point for console script
def main():
    cli()
