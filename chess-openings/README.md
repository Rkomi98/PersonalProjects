# Chess Openings Trainer (mobile-first, offline, no engine)

Web app React + Vite per studiare le aperture come **idee/piani/strutture**, non come pura memorizzazione.

## Requisiti
- Node.js 18+ consigliato

## Setup
```bash
npm install
npm run dev
```

Apri l’URL mostrato in console (tipicamente http://localhost:5173).

## Build (static site)
```bash
npm run build
npm run preview
```

L’output statico è in `dist/` (deployabile su Netlify/Vercel/GitHub Pages ecc).

## Dati offline (JSON)
- `src/data/openingBook.json` contiene:
  - lista aperture
  - nodi del libro (albero mosse) per l’Italiana livello ⭐
  - stub per le altre aperture (estendibile)

## Note
- Nessun motore (no Stockfish): il feedback è concettuale e guidato dal dataset.

## Offline (PWA)
- Il progetto include `vite-plugin-pwa` + registrazione service worker (`src/registerSW.ts`).
- In produzione (build) le risorse vengono cacheate: dopo il primo caricamento il sito continua a funzionare anche senza rete.

Per testare:
```bash
npm run build
npm run preview
```
Poi apri il sito e prova a mettere il device in modalità aereo.
