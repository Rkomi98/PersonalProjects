# La Grande “C” — mini-sito regalo (static)

Questo è un **sito statico** (HTML/CSS/JS) con un mini-gioco “Passaporto della Grande C”.
Quando l'utente completa tutte le tappe, si sbloccano i pulsanti di download.

## Struttura

- `index.html` — pagina unica
- `styles.css` — stile
- `game.js` — logica gioco + neve + sblocco
- `assets/cover.webp` / `assets/cover.jpg` — copertina (sostituiscila liberamente)
- `downloads/` — metti qui EPUB/PDF
- `media/` — metti qui la musica (MP3)

## Dove mettere i tuoi file

Sostituisci questi (nomi consigliati):

- `downloads/romanzo-sud-america.epub`
- `downloads/romanzo-sud-america.pdf`
- `downloads/copertina-libro.pdf`
- `media/colonna-sonora.mp3`

Poi i pulsanti in pagina funzionano senza modifiche.

## Modificare i link dei pulsanti

In `index.html` cerca:

- `id="dlCover"` → `href="./downloads/copertina-libro.pdf"`
- `id="dlEpub"` → `href="./downloads/romanzo-sud-america.epub"`
- `id="dlPdf"` → `href="./downloads/romanzo-sud-america.pdf"`
- `id="dlMusic"` → `href="./media/colonna-sonora.mp3"`

Puoi metterci anche URL esterni.

## Personalizzare le domande del gioco

In `game.js` c'è l'array `stops = [...]`.
Ogni tappa ha:

- `title`, `text`
- `question`
- `options` (array)
- `answer` (indice della risposta corretta)
- `hint`
- `stamp` (testo breve dentro il timbro)

## Eseguire in locale

Se apri `index.html` direttamente funziona già.
Se preferisci un server locale:

### Python
```bash
python -m http.server 8000
```
Poi apri `http://localhost:8000`

### Node (opzionale)
```bash
npx serve .
```

## Note

- I progressi sono salvati in `localStorage`.
- Il pulsante “Reset” azzera i progressi.
- La neve si può disattivare (e rispetta `prefers-reduced-motion`).
