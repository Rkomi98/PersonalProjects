"""Generate a PPTX deck from structured slide data."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .layouts import LayoutPlan, LayoutBlock, LayoutTemplate
from .slide_models import SlideContent, SlideDeck

try:
    import cairosvg
except ImportError:  # pragma: no cover - fallback if dependency missing
    cairosvg = None

try:  # pragma: no cover - Pillow is optional
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


@dataclass(frozen=True)
class SlideStyle:
    background_hex: str = "#FFFFFF"
    accent_hex: str = "#C12A22"
    title_color_hex: str = "#1E293B"
    body_color_hex: str = "#475569"
    title_font: str = "Poppins"
    body_font: str = "Lato"

    @staticmethod
    def _hex_to_rgb(value: str) -> RGBColor:
        value = value.lstrip("#")
        return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))

    def accent_rgb(self) -> RGBColor:
        return self._hex_to_rgb(self.accent_hex)

    def title_rgb(self) -> RGBColor:
        return self._hex_to_rgb(self.title_color_hex)

    def body_rgb(self) -> RGBColor:
        return self._hex_to_rgb(self.body_color_hex)

    def background_rgb(self) -> RGBColor:
        return self._hex_to_rgb(self.background_hex)


class SlideDeckWriter:
    """Create a PPTX document following the Datapizza brand rules."""

    def __init__(
        self,
        *,
        style: SlideStyle,
        logo_path: Path,
        cover_logo_path: Path | None = None,
        svg_output_dir: Path | None = None,
        layout_plan: LayoutPlan | None = None,
    ):
        self.style = style
        self.logo_path = self._prepare_logo_path(logo_path)
        self.cover_logo_path = self._prepare_logo_path(cover_logo_path or logo_path)
        self.svg_output_dir = svg_output_dir
        self.layout_plan = layout_plan

    def build(self, deck: SlideDeck, output_path: Path) -> Path:
        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        self._add_cover_slide(prs, deck)
        for idx, slide in enumerate(deck.slides, start=1):
            self._add_content_slide(prs, slide, idx)

        output_path = output_path if output_path.suffix else output_path.with_suffix(".pptx")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        prs.save(output_path)
        return output_path

    # --- Slide helpers -------------------------------------------------
    def _set_background(self, slide) -> None:
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = self.style.background_rgb()

    def _prepare_logo_path(self, path: Path) -> Path:
        if not path or not path.exists() or Image is None:
            return path
        try:
            with Image.open(path) as img:
                if img.format == "ICO":
                    converted = path.with_name(path.stem + "_converted.png")
                    img.save(converted, format="PNG")
                    return converted
        except Exception:
            return path
        return path

    def _add_title_underline(self, slide, presentation: Presentation) -> None:
        """Add a slim accent bar under the title."""
        line = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            Inches(0.8),
            Inches(1.7),
            Inches(2.5),
            Pt(4),
        )
        line.fill.solid()
        line.fill.fore_color.rgb = self.style.accent_rgb()
        line.line.fill.background()

    def _add_icon_bullet(
        self,
        paragraph,
        bullet_text: str,
        icon_type: str = "check",
        include_icon_glyph: bool = True,
    ) -> str:
        """Prefix bullet text with a simple icon placeholder and return the glyph."""
        icons = {"check": "✓", "arrow": "→", "star": "★", "dot": "●", "alert": "⚠"}
        icon = icons.get(icon_type, "•")
        paragraph.text = f"{icon}  {bullet_text}" if include_icon_glyph else bullet_text
        paragraph.level = 0
        return icon

    def _select_icon_type(self, bullet_text: str, fallback: str = "dot") -> str:
        text = bullet_text.lower()
        keyword_map = {
            "alert": ["risch", "critic", "issue", "proble", "warning"],
            "arrow": ["cresc", "scal", "espans", "aument", "acceler", "roadmap", "rollout"],
            "check": ["qualit", "affid", "sicurez", "compliance", "garant"],
            "star": ["chiave", "strateg", "premium", "core", "highlight", "valore"],
        }
        for icon, keywords in keyword_map.items():
            if any(keyword in text for keyword in keywords):
                return icon
        return fallback

    ICON_HINT_REGEX = re.compile(r"\[icon[:\s]+([a-z0-9_\-]+)\]", re.IGNORECASE)

    def _extract_icon_hint(self, bullet_text: str) -> tuple[str, str | None]:
        match = self.ICON_HINT_REGEX.search(bullet_text)
        if not match:
            return bullet_text.strip(), None
        icon_name = match.group(1).lower()
        cleaned = (bullet_text[: match.start()] + bullet_text[match.end() :]).strip()
        return cleaned, icon_name

    def _map_icon_hint(self, icon_name: str | None, fallback: str) -> str:
        if not icon_name:
            return fallback
        mapping = {
            "chevron_right": "arrow",
            "chevron_forward": "arrow",
            "arrow_forward": "arrow",
            "trending_up": "arrow",
            "check_circle": "check",
            "verified": "check",
            "done": "check",
            "star": "star",
            "grade": "star",
            "workspace_premium": "star",
            "warning": "alert",
            "error": "alert",
            "priority_high": "alert",
            "radio_button_checked": "dot",
            "adjust": "dot",
            "bolt": "dot",
        }
        return mapping.get(icon_name, fallback)

    def _render_icon_bullets(
        self,
        slide,
        bullets: list[str],
        *,
        left,
        top,
        width,
        max_items: int | None = None,
    ) -> int:
        """Render bullets as rows with standalone icon badges."""
        items = bullets[:max_items] if max_items else bullets
        if not items:
            return 0

        icon_cycle = ["check", "arrow", "dot", "star"]
        icon_size = Inches(0.4)
        row_height = Inches(0.78)
        text_left = left + icon_size + Inches(0.25)
        text_width = width - (text_left - left)
        accent_rgb = self.style.accent_rgb()
        light_rgb = RGBColor(254, 242, 242)

        for idx, bullet in enumerate(items):
            current_top = top + idx * row_height
            fallback_icon = icon_cycle[idx % len(icon_cycle)]
            cleaned_bullet, hinted_icon = self._extract_icon_hint(bullet)
            icon_type = self._map_icon_hint(hinted_icon, fallback_icon)
            icon_type = self._select_icon_type(cleaned_bullet, fallback=icon_type)
            icon_top = current_top + (row_height - icon_size) / 2
            text_box = slide.shapes.add_textbox(
                text_left,
                current_top,
                text_width,
                row_height,
            )
            text_frame = text_box.text_frame
            text_frame.clear()
            text_frame.word_wrap = True
            text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            paragraph = text_frame.paragraphs[0]
            icon_char = self._add_icon_bullet(
                paragraph,
                cleaned_bullet,
                icon_type,
                include_icon_glyph=False,
            )
            paragraph.font.name = self.style.body_font
            paragraph.font.size = Pt(20)
            paragraph.font.color.rgb = self.style.body_rgb()

            icon_shape = slide.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.OVAL,
                left,
                icon_top,
                icon_size,
                icon_size,
            )
            use_light_fill = icon_type in {"star", "arrow"}
            icon_shape.fill.solid()
            icon_shape.fill.fore_color.rgb = light_rgb if use_light_fill else accent_rgb
            icon_shape.line.fill.background()
            icon_frame = icon_shape.text_frame
            icon_frame.clear()
            icon_frame.text = icon_char
            icon_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            icon_para = icon_frame.paragraphs[0]
            icon_para.alignment = PP_ALIGN.CENTER
            icon_run = icon_para.runs[0]
            icon_run.font.name = self.style.title_font
            icon_run.font.size = Pt(16)
            icon_run.font.bold = True
            icon_run.font.color.rgb = (
                self.style.accent_rgb() if use_light_fill else self.style.background_rgb()
            )

        return row_height * len(items)

    def _render_simple_list(
        self,
        slide,
        bullets: list[str],
        *,
        left,
        top,
        width,
        font_size: int = 18,
        max_items: int | None = None,
    ) -> None:
        entries = bullets[:max_items] if max_items else bullets
        if not entries:
            return
        box = slide.shapes.add_textbox(left, top, width, Inches(2.5))
        frame = box.text_frame
        frame.clear()
        frame.word_wrap = True
        for idx, text in enumerate(entries):
            paragraph = frame.paragraphs[0] if idx == 0 else frame.add_paragraph()
            cleaned_text, hinted_icon = self._extract_icon_hint(text)
            icon_type = self._map_icon_hint(hinted_icon, "dot")
            icon_type = self._select_icon_type(cleaned_text, fallback=icon_type)
            self._add_icon_bullet(
                paragraph,
                cleaned_text,
                icon_type,
                include_icon_glyph=True,
            )
            paragraph.font.name = self.style.body_font
            paragraph.font.size = Pt(font_size)
            paragraph.font.color.rgb = self.style.body_rgb()

    def _render_card_grid(
        self,
        slide,
        bullets: list[str],
        *,
        left,
        top,
        width,
        columns: int = 2,
        card_height: float = 1.8,
        max_items: int | None = None,
    ) -> None:
        entries = bullets[:max_items] if max_items else bullets
        if not entries:
            return
        gap = Inches(0.3)
        columns = max(1, columns)
        column_width = (width - gap * (columns - 1)) / columns
        card_height_emu = Inches(card_height)
        accent = self.style.accent_rgb()
        light = RGBColor(254, 242, 242)

        for idx, text in enumerate(entries):
            col = idx % columns
            row = idx // columns
            current_left = left + col * (column_width + gap)
            current_top = top + row * (card_height_emu + gap)
            card = slide.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                current_left,
                current_top,
                column_width,
                card_height_emu,
            )
            card.fill.solid()
            card.fill.fore_color.rgb = light
            card.line.color.rgb = accent
            card.shadow.inherit = False
            card.shadow.transparency = 0.8
            card.shadow.blur_radius = 4
            card.shadow.distance = 3

            cleaned_text, hinted_icon = self._extract_icon_hint(text)
            title_text, body_text = (cleaned_text.split(":", 1) + [""])[:2]
            title_text = title_text.strip()
            body_text = body_text.strip()
            icon_type = self._map_icon_hint(hinted_icon, "dot")
            icon_type = self._select_icon_type(title_text or cleaned_text, fallback=icon_type)
            title_text = title_text.strip()
            body_text = body_text.strip()

            frame = card.text_frame
            frame.clear()
            frame.word_wrap = True
            title_para = frame.paragraphs[0]
            self._add_icon_bullet(
                title_para,
                title_text,
                icon_type,
                include_icon_glyph=True,
            )
            title_para.font.name = self.style.title_font
            title_para.font.size = Pt(18)
            title_para.font.bold = True
            title_para.font.color.rgb = self.style.title_rgb()
            if body_text:
                body_para = frame.add_paragraph()
                body_para.text = body_text
                body_para.font.name = self.style.body_font
                body_para.font.size = Pt(14)
                body_para.font.color.rgb = self.style.body_rgb()

    def _render_insights(
        self,
        slide,
        insights: list[str],
        *,
        left,
        top,
        width,
        height,
    ) -> None:
        if not insights:
            return
        box_height = height or Inches(1.8)
        insight_box = slide.shapes.add_textbox(left, top, width, box_height)
        insight_frame = insight_box.text_frame
        insight_frame.clear()
        for idx, insight in enumerate(insights):
            ip = insight_frame.paragraphs[0] if idx == 0 else insight_frame.add_paragraph()
            ip.text = insight
            ip.level = 0
            ip.font.name = self.style.body_font
            ip.font.size = Pt(16)
            ip.font.color.rgb = self.style.title_rgb()
            ip.alignment = PP_ALIGN.LEFT

    def _add_key_message(
        self,
        slide,
        prs: Presentation,
        key_message: str,
        *,
        use_box: bool = True,
    ) -> None:
        if use_box:
            key_box = slide.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                Inches(0.8),
                Inches(1.9),
                prs.slide_width - Inches(3.2),
                Inches(0.85),
            )
            key_box.fill.solid()
            key_box.fill.fore_color.rgb = self.style.accent_rgb()
            key_box.line.fill.background()
            key_box.shadow.inherit = False
            key_box.shadow.style = 2
            key_frame = key_box.text_frame
            key_frame.margin_left = Pt(20)
            key_frame.margin_right = Pt(20)
            key_frame.margin_top = Pt(15)
            key_frame.margin_bottom = Pt(15)
            key_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            key_frame.text = key_message
            key_para = key_frame.paragraphs[0]
            key_para.alignment = PP_ALIGN.LEFT
            key_run = key_para.runs[0]
            key_run.font.name = self.style.body_font
            key_run.font.bold = True
            key_run.font.size = Pt(20)
            key_run.font.color.rgb = self.style.background_rgb()
            return

        text_box = slide.shapes.add_textbox(
            Inches(0.8),
            Inches(1.95),
            prs.slide_width - Inches(3.2),
            Inches(0.6),
        )
        frame = text_box.text_frame
        frame.text = key_message
        paragraph = frame.paragraphs[0]
        paragraph.font.name = self.style.body_font
        paragraph.font.size = Pt(20)
        paragraph.font.bold = True
        paragraph.font.color.rgb = self.style.accent_rgb()

    def _fallback_template(self) -> LayoutTemplate:
        blocks = [
            LayoutBlock(type="bullets", x=0.8, y=3.0, width=6.3, style="badges", max_items=5),
            LayoutBlock(type="visual", x=7.8, y=2.8, width=4.6, height=3.5),
            LayoutBlock(type="insights", x=0.8, y=6.5, width=6.3, height=1.6),
        ]
        return LayoutTemplate(
            name="legacy_split",
            description=None,
            blocks=blocks,
            decorations={"circle": "bottom_right", "underline": True, "key_box": True},
            aliases=[],
        )

    def _resolve_layout_template(
        self, slide_index: int, requested_layout: str | None
    ) -> LayoutTemplate:
        if self.layout_plan:
            return self.layout_plan.resolve_template(slide_index, requested_layout)
        return self._fallback_template()

    def _render_layout_block(
        self,
        block: LayoutBlock,
        slide,
        slide_content: SlideContent,
        slide_index: int,
    ) -> None:
        left = Inches(block.x)
        top = Inches(block.y)
        width = Inches(block.width)
        height = Inches(block.height) if block.height else None
        style = (block.style or "").lower()

        if block.type == "bullets":
            bullets = slide_content.bullets or []
            if not bullets:
                return
            if style == "cards":
                self._render_card_grid(
                    slide,
                    bullets,
                    left=left,
                    top=top,
                    width=width,
                    columns=block.columns or 2,
                    card_height=block.card_height or 1.8,
                    max_items=block.max_items,
                )
            elif style == "simple":
                self._render_simple_list(
                    slide,
                    bullets,
                    left=left,
                    top=top,
                    width=width,
                    max_items=block.max_items,
                )
            else:
                self._render_icon_bullets(
                    slide,
                    bullets,
                    left=left,
                    top=top,
                    width=width,
                    max_items=block.max_items,
                )
            return

        if block.type == "cards":
            self._render_card_grid(
                slide,
                slide_content.bullets or [],
                left=left,
                top=top,
                width=width,
                columns=block.columns or 2,
                card_height=block.card_height or 1.8,
                max_items=block.max_items,
            )
            return

        if block.type == "insights":
            self._render_insights(
                slide,
                slide_content.insights or [],
                left=left,
                top=top,
                width=width,
                height=height,
            )
            return

        if block.type == "visual":
            if slide_content.visual:
                self._draw_visual_block(
                    slide=slide,
                    slide_content=slide_content,
                    slide_index=slide_index,
                    left=left,
                    width=width,
                    top=top,
                    layout=style or "custom",
                    height=height,
                )
            return

    def _add_logo(
        self,
        slide,
        presentation: Presentation,
        *,
        position: str = "top_right",
        logo_path: Path | None = None,
    ) -> None:
        path = logo_path or self.logo_path
        if not path.exists():
            return
        width = Inches(1.6)
        margin = Inches(0.4)
        if position == "bottom_right":
            left = presentation.slide_width - width - margin
            top = presentation.slide_height - Inches(1.2)
        elif position == "bottom_left":
            left = margin
            top = presentation.slide_height - Inches(1.2)
        elif position == "top_left":
            left = margin
            top = Inches(0.3)
        else:  # top_right default
            left = presentation.slide_width - width - margin
            top = Inches(0.3)
        slide.shapes.add_picture(str(path), left, top, width=width)

    def _add_cover_slide(self, prs: Presentation, deck: SlideDeck) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._set_background(slide)
        self._add_logo(slide, prs, position="top_right")
        if self.cover_logo_path:
            self._add_logo(slide, prs, position="bottom_right", logo_path=self.cover_logo_path)

        title_box = slide.shapes.add_textbox(
            Inches(1.6), Inches(2), prs.slide_width - Inches(3.2), Inches(2.4)
        )
        title_frame = title_box.text_frame
        title_frame.clear()
        p = title_frame.paragraphs[0]
        p.text = deck.cover_title
        p.alignment = PP_ALIGN.LEFT
        run = p.runs[0]
        run.font.name = self.style.title_font
        run.font.size = Pt(48)
        run.font.bold = True
        run.font.color.rgb = self.style.title_rgb()

        if deck.cover_subtitle:
            subtitle_box = slide.shapes.add_textbox(
                Inches(1.6), Inches(4.2), prs.slide_width - Inches(3.2), Inches(1.2)
            )
            st_frame = subtitle_box.text_frame
            st_frame.text = deck.cover_subtitle
            st_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            st_run = st_frame.paragraphs[0].runs[0]
            st_run.font.name = self.style.body_font
            st_run.font.size = Pt(24)
            st_run.font.color.rgb = self.style.body_rgb()

        summary_box = slide.shapes.add_textbox(
            Inches(1.6), Inches(5.1), prs.slide_width - Inches(3.2), Inches(1.5)
        )
        summary_frame = summary_box.text_frame
        summary_frame.text = deck.summary
        summary_para = summary_frame.paragraphs[0]
        summary_para.font.name = self.style.body_font
        summary_para.font.size = Pt(18)
        summary_para.font.color.rgb = self.style.body_rgb()

    def _add_content_slide(
        self, prs: Presentation, slide_content: SlideContent, slide_index: int
    ) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._set_background(slide)
        template = self._resolve_layout_template(slide_index, slide_content.layout)
        decorations = template.decorations or {}
        self._add_logo(slide, prs)

        title_box = slide.shapes.add_textbox(
            Inches(0.8), Inches(0.8), prs.slide_width - Inches(2.4), Inches(1.0)
        )
        title_frame = title_box.text_frame
        title_frame.clear()
        title_para = title_frame.paragraphs[0]
        title_para.text = slide_content.title
        title_para.alignment = PP_ALIGN.LEFT
        title_run = title_para.runs[0]
        title_run.font.name = self.style.title_font
        title_run.font.size = Pt(36)
        title_run.font.bold = True
        title_run.font.color.rgb = self.style.title_rgb()
        if decorations.get("underline", True):
            self._add_title_underline(slide, prs)

        if slide_content.key_message:
            self._add_key_message(
                slide,
                prs,
                slide_content.key_message,
                use_box=decorations.get("key_box", True),
            )

        for block in template.blocks:
            self._render_layout_block(block, slide, slide_content, slide_index)

        notes_text = slide_content.speaker_notes
        if notes_text:
            notes_frame = slide.notes_slide.notes_text_frame
            notes_frame.text = notes_text
            notes_frame.paragraphs[0].font.name = self.style.body_font
            notes_frame.paragraphs[0].font.size = Pt(12)

    def _draw_visual_block(
        self,
        *,
        slide,
        slide_content: SlideContent,
        slide_index: int,
        left: float,
        width: float,
        top: float,
        layout: str,
        height: float | None = None,
    ) -> None:
        visual = slide_content.visual
        if not visual:
            return

        visual_height = height or Inches(3.8 if layout == "visual_full" else 2.8)
        png_path = self._materialize_svg(visual.svg_markup, slide_index)
        if png_path and png_path.exists():
            slide.shapes.add_picture(
                str(png_path), left, top, width=width, height=visual_height
            )
            caption_top = top + visual_height + Inches(0.1)
        else:
            visual_box = slide.shapes.add_textbox(left, top, width, visual_height)
            visual_frame = visual_box.text_frame
            visual_frame.text = (
                f"Visual suggerito ({visual.type}): {visual.description}"
            )
            visual_para = visual_frame.paragraphs[0]
            visual_para.font.name = self.style.body_font
            visual_para.font.size = Pt(16)
            visual_para.font.color.rgb = self.style.body_rgb()
            caption_top = top + visual_height

        if visual.caption:
            caption_box = slide.shapes.add_textbox(
                left, caption_top, width, Inches(0.8)
            )
            caption_frame = caption_box.text_frame
            caption_frame.text = visual.caption
            caption_para = caption_frame.paragraphs[0]
            caption_para.font.name = self.style.body_font
            caption_para.font.size = Pt(14)
            caption_para.font.color.rgb = self.style.body_rgb()

    def _materialize_svg(self, svg_markup: str | None, slide_index: int) -> Path | None:
        if not svg_markup or not self.svg_output_dir:
            return None

        cleaned_svg = self._clean_svg_markup(svg_markup)
        if "<svg" not in cleaned_svg:
            return None

        self.svg_output_dir.mkdir(parents=True, exist_ok=True)
        svg_path = self.svg_output_dir / f"slide_{slide_index:02d}.svg"
        svg_path.write_text(cleaned_svg, encoding="utf-8")

        if not cairosvg:
            return None

        png_path = svg_path.with_suffix(".png")
        try:
            cairosvg.svg2png(bytestring=cleaned_svg.encode("utf-8"), write_to=str(png_path))
        except Exception:
            return None

        return png_path

    def _clean_svg_markup(self, svg_markup: str) -> str:
        """Strip markdown fences and guarantee a valid XML prolog."""
        text = svg_markup.strip()
        if "```" in text:
            text = "\n".join(
                line for line in text.splitlines() if not line.strip().startswith("```")
            )
        start = text.find("<svg")
        if start == -1:
            return svg_markup.strip()
        end = text.rfind("</svg>")
        if end != -1 and end > start:
            text = text[start : end + len("</svg>")]
        else:
            text = text[start:].rstrip() + "</svg>"
        return text
