# Linee Guida Stile Datapizza

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
8. Ogni bullet deve iniziare con un tag `[icon:NOME]` usando nomi Material Symbols (es. `[icon:chevron_right]`, `[icon:check_circle]`, `[icon:warning]`).

### Regole layout dinamiche
- Se i punti sono lunghi o numerosi, scegli layout `text_only` e concentrati su bullet con icone.
- Se i punti sono brevi/di impatto, usa layout `split`: a sinistra bullet con icone, a destra uno schema SVG riassuntivo.
- Se il contenuto è meglio spiegato con un visual, usa layout `visual_full` e fornisci uno schema vettoriale completo.

## Branding:

Posiziona il logo 'DatapizzaLogo.png' nell'angolo in alto a destra di ogni slide. 

## SVG Style
Quando generi SVG:
- Usa solo i colori della palette Datapizza
- Stile flat design, linee pulite
- Icone semplici e riconoscibili
- Grafici con aspetto minimal (no griglie pesanti)
- Font: system-ui per testo negli SVG
- Spessore linee: 2-3px
- Border radius: 8px per box
- Fornisci solo markup `<svg>...</svg>` completo, senza testo extra o backtick
- Chiudi sempre il tag `</svg>` e includi viewBox + width/height coerenti
- Non aggiungere intestazioni `<?xml ...?>`, inizia direttamente con `<svg`

### Esempi SVG da Seguire

**Timeline:**
```
<svg viewBox="0 0 1200 250" xmlns="http://www.w3.org/2000/svg">
  <!-- Linea principale -->
  <line x1="100" y1="80" x2="1100" y2="80" stroke="#C12A22" stroke-width="4"/>
  
  <!-- Step 1: Ingest -->
  <circle cx="150" cy="80" r="20" fill="#C12A22"/>
  <circle cx="150" cy="80" r="14" fill="#FFFFFF"/>
  <text x="150" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">1. Ingest</text>
  <text x="150" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Lettura e</text>
  <text x="150" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">standardizzazione</text>
  
  <!-- Step 2: Clean -->
  <circle cx="300" cy="80" r="20" fill="#C12A22"/>
  <circle cx="300" cy="80" r="14" fill="#FFFFFF"/>
  <text x="300" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">2. Clean</text>
  <text x="300" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Pulizia risposte</text>
  <text x="300" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">aperte (null)</text>
  
  <!-- Step 3: Features -->
  <circle cx="450" cy="80" r="20" fill="#C12A22"/>
  <circle cx="450" cy="80" r="14" fill="#FFFFFF"/>
  <text x="450" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">3. Features</text>
  <text x="450" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Calcolo K/S,</text>
  <text x="450" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">clustering</text>
  
  <!-- Step 4: EDA -->
  <circle cx="600" cy="80" r="20" fill="#C12A22"/>
  <circle cx="600" cy="80" r="14" fill="#FFFFFF"/>
  <text x="600" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">4. EDA</text>
  <text x="600" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Grafici e tabelle</text>
  <text x="600" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">quantitative</text>
  
  <!-- Step 5: Qual (LLM) -->
  <circle cx="750" cy="80" r="20" fill="#C12A22"/>
  <circle cx="750" cy="80" r="14" fill="#FFFFFF"/>
  <text x="750" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">5. Qual (LLM)</text>
  <text x="750" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Estrazione temi,</text>
  <text x="750" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">needs, concerns</text>
  
  <!-- Step 6: Synthesis -->
  <circle cx="900" cy="80" r="20" fill="#C12A22"/>
  <circle cx="900" cy="80" r="14" fill="#FFFFFF"/>
  <text x="900" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">6. Synthesis</text>
  <text x="900" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Sintesi e</text>
  <text x="900" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">raccomandazioni</text>
  
  <!-- Step 7: Report -->
  <circle cx="1050" cy="80" r="20" fill="#C12A22"/>
  <circle cx="1050" cy="80" r="14" fill="#FFFFFF"/>
  <text x="1050" y="130" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#1E293B">7. Report</text>
  <text x="1050" y="155" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">Assemblaggio finale</text>
  <text x="1050" y="175" text-anchor="middle" font-family="system-ui" font-size="13" fill="#475569">(PDF/DOCX)</text>
</svg>
```

**Timeline con Milestone**

```
<svg viewBox="0 0 1000 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Linea base -->
  <line x1="50" y1="100" x2="950" y2="100" stroke="#475569" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Q1 -->
  <circle cx="200" cy="100" r="18" fill="#C12A22"/>
  <text x="200" y="106" text-anchor="middle" font-family="system-ui" font-size="14" font-weight="bold" fill="#FFFFFF">Q1</text>
  <text x="200" y="140" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Planning</text>
  <text x="200" y="165" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Gen-Mar 2025</text>
  
  <!-- Q2 -->
  <circle cx="400" cy="100" r="18" fill="#C12A22"/>
  <text x="400" y="106" text-anchor="middle" font-family="system-ui" font-size="14" font-weight="bold" fill="#FFFFFF">Q2</text>
  <text x="400" y="140" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Build</text>
  <text x="400" y="165" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Apr-Giu 2025</text>
  
  <!-- Q3 -->
  <circle cx="600" cy="100" r="18" fill="#C12A22"/>
  <text x="600" y="106" text-anchor="middle" font-family="system-ui" font-size="14" font-weight="bold" fill="#FFFFFF">Q3</text>
  <text x="600" y="140" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Test</text>
  <text x="600" y="165" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Lug-Set 2025</text>
  
  <!-- Q4 -->
  <circle cx="800" cy="100" r="18" fill="#C12A22"/>
  <text x="800" y="106" text-anchor="middle" font-family="system-ui" font-size="14" font-weight="bold" fill="#FFFFFF">Q4</text>
  <text x="800" y="140" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Launch</text>
  <text x="800" y="165" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Ott-Dic 2025</text>
</svg>
```

