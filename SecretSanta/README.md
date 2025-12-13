# La Grande “C” — mini-sito regalo (static)

Questo è un **sito statico** (HTML/CSS/JS) con un mini-gioco “Passaporto della Grande C”.
Quando l'utente completa tutte le tappe, si sbloccano i pulsanti di download.

## Struttura

- `index.html` — pagina unica
- `styles.css` — stile
- `game.js` — logica gioco + neve + sblocco
- `assets/cover.webp` / `assets/cover.jpg` — copertina (sostituiscila liberamente)
- `media/` — metti qui EPUB/PDF/musica

## Dove mettere i tuoi file

Sostituisci questi (nomi consigliati):

- `media/Romanzo Sud America_ Itinerario a _C_.epub`
- `media/Romanzo Sud America_ Itinerario a _C_.pdf`
- `media/colonna-sonora.mp3`
- `media/Copertina libro.pdf` (opzionale, se vuoi conservarla anche lì)

Poi i pulsanti in pagina funzionano senza modifiche.

## Modificare i link dei pulsanti

In `index.html` cerca:

- `id="dlEpub"` → `href="./media/Romanzo%20Sud%20America_%20Itinerario%20a%20_C_.epub"`
- `id="dlPdf"` → `href="./media/Romanzo%20Sud%20America_%20Itinerario%20a%20_C_.pdf"`
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
