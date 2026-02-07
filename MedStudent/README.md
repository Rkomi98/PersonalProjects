# MedStudent - RPG Narrativo Didattico di Gastroenterologia

App web testuale (compatibile GitHub Pages) per studiare gastroenterologia con meccaniche RPG narrative.

## Obiettivo
Allenare Camilla su:
- quiz a scelta multipla stile esame
- scelte cliniche con priorita
- ragionamento clinico guidato

Vincolo rispettato: contenuti medici derivati dalla dispensa `GASTROENTEROLOGIA 2023_pagenumber.pdf`.

## Architettura
Scelta tecnica: **backend logico in JavaScript client-side** (nessun server necessario per GitHub Pages).

Componenti:
- `index.html`: shell dell'app
- `src/styles.css`: interfaccia responsive desktop/mobile
- `src/main.js`: rendering UI e controller interazioni
- `src/engine/gameEngine.js`: stato, regole, punteggi, recovery errori, persistenza (`localStorage`)
- `src/data/season.js`: capitoli, scene, quiz, stat, roadmap programma
- `src/data/sourceBook.js`: tracciamento nozioni e pagine dispensa

## Avvio locale
Dalla root `MedStudent`:

```bash
python3 -m http.server 8080
```

Poi apri:
- `http://localhost:8080`

Nota: non usare `file://` perche' i moduli ES potrebbero non caricarsi correttamente.

## Deploy su GitHub Pages
Repository gia' abilitato a Pages, quindi basta pubblicare la root.

1. Commit e push:
```bash
git add .
git commit -m "feat: rpg narrativo didattico gastroenterologia"
git push origin <tuo-branch>
```

2. Se usi branch principale come sorgente Pages:
- GitHub -> `Settings` -> `Pages`
- `Source`: `Deploy from a branch`
- Branch: `main` (o quello scelto), cartella: `/ (root)`
- Salva

3. Attendi il deploy e apri l'URL Pages mostrato in `Settings > Pages`.

## Come estendere i capitoli
Per aggiungere nuovi episodi didattici:
1. Aggiungi il capitolo in `src/data/season.js`.
2. Inserisci scene con tipo:
- `narrative`
- `choice`
- `quiz_mcq`
- `quiz_clinical`
- `quiz_reasoning`
3. Collega ogni scena a una fonte in `src/data/sourceBook.js` con `sourceKey` (e opzionale `extraSourceKey`).

## Stato attuale
- Stagione completa giocabile: 12 capitoli, ciascuno con scena narrativa, scelta, quiz, scelta clinica, ragionamento, feedback e recupero.
- Progressione automatica capitolo per capitolo con salvataggio locale dello stato.
