# Slide Generator Datapizza

Generatore di presentazioni Datapizza che usa `datapizza-AI` per trasformare un Markdown libero in:

1. un array JSON di slide nel formato richiesto da Claude
2. una cartella di prompt per Gemini dedicata alle slide interne
3. un file `.pptx` che monta cover, section divider, content, bullets e closing

## Ambiente virtuale

Serve **Python 3.10+** (il pacchetto `datapizza-ai` non è compatibile con Python 3.9). Su macOS, se il `python3` di sistema è 3.9, usa ad esempio quello di Homebrew:

```bash
cd "Slide Generator"
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Opzionale, per convertire gli SVG in PNG dentro PowerPoint:

```bash
pip install -r requirements-optional.txt
```

Per eseguire gli stessi comandi senza attivare il venv: `.venv/bin/python main.py ...`

## Output prodotto

Il modello genera slide con questo schema:

```json
[
  {
    "slide_type": "title",
    "title": "Titolo",
    "subtitle": "Sottotitolo opzionale",
    "body": null,
    "bullets": [],
    "speaker_notes": "Note speaker",
    "image_prompt": "SVG 800x500px, viewBox 0 0 800 500 ..."
  }
]
```

Il `dry-run` stampa solo l'array JSON, senza testo aggiuntivo.

## Flusso

1. `main.py` legge il Markdown da `--topic`, `--topic-file` o dalla cartella `Topic/`
2. `SlideGenerationService` usa `datapizza-AI` + OpenAI con schema Pydantic
3. il deck viene salvato come JSON in `output/slides_*.json`
4. per le slide `content` e `bullets` vengono creati prompt Gemini in `output/gemini_prompts/`
5. il builder cerca gli SVG corrispondenti in `output/gemini_assets/` e li inserisce nel `.pptx` se presenti

## Cartelle Gemini

Il progetto usa queste convenzioni:

- Prompt Gemini: `output/gemini_prompts/slide_XX.txt`
- Manifest: `output/gemini_prompts/manifest.json`
- SVG generati da Gemini: `output/gemini_assets/slide_XX.svg`

Formato consigliato dei prompt:

- file `.txt`
- UTF-8
- contenuto puro del prompt, una sola stringa, senza JSON o markdown wrapper

Formato atteso degli asset:

- file `.svg`
- canvas `800x500`
- naming coerente con la slide: `slide_03.svg`, `slide_04.svg`, ecc.

## Uso

```bash
python main.py --topic-file "Materiale a supporto/DivEtImpera.md" --dry-run
```

```bash
python main.py --topic-file Topic/Arkemis_Kinetica.md --output output/deck.pptx
```

Output:

- `output/slides_YYYYMMDD_HHMM.json`
- `output/gemini_prompts/slide_XX.txt`
- `output/gemini_prompts/manifest.json`
- `output/gemini_assets/slide_XX.svg` (da popolare con Gemini)
- `output/deck_YYYYMMDD_HHMM.pptx`

## Skill Datapizza

Il generatore carica anche il pacchetto `Materiale a supporto/datapizza-slides.skill` e ne incorpora:

- `SKILL.md`
- estratto di `dp-01-style.md`
- estratto di `dp-03-workflow.md`

Questo contesto viene passato al prompt del modello per restare allineato alle convenzioni Datapizza.

## Note operative

- Le slide `title` e `section` sono pensate per essere rifinite da Claude.
- Le slide `content` e `bullets` possono mostrare uno placeholder testuale finché non esiste il relativo `slide_XX.svg`.
- Se `cairosvg` è disponibile, gli SVG vengono convertiti automaticamente in PNG per PowerPoint.
- Per una verifica locale completa: vedi [Ambiente virtuale](#ambiente-virtuale) e `requirements.txt`.
