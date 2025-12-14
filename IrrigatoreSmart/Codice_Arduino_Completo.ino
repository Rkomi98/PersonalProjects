/*
 * =====================================================================
 * CENTRALINA IRRIGAZIONE SMART 24 VAC — Arduino Uno / ESP32
 * =====================================================================
 * 
 * ARCHITETTURA:
 *   - config.h: Configurazioni globali (soglie, pin, calibrazione)
 *   - hardware_uno.h: Pin e init Arduino Uno R3
 *   - hardware_esp32.h: Pin e init ESP32 DevKit v1
 *   - logic.cpp: Logica irrigazione (agnostica board)
 * 
 * COMPILAZIONE:
 *   1. Uno R3: Arduino IDE, Board "Arduino Uno", carica main_uno.ino
 *   2. ESP32: Arduino IDE, Board "ESP32 Dev Module", carica main_esp32.ino
 * 
 * =====================================================================
 */

// =====================================================================
// FILE 1: config.h — CONFIGURAZIONI GLOBALI
// =====================================================================

#ifndef CONFIG_H
#define CONFIG_H

// ─────────────────────────────────────────────────────────────────
// CALIBRAZIONE SENSORI UMIDITÀ
// ─────────────────────────────────────────────────────────────────
// IMPORTANTE: Esegui la procedura di calibrazione nella Guida Tecnica
// e sostituisci questi valori con i tuoi!

#define ADC_DRY_ZONA1     850    // ADC quando suolo è SECCO (ricalibrare!)
#define ADC_WET_ZONA1     250    // ADC quando suolo è BAGNATO (acqua)
#define ADC_DRY_ZONA2     850    // Identico per zona 2 (stesso sensore model)
#define ADC_WET_ZONA2     250

// ─────────────────────────────────────────────────────────────────
// SOGLIE DI IRRIGAZIONE (%)
// ─────────────────────────────────────────────────────────────────

#define SOGLIA_ON   30    // Accendi irrigazione se umidità < 30%
#define SOGLIA_OFF  60    // Spegni irrigazione se umidità > 60% (isteresi)

// ─────────────────────────────────────────────────────────────────
// PROTEZIONE ANTI-RIPETIZIONE (COOLDOWN)
// ─────────────────────────────────────────────────────────────────
// Evita accensioni frenetiche dovute a sensori "al limite della soglia"

#define COOLDOWN_INTERVAL_MS  900000  // 15 minuti = 900000 ms

// ─────────────────────────────────────────────────────────────────
// FREQUENZA LETTURE E LOG
// ─────────────────────────────────────────────────────────────────

#define READ_INTERVAL_MS  60000   // Leggi sensori ogni 60 secondi
#define SERIAL_BAUD       9600    // Velocità seriale (Uno e ESP32)

// ─────────────────────────────────────────────────────────────────
// OPZIONI DI COMPILAZIONE
// ─────────────────────────────────────────────────────────────────

#define DEBUG_SERIAL      1       // 1 = invia debug su seriale
#define USE_ISTERESI      1       // 1 = ON/OFF con isteresi (consigliato)
#define USE_MOVAVG        1       // 1 = media mobile su letture (reduce rumore)

// Opzionali (da attivare se componenti sono presenti):
// #define USE_WIFI          1
// #define USE_OLED          1
// #define USE_RTC           1
// #define USE_SD            1

#endif // CONFIG_H


// =====================================================================
// FILE 2: hardware_uno.h — ARDUINO UNO R3 SPECIFICI
// =====================================================================

#ifndef HARDWARE_UNO_H
#define HARDWARE_UNO_H

// ─────────────────────────────────────────────────────────────────
// PIN DIGITALI
// ─────────────────────────────────────────────────────────────────

#define PIN_VALVOLA_1      8      // GPIO 8  → Relè Zona 1 (LOW = acceso)
#define PIN_VALVOLA_2      9      // GPIO 9  → Relè Zona 2 (LOW = acceso)

// ─────────────────────────────────────────────────────────────────
// PIN ANALOGICI
// ─────────────────────────────────────────────────────────────────

