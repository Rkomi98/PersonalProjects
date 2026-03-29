# Voxtral Terminal Backend

Backend Python minimale per:

- scaricare in locale `mistralai/Voxtral-4B-TTS-2603`
- trasformare un file Markdown in testo leggibile usando `datapizza-ai`
- sintetizzare audio con voice cloning a partire da `audio.wav`
- pilotare tutto da terminale

## Cosa fa davvero questo repository

Il codice ora e' centrato sul runtime ufficiale consigliato dal model card di Voxtral:

- tokenizer `mistral-common`
- inferenza `vllm`
- runtime TTS `vllm-omni`

`datapizza-ai` viene usato per orchestrare la pipeline backend:

1. markdown -> parsing e normalizzazione
2. testo speakable -> request TTS
3. request TTS -> generazione WAV

## Limite importante sulla macchina attuale

Su macOS ARM come questo MacBook Air puoi:

- installare il progetto
- scaricare il modello
- testare l'estrazione del testo da markdown
- verificare la pipeline con i test

Non puoi invece eseguire localmente la sintesi ufficiale di Voxtral su questa macchina, perche' il runtime upstream richiede `vllm` + `vllm-omni` su host Linux con GPU supportata.

Per questo il progetto adesso supporta anche un fallback cloud via `MISTRAL_API_KEY`.

Il comando `speak-markdown` prova in ordine:

1. backend locale `vllm-omni`
2. fallback cloud Mistral API, se `MISTRAL_API_KEY` e' presente

## Setup locale

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Nel file `.env` puoi configurare anche:

```bash
MISTRAL_API_KEY=...
MISTRAL_API_BASE_URL=https://api.mistral.ai
MISTRAL_TTS_MODEL=mistralai/Voxtral-4B-TTS-2603
MISTRAL_VOICE_ID=
```

## Comandi disponibili

### 1. Diagnostica runtime

```bash
python app.py doctor
```

Mostra sia lo stato del runtime locale sia se la `MISTRAL_API_KEY` e' configurata.

### 2. Download del modello

```bash
python app.py download-model
```

Il modello viene salvato in:

```text
.cache/models/voxtral/mistralai__Voxtral-4B-TTS-2603
```

### 3. Estrazione testo dal markdown

```bash
python app.py extract-text --markdown samples/demo.md
```

### 4. Sintesi con voice cloning

Su una macchina Linux con runtime pronto:

```bash
python app.py speak-markdown \
  --markdown samples/demo.md \
  --reference-audio audio.wav \
  --output outputs/demo.wav
```

Per forzare il cloud:

```bash
python app.py speak-markdown \
  --engine cloud \
  --markdown samples/demo.md \
  --reference-audio audio.wav \
  --output outputs/demo.wav
```

Per forzare il locale:

```bash
python app.py speak-markdown \
  --engine local \
  --markdown samples/demo.md \
  --reference-audio audio.wav \
  --output outputs/demo.wav
```

## Primo test richiesto

Il flusso previsto e':

```bash
python app.py download-model
python app.py extract-text --markdown samples/demo.md
python app.py speak-markdown --markdown samples/demo.md --reference-audio audio.wav --output outputs/demo.wav
```

Sulla macchina attuale i primi due passaggi funzionano. Il terzo adesso puo' funzionare anche via cloud, ma richiede una `MISTRAL_API_KEY` valida e autorizzata all'endpoint audio speech.

## Installazione runtime Linux per la sintesi

Su una macchina compatibile:

```bash
pip install -U vllm
pip install git+https://github.com/vllm-project/vllm-omni.git --upgrade
```

Poi riesegui:

```bash
python app.py speak-markdown --markdown samples/demo.md --reference-audio audio.wav --output outputs/demo.wav
```

## File principali

- `app.py`: launcher da terminale
- `src/voxtral_terminal_backend/cli.py`: CLI
- `src/voxtral_terminal_backend/markdown_pipeline.py`: parsing markdown con `datapizza-ai`
- `src/voxtral_terminal_backend/service.py`: pipeline datapizza per la sintesi
- `src/voxtral_terminal_backend/voxtral.py`: integrazione offline con tokenizer Mistral + `vllm-omni`
- `src/voxtral_terminal_backend/model_store.py`: download del modello da Hugging Face
- `src/voxtral_terminal_backend/runtime.py`: controlli runtime e messaggi diagnostici

## Test

```bash
.venv/bin/pytest
```
