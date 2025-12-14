# ✅ CHECKLIST FINALE DI VERIFICA — Progetto Irrigazione DIY

---

## 📋 FASE PRE-ORDINE

### Verifica Componenti (Leggi BOM_Base.xlsx prima!)

- [ ] **Arduino Uno R3**: Prezzo €20-25 (Amazon.it o AliExpress)
  - [ ] Verifica: "Originale" vs "Compatibile" (entrambi OK per DIY)
  - [ ] Board: ATmega328P 16MHz 32kB Flash
  
- [ ] **ESP32 DevKit v1** (acquista in Fase 4, non ora)
  - [ ] Verifica: "DOIT" (modello standard, 30 pin)
  - [ ] Non confondere con ESP8266 o altro (sbagliato!)
  
- [ ] **Relè 2 canali optoisolato 5V** (SRD-05VDC-SL-C o equivalente)
  - [ ] Verifica: 5V coil, 10A 250VAC contatti
  - [ ] Isolamento ottico (elemento critico per sicurezza!)
  
- [ ] **Trasformatore 24VAC preassemblato 40VA**
  - [ ] Verifica: 230V input, 24V output, 40VA
  - [ ] Certificazione: CE, IEC 60950, doppio isolamento (Classe II)
  - [ ] Nota: se 50VA disponibile = preferibile (margine maggiore)
  
- [ ] **2x Sensori umidità capacitivi**
  - [ ] Modello: DFRobot v1.2 o SEN0193 (non resistivi!)
  - [ ] Verifica: ADC 10-bit, 3.3-5V, scala 0-100%
  
- [ ] **Box IP65 200×300×150mm**
  - [ ] Verifica: IP65 (polvere+getti), guarnizione neoprene
  - [ ] Pressacavi M20 inclusi (min. 2, meglio 4-5)
  
- [ ] **Fusibili + Portafusibili DIN**
  - [ ] 20A T250V primario (protezione 230V)
  - [ ] 5A T250V secondario (protezione 24VAC)
  - [ ] Portafusibili DIN rail compatible
  
- [ ] **RCD 30mA 2×25A** (OPZIONALE ma consigliato)
  - [ ] Verifica: Type AC (non A), 30mA, IEC 61008
  - [ ] Per uso giardino umido = VIVAMENTE consigliato
  
- [ ] **Deviatore manuale 2-vie 250VAC 16A**
  - [ ] Permette switch "Hunter ↔ Arduino"
  - [ ] Tipo IEC 60669-1 (standard)
  - [ ] Verifica: isolamento stabile (no usura contatti)
  
- [ ] **Cavi e Cablaggio**
  - [ ] Cavo 1.5mm² per primario 230V (~5m, rotolo 50m)
  - [ ] Cavo 0.75mm² per secondario 24VAC (~30m, rotolo 100m)
  - [ ] Tubo isolante: giallo (230V), grigio (24VAC), schermato (sensori)
  - [ ] Morsetti a vite 2-poli 24VAC (min. 4 pezzi)
  - [ ] Morsetti a vite 3-poli 230V (min. 2 pezzi)
  
- [ ] **Connettori e Montaggio**
  - [ ] Pressacavi M20 IP67 (min. 3-4, confezione 5)
  - [ ] Guarnizioni silicone ricambio
  - [ ] Guida DIN 35mm (~40cm necessari, rotolo 2m)
  - [ ] Etichette adesive vinile (cavi, morsetti)
  - [ ] Nastro isolante PVC (20m rotolo)

### Budget Totale Stima

- **Fase 1 (Uno + test)**: €32-40
- **Fase 2 (sensori)**: €10-15
- **Fase 3 (trasformatore + protezioni)**: €60-80
- **Fase 4 (migrazione ESP32, opzionale)**: €15-25
- **Opzionali (OLED, RTC, Logging)**: €15-35

**TOTALE MINIMO (Uno): €100-150**  
**TOTALE COMPLETO (ESP32 + optional): €180-220**

---

## 📦 FASE ACQUISTO