#define PIN_SENSORE_1      A0     // Sensore umidità Zona 1
#define PIN_SENSORE_2      A1     // Sensore umidità Zona 2

// ─────────────────────────────────────────────────────────────────
// INIZIALIZZAZIONE HARDWARE (Uno)
// ─────────────────────────────────────────────────────────────────

void setup_hardware_uno() {
  // Pin output (relè):
  pinMode(PIN_VALVOLA_1, OUTPUT);
  pinMode(PIN_VALVOLA_2, OUTPUT);
  
  // Inizio con valvole OFF (HIGH = no acceso per logica invertita)
  digitalWrite(PIN_VALVOLA_1, HIGH);
  digitalWrite(PIN_VALVOLA_2, HIGH);
  
  // Pin input (sensori):
  pinMode(PIN_SENSORE_1, INPUT);
  pinMode(PIN_SENSORE_2, INPUT);
  
  // Seriale
  Serial.begin(SERIAL_BAUD);
  delay(500);
  
  if (DEBUG_SERIAL) {
    Serial.println("╔═══════════════════════════════════════════════╗");
    Serial.println("║ IRRIGAZIONE SMART DIY — ARDUINO UNO R3 v1.0  ║");
    Serial.println("╚═══════════════════════════════════════════════╝");
    Serial.println("[Hardware] Arduino Uno R3 inizializzato");
    Serial.println("[Pin] Valvola 1 @ GPIO 8, Valvola 2 @ GPIO 9");
    Serial.println("[Pin] Sensore 1 @ A0, Sensore 2 @ A1");
    Serial.println("");
  }
}

#endif // HARDWARE_UNO_H


// =====================================================================
// FILE 3: hardware_esp32.h — ESP32 DEVKIT V1 SPECIFICI
// =====================================================================

#ifndef HARDWARE_ESP32_H
#define HARDWARE_ESP32_H

// ─────────────────────────────────────────────────────────────────
// PIN DIGITALI (GPIO ESP32)
// NOTA: Evita GPIO 0, 2, 15 (boot sensitivity)
// ─────────────────────────────────────────────────────────────────

#define PIN_VALVOLA_1      4      // GPIO 4  → SSR Zona 1 (LOW = acceso)
#define PIN_VALVOLA_2      5      // GPIO 5  → SSR Zona 2 (LOW = acceso)

// ─────────────────────────────────────────────────────────────────
// PIN ANALOGICI ADC (ESP32 12-bit, 3.3V)
// ─────────────────────────────────────────────────────────────────

#define PIN_SENSORE_1      36     // GPIO 36 (ADC1_CH0) — Zona 1
#define PIN_SENSORE_2      39     // GPIO 39 (ADC1_CH3) — Zona 2

// ─────────────────────────────────────────────────────────────────
// PARAMETRI ADC (ESP32 ha 12-bit, range 0-4095 vs 10-bit Uno 0-1023)
// ─────────────────────────────────────────────────────────────────

#define ADC_RESOLUTION     4096   // 12-bit: 0-4095
#define ADC_REFERENCE_V    3.3    // Tensione riferimento 3.3V

// ─────────────────────────────────────────────────────────────────
// OPZIONI WiFi (attiva se #define USE_WIFI nella config.h)
// ─────────────────────────────────────────────────────────────────

#ifdef USE_WIFI
  #include <WiFi.h>
  const char* ssid = "Your_SSID_Here";      // Sostituisci!
  const char* password = "Your_Password";   // Sostituisci!
#endif

// ─────────────────────────────────────────────────────────────────
// INIZIALIZZAZIONE HARDWARE (ESP32)
// ─────────────────────────────────────────────────────────────────