**Icona:**
```
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="60" height="60" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="2"/>
  <path d="M40 50 L50 60 L70 35" stroke="#C12A22" stroke-width="3" fill="none"/>
</svg>
```
**Icona Database / Single Source of Truth:**
```
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Cilindro database -->
  <ellipse cx="50" cy="30" rx="28" ry="10" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  <rect x="22" y="30" width="56" height="35" fill="#FEF2F2"/>
  <line x1="22" y1="30" x2="22" y2="65" stroke="#C12A22" stroke-width="3"/>
  <line x1="78" y1="30" x2="78" y2="65" stroke="#C12A22" stroke-width="3"/>
  <ellipse cx="50" cy="65" rx="28" ry="10" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  
  <!-- Linee interne -->
  <line x1="35" y1="42" x2="65" y2="42" stroke="#C12A22" stroke-width="2"/>
  <line x1="35" y1="50" x2="65" y2="50" stroke="#C12A22" stroke-width="2"/>
  <line x1="35" y1="58" x2="50" y2="58" stroke="#C12A22" stroke-width="2"/>
</svg>
```
**Icona Tech Stack / Ingranaggi:**
```
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Ingranaggio grande -->
  <circle cx="40" cy="50" r="22" fill="none" stroke="#C12A22" stroke-width="3"/>
  <circle cx="40" cy="50" r="10" fill="#C12A22"/>
  
  <!-- Denti ingranaggio grande -->
  <rect x="38" y="25" width="4" height="8" fill="#C12A22"/>
  <rect x="38" y="67" width="4" height="8" fill="#C12A22"/>
  <rect x="17" y="48" width="8" height="4" fill="#C12A22"/>
  <rect x="55" y="48" width="8" height="4" fill="#C12A22"/>
  
  <!-- Ingranaggio piccolo -->
  <circle cx="65" cy="35" r="16" fill="none" stroke="#C12A22" stroke-width="3"/>
  <circle cx="65" cy="35" r="7" fill="#C12A22"/>
  
  <!-- Denti ingranaggio piccolo -->
  <rect x="63" y="16" width="4" height="6" fill="#C12A22"/>
  <rect x="63" y="48" width="4" height="6" fill="#C12A22"/>
  <rect x="46" y="33" width="6" height="4" fill="#C12A22"/>
  <rect x="78" y="33" width="6" height="4" fill="#C12A22"/>
</svg>
```
**Diagramma a blocchi:**
```
<svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Blocco 1 -->
  <rect x="50" y="60" width="140" height="80" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  <text x="120" y="95" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Input</text>
  <text x="120" y="115" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Dati grezzi</text>
  
  <!-- Freccia 1 -->
  <path d="M 190 100 L 230 100" stroke="#C12A22" stroke-width="3" fill="none"/>
  <path d="M 225 95 L 235 100 L 225 105" fill="#C12A22"/>
  
  <!-- Blocco 2 -->
  <rect x="235" y="60" width="140" height="80" rx="8" fill="#C12A22"/>
  <text x="305" y="95" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#FFFFFF">Processing</text>
  <text x="305" y="115" text-anchor="middle" font-family="system-ui" font-size="12" fill="#FFFFFF">Trasformazione</text>
  
  <!-- Freccia 2 -->
  <path d="M 375 100 L 415 100" stroke="#C12A22" stroke-width="3" fill="none"/>
  <path d="M 410 95 L 420 100 L 410 105" fill="#C12A22"/>
  
  <!-- Blocco 3 -->
  <rect x="420" y="60" width="140" height="80" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  <text x="490" y="95" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Analysis</text>
  <text x="490" y="115" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Insights</text>
  
  <!-- Freccia 3 -->
  <path d="M 560 100 L 600 100" stroke="#C12A22" stroke-width="3" fill="none"/>
  <path d="M 595 95 L 605 100 L 595 105" fill="#C12A22"/>
  
  <!-- Blocco 4 -->
  <rect x="605" y="60" width="140" height="80" rx="8" fill="#FEF2F2" stroke="#C12A22" stroke-width="3"/>
  <text x="675" y="95" text-anchor="middle" font-family="system-ui" font-size="15" font-weight="bold" fill="#1E293B">Output</text>
  <text x="675" y="115" text-anchor="middle" font-family="system-ui" font-size="12" fill="#475569">Report finale</text>
</svg>
```