- [ ] Ordina in lotti (non tutto insieme per risparmiare spedizione)
  - Lotto 1: Arduino Uno + Relè + Alimentatore 5V (3-5 giorni)
  - Lotto 2: Trasformatore + Fusibili + Box IP65 (5-7 giorni)
  - Lotto 3: Sensori + Cavi (dipende da fornitore)
  
- [ ] Verifica compatibilità Amazon.it vs AliExpress
  - [ ] Amazon: consegna veloce (2-3 giorni Prime), prezzo +20-30%
  - [ ] AliExpress: prezzo basso, ma 15-30 giorni di attesa
  
- [ ] IMPORTANTE: non ordinare Uno se lo hai già!
  - [ ] Inventario: controlla Arduino in garage/cassetti

---

## 🔧 FASE PRE-MONTAGGIO

### Preparazione Postazione di Lavoro

- [ ] Area di lavoro asciutta e ben illuminata (niente umidità!)
- [ ] Tavolo ampio con **tappeto antistatico** (protezione Arduino ESD)
- [ ] Multimetro digitale a batteria (per test senza contatti pericolosi)
- [ ] Attrezzi:
  - [ ] Cacciavite a croce (piccolo, per morsetti)
  - [ ] Cacciavite piatto (taglio cavi guaina)
  - [ ] Forbici per cavi
  - [ ] Pinza spelacavi 0.75–1.5mm²
  - [ ] Pinza crimpatrice (opzionale, se usi Wago push-fit)
  - [ ] Chiave dinamometrica ~2 N⋅m (per pressacavi)
  
- [ ] **Verifiche componenti da fare al ricevimento:**
  - [ ] Arduino Uno: LED rosso acceso quando alimentato? (OK)
  - [ ] Relè: bottone di test meccanico? (click udibile)
  - [ ] Trasformatore: peso ≥ 800g? (controllo qualità)
  - [ ] Box IP65: guarnizioni integre senza crepe?
  - [ ] Sensori: tre fili integri senza cortocircuiti? (multimetro)

---

## 🏗️ FASE MONTAGGIO

### Step 1: Preparazione Box IP65

- [ ] **Pulizia interna**: panno umido asciutto → asciuga completamente
- [ ] **Montaggio DIN rail**: allineamento orizzontale perfetto (livella)
- [ ] **Ispezione guarnizioni**: neoprene integro, no secchezza?
- [ ] **Montaggio staffa Arduino**: fissaggio stabile (vibrazione test)

### Step 2: Montaggio Componenti DIN Rail (IN ORDINE)

1. [ ] **Portafusibile primario 20A**
   - Posizione: sinistra, dopo ingresso trasformatore
   - Azione: inserisci fusibile 20A T250V, test scatto meccanico
   
2. [ ] **RCD 30mA** (se presente)
   - Posizione: centro-sinistra
   - Azione: test button → dovrebbe scattare e tornare
   
3. [ ] **Trasformatore 40VA**
   - Posizione: centro-destra DIN rail
   - Azione: verifica fissaggio, no vibrazioni con mano
   - Test: continutà bobina primaria ~100-500Ω (multimetro Ω)
   
4. [ ] **Portafusibile secondario 5A**
   - Posizione: destra trasformatore
   - Azione: inserisci fusibile 5A T250V

### Step 3: Collegamento Cavi Primario 230V

**⚠️ DOPPIA VERIFICAZIONE SICUREZZA**

- [ ] Spegni completamente (scollega presa di corrente dalla parete)
- [ ] **Multimetro**: verifica 0V tra qualunque morsetto di input
  - Se legge tensione: NON PROCEDERE, presa ancora live!
  
- [ ] Cavo rosso (FASE) presa → morsetto 1 portafusibile
- [ ] Cavo blu (NEUTRO) presa → morsetto N portafusibile
- [ ] Terra giallo/verde (opzionale se classe II): → morsetto PE box
  
- [ ] Uscita portafusibile → Ingresso RCD L (o diretto trasformatore se no RCD)
- [ ] Neutro presa → Ingresso RCD N (o diretto trasformatore)