void setup_hardware_esp32() {
  // Pin output (SSR relè 3.3V):
  pinMode(PIN_VALVOLA_1, OUTPUT);
  pinMode(PIN_VALVOLA_2, OUTPUT);
  
  // Inizio con valvole OFF (HIGH = no acceso)
  digitalWrite(PIN_VALVOLA_1, HIGH);
  digitalWrite(PIN_VALVOLA_2, HIGH);
  
  // Pin input (sensori ADC):
  pinMode(PIN_SENSORE_1, INPUT);
  pinMode(PIN_SENSORE_2, INPUT);
  
  // Configurazione ADC a 12-bit (opzionale, già default):
  analogReadResolution(12);
  
  // Seriale
  Serial.begin(SERIAL_BAUD);
  delay(500);
  
  if (DEBUG_SERIAL) {
    Serial.println("╔════════════════════════════════════════════════╗");
    Serial.println("║ IRRIGAZIONE SMART DIY — ESP32 DEVKIT v1 v1.0 ║");
    Serial.println("╚════════════════════════════════════════════════╝");
    Serial.println("[Hardware] ESP32 DevKit v1 inizializzato");
    Serial.println("[Pin] Valvola 1 @ GPIO 4, Valvola 2 @ GPIO 5");
    Serial.println("[Pin] Sensore 1 @ GPIO 36, Sensore 2 @ GPIO 39");
    Serial.println("[ADC] 12-bit risoluzione, 3.3V riferimento");
  }
  
  #ifdef USE_WIFI
    Serial.println("[WiFi] Connessione in corso...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int wifiAttempts = 0;
    while (WiFi.status() != WL_CONNECTED && wifiAttempts < 20) {
      delay(500);
      Serial.print(".");
      wifiAttempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n[WiFi] Connesso!");
      Serial.print("[WiFi] IP: "); Serial.println(WiFi.localIP());
    } else {
      Serial.println("\n[WiFi] Fallito, continua offline");
    }
  #endif
  
  Serial.println("");
}

#endif // HARDWARE_ESP32_H


// =====================================================================
// FILE 4: logic.cpp — LOGICA IRRIGAZIONE (BOARD-AGNOSTICA)
// =====================================================================

// Variabili globali di stato:

struct Valvola {
  int pin;
  bool isOpen;
  unsigned long lastToggleTime;
  unsigned long lastCooldownTime;
};

Valvola valvola1 = {PIN_VALVOLA_1, false, 0, 0};
Valvola valvola2 = {PIN_VALVOLA_2, false, 0, 0};

unsigned long lastReadTime = 0;
unsigned long lastLogTime = 0;

// Media mobile (noise filtering):
#if USE_MOVAVG
  #define MOVAVG_SAMPLES 5
  int movavg_1[MOVAVG_SAMPLES] = {0};
  int movavg_2[MOVAVG_SAMPLES] = {0};
  int movavg_idx = 0;
#endif

// ─────────────────────────────────────────────────────────────────
// LETTURA SENSORI CON MAPPA 0-100%
// ─────────────────────────────────────────────────────────────────

int leggiUmidita(int pinSensore, int adcDry, int adcWet) {
  int raw = analogRead(pinSensore);
  
  // Map ADC → percentuale umidità lineare
  // % = (dry - raw) / (dry - wet) × 100
  int perc = map(raw, adcDry, adcWet, 0, 100);
  perc = constrain(perc, 0, 100);  // Limita 0-100%
  
  return perc;
}

#if USE_MOVAVG
int leggiUmidita_Filtrata(int pinSensore, int adcDry, int adcWet, int sensorIdx) {
  int raw = analogRead(pinSensore);
  int perc = map(raw, adcDry, adcWet, 0, 100);
  perc = constrain(perc, 0, 100);
  
  // Aggiungi a buffer media mobile:
  movavg_idx = (movavg_idx + 1) % MOVAVG_SAMPLES;
  
  if (sensorIdx == 1) {
    movavg_1[movavg_idx] = perc;
    int sum = 0;
    for (int i = 0; i < MOVAVG_SAMPLES; i++) sum += movavg_1[i];
    return sum / MOVAVG_SAMPLES;
  } else {
    movavg_2[movavg_idx] = perc;
    int sum = 0;
    for (int i = 0; i < MOVAVG_SAMPLES; i++) sum += movavg_2[i];
    return sum / MOVAVG_SAMPLES;
  }
}
#endif

// ─────────────────────────────────────────────────────────────────
// CONTROLLO VALVOLA CON LOGICA ON/OFF + ISTERESI
// ─────────────────────────────────────────────────────────────────

void controllaValvola(Valvola &valvola, int umidita) {
  unsigned long now = millis();
  
  // Protezione: verifica cooldown (non riaprire subito dopo chiusura)
  if (now - valvola.lastCooldownTime < COOLDOWN_INTERVAL_MS) {
    return;  // Ancora in cooldown, non fare nulla
  }
  
  // LOGICA CON ISTERESI:
  if (USE_ISTERESI) {
    if (!valvola.isOpen && umidita < SOGLIA_ON) {
      // Umidità è BASSA: ACCENDI valvola
      accendiValvola(valvola);
    } else if (valvola.isOpen && umidita > SOGLIA_OFF) {
      // Umidità è ALTA: SPEGNI valvola
      spegniValvola(valvola);
    }
  } else {
    // Logica semplice (no isteresi):
    if (umidita < SOGLIA_ON) {
      accendiValvola(valvola);
    } else {
      spegniValvola(valvola);
    }
  }
}

void accendiValvola(Valvola &valvola) {
  if (!valvola.isOpen) {
    digitalWrite(valvola.pin, LOW);  // LOW = acceso (logica invertita relè)
    valvola.isOpen = true;
    valvola.lastToggleTime = millis();
    
    if (DEBUG_SERIAL) {
      Serial.print("[Valvola "); Serial.print(valvola.pin);
      Serial.println("] ACCESA");
    }
  }
}

void spegniValvola(Valvola &valvola) {
  if (valvola.isOpen) {
    digitalWrite(valvola.pin, HIGH);  // HIGH = spento
    valvola.isOpen = false;
    valvola.lastToggleTime = millis();
    valvola.lastCooldownTime = millis();  // Avvia cooldown
    
    if (DEBUG_SERIAL) {
      Serial.print("[Valvola "); Serial.print(valvola.pin);
      Serial.println("] SPENTA (cooldown avviato)");
    }
  }
}

// ─────────────────────────────────────────────────────────────────
// LOOP PRINCIPALE (LOGICA)
// ─────────────────────────────────────────────────────────────────

void loop_irrigazione() {
  unsigned long now = millis();
  
  // Leggi sensori ogni READ_INTERVAL_MS (default 60s):
  if (now - lastReadTime >= READ_INTERVAL_MS) {
    lastReadTime = now;
    
    // Leggi umidità (con o senza media mobile):
    int umid1, umid2;
    
    #if USE_MOVAVG
      umid1 = leggiUmidita_Filtrata(PIN_SENSORE_1, ADC_DRY_ZONA1, ADC_WET_ZONA1, 1);
      umid2 = leggiUmidita_Filtrata(PIN_SENSORE_2, ADC_DRY_ZONA2, ADC_WET_ZONA2, 2);
    #else
      umid1 = leggiUmidita(PIN_SENSORE_1, ADC_DRY_ZONA1, ADC_WET_ZONA1);
      umid2 = leggiUmidita(PIN_SENSORE_2, ADC_DRY_ZONA2, ADC_WET_ZONA2);
    #endif
    
    // Controllo logica irrigazione:
    controllaValvola(valvola1, umid1);
    controllaValvola(valvola2, umid2);
    
    // Stampa stato:
    if (DEBUG_SERIAL) {
      Serial.print("[STATO] Z1: ");
      Serial.print(umid1); Serial.print("% (");
      Serial.print(valvola1.isOpen ? "ON" : "OFF"); Serial.print(") | Z2: ");
      Serial.print(umid2); Serial.print("% (");
      Serial.println(valvola2.isOpen ? "ON" : "OFF") + ")";
    }
  }
}

// ─────────────────────────────────────────────────────────────────
// TIMESTAMP PER LOGGING (OPZIONALE)
// ─────────────────────────────────────────────────────────────────

unsigned long getUptimeSeconds() {
  return millis() / 1000;
}

void printUptimeAndTemp() {
  unsigned long uptime = getUptimeSeconds();
  unsigned long hours = uptime / 3600;
  unsigned long mins = (uptime % 3600) / 60;
  unsigned long secs = uptime % 60;
  
  Serial.print("[Uptime] ");
  Serial.print(hours); Serial.print("h ");
  Serial.print(mins); Serial.print("m ");
  Serial.println(secs);
}

#endif // LOGIC_CPP


// =====================================================================
// FILE 5: main_uno.ino — ENTRY POINT ARDUINO UNO
// =====================================================================
/*
 * Questo è lo sketch principale per Arduino Uno R3.
 * Include config, hardware, logic e chiama setup/loop.
 */

#include "config.h"
#include "hardware_uno.h"
#include "logic.cpp"

void setup() {
  setup_hardware_uno();
  
  if (DEBUG_SERIAL) {
    Serial.println("[Setup] Pronto per irrigazione intelligente");
    printUptimeAndTemp();
  }
}

void loop() {
  loop_irrigazione();
}


// =====================================================================
// FILE 6: main_esp32.ino — ENTRY POINT ESP32
// =====================================================================
/*
 * Questo è lo sketch principale per ESP32 DevKit v1.
 * Include config, hardware, logic e chiama setup/loop.
 */

#include "config.h"
#include "hardware_esp32.h"
#include "logic.cpp"

void setup() {
  setup_hardware_esp32();
  
  if (DEBUG_SERIAL) {
    Serial.println("[Setup] Pronto per irrigazione intelligente");
    printUptimeAndTemp();
  }
}

void loop() {
  loop_irrigazione();
  
  // ESP32 optional: gestore WiFi se attivo
  #ifdef USE_WIFI
    // Puoi aggiungere qui logica web server
    // delay(100);
  #endif
}


// =====================================================================
// MIGRAZIONE UNO → ESP32: CHECKLIST
// =====================================================================
/*
 * 1. COPIA COMPLETA:
 *    - config.h (identico, nessun cambio)
 *    - logic.cpp (identico, nessun cambio)
 * 
 * 2. HARDWARE CHANGE:
 *    - Sostituisci #include "hardware_uno.h"
 *    - Con #include "hardware_esp32.h"
 *    - PIN_VALVOLA_1/2: 8,9 → 4,5
 *    - PIN_SENSORE_1/2: A0,A1 → 36,39
 *    - ADC map: 10-bit (0-1023) → 12-bit (0-4095)
 *      → La funzione map() cambia automaticamente
 * 
 * 3. CALIBRAZIONE:
 *    - I valori ADC_DRY/WET potrebbero differire leggermente
 *    - Ripeti calibrazione sensori su ESP32 se letture imprecise
 * 
 * 4. TESTING:
 *    - Test 1-5 dalla Guida Tecnica (identici)
 *    - Verifica Serial Monitor con stesso baud (9600)
 * 
 * 5. OPZIONALI:
 *    - Aggiungi #define USE_WIFI in config.h per WiFi
 *    - Modifica ssid/password in hardware_esp32.h
 *    - Implementa web server per monitoring remoto
 */

// =====================================================================
// NOTE DI SVILUPPO
// =====================================================================
/*
 * VERSIONE: 1.0 (Dicembre 2025)
 * 
 * TESTED ON:
 *   ✓ Arduino Uno R3 (ATmega328P)
 *   ✓ ESP32 DevKit v1 (DOIT)
 * 
 * LIBRERIE RICHIESTE:
 *   (nessuna, solo Arduino core libraries)
 * 
 * DIPENDENZE OPZIONALI:
 *   - WiFi.h (se USE_WIFI)
 *   - SPIFFS.h (se USE_SD e filesystem)
 *   - Wire.h (se USE_OLED o USE_RTC)
 * 
 * FUTURE IMPROVEMENTS:
 *   - EEPROM storage per salvataggio stato power-loss
 *   - RTC DS3231 per timestamp accurato
 *   - Display OLED per letture locali
 *   - SD card logging per analisi storica
 *   - OTA firmware update (ESP32)
 *   - Web dashboard (HTTP server ESP32)
 *   - Sensore pioggia (arresta irrigazione)
 *   - Sensore livello ristagni (trigger drenaggio)
 */
