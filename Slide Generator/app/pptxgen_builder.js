#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const [slidesJsonPath, outputPath, logoPathArg, coverLogoPathArg, geminiAssetDirArg] = process.argv.slice(2);

if (!slidesJsonPath || !outputPath) {
  console.error("Usage: node app/pptxgen_builder.js <slides.json> <output.pptx> [logo] [coverLogo] [geminiAssetDir]");
  process.exit(1);
}

const slides = JSON.parse(fs.readFileSync(slidesJsonPath, "utf8"));
const logoPath = logoPathArg && fs.existsSync(logoPathArg) ? logoPathArg : null;
const coverLogoPath = coverLogoPathArg && fs.existsSync(coverLogoPathArg) ? coverLogoPathArg : logoPath;
const geminiAssetDir = geminiAssetDirArg && fs.existsSync(geminiAssetDirArg) ? geminiAssetDirArg : null;

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.company = "Datapizza";
pptx.subject = "Datapizza presentation";
pptx.title = slides[0]?.title || "Datapizza Deck";

const C = {
  white: "FFFFFF",
  light: "F4F7FB",
  border: "D0D5DD",
  blue: "1B64F5",
  red: "C64336",
  navy: "111F2D",
  body: "0D1F2E",
  muted: "737373",
};

function addLogo(slide, { icon = false, bottom = false } = {}) {
  const asset = icon ? coverLogoPath : logoPath;
  if (!asset) return;
  slide.addImage({
    path: asset,
    x: icon ? 10.15 : 11.55,
    y: bottom ? 5.15 : 0.28,
    w: icon ? 1.55 : 1.25,
    h: icon ? 1.55 : 0.42,
  });
}

function addCornerGrid(slide) {
  for (let row = 0; row < 4; row += 1) {
    for (let col = 0; col < 4; col += 1) {
      slide.addShape(pptx.ShapeType.ellipse, {
        x: 10.45 + col * 0.18,
        y: 1.12 + row * 0.18,
        w: 0.045,
        h: 0.045,
        line: { color: C.border, transparency: 100 },
        fill: { color: C.border },
      });
    }
  }
}

function addNotes(slide, notes) {
  if (notes) {
    slide.addNotes(notes);
  }
}

function renderTitle(slide, data) {
  slide.background = { color: C.white };
  addLogo(slide);
  addLogo(slide, { icon: true, bottom: true });
  addCornerGrid(slide);
  slide.addText("DATAPIZZA AI4BUILDERS", {
    x: 1.1,
    y: 1.42,
    w: 4.8,
    h: 0.25,
    fontFace: "Poppins",
    fontSize: 10,
    bold: true,
    color: C.blue,
    margin: 0,
  });
  slide.addText(data.title || "", {
    x: 1.1,
    y: 1.85,
    w: 7.9,
    h: 1.5,
    fontFace: "Poppins",
    fontSize: 28,
    bold: true,
    color: C.red,
    margin: 0,
  });
  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: 1.1,
      y: 4.2,
      w: 7.2,
      h: 0.6,
      fontFace: "Inter",
      fontSize: 16,
      color: C.navy,
      margin: 0,
    });
  }
}

function renderSection(slide, data) {
  slide.background = { color: C.white };
  addLogo(slide);
  addCornerGrid(slide);
  slide.addText("SECTION", {
    x: 1.0,
    y: 1.85,
    w: 2.0,
    h: 0.25,
    fontFace: "Poppins",
    fontSize: 10,
    bold: true,
    color: C.blue,
    margin: 0,
  });
  slide.addText(data.title || "", {
    x: 1.0,
    y: 2.28,
    w: 8.0,
    h: 0.8,
    fontFace: "Poppins",
    fontSize: 24,
    bold: true,
    color: C.red,
    margin: 0,
  });
  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: 1.0,
      y: 3.35,
      w: 7.0,
      h: 0.5,
      fontFace: "Inter",
      fontSize: 14,
      color: C.navy,
      margin: 0,
    });
  }
  slide.addText(">>", {
    x: 11.15,
    y: 5.15,
    w: 0.6,
    h: 0.3,
    fontFace: "Poppins",
    fontSize: 18,
    bold: true,
    color: C.blue,
    margin: 0,
  });
}

function renderClosing(slide, data) {
  slide.background = { color: C.white };
  addLogo(slide);
  addLogo(slide, { icon: true, bottom: true });
  slide.addText(data.title || "Grazie", {
    x: 1.1,
    y: 2.45,
    w: 4.5,
    h: 0.8,
    fontFace: "Poppins",
    fontSize: 28,
    bold: true,
    color: C.red,
    margin: 0,
  });
  if (data.body) {
    slide.addText(data.body, {
      x: 1.1,
      y: 3.5,
      w: 5.4,
      h: 0.8,
      fontFace: "Inter",
      fontSize: 16,
      color: C.body,
      margin: 0,
    });
  }
}

function renderInternal(slide, data, slideIndex) {
  slide.background = { color: C.white };
  const svgPath = geminiAssetDir ? path.join(geminiAssetDir, `slide_${String(slideIndex).padStart(2, "0")}.svg`) : null;
  if (svgPath && fs.existsSync(svgPath)) {
    slide.addImage({ path: svgPath, x: 0, y: 0, w: 13.333, h: 7.5 });
    return;
  }
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.45,
    y: 0.45,
    w: 12.43,
    h: 6.6,
    rectRadius: 0.08,
    line: { color: C.border, pt: 1.5 },
    fill: { color: C.light },
  });
  slide.addText(data.title || "", {
    x: 0.9,
    y: 0.9,
    w: 11.0,
    h: 0.5,
    fontFace: "Poppins",
    fontSize: 24,
    bold: true,
    color: C.blue,
    margin: 0,
  });
  slide.addText(data.image_prompt || "", {
    x: 0.9,
    y: 1.7,
    w: 11.3,
    h: 3.8,
    fontFace: "Inter",
    fontSize: 11,
    color: C.body,
    margin: 0,
    breakLine: false,
  });
}

for (let index = 0; index < slides.length; index += 1) {
  const data = slides[index];
  const slide = pptx.addSlide();
  if (data.slide_type === "title") {
    renderTitle(slide, data);
  } else if (data.slide_type === "section") {
    renderSection(slide, data);
  } else if (data.slide_type === "closing") {
    renderClosing(slide, data);
  } else {
    renderInternal(slide, data, index + 1);
  }
  addNotes(slide, data.speaker_notes);
}

pptx.writeFile({ fileName: outputPath }).catch((error) => {
  console.error(error);
  process.exit(1);
});