**Verifica finale primario (spina ancora disconnessa):**
- [ ] Test continuità fusibile con multimetro: ~0Ω (no resistenza)
- [ ] Test isolamento primario-secondario: >1 MΩ (multimetro Ω×1000)

### Step 4: Collegamento Secondario 24VAC

- [ ] OUT1 trasformatore (L 24VAC) → Morsetto L relè
- [ ] OUT2 trasformatore (N 24VAC) → Morsetto N relè
- [ ] Fusibile 5A secondario: inserito in portafusibile
- [ ] Test continuità secondario con multimetro: 5-10Ω (OK)

### Step 5: Collegamento Relè a Valvole

- [ ] Relè 1 [NO] → Valvola Zona 1 ingresso [L/hot]
- [ ] Relè 2 [NO] → Valvola Zona 2 ingresso [L/hot]
- [ ] Relè 1 [COM] + Relè 2 [COM] → Entrambe valvole [N/return]
  - Nota: COM deve essere unico punto ritorno, no diramazioni multiple!

### Step 6: Collegamento Arduino + Sensori

- [ ] Arduino **GND** → Relè GND (comune con trasformatore)
- [ ] Arduino **5V** → Relè VCC + Sensori VCC
- [ ] Arduino **GPIO 8** → Relè IN1
- [ ] Arduino **GPIO 9** → Relè IN2
- [ ] Arduino **A0** → Sensore Zona 1 OUT
- [ ] Arduino **A1** → Sensore Zona 2 OUT
- [ ] Arduino **Alimentazione**: USB 5V/2A esterno (o USB-C computer test)

### Step 7: Installazione Pressacavi M20 IP67

- [ ] Prova a secco (no aperto): inserisci in foro box (dovrebbe resistere)
- [ ] Aggiungi guarnizione silicone extra (doppio sigillo)
- [ ] Serrata leggera con chiave dinamometrica ~2 N⋅m
  - Nota: non forzare! Rischio danno guarnizioni.

---

## ⚡ FASE TEST PRIMA ALIMENTAZIONE

### Test 1: Isolamento 230V (NO power, multimetro solo)

- [ ] Tra L-N presa: ~230V AC (normale, spina collegata)
- [ ] Tra 230V L e 24VAC L (trasformatore output): >1 MΩ
  - Se <1 MΩ: STOP! Trasformatore difettoso, non usare!
- [ ] Tra 230V L e chassis box (terra): >1 MΩ
- [ ] Tra 230V N e 24VAC L: >1 MΩ (doppio isolamento ok)

### Test 2: Continuità e Cortocircuiti

- [ ] Primario L → portafusibile → uscita: ~0Ω
- [ ] Primario N → portafusibile → uscita: ~0Ω
- [ ] Secondario L ↔ N (acceso, in vuoto): 5-10Ω (trasformatore OK)
- [ ] Tra 230V L ↔ 230V N (multimetro): ∞Ω (no cortocircuito primario)

### Test 3: Accensione RCD (se presente)

- [ ] Collega spina 230V
- [ ] Premi pulsante **TEST** RCD: dovrebbe scattare (interruttore OFF)
- [ ] Premi **RESET**: alimentazione ritorna (interruttore ON)
- [ ] Se non scatta: RCD difettoso, sostituisci e ripeti

### Test 4: Tensione Secondaria (senza carichi)

- [ ] Accendi RCD (interruttore ON)
- [ ] Multimetro AC tra OUT trasformatore:
  - [ ] Dovrebbe leggere **24V ± 1V** (tolleranza ±5%)
  - [ ] Se 0V: verifica fusibile 20A intatto
  - [ ] Se <22V: possibile trasformatore sovraccarico (collaudo con relè)

### Test 5: Arduino Uno Caricamento Sketch

