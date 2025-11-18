"""Utilities to work with the slide style prompt."""
from __future__ import annotations

from pathlib import Path


DEFAULT_STYLE_PROMPT = """# Linee Guida Stile Datapizza

## Palette Colori
- Rosso principale: #C12A22
- Grigio scuro titoli: #1E293B
- Grigio corpo: #475569
- Sfondo: #FFFFFF
- Accento chiaro: #FEF2F2

Lo stile deve essere minimalista, pulito e corporate.

## Tipografia
- Titoli: Poppins Bold, 36-48pt
- Sottotitoli: Poppins SemiBold, 24-28pt
- Corpo: Lato Regular, 18-20pt
- Note: Lato Regular, 14-16pt

## Layout Rules
1. Titoli sempre in sentence case
2. Logo in alto a destra (1.3" width)
3. Linea decorativa rossa (#C12A22, 4pt) sotto ogni titolo
4. Key message in box rosso con testo bianco
5. Max 5 bullet per slide
6. Icone minimaliste per i bullet point
7. Case (solo la prima lettera della prima parola in maiuscolo).
8. Ogni bullet deve iniziare con `[icon:NOME]` usando nomi delle Material Symbols (es. chevron_right, check_circle, warning).

### Regole layout dinamiche
- Se i punti sono lunghi o numerosi, scegli layout `text_only` e concentra la slide sui bullet con icone.
- Se i punti sono brevi e incisivi, scegli layout `split`: metà testo con icone, metà visual esplicativo.
- Se il contenuto è soprattutto visivo o processuale, scegli layout `visual_full` e produci uno schema SVG completo.

## Branding
Posiziona il logo 'DatapizzaLogo.png' nell'angolo in alto a destra di ogni slide.

## SVG Style
Quando generi SVG:
- Usa solo i colori della palette Datapizza
- Stile flat design, linee pulite
- Icone semplici e riconoscibili
- Grafici minimal (no griglie pesanti)
- Font: system-ui per testo negli SVG
- Spessore linee: 2-3px
- Border radius: 8px per box
- Restituisci sempre markup <svg> completo
- Mantieni SVG valido (senza ``` markdown) e includi sempre viewBox + width/height
- Niente testo fuori dal tag <svg> e chiudi sempre con </svg>
- Non aggiungere intestazioni `<?xml ...?>`, inizia direttamente con `<svg`

### Esempi SVG

**Timeline**
```
<svg viewBox="0 0 1200 250" xmlns="http://www.w3.org/2000/svg">
  <line x1="100" y1="80" x2="1100" y2="80" stroke="#C12A22" stroke-width="4"/>
  <circle cx="150" cy="80" r="20" fill="#C12A22"/>
  <circle cx="150" cy="80" r="14" fill="#FFFFFF"/>
  <text x="150" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">1. Ingest</text>
  <text x="150" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Lettura e</text>
  <text x="150" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">standardizzazione</text>
</svg>
```

**Icona check**
```
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="60" height="60" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="2"/>
  <path d="M40 50 L50 60 L70 35" stroke="#C12A22" stroke-width="3" fill="none"/>
</svg>
```

**Diagramma a blocchi**
```
<svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="60" width="140" height="80" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  <path d="M 190 100 L 230 100" stroke="#C12A22" stroke-width="3" fill="none"/>
  <path d="M 225 95 L 235 100 L 225 105" fill="#C12A22"/>
  <rect x="235" y="60" width="140" height="80" rx="8" fill="#C12A22"/>
  <text x="305" y="95" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#FFFFFF">Processing</text>
</svg>
```"""


def load_style_prompt(prompt_path: Path) -> str:
    """Return the content of the prompt file or a sensible default."""
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()

    return DEFAULT_STYLE_PROMPT
