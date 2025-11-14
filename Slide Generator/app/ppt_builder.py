"""Generate a PPTX deck from structured slide data."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .slide_models import SlideContent, SlideDeck

try:
    import cairosvg
except ImportError:  # pragma: no cover - fallback if dependency missing
    cairosvg = None


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
        svg_output_dir: Path | None = None,
    ):
        self.style = style
        self.logo_path = logo_path
        self.svg_output_dir = svg_output_dir

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

    def _add_logo(self, slide, presentation: Presentation) -> None:
        if not self.logo_path.exists():
            return
        width = Inches(1.3)
        left = presentation.slide_width - width - Inches(0.4)
        top = Inches(0.2)
        slide.shapes.add_picture(str(self.logo_path), left, top, width=width)

    def _add_cover_slide(self, prs: Presentation, deck: SlideDeck) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._set_background(slide)
        self._add_logo(slide, prs)

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
        self._add_logo(slide, prs)

        layout = (slide_content.layout or "split").lower()
        layout = layout if layout in {"text_only", "split", "visual_full"} else "split"

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

        if slide_content.key_message:
            key_box = slide.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.RECTANGLE,
                Inches(0.8),
                Inches(1.9),
                prs.slide_width - Inches(3.2),
                Inches(0.9),
            )
            key_box.fill.solid()
            key_box.fill.fore_color.rgb = self.style.accent_rgb()
            key_box.line.color.rgb = self.style.accent_rgb()
            key_frame = key_box.text_frame
            key_frame.margin_left = 25000
            key_frame.margin_right = 25000
            key_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            key_frame.text = slide_content.key_message
            key_para = key_frame.paragraphs[0]
            key_para.alignment = PP_ALIGN.LEFT
            key_run = key_para.runs[0]
            key_run.font.name = self.style.body_font
            key_run.font.bold = True
            key_run.font.size = Pt(20)
            key_run.font.color.rgb = self.style.background_rgb()

        bullet_left = Inches(0.8)
        bullet_top = Inches(3.0)
        bullet_height = Inches(3.5)

        if layout == "text_only":
            bullet_width = prs.slide_width - Inches(1.6)
            visual_left = None
            visual_width = None
        elif layout == "visual_full":
            bullet_width = prs.slide_width - Inches(1.6)
            visual_left = Inches(0.8)
            visual_width = prs.slide_width - Inches(1.6)
        else:  # split
            bullet_width = prs.slide_width * 0.52
            visual_left = bullet_left + bullet_width + Inches(0.4)
            visual_width = prs.slide_width - visual_left - Inches(0.6)

        if slide_content.bullets and layout != "visual_full":
            bullet_box = slide.shapes.add_textbox(
                bullet_left, bullet_top, bullet_width, bullet_height
            )
            bullet_frame = bullet_box.text_frame
            bullet_frame.clear()
            for idx, bullet in enumerate(slide_content.bullets):
                paragraph = (
                    bullet_frame.paragraphs[0]
                    if idx == 0
                    else bullet_frame.add_paragraph()
                )
                paragraph.text = bullet
                paragraph.level = 0
                paragraph.font.name = self.style.body_font
                paragraph.font.size = Pt(20)
                paragraph.font.color.rgb = self.style.body_rgb()

        insight_top = bullet_top + (bullet_height if slide_content.bullets else 0)
        if slide_content.insights and layout != "visual_full":
            insight_box = slide.shapes.add_textbox(
                bullet_left,
                insight_top + Inches(0.2),
                bullet_width,
                Inches(1.8),
            )
            insight_frame = insight_box.text_frame
            insight_frame.clear()
            for idx, insight in enumerate(slide_content.insights):
                ip = (
                    insight_frame.paragraphs[0]
                    if idx == 0
                    else insight_frame.add_paragraph()
                )
                ip.text = insight
                ip.level = 0
                ip.font.name = self.style.body_font
                ip.font.size = Pt(16)
                ip.font.color.rgb = self.style.title_rgb()
                ip.alignment = PP_ALIGN.LEFT

        if slide_content.visual and visual_left is not None and visual_width:
            self._draw_visual_block(
                slide=slide,
                slide_content=slide_content,
                slide_index=slide_index,
                left=visual_left,
                width=visual_width,
                top=bullet_top,
                layout=layout,
            )

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
    ) -> None:
        visual = slide_content.visual
        if not visual:
            return

        visual_height = Inches(3.8 if layout == "visual_full" else 2.8)
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

        self.svg_output_dir.mkdir(parents=True, exist_ok=True)
        svg_path = self.svg_output_dir / f"slide_{slide_index:02d}.svg"
        svg_path.write_text(svg_markup, encoding="utf-8")

        if not cairosvg:
            return None

        png_path = svg_path.with_suffix(".png")
        try:
            cairosvg.svg2png(bytestring=svg_markup.encode("utf-8"), write_to=str(png_path))
        except Exception:
            return None

        return png_path