- [ ] Collega Arduino Uno a computer via USB
- [ ] Arduino IDE: seleziona Board "Arduino Uno", Port "COM X"
- [ ] Carica sketch test semplice:
  ```cpp
  void setup() {
    pinMode(8, OUTPUT);
    Serial.begin(9600);
  }
  void loop() {
    digitalWrite(8, LOW);
    Serial.println("LOW");
    delay(1000);
    digitalWrite(8, HIGH);
    Serial.println("HIGH");
    delay(1000);
  }
  ```
- [ ] Apri Serial Monitor (9600 baud)
- [ ] Verifica: messaggio "LOW" e "HIGH" alternato
- [ ] Ascolta GPIO 8: dovrebbe avere "click" meccanico (relè)
- [ ] Se no click: verificare continuità cavo GPIO 8 → Relè IN1

### Test 6: Lettura Sensori (no valvole ancora)

- [ ] Carica sketch sensori:
  ```cpp
  void setup() { Serial.begin(9600); }
  void loop() {
    Serial.print(analogRead(A0)); Serial.print(" ");
    Serial.println(analogRead(A1));
    delay(500);
  }
  ```
- [ ] Apri Serial Monitor
- [ ] Letture devono essere:
  - [ ] Sensore secco (aria): 800-900 ADC
  - [ ] Sensore bagnato (acqua): 200-300 ADC
  - [ ] Se invertito o fuori range: verificare calibrazione o sensore difettoso

### Test 7: Ciclo Completo (Uno + Trasformatore + Valvola)

- [ ] Carica sketch completo da "Codice_Arduino_Completo.ino"
- [ ] Accendi spina 230V
- [ ] Serial Monitor: dovrebbe mostrare stato umidità + stato valvola
- [ ] Asciuga sensore → ADC basso → relè attiva valvola (click)
- [ ] Bagna sensore → ADC alto → relè spegne valvola (click)
- [ ] Multimetro AC su morsetti valvola: alternare 24V e 0V ✓

---

## 🔀 FASE MIGRAZIONE UNO → ESP32 (FASE 4)

### Pre-Migrazione Checklist

- [ ] Uno funzionante e testato completamente
- [ ] Arduino IDE: installa supporto ESP32 (Board Manager)
  - Arduino IDE → Preferences → Additional Boards URLs
  - Aggiungi: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
  
- [ ] Compra ESP32 DevKit v1 (DOIT, 30-pin)

### Procedura Migrazione Codice

- [ ] **Coppo file identici**:
  - [ ] config.h: identico (nessun cambio)
  - [ ] logic.cpp: identico (nessun cambio)
  
- [ ] **Modifica hardware**:
  - [ ] Sostituisci `#include "hardware_uno.h"`
  - [ ] Con `#include "hardware_esp32.h"`
  - [ ] Verifica pin ESP32: GPIO 4, 5 (relè), GPIO 36, 39 (sensori)
  
- [ ] **Ricompilazione**:
  - [ ] Arduino IDE: Board "ESP32 Dev Module"
  - [ ] Port: COM della ESP32
  - [ ] Upload speed: 115200
  - [ ] Verifica compilazione OK (no errori)
  
- [ ] **Caricamento e test**:
  - [ ] Carica sketch
  - [ ] Serial Monitor: verificati log startup ESP32
  - [ ] Ripeti Test 1-5 precedenti (identici proceduralmente)
  - [ ] Calibrazione sensori: potrebbe differire leggermente

### Post-Migrazione (Opzionale)

- [ ] Aggiungi WiFi:
  - [ ] Attiva `#define USE_WIFI` in config.h
  - [ ] Modifica ssid/password in hardware_esp32.h
  
- [ ] Aggiungi Display OLED (I2C):
  - [ ] Connetti SDA → GPIO 21, SCL → GPIO 22 (standard ESP32)
  - [ ] Attiva `#define USE_OLED` e implementa libreria Adafruit
  
- [ ] Logging SD (opzionale):
  - [ ] Modulo microSD reader SPI: CS→GPIO 5, MOSI→GPIO 23, etc.
  - [ ] Attiva `#define USE_SD` e libreria SD.h

---

