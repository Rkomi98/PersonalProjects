# Chess Openings Trainer

Allenatore di aperture scacchistiche pensato per il mobile, offline, senza motore: l’obiettivo è capire **idee, piani e strutture**, non imparare mosse a memoria.

## Requisiti
- Node.js 18+ consigliato

## Avvio in locale
```bash
npm install
npm run dev
```

Apri l’URL mostrato in console (tipicamente http://localhost:5173).

## Build statico
```bash
npm run build
npm run preview
```

L’output finisce in `dist/` (puoi pubblicarlo su Netlify/Vercel/GitHub Pages, ecc.).

## Dati delle aperture (JSON)
- `src/data/openingBook.json` contiene:
  - elenco aperture
  - albero mosse per l’Italiana (livello ⭐)
  - stub per le altre aperture (estendibile)

## Nota sul feedback
- Nessun motore (no Stockfish): il feedback è concettuale e guidato dal dataset.

## Offline (PWA)
- Il progetto usa `vite-plugin-pwa` e registra un service worker (`src/registerSW.ts`).
- In build, le risorse vengono cacheate: dopo il primo caricamento il sito funziona anche senza rete.

Per testare:
```bash
npm run build
npm run preview
```
Poi apri il sito e prova a mettere il device in modalità aereo.
