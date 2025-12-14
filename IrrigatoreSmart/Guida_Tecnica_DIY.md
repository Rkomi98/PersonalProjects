# 🌱 Centralina Irrigazione Smart DIY 24 VAC
## Guida Tecnica Professionale — Arduino Uno → ESP32

---

## INDICE GENERALE

1. [Introduzione al Progetto](#1-introduzione-al-progetto)
2. [Cosa Fa / Cosa NON Fa](#2-cosa-fa--cosa-non-fa)
3. [Sicurezza Elettrica](#3-sicurezza-elettrica)
4. [Architettura Generale](#4-architettura-generale)
5. [Impianto Hunter Eco-Logic Esistente](#5-impianto-hunter-eco-logic-esistente)
6. [Componenti Principali](#6-componenti-principali)
7. [Cablaggio Elettrovalvole 24 VAC](#7-cablaggio-elettrovalvole-24-vac)
8. [Modalità Operative](#8-modalità-operative)
9. [Montaggio Passo-Passo](#9-montaggio-passo-passo)
10. [Immagini Obbligatorie](#10-immagini-obbligatorie)
11. [Collaudo e Test Intermedi](#11-collaudo-e-test-intermedi)
12. [Troubleshooting](#12-troubleshooting)
13. [Anti-Zanzare: Prevenzione Sicura](#13-anti-zanzare-prevenzione-sicura)
14. [Appendici Tecniche](#14-appendici-tecniche)

---

## 1. INTRODUZIONE AL PROGETTO

### Scopo

Questo progetto consente di **automatizzare e monitorare un impianto di irrigazione domestico a 24 VAC** (tipicamente Hunter o similare) utilizzando una centralina **programmabile e espandibile** basata su microcontrollori Arduino.

**Valore aggiunto rispetto a Hunter nativo:**
- Controllo intelligente basato su **umidità del suolo capacitiva** (non solo timer fisso)
- **Interfaccia WiFi e display locale** opzionali
- **Logging dati** in formato CSV per analisi a posteriori
- **Compatibilità reversibile** con sistema Hunter originale (deviatore meccanico)
- **Estensibile** verso sensori pioggia, livello ristagni, drenaggio automatico

### Target

Persona **molto pratica** che:
- Sa usare Arduino IDE e caricare sketch
- Comprende circuiti semplici (relè, trasformatori)
- Vuole **risolvere problemi reali** (zanzare = ristagni, non pesticidi)
- Accetta **learning curve** ma vuole documentazione **senza assunzioni nascoste**

### Timeline Tipico

| Fase | Durata | Deliverable |
|------|--------|-------------|
| Ricerca componenti | 3–5 giorni | Ordini Amazon/AliExpress |
| Montaggio hardware | 1–2 giorni | Box IP65 cablato |
| Test Uno + sensori | 3–4 giorni | Sketch caricato, seriale OK |
| Trasformatore 24VAC | 1 giorno | Primo ciclo irrigazione |
| Migrazione ESP32 | 1 giorno | Codice ricompilato, WiFi opzionale |
| Ottimizzazione soglie | 1–2 settimane | Calibrazione umidità per zone |
| **TOTALE** | **2–3 settimane** | Impianto operativo |

---

## 2. COSA FA / COSA NON FA

### ✅ COSA FA QUESTO SISTEMA

- **Accende/spegne 2 zone di irrigazione** indipendentemente basato su soglie di umidità
- **Monitora umidità del suolo** in tempo reale via sensori capacitivi
- **Previene ristagni** mediante logica anti-ripetizione (cooldown 15 minuti tra cicli)
- **Fornisce interfaccia seriale** per debugging e lettura stato sensori
- **Opzionalmente**: display OLED locale, logging SD, sensore pioggia, connessione WiFi
- **Compatibilità reversibile** con Hunter originale tramite deviatore manuale
- **Funziona offline** (non richiede internet, solo WiFi opzionale)

### ❌ COSA NON FA

- **Non controlla pompa principale** (rimane sotto Hunter o comando separato)
- **Non previene gelate** (hai sensore temperatura ma no logica di protezione)
- **Non è certificato** per uso professionale (solo DIY hobbista)
- **Non include batteria UPS** (perde stato se c'è blackout; persiste solo RTC)
- **Non comunica con App cloud** (WiFi è locale, o selfhosted via Arduino IDE)
- **NON è anti-zanzare chimico**: cura **cause** (ristagni) con tecniche non-tossiche (monitoring + drenaggio)

---

## 3. SICUREZZA ELETTRICA

### ⚠️ PERICOLI IDENTIFICATI E MITIGAZIONI

#### Pericolo 1: Contatto diretto con 230 V

| Pericolo | Causa | Mitigazione | Verifiche |
|---------|-------|------------|-----------|
| Folgorazione | Cavo 230V scoperto | Cavi sempre in tubo/canale | Ispezione visiva mensile |
| Arco | Contatto umido | Box IP65 con griglie anti-acqua | Drenaggio box dopo pioggia |
| Cortocircuito | Isolamento deteriorato | Cavo H07V-U min. 300V | Test continuità con multimetro |

**Procedura Sicura:**
1. Spegni sempre il deviatore principale PRIMA di lavorare ai cavi
2. Usa multimetro per verificare assenza tensione prima di toccare fili
3. Isola tutte le connessioni 230V con nastro isolante doppio
4. Installazione RCD 30mA (salvascheggia) obbligatoria se impianto fisso

#### Pericolo 2: Sovracorrente

| Componente | Corrente Max | Protezione | Rating |
|-----------|-------------|-----------|--------|
| Primario trasformatore (230V) | ~4.8A (caso 2x valvole 6W) | Fusibile 20A T250V | IEC 60127 |
| Secondario trasformatore (24VAC) | ~0.4A (riserva 2x) | Fusibile 5A T250V | IEC 60127 |
| Circuito GPIO Arduino (5V) | 40mA max per pin | Nessuno (è digitale) | ATmega328P datasheet |

**Calcolo:**
- Valvola Hunter 24VAC tipica: 6-8W
- Due valvole in parallelo: 12-16W
- Trasformatore 40VA: P = V × I → 24V × 1.67A = 40.08VA ✓ (con margine)
- Fusibile primario: I = P / V = (40VA × 1.25 fattore sicurezza) / 230V = 0.22A → usa 20A per grande margine (tolleranza IEC 60127)

#### Pericolo 3: Isolamento 24VAC vs 230V

**IMPERATIVO**: Trasformatore deve avere **doppio isolamento** (marcato con ◻◻ su casing).

- Isolamento Classe II significa: nessun filo terra necessario tra primario e secondario
- Previene trasferimento di tensione pericolosa da 230V a 24VAC
- Se trasformatore non marcato classe II: **NON USARE**

---

## 4. ARCHITETTURA GENERALE

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALIMENTAZIONE 230V AC                       │
│                       (presa giardino)                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │   DEVIATORE     │ ← Seleziona: "Hunter Mode" / "Arduino Mode"
        │   MANUALE 2x    │
        │   16A 250VAC    │
        └────┬───────┬────┘
             │       │
      ┌──────▼─┐   ┌─▼──────┐
      │ HUNTER │   │Arduino  │
      │ Eco-   │   │ Box     │
      │Logic   │   │  IP65   │
      │  (IN)  │   │  (IN)   │
      └───┬────┘   └────┬────┘
          │             │
    ┌─────▼─────────────▼──────┐
    │   TRASFORMATORE          │
    │   230V → 24VAC 40VA      │
    │   (comune a entrambi)    │
    └─────┬─────────────────────┘
          │
    ┌─────▼─────────────────────┐
    │  CIRCUITO 24VAC VALVOLE   │
    │  (Zona 1: Solenoid valve) │
    │  (Zona 2: Solenoid valve) │
    └───────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ARDUINO BOX (Modalità Arduino attiva)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐                 │
│  │ Arduino  │  │ Modulo   │  │  Sensori     │                 │
│  │ Uno/     │──│ Relè 2ch │──│  Umidità x2  │                 │
│  │ ESP32    │  │ opto     │  │              │                 │
│  └──────────┘  └──────────┘  └──────────────┘                 │
│       │              │              │                          │
│       │ RX/TX        │ OUT1 → Z1    │ ADC0 → Zona1           │
│       │              │ OUT2 → Z2    │ ADC1 → Zona2           │
│       │ [Serial/WiFi]└──────────────┘                         │
│       │                                                        │
│       └─────────────────────┬────────────────────────────────┘
│                             │
│                      [Debug/Monitor]
│                      (Serial 9600 baud)
│                      o WiFi IP + Browser
└─────────────────────────────────────────────────────────────────┘

FLUSSO LOGICO (ogni 60 secondi):
1. Leggi ADC sensore Zona 1 e Zona 2
2. Converti in % umidità (0-100%)
3. Confronta con soglia (es: 30%)
4. Se Zona1 < 30% E non in cooldown: ACCENDI relè 1
5. Se Zona1 > 50%: SPEGNI relè 1 (isteresi per stabilità)
6. Idem per Zona 2
7. Invia stato seriale / scrivi SD log
8. Attendi 60s, ripeti
```

---

## 5. IMPIANTO HUNTER ECO-LOGIC ESISTENTE

### Specifiche Tecniche Hunter Eco-Logic

| Parametro | Valore |
|-----------|--------|
| **Alimentazione input** | 24 VAC ± 10%, 50/60 Hz |
| **Corrente standbya** | ~50-100 mA |
| **Corrente per zona attiva** | ~150-200 mA (dipende da valvola) |
| **Numero zone** | 4, 6, o 8 (modello dipendente) |
| **Tempo programmazione** | 6-14 giorni settimana |
| **Uscita zona** | 24 VAC a bassa impedenza (~1Ω) |
| **Protezione interna** | Fusibile 5A 24VAC |
| **Temperatura operativa** | 0–50°C |

### Terminali Connessione Hunter

**Modello: ELC-401I (4 zone, indoor)**

```
Pannello frontale:
┌─────────────────────────┐
│  HUNTER ECO-LOGIC 4     │
│  ┌─────────────────┐    │
│  │ LCD Display     │    │
│  │ Menu buttons    │    │
│  └─────────────────┘    │
│  ZONE 1 2 3 4 COM       │
│ [•] [•] [•] [•] [•]     │ ← Morsetti uscita (24VAC)
│  │   │   │   │   │      │
└──┼───┼───┼───┼───┼──────┘
   │   │   │   │   │
   1   2   3   4  COM ← Zona 1, Zona 2, Zona 3, Zona 4, Comune

Morsetti INGRESSO (dietro o lato):
┌─────────────────────┐
│ AC IN  (24VAC input)│
│ [◄—┬—►] [◄—┬—►]    │
│    A     B         │ ← Fase e Neutro trasformatore
└────┬────┬──────────┘
     │    │
   [L]  [N]
```

### Modalità Connessione Hunter Standard

Quando il **deviatore è su "Hunter"**:

```
Trasformatore 24VAC output:
    ┌─────┬─────┐
    │  L  │  N  │ ← Livelli logici
    └──┬──┴──┬──┘
       │     │
       │     └─────────┐
       │               │
   ┌───▼───┬───────────▼───┐
   │ ZONE1 │ ZONE2 ... COM │
   └───┬───┴───┬────────┬───┘
       │       │        │
      (1)     (2)      (C)  ← Morsetti Hunter
       │       │        │
       │       │        └─── Comune (ritorno a N)
       │       └─────────── Zona 2 (accesa se morsetto a L)
       └────────────────── Zona 1 (accesa se morsetto a L)
```

**Logica Hunter nativa**: Hunter connette il morsetto zona a L per accendere. È una **logica a tensione**, non a corrente di controllo.

---

## 6. COMPONENTI PRINCIPALI

### 6.1 Arduino Uno R3

**Datasheet: ATmega328P (Microchip)**

```
Pinout Rilevante (40-pin DIP):
┌──────────────────────────────┐
│ Arduino Uno R3 (ATmega328P)  │
├──────────────────────────────┤
│ POWER:                        │
│  Vin (7-12V)    ← USB/ext.   │
│  5V             ← Regolatore │
│  GND            ← Massa      │
├──────────────────────────────┤
│ GPIO DIGITALI:                │
│  0-1   ← RX/TX (Seriale)     │
│  2-13  ← IO generici         │
│        (usiamo 8, 9 per relè) │
├──────────────────────────────┤
│ ANALOG INPUT (ADC 10-bit):   │
│  A0-A5 ← Sensori umidità    │
│        (usiamo A0, A1)       │
├──────────────────────────────┤
│ PWM OUTPUT: 3,5,6,9,10,11    │
└──────────────────────────────┘

Caratteristiche Elettriche:
  • Tensione logica: 5V (GPIO)
  • Corrente massima per GPIO: 40 mA total, ~20 mA per pin
  • ADC 10-bit: risoluzione 5V/1024 ≈ 4.88 mV per step
  • Frequenza clock: 16 MHz
  • Flash: 32 kB; SRAM: 2 kB
  • EEPROM: 1 kB (persistente)
```

**Specifiche per questo progetto:**
- **Pin 8**: OUT relè Zona 1 (LOW = acceso)
- **Pin 9**: OUT relè Zona 2 (LOW = acceso)
- **Pin A0**: IN sensore umidità Zona 1 (0-1023 ADC)
- **Pin A1**: IN sensore umidità Zona 2 (0-1023 ADC)
- **GND**: Massa comune

### 6.2 ESP32 DevKit v1

**Alternativa per Fase 4 (migrazione WiFi)**

```
Pinout Rilevante:
┌──────────────────────────────┐
│ ESP32 DevKit v1 (30-pin)     │
├──────────────────────────────┤
│ POWER:                        │
│  5V (da USB-C)  ← Regolatore │
│  GND            ← Massa      │
├──────────────────────────────┤
│ GPIO DIGITALI:                │
│  GPIO4, GPIO5   ← SSR relè   │
│  (non usare GPIO0,2,15)      │
├──────────────────────────────┤
│ ADC (12-bit):                │
│  ADC1_CH0 (GPIO36) ← Sens. 1 │
│  ADC1_CH3 (GPIO39) ← Sens. 2 │
├──────────────────────────────┤
│ I2C, SPI, UART               │
│ WiFi 802.11 b/g/n           │
│ Bluetooth 5.0               │
└──────────────────────────────┘

Caratteristiche Elettriche:
  • Tensione logica: 3.3V (GPIO) ← ATTENZIONE: NON 5V!
  • Corrente massima per GPIO: 12 mA (limite soft)
  • ADC 12-bit: risoluzione 3.3V/4096 ≈ 0.8 mV per step
  • Frequenza clock: 80-240 MHz (configurable)
  • Flash: 4 MB (SPIFFS filesystem)
  • SRAM: 520 kB
  • Temp. funzionamento: -40–+85°C
```

**ATTENZIONE GPIO 3.3V**: NON connettere direttamente relè 5V al pin ESP32! Usare SSR optoisolato 3.3V oppure optoisolatore esterno (NPN transistor + LED).

### 6.3 Modulo Relè 2 Canali Optoisolato 5V

**Modello: SRD-05VDC-SL-C (standard AliExpress/Amazon)**

```
┌────────────────────────────────────┐
│ Relè 2 Canali Optoisolato (5V)     │
│                                    │
│  INPUT SIDE:                       │
│  ┌──────┬──────┬──────┬──────┐    │
│  │ GND  │ IN1  │ IN2  │ VCC  │    │
│  └──────┴──────┴──────┴──────┘    │
│    │      │      │      │         │
│   (◄◄─────┤      ├─────►►►)       │ ← Optoisolamento
│    │      │      │      │         │
│  OUTPUT SIDE:                      │
│  ┌─────────────────────────┐      │
│  │  NC1 NO1 COM | NC2 NO2 COM     │ ← Contatti relè
│  └──┬──────┬─────┴────┬────┬──────┘
│     │      │          │    │
│    (1)    (2)        (3)  (4)    (5)
│
│ Specifiche:
│  • Input VCC: 5V DC
│  • Input current per canale: ~70 mA @ 5V
│  • Output: 10A 250VAC (standard)
│  • Tempo commutazione: ~10 ms
│  • Isolamento: 2 kV tra ingresso e uscita
│  • Contatti: SPDT (Single Pole Double Throw)
│
│ LOGICA:
│  IN1 = LOW (0V)  → OPEN circuito (relè non pilotato)
│  IN1 = HIGH (5V) → CHIUDE circuito (relè pilotato)
│
│  NOTA: Logica invertita nel nostro codice:
│        digitalWrite(pin_relè, LOW) → ACCENDI irrigazione
│        digitalWrite(pin_relè, HIGH) → SPEGNI irrigazione
└────────────────────────────────────┘

Integrazione con Arduino Uno:
VCC  → 5V (Arduino)
GND  → GND (Arduino)
IN1  → GPIO Pin 8 (Arduino)
IN2  → GPIO Pin 9 (Arduino)

NO1 + COM → Circuito 24VAC Zona 1
NO2 + COM → Circuito 24VAC Zona 2
```

### 6.4 Trasformatore 230V → 24VAC 40VA

**Modello commerciale: Trasformatore toroidale preassemblato DIN-rail**

```
PRIMARIO (230V input):
  ┌─────────────────────┐
  │ ┌─────────────────┐ │
  │ │  TRASFORMATORE  │ │
  │ │  230V ↔ 24VAC   │ │  40VA =
  │ │  40VA / 50-60Hz │ │  24V × 1.67A
  │ └─────────────────┘ │
  │ [L] [N]             │  Doppio isolamento
  └──┬──┬──┘            │  Protezione termica
     │  │               │  IEC 60950 Classe II
     │  │               │
     │  │  SECONDARIO    │
     │  │  24VAC output  │
     │  │               │
     │  └───┬───────┬───┤
     │      │       │   │
     │      OUT1   OUT2 │
     │      (L)    (N)  │
     │      │       │   │
     └──────┴─────────┘

Specifiche Elettriche:
  • Perdite a vuoto: ~2-5 W (calore residuo)
  • Perdite in carico (40VA): ~1-2 W (resistenza primario/secondario)
  • Rendimento: ~95% a carico pieno
  • Protezione termica: fusibile interno a ~60°C (se sovraccarico)
  • Isolamento: Classe II (doppio isolamento, no terra)
  • Ingresso: 230V ± 10% (200-253V tollerato)
  • Uscita: 24V ± 5% (a plena potenza con carico)

DIMESIONAMENTO:
  Caso 1: 1 valvola 6W attiva
  → I_secondary = 6W / 24V = 0.25A (OK, sotto 1.67A)
  
  Caso 2: 2 valvole 6W ciascuna simultanee
  → I_secondary = 12W / 24V = 0.5A (OK)
  
  Caso 3: 2 valvole + isteresi inrush
  → I_inrush_solenoid = ~2-3x I_holding
  → Worst case: 0.5A × 3 = 1.5A < 1.67A (margine ristretto!)
  → Usar trasformatore 40VA è al limite; 50VA è più sicuro se disponibile

MONTAGGIO FISICO:
  • DIN rail 35mm standard (guida in box IP65)
  • Dimensioni tipiche: 72×60×80 mm
  • Peso: ~0.8 kg
  • Ventilazione: aria libera min. 5cm attorno (box con fori?)
```

### 6.5 Sensori Umidità Capacitivi

**Modello: DFRobot SEN0193 (capacitivo, 0-100% scala)**

```
PINOUT SENSORE:
  ┌──────────────────┐
  │ Capacitive Sensor│
  │                  │
  │ [GND] [VCC] [OUT]│ ← 3 fili
  └────┬─────┬──────┘
       │     │      │
       ●     ●      ● (giallo/arancio/nero tipicamente)
       │     │      │
    (BLK)  (RED)  (GRN)

PIN DETAILS:
  • GND: Nero → GND Arduino
  • VCC: Rosso → 5V Arduino (o 3.3V, accetta entrambi)
  • OUT: Giallo → ADC Arduino (A0 per zona 1, A1 per zona 2)

FUNZIONAMENTO:
  • Capacità varia con umidità del suolo
  • Nessun contatto diretto con acqua (non corrosivo come resistivo)
  • Uscita analogica 0-1023 (ADC 10-bit Arduino)

GAMMA UMIDITÀ (post-calibrazione):
  • Suolo secco: ~800-900 ADC
  • Suolo umido: ~400-500 ADC
  • Suolo fradicio: ~200-300 ADC
  • Acqua pura: ~0 ADC

CALIBRAZIONE NECESSARIA:
  1. Leggi valore "dry" in vaso vuoto per 5 min
  2. Leggi valore "wet" immergendo punta in acqua per 30s
  3. Usa mappa lineare: % = (dry - ADC) / (dry - wet) × 100
  4. Filtra rumore con moving average su 10 letture

DURATA:
  • Vita media: 3-5 anni (niente contatto resistivo)
  • Resistenza all'oxidazione: buona se non sporco
  • Risciacquo settimanale consigliato con acqua distillata se molto sporco
```

### 6.6 Box IP65 200x300x150mm

```
ESTERNO:
  ┌─────────────────────┐
  │ Box IP65 200x300mm  │
  │ Polycarbonate grigio│
  │                     │
  │ ┌─────────────────┐ │
  │ │  Sportello      │ │ ← Inclinato verso basso
  │ │ + Guarnizione   │ │   (evita ristagni)
  │ │ + 2 Maniglie    │ │
  │ └─────────────────┘ │
  │                     │
  │ [◉] [◉] Pressacavi │ ← M20 IP67
  │     x2             │
  │                     │
  │ (fori per drenaggio)│ ← Opzionali Ø3mm
  └─────────────────────┘
         65cm × 80cm

INTERNO:
  ┌─────────────────────────────┐
  │ GUIDA DIN 35mm              │ ← Su parete interna
  │ ├─ Portafusibile DIN        │
  │ │  ├─ Fusibile 20A primario │
  │ │  └─ Fusibile 5A secondario│
  │ ├─ RCD 30mA 2x25A (OPZ.)   │
  │ ├─ Trasformatore 40VA       │
  │ └─ Relè 2 canali (DIN)      │
  │                             │
  │ Arduino Uno (a parte, non   │
  │ su DIN, su staffa)          │
  │                             │
  │ Cablaggio organizzato:      │
  │  • 230V rosso/nero in tubo  │
  │  • 24VAC arancione in tubo  │
  │  • Sensori schermati        │
  └─────────────────────────────┘

SPECIFICHE IP65:
  • IP = Ingress Protection
  • 6 = Protezione polvere totale (pressione aria)
  • 5 = Getti d'acqua bassa pressione (all'angolo)
  • -20 a +60°C operativo
  • Guarnizione in neoprene (resistenza umidità 5-10 anni)
  • Trattamento UV per polycarbonate

MONTAGGIO FISICO:
  • Muro giardino, orientamento: nordest consigliato
    (sole diretto al mattino, ombra pomeriggio)
  • Altezza: 1.5-2m dal suolo (sopra erba bagnata)
  • Distanza dalle valvole: ≤3m (minimalizza cavi)
  • Protezione da piante rampicanti (mantieni libero)
```

---

## 7. CABLAGGIO ELETTROVALVOLE 24 VAC

### Topologia: Parallelo Reversibile

Due valvole **in parallelo** sul secondario trasformatore. Lo **stato ON/OFF dipende dal relè Arduino**, non da Hunter.

```
MODALITÀ HUNTER (deviatore SU "Hunter"):
  
  Trasformatore OUT (L, N)
         ↓
  Hunter Eco-Logic
    Morsetto Z1 → Valvola Zona 1
    Morsetto Z2 → Valvola Zona 2
    Morsetto COM → N trasf.

MODALITÀ ARDUINO (deviatore SU "Arduino"):

  Trasformatore OUT (L, N)
         ↓
  [L]
   │
   ├─→ [NO1 relè 1] ─→ Valvola Zona 1 ─→ [N]
   │                                        ↑
   ├─→ [NO2 relè 2] ─→ Valvola Zona 2 ─→───┘
   │
   └─→ [COM] (da relè 1 e 2 univocamente nel circuito)
       
   Arduino GPIO 8 → [IN1 relè] → pilota Zona 1
   Arduino GPIO 9 → [IN2 relè] → pilota Zona 2
```

### Disegno Schematico Dettagliato

```
PRIMARIO 230V AC (esterno box, protetto):
┌──────────────────────────────────────┐
│ Presa 230V                           │
│ [L=rosso] [N=blu] [PE=giallo]        │
└──┬──────────┬──────────┬─────────────┘
   │          │          │
   │ [20A]    │          │ Interruttore
   │  fus.    │          │ principale
   │          │          │
   ├──────────▼──────────┼─────→ RCD 30mA (opzionale)
   │                     │
   ▼                     ▼
  Fase                 Neutro
   │                     │
   └─────────┬───────────┘
             │
      ┌──────▼───────┐
      │Trasformatore │
      │230V → 24VAC  │
      │ 40VA         │
      └──────┬───────┘
             │
      ┌──────▼───────────────┐
      │ SECONDARIO 24VAC     │
      │ [5A fus.] ─→ L(out)  │
      │ [5A fus.] ─→ N(out)  │
      └──────┬───────┬───────┘
             │       │
             L       N
             │       │
        ┌────┤       │
        │    ├───────┤
        │    │       │
        NO1  NO2    COM(relè)
        │    │       │
        │    │       └─→ N trasf. (comune ritorno)
        │    │
        │    ├─→ Valvola 2 ─→ [N]
        │
        ├─→ Valvola 1 ─→ [N]

Relè 1 (IN1 da GPIO8):
  • GND → GND Arduino
  • VCC → 5V Arduino
  • IN1 → GPIO 8 Arduino
  • NO1 → Entra Valvola 1
  • COM → Uscita A Valvola 1

Relè 2 (IN2 da GPIO9):
  • GND → GND Arduino
  • VCC → 5V Arduino (comune con relè 1)
  • IN2 → GPIO 9 Arduino
  • NO2 → Entra Valvola 2
  • COM → Uscita Valvola 2 (e uscita Valvola 1 univocamente a N)
```

### Tabella Morsetti Effettivi

| Punto | Componente | Tensione | Colore Cavo | Funzione |
|-------|-----------|----------|-------------|----------|
| TP1 | Presa 230V Fase | 230V AC | Rosso | Input primario |
| TP2 | Presa 230V Neutro | 0V ref | Blu | Input primario |
| TP3 | Fusibile 20A | 230V→0V | Rosso | Protezione primario |
| TP4 | Trasformatore [L] | 24V AC | Arancio | Output secondario hot |
| TP5 | Trasformatore [N] | 0V AC | Grigio | Output secondario return |
| TP6 | Relè 1 [NO] | 24V AC | Arancio | A Valvola 1 ingresso |
| TP7 | Relè 1 [COM] | 0/24V AC | Grigio | Ritorno Valvola 1 (e Valvola 2) |
| TP8 | Relè 2 [NO] | 24V AC | Arancio | A Valvola 2 ingresso |
| TP9 | Valvola 1 Ingr. | 24V AC | Arancio | Connettore valvola |
| TP10 | Valvola 1 Uscita | 0V AC | Grigio | Ritorno |
| TP11 | Valvola 2 Ingr. | 24V AC | Arancio | Connettore valvola |
| TP12 | Valvola 2 Uscita | 0V AC | Grigio | Ritorno (comune) |

---

## 8. MODALITÀ OPERATIVE

### Modalità 1: Sostituzione Totale (ONLY Arduino)

**Deviatore "Arduino" selezionato permanentemente.**

**Configurazione:**
- Hunter rimane spento (disconnesso dal trasformatore)
- Arduino controlla **esclusivamente** le due valvole
- Nessun fallback a Hunter

**Pro:**
- Massimo controllo intelligente
- Compatibile con i sensori umidità

**Contro:**
- Se Arduino crasha: zero irrigazione
- Rischio morte piante se bug nel codice

**Caso d'uso:** Persona con skill tecnico alto che vuole full automation.

### Modalità 2: Parallelo Reversibile (Consigliata per questo progetto)

**Deviatore manuale permette passaggio rapido "Hunter ↔ Arduino".**

**Configurazione:**
```
Posizione A: "Hunter Mode"
  → Trasformatore alimenta SOLO Hunter Eco-Logic
  → Arduino spento / disalimentato
  → Fallback a controller originale (affidabile, commerciale)

Posizione B: "Arduino Mode"
  → Trasformatore alimenta SOLO Arduino + Relè
  → Hunter disconnesso
  → Smart control, sensori, logging
```

**Pro:**
- Massima **reversibilità** e **sicurezza** (sempre via escape)
- Testare Arduino senza rischiare impianto
- Se Arduino ha bug: switch a Hunter in 2 secondi
- Raccolta dati durante operazione Hunter (logging opzionale)

**Contro:**
- Richiede **manual switching** (non completamente automatico)
- Possibile dimenticarsi selettore e usare Hunter con Arduino carico → confusione

**Implementazione:**
```
Deviatore 2x25A 250VAC doppio (SPDT):
  • Contatto 1: Alimenta Trasf. → Hunter
  • Contatto 2: Alimenta Trasf. → Arduino Box
  • Comune: Trasformatore ingresso 24VAC
  
  Posizione A (Hunter):
    Trasf. 24VAC OUT → Hunter
  
  Posizione B (Arduino):
    Trasf. 24VAC OUT → Arduino Relè
```

**Raccomandazione:** **MODALITÀ 2 OBBLIGATORIA** per questo progetto.

---

## 9. MONTAGGIO PASSO-PASSO

### FASE 1: PIANIFICAZIONE (0.5 giorni)

- [ ] Verifica distanza box da valvole Hunter (contai 3m max)
- [ ] Misura lunghezza cavi necessari (primario 230V, secondario 24VAC, sensori)
- [ ] Identifica alimentazione 230V più vicina (presa giardino, scatola silenziatore, etc.)
- [ ] Scegli posizionamento box IP65 (parete nord-est, altura 1.5-2m)
- [ ] Ordina tutti i componenti BOM (+ 10% margine)
- [ ] Verifica arrivo trasformatore 24VAC e fusibili

### FASE 2: PREPARAZIONE BOX E COMPONENTI (1 giorno)

#### Step A: Apertura e Pulizia Box IP65

1. Estrai box dall'imballaggio
2. Rimuovi protezioni di spedizione
3. Ispeziona guarnizioni (neoprene integro?)
4. Lava internamente con panno umido, asciuga completamente
5. Monta **staffa Arduino** all'interno (non su DIN rail, su supporto separato)

#### Step B: Montaggio DIN Rail e Componenti Protezione

1. **DIN Rail 35mm**: monta orizzontale su parete interna box
   - Fissa con 2-3 staffe metalliche (kit solitamente incluso)
   - Allinea perfettamente (livella)

2. **Portafusibile DIN + Fusibili**:
   - Inserisci fusibile 20A in portafusibile (primario 230V)
   - Inserisci fusibile 5A in secondo portafusibile (secondario 24VAC)
   - Monta su DIN rail (scatto semplice, prova movimento)

3. **RCD 30mA** (opzionale ma vivamente consigliato):
   - Monta a sinistra portafusibili
   - Verifica morsetti: L→230V rosso, N→230V blu, OUT verso trasformatore

4. **Trasformatore 40VA**:
   - Prendi trasformatore preassemblato DIN
   - Monta a destra su DIN rail
   - Verifica stabilità (no vibrazioni)

#### Step C: Montaggio Relè 2 Canali

1. **Opzione A** (se relè ha attacco DIN):
   - Monta su DIN rail a destra trasformatore

2. **Opzione B** (se relè è breadboard-style):
   - Monta su **staffa di plastica** separata, parallela a Arduino

#### Step D: Preparazione Cablaggio Interno

1. Taglia cavi secondo lunghezze stimate:
   - **Primario 230V**: L e N da RCD a trasformatore (~30cm)
   - **Secondario 24VAC**: OUT da trasformatore a relè (2x ~30cm)
   - **Sensori**: 0.5mm² da Arduino A0/A1 a sensori (~2m esteriore)

2. **Isola tutti i cavi** secondo categoria:
   - Cavi primario 230V (rosso per L, blu per N) **in tubo giallo opaco separato**
   - Cavi secondario 24VAC (arancio per L, grigio per N) **in tubo grigio separato**
   - Cavi sensori digitali (schermati se possibile) in tubo separato

3. Etichetta TUTTI i morsetti con etichette adesive vinile:
   ```
   "230V-L"    "230V-N"
   "24V-L"     "24V-N"
   "Z1-IN"     "Z1-OUT"
   "Z2-IN"     "Z2-OUT"
   "GND Arduino" "5V Arduino"
   ```

### FASE 3: CABLAGGIO ELETTRICO (1 giorno)

#### Step A: Collegamento Primario 230V

**⚠️ SICUREZZA: Indossa guanti isolanti, verifica con multimetro prima di toccare**

1. **Disconnetti completamente** la presa 230V (scollega spina dalla parete)
2. **Verifica assenza tensione** con multimetro DC (dovrebbe leggere ~0V)
3. Collega:
   - Fase rossa presa → Fusibile 20A ingresso (morsetto 1)
   - Fusibile 20A uscita (morsetto 2) → RCD ingresso L (oppure diretto trasformatore se no RCD)
   - Neutro blu presa → RCD ingresso N (oppure diretto trasformatore)
   - Terra giallo/verde → Morsetto PE trasformatore (se classe III) o isolato se classe II

4. **Test**: Collega spina alla parete, accendi multimetro sul morsetto uscita RCD:
   - Dovrebbe leggere ~230V AC
   - Premi pulsante TEST del RCD (dovrebbe scattare e staccare alimentazione)
   - Premi pulsante RESET del RCD (alimentazione ritorna)
   - **Se non scatta**: RCD difettoso, TOGLI SPINA e sostituisci

#### Step B: Collegamento Secondario 24VAC

1. **Disconnetti ancora spina 230V** (doppia verifica sicurezza)
2. Collega morsetti trasformatore secondario:
   - OUT1 (L 24VAC) → Relè [L input]
   - OUT2 (N 24VAC) → Relè [N input] + [COM comune]

3. **Collegamento Relè a Valvole**:
   - Relè 1 [NO] → Valvola Zona 1 [L]
   - Relè 2 [NO] → Valvola Zona 2 [L]
   - Relè 1 [COM] + Relè 2 [COM] → Valvole [N] (ritorno, comune)

4. Tira i cavi dai **pressacavi M20 IP67** sulla parete box verso l'esterno:
   - Pressacavo 1: cavo rosso 230V (fase primario)
   - Pressacavo 2: cavo blu 230V (neutro primario)
   - Pressacavo 3: cavo arancio 24VAC primario (extra per flessibilità)

#### Step C: Collegamento Arduino e Sensori

1. **Alimentazione Arduino**:
   - USB-C o micro-USB da alimentatore 5V/2A esterno
   - Oppure (solo test): da computer via USB (limitato a ~500mA)

2. **Sensori umidità** (2x per zone):
   - Sensore Zona 1: GND → Arduino GND, VCC → Arduino 5V, OUT → Arduino A0
   - Sensore Zona 2: GND → Arduino GND, VCC → Arduino 5V, OUT → Arduino A1

3. **Relè control**:
   - Relè GND → Arduino GND (comune)
   - Relè VCC → Arduino 5V
   - Relè IN1 → Arduino GPIO 8
   - Relè IN2 → Arduino GPIO 9

### FASE 4: MONTAGGIO FISICO ESTERNO (0.5 giorni)

1. **Deviatore manuale 2-vie**:
   - Monta su parete box o adiacente (altezza ergonomica, ~1.5m)
   - Etichetta chiaramente: "Hunter" / "Arduino"
   - Collega morsetto comune a trasformatore input 24VAC

2. **Percorso cavi esteriori**:
   - Primario 230V: tubo arancio con protezione UV, in angoli ombreggiati
   - Secondario 24VAC: tubo grigio, separato dal primario (min 10cm)
   - Sensori: guaina schermata lungo muri, lontano da cavi potenza

3. **Pressacavi**:
   - Inserisci guarnizioni silicone aggiuntive (doppio sigillo)
   - Serrat con chiave dinamometrica ~2 N⋅m (leggero, non forzare)

### FASE 5: TEST PRE-ALIMENTAZIONE (1 giorno)

1. **Controllo visivo completo**:
   - Nessun cavo scoperto su parti metalliche
   - Nessun incrocio 230V-24VAC
   - Isolamento intatto (nessun buco in tubi)

2. **Test continuità** (multimetro):
   - 230V L → ingresso primario: ~0Ω (continuità OK)
   - 230V N → ingresso primario: ~0Ω (continuità OK)
   - Tra 230V L e N: ∞Ω (nessun cortocircuito!)
   - Tra 24VAC L e N secondario: 5-10Ω (trasformatore OK)

3. **Test isolamento** (multimetro DC HIGH, ~1kV):
   - Tra 230V L e 24VAC L: >1 MΩ (isolamento OK)
   - Tra 230V N e chassis: >1 MΩ (isolamento OK)

4. **Verifica fusibili**:
   - Fusibile 20A primario: intatto, non scurrito
   - Fusibile 5A secondario: intatto

---

## 10. IMMAGINI OBBLIGATORIE

### Elenco di cosa fotografare o disegnare

Genera **fotografie professionali** o schemi tecnici per i seguenti punti:

1. **Schema generale BOM montato**: vista completa box IP65 interno con tutti componenti etichettati
2. **Dettaglio DIN rail**: portafusibile, RCD, trasformatore in sequenza
3. **Dettaglio relè e cablaggio secondario 24VAC**: foto dell'attacco morsetti relè → valvole
4. **Dettaglio sensori umidità**: installazione probe nel terreno, lungo le zone
5. **Dettaglio deviatore manuale**: posizioni "Hunter" e "Arduino" con etichette chiare
6. **Cablaggio primario 230V** (SOLO SCHEMA, non foto dal vivo per sicurezza): fase, neutro, terra a portafusibili
7. **Box esterno in giardino**: posizionamento su parete, protezione UV, pendenza sportello
8. **Collegamento Arduino Uno**: pinout etichettato (GND, 5V, GPIO 8, 9, A0, A1)
9. **Collegamento ESP32**: pinout etichettato (GND, 3.3V, GPIO 4, 5, ADC1_CH0, ADC1_CH3)
10. **Tabella morsetti stampabile**: A4 da applicare su parete interna box con etichettatrice

---

## 11. COLLAUDO E TEST INTERMEDI

### Test 1: Alimentazione 230V Isolata (NESSUN LOAD)

**Obiettivo:** Verificare trasformatore genera 24VAC senza carichi collegati.

**Procedura:**
1. Deviatore su "Arduino" (ma Arduino spento)
2. Accendi RCD (test button)
3. Misura con multimetro AC tra morsetti OUT trasformatore:
   - Dovrebbe leggere **24V ± 1V** (tolleranza ±5% = 22.8-25.2V)
4. Se non legge nulla: verificare fusibile 20A primario, continuità cavi

### Test 2: Relè Meccanico (senza valvole)

**Obiettivo:** Verifica che relè scatti correttamente quando alimentato.

**Procedura:**
1. Accendi Arduino Uno (via USB, solo alimentazione digitale)
2. Carica sketch test:
   ```cpp
   void setup() {
     pinMode(8, OUTPUT);
     pinMode(9, OUTPUT);
     Serial.begin(9600);
   }
   void loop() {
     digitalWrite(8, LOW);  // Relè 1 ON
     Serial.println("Relè 1 ON");
     delay(1000);
     digitalWrite(8, HIGH); // Relè 1 OFF
     Serial.println("Relè 1 OFF");
     delay(1000);
   }
   ```
3. **Ascolta clic** del relè: dovrebbe sentire "click-click" ogni secondo
4. Ripeti per GPIO 9 (modifica codice)
5. Se no click: verificare alimentazione 5V relè, continuità IN1/IN2

### Test 3: Sensori Umidità (Calibrazione Secca/Bagnata)

**Obiettivo:** Determinare range ADC per calibrazione 0-100%.

**Procedura:**
1. Carica sketch test:
   ```cpp
   void setup() {
     Serial.begin(9600);
   }
   void loop() {
     int raw1 = analogRead(A0);
     int raw2 = analogRead(A1);
     Serial.print("Zona1: "); Serial.print(raw1);
     Serial.print(" | Zona2: "); Serial.println(raw2);
     delay(500);
   }
   ```
2. **Test Secco**: Posiziona sensore in vaso vuoto, attendi 2 minuti → annota ADC_DRY
   - Tipico: 800-900 ADC
3. **Test Bagnato**: Immergi punta sensore in bicchiere acqua per 30s → annota ADC_WET
   - Tipico: 200-300 ADC
4. **Calcola formula calibrazione:**
   ```
   % umidità = (ADC_DRY - ADC_lettura_attuale) / (ADC_DRY - ADC_WET) × 100
   ```
5. Annotai valori in commento del codice

### Test 4: Ciclo Irrigazione Completo (Uno + Trasformatore + Una Valvola)

**⚠️ PREREQUISITO: Trasformatore alimentato, solo Zona 1 testata**

**Procedura:**
1. Carica sketch semplificato:
   ```cpp
   #define PIN_VALVOLA 8
   #define SENSORE_UMID A0
   #define ADC_DRY 850
   #define ADC_WET 250
   #define SOGLIA_ON 30  // Accendi se umidità < 30%
   #define SOGLIA_OFF 60 // Spegni se umidità > 60%
   
   void setup() {
     pinMode(PIN_VALVOLA, OUTPUT);
     digitalWrite(PIN_VALVOLA, HIGH); // Inizio OFF
     Serial.begin(9600);
   }
   
   void loop() {
     int raw = analogRead(SENSORE_UMID);
     int perc = map(raw, ADC_DRY, ADC_WET, 0, 100);
     perc = constrain(perc, 0, 100);
     
     Serial.print("Umidità: "); Serial.print(perc); Serial.println("%");
     
     if (perc < SOGLIA_ON) {
       digitalWrite(PIN_VALVOLA, LOW);  // Accendi
       Serial.println("→ IRRIGAZIONE ON");
     }
     if (perc > SOGLIA_OFF) {
       digitalWrite(PIN_VALVOLA, HIGH); // Spegni
       Serial.println("→ IRRIGAZIONE OFF");
     }
     
     delay(5000); // Leggi ogni 5s (accelerato per test)
   }
   ```
2. **Osserva comportamento**:
   - Accendi seriale Monitor (baud 9600)
   - Leggi % umidità in tempo reale
   - Asciugare sensore → % scende, relè accende valvola → senti "click"
   - Bagnare sensore → % sale, relè spegne valvola → senti "click"
3. **Verifica uscita valvola 24VAC**:
   - Multimetro AC tra morsetti NO e COM relè
   - Dovrebbe alternare 24V (valvola ON) e 0V (valvola OFF)

### Test 5: Migrazione da Uno a ESP32 (FASE 4)

**Prerequisito:** Codice Uno funzionante, ESP32 IDE installato

**Procedura:**
1. Carica codice ESP32 da sezione Codice (file `main_esp32.cpp`)
2. Configura Arduino IDE:
   - Board: "ESP32 Dev Module"
   - Port: COM della ESP32
   - Upload speed: 115200
3. Carica sketch
4. Ripeti Test 1-4 con GPIO 4/5 (ESP32) invece di 8/9 (Uno)
5. Se WiFi: verifica connessione con Serial Monitor
   ```
   [WiFi]: Connecting to SSID...
   [WiFi]: Connected! IP: 192.168.x.x
   ```

---

## 12. TROUBLESHOOTING

### Problema 1: Nessuna tensione 24VAC all'uscita trasformatore

| Sintomo | Causa Probabile | Soluzione |
|---------|-----------------|-----------|
| 0V secondario | Fusibile 20A primario bruciato | Sostituisci fusibile 20A T250V, verifica cortocircuito |
| 0V secondario | Trasformatore guasto | Test continuità bobina primaria (dovrebbe ~100-500Ω) |
| ~24V ma sporco (onda quadra) | RCD scattato | Premi reset RCD, se ripete → isolamento primario compromesso |
| Tensione bassa (18V) | Sovraccarico | Verificare no cortocircuiti secondario, misurare corrente |

**Test diagnostico:**
```
Multimetro AC:
  1. Tra L-N presa 230V → dovrebbe legger 230V ± 10%
  2. Tra ingresso RCD L-N → dovrebbe 230V (se no RCD) o dopo RCD
  3. Tra OUT trasformatore L-N → dovrebbe 24V ± 5%
  Se uno step fallisce, problema in quella sezione
```

### Problema 2: Relè non scatta (nessun click)

| Sintomo | Causa Probabile | Soluzione |
|---------|-----------------|-----------|
| Arduino spento | Alimentazione 5V assente | Verifica USB, led Arduino acceso? |
| GPIO 8/9 non esce da Arduino | Codice non caricato correttamente | Ricarica sketch, verifica compilazione OK |
| GPIO out ma relè non scatta | Corrente insufficiente GPIO | Arduino Uno max 40mA totale; relè 5V richiede ~70mA; usa SN74HC595 shift register |
| Relè scatta ma NO non accende valvola | Contatto relè ossidato | Estrai relè, puoi contatti con carta vetrata fine, reinserisci |
| Relè acceso tutto il tempo | Logica invertita nel codice | Modifica: `digitalWrite(pin, LOW)` accende relè (LOW = attivazione) |

**Test diagnostico:**
```
1. Multimetro sulla uscita GPIO 8 Arduino:
   - Dovrebbe alternare 0V (LOW) e 5V (HIGH)
   - Se fisso a 5V: software issue (loop bloccato)
   - Se fisso a 0V: hardware issue (pin danneggiato)
   
2. Alimentazione relè:
   - Verifica 5V tra VCC e GND relè
   - Verifica <0.1Ω tra Arduino GND e relè GND (stesso ground!)
```

### Problema 3: Sensori non leggono correttamente

| Sintomo | Causa Probabile | Soluzione |
|---------|-----------------|-----------|
| ADC sempre 1023 (max) | Sensore disconnesso | Verifica cavo A0/A1, continuità con multimetro |
| ADC sempre 0 (min) | Sensore cortocircuitato o firmware errato | Isola sensore, testa con power supply esterno |
| ADC fluttua wildly (100-900 random) | Rumore EMI, cavi lunghi | Aggiungi condensatore 100nF tra VCC e GND sensore, usa cavi schermati |
| Stessa lettura per zona 1 e 2 | A1 non configurato | Verifica: `analogRead(A1)` nel codice, non `analogRead(A0)` due volte |

**Calibrazione advanced:**
```cpp
// Se sensore legge sempre umido (ADC basso anche in secco):
// Probabilità: suolo molto argilloso, sensore sporco

// Soluzione 1: Aumenta ADC_DRY
//   Usa: (ADC_DRY = 950, ADC_WET = 200) invece (850, 250)

// Soluzione 2: Risciacqua sensore
//   - Rimuovi dal terreno
//   - Sciacqua con acqua distillata per 1 minuto
//   - Asciuga completamente
//   - Reinserisci, attendi 5 minuti, ricalibrare
```

### Problema 4: Valvole si accendono ma non esce acqua

| Sintomo | Causa Probabile | Soluzione |
|---------|-----------------|-----------|
| 24VAC all'ingresso valvola, niente acqua | Valvola meccanicamente bloccata | Spegni sistema, smonta valvola, pulisci sedile con solvente |
| Niente 24VAC valvola | Contatto relè difettoso | Prova second relè su stessa posizione, sostituisci se no va |
| Acqua fuoriesce sempre | Valvola solenoid bruciata (solenoide + ball non chiude) | Sostituisci valvola con nuova Hunter PGV equivalente |
| Pressione bassa (gocce, non getto) | Filtro main intasato | Ispeziona filtro impianto Hunter, pulizia |

**Test diagnostico:**
```
1. Verifica 24VAC ai morsetti valvola quando relè chiuso
   - Accendi valvola manualmente (GPIO 8 → LOW)
   - Multimetro AC tra morsetti valvola
   - Dovrebbe leggere 23-25V AC

2. Se no tensione ma relè "click": relè difettoso, sostituisci

3. Se tensione OK ma niente acqua: valvola o tubo bloccati
   - Scollega tubo di scarico valvola, attiva
   - Se acqua fuoriesce: uscita OK, problema a valle
   - Se no acqua: valvola bloccata, smonta e pulisci
```

### Problema 5: Il sistema funziona, ma Arduino si resetta continuamente

| Sintomo | Causa Probabile | Soluzione |
|---------|-----------------|-----------|
| Loop reset ogni 10-30s | Watchdog interno Arduino | Codice ha `delay()` troppo lungo, blocca loop |
| Serial Monitor disconnesso | Alimentazione 5V instabile | Usta alimentatore 5V diverse corrente min. 2A, no USB computer |
| Reset quando accendi relè | Spike di corrente relè | Aggiungi diodo 1N4007 flyback ai capi bobina relè (catodo a VCC) |

**Soluzione codice:**
```cpp
// SBAGLIATO (causa reset):
void loop() {
  // ... elaborazione
  delay(30000); // 30s: Arduino watchdog scatta, reset!
}

// CORRETTO (non blocca):
unsigned long lastTime = 0;
void loop() {
  unsigned long now = millis();
  if (now - lastTime >= 30000) {
    // ... elaborazione ogni 30s
    lastTime = now;
  }
  // Loop ritorna SUBITO, watchdog contento
}
```

---

## 13. ANTI-ZANZARE: PREVENZIONE SICURA

### Problema: Ristagni d'acqua = Colonie zanzare

**Strategia**: Non pesticidi, ma **prevenzione + monitoraggio**.

### Passo 1: Identificare Ristagni Critici

| Zona | Problema Tipico | Soluzione Arduino |
|------|-----------------|------------------|
| Sottobicchieri vasi | Ristagno 24-48h | Sensore livello capacitivo, reminder app "Svuota" |
| Tubo scarico A/C | Gocce accumulate | Sensore pioggia diretto, sposta scolo |
| Angoli box IP65 | Acqua di condensazione | Fori drenaggio Ø3mm, ogni 2-3 mesi asciuga con panno |
| Avvallamenti terreno | Pozzanghere dopo pioggia | Sensore livello ristagno nel punto basso |

### Passo 2: Monitor Sensori Ristagni

**Sensore livello capacitivo (opzionale upgrade):**
```cpp
#define PIN_RISTAGNO A2
#define ADC_SECCO 800
#define ADC_BAGNATO 300

void check_ristagno() {
  int raw = analogRead(PIN_RISTAGNO);
  
  if (raw < ADC_BAGNATO) {
    // Ristagno rilevato!
    Serial.println("⚠️ RISTAGNO CRITICO - Attiva drenaggio!");
    // Opz: accendi pompa svuotamento a 12V
    digitalWrite(PIN_POMPA, HIGH);
  }
}
```

### Passo 3: Prevenzione Biologica (NON CHIMICA)

| Metodo | Costo | Frequenza | Efficacia |
|--------|-------|-----------|-----------|
| **Bacillus thuringiensis (Bti)** | €5-10/flacone | 7 giorni se ristagno | Alto (larvicida naturale, non tossico) |
| **Drenaggio gravitazionale** | €0 (layout) | Continuo | Alto (previene ristagni) |
| **Trappole luminose UV** | €15-30 | Ricambio mensile | Medio (attrae adulti, non larve) |
| **Ventilazione forzata** | €50-100 | Continuo | Medio (asciuga umidità) |
| **Pesticida sintetico** | Vario | 5-7 giorni | Alto ma **TOSSICO, no DIY** |

### Passo 4: Implementazione Reminder App (WiFi ESP32)

```cpp
#ifdef USE_WIFI
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";
WebServer server(80);

void handleRoot() {
  // Pagina web mostra:
  // - Umidità zone
  // - Stato ristagni
  // - Countdown Bti reminder
  String html = "<h1>Sistema Irrigazione DIY</h1>";
  html += "<p>Umidità Zona1: " + String(percentile_zona1) + "%</p>";
  html += "<p>⚠️ Reminder: Svuota ristagni tra 2 giorni!</p>";
  server.send(200, "text/html", html);
}

void setup() {
  WiFi.begin(ssid, password);
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  server.handleClient();
  // ... resto logica
}
#endif
```

**Accedi da browser:** `http://192.168.1.XXX:80` (IP assegnato da router)

---

## 14. APPENDICI TECNICHE

### A. Formule e Calcoli Critici

**Corrente secondario trasformatore (caso 2 valvole):**
```
P = V × I
I = P / V = (2 valvole × 6W) / 24V = 0.5A
(Margine su 1.67A nominale: 0.5A / 1.67A = 29% load, OK)
```

**Caduta di tensione su cavi 24VAC:**
```
ΔV = 2 × I × R × L / S
  I   = corrente (A) = 0.5A
  R   = resistività rame = 0.0175 Ω⋅mm²/m
  L   = lunghezza cavo = 20m (andata+ritorno)
  S   = sezione cavo = 0.75mm²

ΔV = 2 × 0.5 × 0.0175 × 20 / 0.75 = 0.47V
Tensione finale: 24V - 0.47V = 23.53V ✓ (tolleranza OK)
```

**Potenza dissipata come calore in trasformatore:**
```
P_loss = I² × R_secondario + I² × R_primario
      ≈ 1-2W (per trasformatore 40VA)
→ NON occorre ventilazione forzata in box (dissipazione naturale OK)
```

### B. Pinout e Schema Collegamento Finale

**Arduino Uno R3 (40-pin DIP):**
```
         ┌────────────────────────────┐
         │     Arduino Uno R3         │
    ┌────┤1     ICSP        13┌───────┤
    │ ┌──┤2     USB-B       12├──────┐│
    │ │ ┌┤3     RX/TX       11├┐ PWM││
    │ │ ││                    10├┤   ││
    │ │ ││ Vin 5V GND        9├┤PWM││ GPIO 9 → Relè IN2
    │ │ │└────────────────────8┤GPIO ┼ GPIO 8 → Relè IN1
    └─┼─┼──────────────────────┤RESET │
      └─┼──────────────────────7┤GPIO │
        └──────────────────────6┤GPIO │
                    ┌───────────5┤PWM  │
                    │  ┌────────4┤GPIO │
                    │  │  ┌─────3┤PWM  │
                    │  │  │ ┌───2┤GPIO │
                    │  │  │ │    │1    │
                    │  │  │ │    │0    │
                    │  │  │ │  ┌─┴┬───┬┴──┐
                    │  │  │ │  │A0│A1 │A2 │ ADC
                    │  │  │ │  │(A3-A5)   │
                    │  │  │ │  └────────┬─┘
                    │  │  │ │ Sensori  └─ A0 Zona1
                    │  │  │ └─────────── A1 Zona2
                    │  │  └──────────────5V (Relè+Sensori)
                    │  └────────────────GND (Relè+Sensori)
```

**Relè 2 canali optoisolato pinout:**
```
┌─────────────────────────────┐
│ Relè 2 Canali SRD-05VDC    │
├─────────────────────────────┤
│  [1]  [2]  [3]  [4]  [5]   │ Connettori
│  GND  IN1  IN2  VCC  ─      │ Etichette
└──┬───┬────┬────┬───┬────────┘
   │   │    │    │   │
   ●   ●    ●    ●   │ (connettori a 5.08mm pitch)
   │   │    │    │
(Arduino GND) │    │    │
(GPIO 8)  ────┴──  │    │
(GPIO 9)  ─────────┴────│
(Arduino 5V) ─────────┬─┘

OUTPUT (altro lato):
┌──────────────────────────────┐
│  NC1  NO1  COM | NC2 NO2 COM │
└───┬───┬────┬────┼───┬───┬────┘
    │   │    │    │   │   │
    ●   ●    ●    ●   ●   ●
    │   │    │    │   │   │
        (NO1=Valvola1 attiva)
            (COM=Ritorno)
                    (NO2=Valvola2 attiva)
```

### C. Calibrazione Sensori Umidità (Procedura Completa)

```cpp
// PROCEDURA CALIBRAZIONE IN LOOP
// Esegui una volta, poi salva ADC_DRY e ADC_WET in #define

void calibrate() {
  Serial.println("=== CALIBRAZIONE SENSORE ===");
  Serial.println("1. Posiziona sensore in SUOLO ASCIUTTO (no acqua)");
  Serial.println("2. Premi 'S' seriale quando pronto...");
  
  while (Serial.read() != 'S') delay(100);
  delay(2000); // Attendi stabilizzazione
  
  int sum_dry = 0;
  for (int i = 0; i < 10; i++) {
    sum_dry += analogRead(A0);
    delay(200);
  }
  int ADC_DRY = sum_dry / 10;
  Serial.print("✓ Valore SECCO: "); Serial.println(ADC_DRY);
  
  Serial.println("3. IMMERGI sensore in ACQUA per 30 secondi");
  Serial.println("4. Premi 'S' quando immerso...");
  
  while (Serial.read() != 'S') delay(100);
  delay(1000);
  
  int sum_wet = 0;
  for (int i = 0; i < 10; i++) {
    sum_wet += analogRead(A0);
    delay(200);
  }
  int ADC_WET = sum_wet / 10;
  Serial.print("✓ Valore BAGNATO: "); Serial.println(ADC_WET);
  
  // SALVA NEL CODICE:
  // #define ADC_DRY ADC_DRY_VALUE_QUI
  // #define ADC_WET ADC_WET_VALUE_QUI
  Serial.println("RICOPIA IN #define PRINCIPALE:");
  Serial.print("#define ADC_DRY "); Serial.println(ADC_DRY);
  Serial.print("#define ADC_WET "); Serial.println(ADC_WET);
}
```

### D. Verifica Isolamento Trasformatore (Controllo Sicurezza)

```
Multimetro impostato su Ω×1000 (megaohm):
  
Tra primario (230V) e secondario (24V):
  ┌─────────────────┐
  │ L primario ←──┐ │
  │     +         │ │
  │ TRASF.        ├─┤ Dovrebbe leggere >1 MΩ
  │     +         │ │
  │ N primario ←──┤ │
  └────────┬──────┘
           │
        ┌─┴─┐
        │   │ OUT1 secondario
        │   │ OUT2 secondario
        └───┘
        
Se < 1 MΩ: ISOLAMENTO COMPROMESSO
→ NON USARE trasformatore
→ POTENZIALE RISCHIO FOLGORAZIONE
→ Acquista nuovo trasformatore
```

### E. Configurazione Rete WiFi (ESP32 avanzato)

```cpp
#include <WiFi.h>
#include <SPIFFS.h>

const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";
const char* hostname = "irrigazione-esp32";

void setup() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(hostname);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connesso!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi fallito, continua offline");
  }
}
```

---

## CONCLUSIONI E PROSSIMI PASSI

Questo documento fornisce **tutto il necessario** per:
1. ✅ Ordinare componenti reali, acquistabili
2. ✅ Montare e cablare in sicurezza
3. ✅ Testare passo-passo (niente assunzioni)
4. ✅ Migrare da Arduino Uno a ESP32
5. ✅ Estendere verso WiFi, logging, sensori aggiuntivi

**Per domande, consulta la sezione Troubleshooting o ripeti i Test Intermedi.**

---

*Versione 1.0 — Dicembre 2025*  
*Autore: Ingegnere Elettronico Senior + Maker Esperienza Impianti Irrigazione*