## 🌱 FASE COLLAUDO FINALE

### Test Completo Campo (Sistema Live)

- [ ] Deviatore su "Arduino" (non Hunter!)
- [ ] Accendi 230V
- [ ] Osserva comportamento zona 1:
  - [ ] Sensore secco → Valvola 1 accesa (irrigazione attiva)
  - [ ] Sensore bagnato → Valvola 1 spenta (riposo)
  - [ ] Transizioni: verificare cooldown (no accensioni frenetiche)
  
- [ ] Osserva zona 2: stesso comportamento
  
- [ ] Test fallback:
  - [ ] Spegni 230V
  - [ ] Deviatore su "Hunter"
  - [ ] Accendi 230V
  - [ ] Verifica Hunter ancora funzionante (timer test)

### Calibrazione Soglie Umidità (1-2 settimane)

- [ ] Osserva pattern naturale giardino
- [ ] Regola SOGLIA_ON/OFF se necessario:
  - [ ] Se valvole si accendono troppo spesso: aumenta SOGLIA_ON (es: 35%)
  - [ ] Se piante soffrono secchezza: diminuisci SOGLIA_ON (es: 25%)
  - [ ] Isteresi (SOGLIA_OFF - SOGLIA_ON) ideale: 20-30%
  
- [ ] Annota comportamento in foglio (data, ora, umidità, stato)

### Test Sensore Pioggia (Opzionale, Fase 5+)

- [ ] Installazione sensore pioggia: sotto gronda principale
- [ ] Logica: se piove → arresta irrigazione per 2-3 ore
- [ ] Verifica con nebulizzatore (simulate rain)

---

## 🐛 TROUBLESHOOTING RAPIDO

### Arduino non carica sketch

```
Soluzione:
  1. Verifica Port e Board corretti (Arduino IDE)
  2. Prova porta USB diversa (o altro cavo)
  3. Se ancora no: Arduino difettoso, prova su altro PC
```

### Relè non scatta (no click)

```
Soluzione:
  1. Misura 5V tra VCC e GND relè (alimentazione OK?)
  2. Misura GPIO 8/9 con multimetro: alterna 0V-5V?
  3. Se GPIO fisso: software issue o pin danneggiato
  4. Se GPIO OK ma relè immobile: relè guasto, sostituisci
```

### Sensori leggono male (sempre 1023 o sempre 0)

```
Soluzione:
  1. Verifica cavi A0/A1: continuità con multimetro
  2. Disconnetti sensore, misura ADC (dovrebbe 0 o 1023)
  3. Se stabile: problema sensore o calibrazione
  4. Ricalibrare: ripeti procedura calibrazione con ADC_DRY/WET nuovi
```

### Valvole si accendono ma acqua non esce

```
Soluzione:
  1. Multimetro AC su morsetti valvola: leggi 24V?
  2. Se no 24V: relè difettoso o cavi scollati
  3. Se 24V OK: valvola bloccata meccanicamente
     → Spegni, smonta valvola, pulisci sedile e sfera
     → Test con pressione d'aria compressa (max 1 bar!)
```

---

## ✅ FIRMA FINALE DI COMPLETAMENTO

Una volta completati TUTTI i test e funzionante nel vostro giardino:

```
Data inizio progetto: ___/___/______
Data completamento: ___/___/______

Arduino (Uno/ESP32): ________________ (modello)
Sensore Zona 1 ADC_DRY: _____ ADC_WET: _____
Sensore Zona 2 ADC_DRY: _____ ADC_WET: _____

Soglia ON: _____% Soglia OFF: _____%

Irriga automaticamente: ☐ SÌ ☐ NO

Eventuali problemi residui:
_________________________________________
_________________________________________

Firma: ________________ Data: __________
```

---

**CONGRATULAZIONI! 🎉 Sistema operativo e monitored.**

Per future espansioni o debugging, consultare sempre:
1. Guida Tecnica (troubleshooting section)
2. Codice Arduino (commenti dettagliati)
3. BOM (componenti equivalenti e alternative)
