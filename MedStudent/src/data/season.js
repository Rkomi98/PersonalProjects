export const season = {
  title: "Stagione Decisiva - Gastroenterologia",
  protagonist: {
    name: "Camilla",
    age: 25,
    profile: [
      "Studentessa di medicina (gastroenterologia)",
      "Giocatrice di pallavolo di buon livello",
      "Allenatrice Under femminile",
      "Determinata, abituata a leadership e pressione",
      "Ama la birra IPA"
    ]
  },
  stats: {
    knowledge: { label: "Conoscenza Gastro", initial: 42, min: 0, max: 100 },
    determination: { label: "Determinazione", initial: 74, min: 0, max: 100 },
    leadership: { label: "Leadership", initial: 68, min: 0, max: 100 },
    balance: { label: "Equilibrio Fisico", initial: 61, min: 0, max: 100 },
    morale: { label: "Morale", initial: 57, min: 0, max: 100 }
  },
  chapters: [
    {
      id: "ch1",
      title: "Capitolo 1 - Le Feci Nere Non Aspettano",
      status: "playable",
      objective: "Allineare ragionamento clinico, priorita acute e red flags da esame.",
      sourcePages: [2, 25, 34, 49, 15, 48],
      scenes: [
        {
          id: "ch1_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Ore 06:40. Palestra semi-vuota, scarpe che stridono sul parquet. Camilla chiude l'ultimo esercizio con le Under, si cambia al volo e parte per il reparto: oggi la partita vera e doppia, corsia ed esame.",
          examHook: "Focus: problem solving clinico in 4 mosse (diagnosi, monitoraggio, terapia, educazione).",
          sourceKey: "problem_solving_framework"
        },
        {
          id: "ch1_s2",
          type: "choice",
          prompt: "Fine allenamento. Camilla ha ancora un'ora di studio: come gestisce energia e concentrazione?",
          options: [
            {
              text: "Una IPA veloce e poi dritta sui quiz.",
              effects: { morale: 6, balance: -5 },
              tags: ["ipa_taken"],
              feedback:
                "Morale su, ma recupero piu fragile. In dispensa l'alcol e tra i trigger da evitare nei sintomi da reflusso.",
              transitionLine: "Si sente piu leggera mentalmente, ma la fatica resta sotto pelle."
            },
            {
              text: "Niente IPA: acqua, doccia e power-nap.",
              effects: { balance: 8, determination: 3 },
              feedback:
                "Scelta pulita: arrivi al caso clinico con piu lucidita e tenuta.",
              transitionLine: "Rientra in reparto con testa piu chiara e ritmo piu stabile."
            },
            {
              text: "Video-analisi con le Under e poi studio.",
              effects: { leadership: 7, determination: 4, balance: -2 },
              feedback: "Leadership alta, ma il margine fisico si accorcia.",
              transitionLine: "La squadra cresce. Camilla pure, ma con un po di benzina in meno."
            }
          ],
          sourceKey: "reflux_lifestyle"
        },
        {
          id: "ch1_s3",
          type: "quiz_mcq",
          prompt:
            "Mini-simulazione. Donna 58 anni: dolore epigastrico, sazieta precoce, -6 kg in 6 mesi, Hb 9 g/dL, feci picee occasionali. Quale elemento NON e red flag che da solo giustifica EGDS nel contesto?",
          options: [
            { text: "Eta >45 nel contesto clinico", correct: false, why: "Nel caso clinico rafforza l'indicazione all'approfondimento.", transitionLine: "Correzione segnata: meglio sbagliare qui che all'orale." },
            { text: "Anemia", correct: false, why: "Anemia e segnale d'allarme.", transitionLine: "Camilla rilegge i red flags e riallinea la griglia mentale." },
            {
              text: "Stipsi",
              correct: true,
              why: "Esatto. Nel quiz in dispensa la stipsi non e il sintomo d'allarme che da solo porta a EGDS del tratto superiore.",
              transitionLine: "Punto preso: ora il ragionamento e piu netto."
            },
            { text: "Calo ponderale non intenzionale", correct: false, why: "E red flag.", transitionLine: "Errore utile: adesso la gerarchia dei segnali e piu chiara." },
            { text: "Melena", correct: false, why: "Orienta a possibile sanguinamento GI superiore.", transitionLine: "Segna il razionale: melena non si sottovaluta." }
          ],
          onCorrect: { knowledge: 10, determination: 4 },
          onWrong: { knowledge: 3 },
          sourceKey: "problem_solving_framework",
          teacherAsk: "Quali red flags anticipano EGDS nel tratto superiore?"
        },
        {
          id: "ch1_s4",
          type: "quiz_clinical",
          prompt: "Paziente con melena osservata, ipoteso e tachicardico. Qual e la prima mossa?",
          options: [
            {
              text: "Accessi venosi robusti + fluidi; poi vie aeree/ossigenazione se necessario.",
              correct: true,
              why: "Corretto: la priorita iniziale e stabilizzare.",
              transitionLine: "Scelta da corsia vera: prima sicurezza, poi diagnosi etiologica."
            },
            {
              text: "EGDS immediata prima di qualunque stabilizzazione.",
              correct: false,
              why: "EGDS e cruciale, ma non prima della stabilizzazione iniziale.",
              transitionLine: "Camilla segna: mai saltare ABC per rincorrere l'esame strumentale."
            },
            {
              text: "Aspettare solo gli esami ematici.",
              correct: false,
              why: "Ritarda una fase tempo-dipendente.",
              transitionLine: "Errore corretto subito: in urgenza il tempo clinico pesa tantissimo."
            }
          ],
          onCorrect: { knowledge: 9, leadership: 5 },
          onWrong: { knowledge: 2, determination: 2 },
          sourceKey: "melena_first_steps",
          extraSourceKey: "upper_bleeding_timing",
          teacherAsk: "Come giustifichi timing EGDS vs stabilizzazione?"
        },
        {
          id: "ch1_s5",
          type: "quiz_reasoning",
          prompt: "Diarrea oltre 6 settimane: quale dato orienta verso fenotipo infiammatorio?",
          options: [
            {
              text: "Sangue e muco nelle feci con calprotectina elevata.",
              correct: true,
              why: "E il pattern tipico descritto per diarrea infiammatoria.",
              transitionLine: "Ragionamento pulito: sintomo, marker, ipotesi."
            },
            { text: "Diarrea solo post-latticini senza marker infiammatori.", correct: false, why: "Non orienta in prima battuta a forma infiammatoria.", transitionLine: "Corretto in recupero: ora distingue meglio i fenotipi." },
            { text: "Nessun sangue, alvo notturno regolare, niente calo ponderale.", correct: false, why: "Quadro poco coerente con infiammazione intestinale attiva.", transitionLine: "Errore utile: adesso i criteri sono piu ancorati." }
          ],
          onCorrect: { knowledge: 8, determination: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "inflammatory_diarrhea_workup",
          teacherAsk: "Dopo sospetto di diarrea infiammatoria, quali step imposti?"
        },
        {
          id: "ch1_s6",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Bel set. Hai tenuto insieme urgenza e ragionamento. Ora difendi il sistema: sonno, carico fisico, continuita. Se vai in riserva fuori reparto, cedi anche all'orale.'",
          examHook: "Fine capitolo: niente game over, solo recupero strutturato.",
          sourceKey: "problem_solving_framework"
        }
      ]
    },
    {
      id: "ch2",
      title: "Capitolo 2 - Dolore Addominale e Disfagia",
      status: "playable",
      objective: "Distinguere pattern clinici, segnali d'allarme e prima indagine.",
      sourcePages: [5, 7, 8, 49],
      scenes: [
        {
          id: "ch2_s1",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "In ambulatorio arriva una paziente con dolore alto addominale e difficolta a deglutire. Camilla apre il quaderno: niente intuito puro, solo struttura.",
          examHook: "Prima regola: classificare i sintomi GI in modo ordinato.",
          sourceKey: "gi_symptoms_core"
        },
        {
          id: "ch2_s2",
          type: "choice",
          prompt: "Prima domanda di Camilla in anamnesi sulla disfagia:",
          options: [
            {
              text: "Chiedo se fa fatica a iniziare la deglutizione o se sente il cibo bloccarsi nel torace.",
              effects: { knowledge: 7, leadership: 3 },
              feedback: "Ottimo: separi subito disfagia alta da disfagia esofagea.",
              transitionLine: "Il colloquio si fa preciso: la paziente inizia a descrivere meglio il sintomo."
            },
            {
              text: "Chiedo solo da quanti anni ha il sintomo, senza dettaglio funzionale.",
              effects: { knowledge: 2 },
              feedback: "Dato utile ma incompleto: ti manca la distinzione chiave.",
              transitionLine: "Camilla sente che manca un pezzo e torna a fare domande mirate."
            },
            {
              text: "Passo subito alla terapia empirica senza chiarire il tipo di disfagia.",
              effects: { knowledge: -1, determination: 1 },
              feedback: "Scelta debole: prima va definito il problema.",
              transitionLine: "Stop tecnico: prima classificare, poi trattare."
            }
          ],
          sourceKey: "dysphagia_definition"
        },
        {
          id: "ch2_s3",
          type: "quiz_mcq",
          prompt: "Quale descrizione corrisponde alla disfagia alta (orofaringea)?",
          options: [
            { text: "Sensazione di cibo fermo in torace dopo deglutizione.", correct: false, why: "Questo quadro orienta verso disfagia esofagea." },
            {
              text: "Difficolta ad avviare l'atto della deglutizione.",
              correct: true,
              why: "Corretto: e la definizione operativa di disfagia alta in dispensa."
            },
            { text: "Pirosi isolata senza disturbo del passaggio del bolo.", correct: false, why: "Non definisce disfagia alta." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "dysphagia_definition",
          teacherAsk: "Come distingui disfagia alta e bassa gia al letto del paziente?"
        },
        {
          id: "ch2_s4",
          type: "quiz_clinical",
          prompt: "Disfagia progressiva + calo ponderale non intenzionale: qual e la prima indagine?",
          options: [
            {
              text: "EGDS come prima indagine.",
              correct: true,
              why: "Corretto: in presenza di sintomi d'allarme l'EGDS e la prima scelta.",
              transitionLine: "Camilla chiude il cerchio: allarme clinico, indagine giusta, timing corretto."
            },
            {
              text: "Solo dieta empirica per alcune settimane.",
              correct: false,
              why: "Con allarmi non e la priorita.",
              transitionLine: "Segna l'errore: i sintomi d'allarme non si rinviano."
            },
            {
              text: "Nessuna indagine finche non compare anemia.",
              correct: false,
              why: "Approccio non adeguato in presenza di allarmi gia presenti.",
              transitionLine: "Camilla ricalibra: allarme gia adesso, non dopo."
            }
          ],
          onCorrect: { knowledge: 9, leadership: 4 },
          onWrong: { knowledge: 2 },
          sourceKey: "dysphagia_alarm_egds",
          teacherAsk: "Quando consideri la disfagia un red flag endoscopico?"
        },
        {
          id: "ch2_s5",
          type: "quiz_reasoning",
          prompt: "Nel dolore epigastrico, quale gruppo diagnostico e esplicitamente citato in dispensa?",
          options: [
            {
              text: "Ulcera peptica e patologia biliare.",
              correct: true,
              why: "Corretto: compare tra le diagnosi differenziali del distretto epigastrico."
            },
            { text: "Solo patologia neurologica centrale.", correct: false, why: "Non e il cluster indicato per epigastrio." },
            { text: "Solo cause dermatologiche.", correct: false, why: "Non coerente con la sezione dolore addominale." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "abdominal_pain_epigastrium",
          teacherAsk: "Come costruisci la differenziale iniziale di un dolore epigastrico?"
        },
        {
          id: "ch2_s6",
          type: "narrative",
          speaker: "Contadino",
          text:
            "'Quando uno dice \"non mi scende\", devi capire dove si ferma: gola o torace. Se sbagli qui, sbagli tutto dopo.'",
          examHook: "Fine capitolo: classificazione sintomo prima di terapia.",
          sourceKey: "dysphagia_definition"
        }
      ]
    },
    {
      id: "ch3",
      title: "Capitolo 3 - Diarrea, Stipsi, Incontinenza",
      status: "playable",
      objective: "Classificare correttamente alvo e orientare l'iter diagnostico.",
      sourcePages: [13, 14, 15, 17],
      scenes: [
        {
          id: "ch3_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "In guardia breve arrivano tre storie diverse: diarrea cronica, stipsi ostinata, incontinenza. Camilla deve separare i percorsi senza confonderli.",
          examHook: "Il docente premia chi classifica bene prima di prescrivere.",
          sourceKey: "gi_symptoms_core"
        },
        {
          id: "ch3_s2",
          type: "choice",
          prompt: "Davanti a un alvo alterato, Camilla da dove parte?",
          options: [
            {
              text: "Durata, consistenza con Bristol, segni associati (sangue/muco/caloprotectina).",
              effects: { knowledge: 8, leadership: 3 },
              feedback: "Ottimo set iniziale: definisci subito fenotipo e gravita.",
              transitionLine: "Le informazioni iniziano a incastrarsi senza rumore."
            },
            {
              text: "Solo numero delle scariche, senza caratteristiche fecali.",
              effects: { knowledge: 2 },
              feedback: "Dato incompleto: manca la parte qualitativa.",
              transitionLine: "Camilla si accorge che i dati sono ancora troppo grezzi."
            },
            {
              text: "Parto direttamente con antibiotico empirico.",
              effects: { knowledge: -1, determination: 1 },
              feedback: "Approccio non centrato senza classificazione iniziale.",
              transitionLine: "Stop e reset: prima capire il tipo di diarrea."
            }
          ],
          sourceKey: "diarrhea_definition"
        },
        {
          id: "ch3_s3",
          type: "quiz_mcq",
          prompt: "Quali tipi Bristol sono associati alla diarrea nella dispensa?",
          options: [
            { text: "Tipi 1-2", correct: false, why: "Questi sono associati a stipsi." },
            { text: "Tipi 3-4", correct: false, why: "Sono considerati alvo normale." },
            { text: "Tipi 5-7", correct: true, why: "Corretto: la dispensa associa diarrea ai tipi 5, 6 e 7." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "bristol_scale",
          teacherAsk: "Come usi Bristol per orientare la prima distinzione clinica?"
        },
        {
          id: "ch3_s4",
          type: "quiz_clinical",
          prompt: "Diarrea cronica con sangue/muco e calprotectina elevata: prossimo passo?",
          options: [
            {
              text: "Sospetto forma infiammatoria e avvio valutazione con colonscopia + biopsia.",
              correct: true,
              why: "Corretto: e il percorso indicato in dispensa.",
              transitionLine: "Camilla passa da sintomo a percorso diagnostico senza perdere tempo."
            },
            {
              text: "Tratto come IBS senza indagini.",
              correct: false,
              why: "Con marker infiammatori elevati non e coerente.",
              transitionLine: "Correzione secca: IBS non si etichetta con infiammazione attiva."
            },
            {
              text: "Aspetto tre mesi prima di rivalutare.",
              correct: false,
              why: "Rinvio non adeguato nel sospetto infiammatorio.",
              transitionLine: "Camilla ricalibra il timing: qui non si puo attendere passivamente."
            }
          ],
          onCorrect: { knowledge: 9, leadership: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "inflammatory_diarrhea_workup",
          teacherAsk: "Quali marker fecali usi per sospettare diarrea infiammatoria?"
        },
        {
          id: "ch3_s5",
          type: "quiz_reasoning",
          prompt: "Quale elemento e coerente con la definizione di stipsi cronica in dispensa?",
          options: [
            {
              text: "Defecazione non soddisfacente con feci spesso Bristol 1-2.",
              correct: true,
              why: "Corretto: e il nucleo definitorio riportato.",
              transitionLine: "Punto tecnico preso: definizione fissata."
            },
            { text: "Solo alvo tipo 6-7.", correct: false, why: "Questo orienta alla diarrea." },
            { text: "Solo dolore addominale senza alterazioni dell'alvo.", correct: false, why: "Non basta per definire stipsi cronica." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "constipation_definition",
          teacherAsk: "Come distingui stipsi funzionale da cause secondarie?"
        },
        {
          id: "ch3_s6",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Non confondere etichette. Se definisci male l'alvo, ti si inceppa tutta la catena: esami, terapia, follow-up.'",
          examHook: "Fine capitolo: definizione corretta prima del trattamento.",
          sourceKey: "bristol_scale"
        }
      ]
    },
    {
      id: "ch4",
      title: "Capitolo 4 - Emorragie GI Superiori e Inferiori",
      status: "playable",
      objective: "Gestire urgenza, localizzazione probabile e timing endoscopico.",
      sourcePages: [25, 34],
      scenes: [
        {
          id: "ch4_s1",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "Chiamata rapida dal PS: paziente pallido, tachicardico, riferita melena. Camilla entra in modalita protocollo.",
          examHook: "ABC e priorita immediate prima della causa definitiva.",
          sourceKey: "melena_first_steps"
        },
        {
          id: "ch4_s2",
          type: "choice",
          prompt: "Quale report SBAR fa Camilla al tutor?",
          options: [
            {
              text: "S: melena e ipotensione; B: farmaci/comorbidita; A: segni deplezione; R: accessi robusti, fluidi, EGDS.",
              effects: { leadership: 7, knowledge: 4 },
              feedback: "Comunicazione precisa e utile all'azione.",
              transitionLine: "Il team si muove coordinato: nessun passaggio perso."
            },
            {
              text: "Il paziente non sta bene, vediamo poi.",
              effects: { leadership: -1, determination: 1 },
              feedback: "Troppo vago per un'urgenza.",
              transitionLine: "Camilla sente il caos e torna subito a uno schema rigoroso."
            },
            {
              text: "Aspettiamo solo i risultati e poi decidiamo.",
              effects: { knowledge: -1 },
              feedback: "Inadeguato in una fase tempo-dipendente.",
              transitionLine: "Reset: in urgenza servono dati e decisioni parallele."
            }
          ],
          sourceKey: "problem_solving_framework"
        },
        {
          id: "ch4_s3",
          type: "quiz_mcq",
          prompt: "Quale elemento orienta di meno a sanguinamento GI superiore?",
          options: [
            { text: "Melena", correct: false, why: "Melena orienta a tratto superiore." },
            { text: "Rapporto BUN/creatinina elevato", correct: false, why: "E un elemento orientativo per tratto superiore." },
            {
              text: "Coaguli ematici nelle feci",
              correct: true,
              why: "Corretto: in dispensa orientano piu verso tratto inferiore."
            }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "upper_bleeding_clots_lower_hint",
          extraSourceKey: "upper_bleeding_predictors",
          teacherAsk: "Quali indizi clinici usi per ipotizzare la sede del sanguinamento?"
        },
        {
          id: "ch4_s4",
          type: "quiz_clinical",
          prompt: "Melena confermata e instabilita emodinamica: prima azione corretta?",
          options: [
            {
              text: "Accessi venosi robusti e fluid challenge, poi percorso endoscopico.",
              correct: true,
              why: "Corretto: la stabilizzazione iniziale e prioritaria.",
              transitionLine: "Camilla resta fredda: prima sostegno circolo, poi eziologia."
            },
            { text: "Solo terapia antiacida orale e osservazione.", correct: false, why: "Insufficiente in quadro instabile." },
            { text: "Rinvio di tutte le decisioni all'indomani.", correct: false, why: "Timing non adeguato in urgenza." }
          ],
          onCorrect: { knowledge: 9, leadership: 4 },
          onWrong: { knowledge: 2 },
          sourceKey: "melena_first_steps",
          teacherAsk: "Come imposti le priorita immediate in una melena instabile?"
        },
        {
          id: "ch4_s5",
          type: "quiz_reasoning",
          prompt: "Nel sospetto di emorragia digestiva superiore, quale affermazione e corretta?",
          options: [
            {
              text: "EGDS entro 24h, con stabilizzazione iniziale se necessario.",
              correct: true,
              why: "E il principio operativo riportato in dispensa."
            },
            { text: "EGDS sempre dopo 7 giorni.", correct: false, why: "Timing non coerente con urgenza." },
            { text: "EGDS solo se Hb > 12.", correct: false, why: "Affermazione non coerente con l'iter riportato." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "upper_bleeding_timing",
          teacherAsk: "Come motivi il timing endoscopico in base alla stabilita emodinamica?"
        },
        {
          id: "ch4_s6",
          type: "narrative",
          speaker: "Contadino",
          text:
            "'Quando vedi nero nelle feci, non andare a intuito: tieni su il paziente e poi vai a cercare il buco.'",
          examHook: "Fine capitolo: urgenza = priorita corrette + timing.",
          sourceKey: "upper_bleeding_timing"
        }
      ]
    },
    {
      id: "ch5",
      title: "Capitolo 5 - Endoscopia: EGDS, Pancolonscopia, VCE",
      status: "playable",
      objective: "Scegliere l'esame giusto al momento giusto.",
      sourcePages: [31, 37, 39, 49],
      scenes: [
        {
          id: "ch5_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Nel corridoio endoscopia, Camilla deve scegliere tra EGDS, pancolonscopia e videocapsula senza farsi distrarre dal rumore del reparto.",
          examHook: "Domanda classica d'esame: indicazione corretta della metodica.",
          sourceKey: "egds_indications"
        },
        {
          id: "ch5_s2",
          type: "choice",
          prompt: "Sanguinamento persistente, EGDS e pancolonscopia negative. Cosa propone Camilla?",
          options: [
            {
              text: "Videocapsula endoscopica per sospetto fonte nel tenue.",
              effects: { knowledge: 8, leadership: 3 },
              feedback: "Scelta corretta nel contesto descritto.",
              transitionLine: "Il percorso diagnostico torna lineare: ora guardi dove prima non vedevi."
            },
            {
              text: "Ripetere sempre e solo EGDS senza altro razionale.",
              effects: { knowledge: 1 },
              feedback: "Possibile solo in contesti specifici, qui non e la scelta piu coerente.",
              transitionLine: "Camilla rilegge indicazioni e amplia il campo al tenue."
            },
            {
              text: "Nessuna indagine ulteriore.",
              effects: { knowledge: -1 },
              feedback: "Scelta debole: quadro ancora aperto.",
              transitionLine: "Stop: il caso non e risolto, serve una metodica coerente."
            }
          ],
          sourceKey: "capsule_endoscopy_role"
        },
        {
          id: "ch5_s3",
          type: "quiz_mcq",
          prompt: "Quale tra questi e un classico sintomo d'allarme che orienta a EGDS come prima indagine?",
          options: [
            {
              text: "Disfagia",
              correct: true,
              why: "Corretto: e tra i red flags riportati per indicazione a EGDS."
            },
            { text: "Alvo regolare senza altri sintomi", correct: false, why: "Da solo non rappresenta allarme per EGDS." },
            { text: "Nessun sintomo ma ansia del paziente", correct: false, why: "Non e indicazione clinica in se." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "egds_indications",
          teacherAsk: "Quando l'EGDS e la prima scelta non rinviabile?"
        },
        {
          id: "ch5_s4",
          type: "quiz_clinical",
          prompt: "Alvo modificato di recente con sintomi d'allarme: esame di riferimento?",
          options: [
            {
              text: "Pancolonscopia con adeguata preparazione.",
              correct: true,
              why: "Corretto secondo indicazioni riportate.",
              transitionLine: "Scelta netta: il percorso diagnostico ha un binario chiaro."
            },
            { text: "Solo test domiciliare non invasivo e stop", correct: false, why: "In questo contesto non basta." },
            { text: "Nessuna indagine per 6 mesi", correct: false, why: "Ritardo non appropriato con sintomi d'allarme." }
          ],
          onCorrect: { knowledge: 9, leadership: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "colonoscopy_indication_alarm",
          teacherAsk: "Come motivi indicazione e priorita della pancolonscopia?"
        },
        {
          id: "ch5_s5",
          type: "quiz_reasoning",
          prompt: "Quale affermazione descrive correttamente la videocapsula nel testo?",
          options: [
            {
              text: "E soprattutto diagnostica e non consente manovre operative.",
              correct: true,
              why: "Corretto: e riportato esplicitamente in dispensa."
            },
            { text: "Sostituisce sempre EGDS e colonscopia", correct: false, why: "Non e questo il ruolo indicato." },
            { text: "Serve solo in patologie gastriche", correct: false, why: "Non e il focus descritto." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "capsule_endoscopy_role",
          teacherAsk: "Limiti e vantaggi della videocapsula nel sanguinamento occulto?"
        },
        {
          id: "ch5_s6",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "'Esame giusto, paziente giusto, timing giusto. E qui che passi da studentessa preparata a clinica affidabile.'",
          examHook: "Fine capitolo: indicazione corretta della metodica.",
          sourceKey: "capsule_endoscopy_role"
        }
      ]
    },
    {
      id: "ch6",
      title: "Capitolo 6 - Esofago: MRGE, Esofagiti, Barrett",
      status: "playable",
      objective: "Collegare sintomi tipici, allarmi, test funzionali e complicanze.",
      sourcePages: [45, 48, 49, 36],
      scenes: [
        {
          id: "ch6_s1",
          type: "narrative",
          speaker: "Contadino",
          text:
            "'Bruciore, rigurgito, tosse notturna... sembrano uguali ma non lo sono. Se ascolti bene, capisci chi ha reflusso vero e chi no.'",
          examHook: "Distinguere sintomi tipici, atipici e red flags.",
          sourceKey: "reflux_symptoms_and_egds"
        },
        {
          id: "ch6_s2",
          type: "choice",
          prompt: "Camilla imposta il counseling iniziale sulla MRGE:",
          options: [
            {
              text: "Riduzione trigger (incluso alcol) + misure posturali e stile di vita.",
              effects: { knowledge: 6, leadership: 3 },
              feedback: "Approccio coerente con le raccomandazioni in dispensa.",
              transitionLine: "La paziente capisce cosa puo cambiare gia da oggi."
            },
            {
              text: "Solo farmaco, zero indicazioni comportamentali.",
              effects: { knowledge: 1 },
              feedback: "Incompleto rispetto al testo.",
              transitionLine: "Camilla integra subito la parte comportamentale."
            },
            {
              text: "Nessuna modifica e controllo tra un anno.",
              effects: { knowledge: -1 },
              feedback: "Non adeguato.",
              transitionLine: "Reset rapido: la gestione deve partire subito in modo strutturato."
            }
          ],
          sourceKey: "reflux_lifestyle"
        },
        {
          id: "ch6_s3",
          type: "quiz_mcq",
          prompt: "Qual e il sintomo tipico piu caratteristico della MRGE in dispensa?",
          options: [
            {
              text: "Pirosi",
              correct: true,
              why: "Corretto: e indicata come sintomo tipico piu caratteristico."
            },
            { text: "Ittero", correct: false, why: "Non appartiene al core sintomatologico di MRGE." },
            { text: "Ematuria", correct: false, why: "Non pertinente al quadro esofageo descritto." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "reflux_symptoms_and_egds",
          teacherAsk: "Che differenza fai tra sintomi tipici e atipici di MRGE?"
        },
        {
          id: "ch6_s4",
          type: "quiz_clinical",
          prompt: "Paziente con pirosi cronica che sviluppa disfagia: cosa fai?",
          options: [
            {
              text: "Richiedo EGDS per sintomo d'allarme.",
              correct: true,
              why: "Corretto: disfagia in questo contesto e un allarme.",
              transitionLine: "Camilla cambia marcia: da gestione empirica a valutazione strutturale."
            },
            { text: "Continuo solo terapia empirica per mesi", correct: false, why: "Con allarme non e sufficiente." },
            { text: "Nessuna rivalutazione", correct: false, why: "Non appropriato in progressione sintomatica." }
          ],
          onCorrect: { knowledge: 9, leadership: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "egds_indications",
          teacherAsk: "Quando il caso passa da terapia empirica a endoscopia?"
        },
        {
          id: "ch6_s5",
          type: "quiz_reasoning",
          prompt: "Per documentare il reflusso in casi complessi, quale test e gold standard nel testo?",
          options: [
            {
              text: "pH-metria/pH-impedenzometria esofagea.",
              correct: true,
              why: "Corretto: e riportato esplicitamente.",
              transitionLine: "Camilla passa dal sintomo al dato fisiopatologico misurabile."
            },
            { text: "Solo radiografia torace", correct: false, why: "Non e indicata come gold standard per reflusso." },
            { text: "Solo ecografia addome", correct: false, why: "Non e il test funzionale di riferimento." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "ph_impedance_gold_standard",
          teacherAsk: "Quando scegli pH-metria rispetto a EGDS?"
        },
        {
          id: "ch6_s6",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Il reflusso cronico non e solo fastidio: puo aprire la strada a complicanze come il Barrett. Niente sottovalutazioni.'",
          examHook: "Fine capitolo: sintomi + allarmi + complicanze.",
          sourceKey: "barrett_complication"
        }
      ]
    },
    {
      id: "ch7",
      title: "Capitolo 7 - Stomaco, Ulcera, H. pylori, Neoplasie",
      status: "playable",
      objective: "Riconoscere pattern ulcerosi e impostare percorso H. pylori.",
      sourcePages: [69, 75],
      scenes: [
        {
          id: "ch7_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Camilla entra nel modulo stomaco: epigastralgia, sanguinamento, H. pylori, rischio neoplastico. Qui serve ordine mentale netto.",
          examHook: "Dolore ulceroso e complicanze sono domande frequenti all'orale.",
          sourceKey: "peptic_ulcer_patterns"
        },
        {
          id: "ch7_s2",
          type: "choice",
          prompt: "Prima mossa davanti a dolore epigastrico ricorrente:",
          options: [
            {
              text: "Anamnesi mirata su timing col pasto, FANS e storia ulcerosa/sanguinamento.",
              effects: { knowledge: 7, leadership: 2 },
              feedback: "Approccio clinico solido.",
              transitionLine: "La storia clinica inizia a spiegare il pattern del dolore."
            },
            {
              text: "Solo antiacido senza anamnesi dettagliata.",
              effects: { knowledge: 1 },
              feedback: "Scelta troppo corta per un caso da esame.",
              transitionLine: "Camilla fa un passo indietro e ricostruisce la storia con precisione."
            },
            {
              text: "Ignoro il rapporto col pasto.",
              effects: { knowledge: -1 },
              feedback: "Perdi una chiave differenziale importante.",
              transitionLine: "Errore tecnico: il timing con il pasto va sempre cercato."
            }
          ],
          sourceKey: "peptic_ulcer_patterns"
        },
        {
          id: "ch7_s3",
          type: "quiz_mcq",
          prompt: "Quale pattern e coerente con ulcera duodenale nel testo?",
          options: [
            { text: "Dolore subito post-prandiale", correct: false, why: "Questo e piu coerente con ulcera gastrica." },
            {
              text: "Dolore a digiuno/notturno, attenuato dal cibo.",
              correct: true,
              why: "Corretto: e la descrizione riportata per ulcera duodenale."
            },
            { text: "Solo dolore in quadrante inferiore destro", correct: false, why: "Non e il pattern classico ulceroso descritto." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "peptic_ulcer_patterns",
          teacherAsk: "Come distingui clinicamente ulcera gastrica e duodenale?"
        },
        {
          id: "ch7_s4",
          type: "quiz_clinical",
          prompt: "Ulcera peptica H. pylori positiva: asse terapeutico fondamentale?",
          options: [
            {
              text: "Eradicazione di H. pylori con schema di prima linea appropriato.",
              correct: true,
              why: "Corretto: la dispensa sottolinea l'eradicazione in tutti i soggetti diagnosticati.",
              transitionLine: "Camilla collega eziologia e terapia in modo preciso."
            },
            { text: "Solo analgesico al bisogno", correct: false, why: "Non affronta la causa infettiva." },
            { text: "Nessuna terapia se i sintomi calano", correct: false, why: "Non coerente con gestione indicata." }
          ],
          onCorrect: { knowledge: 9, leadership: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "hpylori_eradication",
          teacherAsk: "Qual e il razionale dell'eradicazione nell'ulcera H. pylori positiva?"
        },
        {
          id: "ch7_s5",
          type: "quiz_reasoning",
          prompt: "Quale coppia di test non invasivi per H. pylori e citata in dispensa?",
          options: [
            {
              text: "Urea breath test e ricerca antigeni fecali.",
              correct: true,
              why: "Corretto: entrambi sono esplicitamente citati."
            },
            { text: "Solo ecografia e emocromo", correct: false, why: "Non sono i test diagnostici non invasivi specifici riportati." },
            { text: "Solo pH-metria", correct: false, why: "Esame non finalizzato a diagnosi H. pylori." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "hpylori_diagnosis",
          teacherAsk: "Quando preferisci test non invasivi vs test invasivi per H. pylori?"
        },
        {
          id: "ch7_s6",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "'Ottimo. Hai letto il dolore come un segnale, non come un'etichetta. Adesso aggiungi il tema neoplasie gastriche nel ragionamento lungo.'",
          examHook: "Fine capitolo: ulcera e oncologia gastrica nello stesso percorso.",
          sourceKey: "gastric_neoplasia_topic"
        }
      ]
    },
    {
      id: "ch8",
      title: "Capitolo 8 - Malassorbimento: Celiachia e SIBO",
      status: "playable",
      objective: "Impostare iter corretto tra steatorrea, celiachia e sovracrescita batterica.",
      sourcePages: [15, 89, 98],
      scenes: [
        {
          id: "ch8_s1",
          type: "narrative",
          speaker: "Contadino",
          text:
            "'Se il cibo entra ma non nutre, devi pensare al malassorbimento. Non basta dire \"diarrea\": devi capire perche.'",
          examHook: "Steatorrea e nodi diagnostici principali.",
          sourceKey: "malabsorption_overview"
        },
        {
          id: "ch8_s2",
          type: "choice",
          prompt: "Diarrea cronica con steatorrea: prima traiettoria proposta da Camilla?",
          options: [
            {
              text: "Sierologia per celiachia; se positiva, EGDS con biopsia duodenale.",
              effects: { knowledge: 9, leadership: 2 },
              feedback: "Percorso coerente con l'iter riportato.",
              transitionLine: "Il caso prende forma: ipotesi chiara e passaggi ordinati."
            },
            {
              text: "Terapia casuale senza conferma diagnostica.",
              effects: { knowledge: 0 },
              feedback: "Non e il percorso didattico richiesto.",
              transitionLine: "Camilla torna al protocollo: prima conferma, poi terapia."
            },
            {
              text: "Ignoro la steatorrea e classifico come IBS.",
              effects: { knowledge: -1 },
              feedback: "Scelta non coerente con i dati.",
              transitionLine: "Errore corretto: steatorrea cambia la rotta diagnostica."
            }
          ],
          sourceKey: "celiac_workup_steatorrhea"
        },
        {
          id: "ch8_s3",
          type: "quiz_mcq",
          prompt: "Quale quadro e tipico della celiachia classica secondo dispensa?",
          options: [
            {
              text: "Diarrea, steatorrea e calo ponderale.",
              correct: true,
              why: "Corretto: e il pattern classico indicato."
            },
            { text: "Solo pirosi notturna isolata", correct: false, why: "Non e il fenotipo classico riportato." },
            { text: "Emottisi e dolore toracico", correct: false, why: "Non pertinente al quadro celiaco descritto." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "celiac_classic_features",
          teacherAsk: "Quali segnali clinici fanno pensare a celiachia classica?"
        },
        {
          id: "ch8_s4",
          type: "quiz_clinical",
          prompt: "Sospetto SIBO nel tenue: quale test e richiamato in dispensa?",
          options: [
            {
              text: "Breath test nel percorso diagnostico disponibile.",
              correct: true,
              why: "Corretto: i breath test sono citati nel workup SIBO.",
              transitionLine: "Camilla lega sintomo, fisiopatologia e test pratico."
            },
            { text: "Solo ECG", correct: false, why: "Non pertinente." },
            { text: "Solo pH-metria esofagea", correct: false, why: "Test di altro distretto." }
          ],
          onCorrect: { knowledge: 8, leadership: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "sibo_definition_diagnosis",
          teacherAsk: "Quando metti SIBO nella differenziale della diarrea cronica?"
        },
        {
          id: "ch8_s5",
          type: "quiz_reasoning",
          prompt: "Nel percorso diarrea cronica, quale combinazione orienta piu verso infiammazione che malassorbimento?",
          options: [
            {
              text: "Calprotectina alta con sangue/muco.",
              correct: true,
              why: "Corretto: e orientativa per fenotipo infiammatorio."
            },
            { text: "Steatorrea con sierologia celiachia positiva", correct: false, why: "Questo orienta piu al versante malassorbitivo." },
            { text: "Bristol 3-4 stabile", correct: false, why: "Non indica attivita infiammatoria." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "inflammatory_diarrhea_workup",
          extraSourceKey: "celiac_workup_steatorrhea",
          teacherAsk: "Come separi diarrea infiammatoria da malassorbitiva in prima battuta?"
        },
        {
          id: "ch8_s6",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Hai fatto bene: non tutto quello che e diarrea e uguale. Qui contano i dettagli, non la fretta.'",
          examHook: "Fine capitolo: fenotipo prima di etichetta.",
          sourceKey: "malabsorption_overview"
        }
      ]
    },
    {
      id: "ch9",
      title: "Capitolo 9 - IBD e IBS",
      status: "playable",
      objective: "Distinguere patologia infiammatoria cronica da disturbo funzionale.",
      sourcePages: [2, 117, 122, 125, 132],
      scenes: [
        {
          id: "ch9_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Turno ambulatoriale: due pazienti, sintomi simili, meccanismi diversi. Camilla deve evitare l'errore classico: chiamare IBS cio che e IBD.",
          examHook: "Diagnosi IBD: clinica + endoscopia + istologia.",
          sourceKey: "ibd_core"
        },
        {
          id: "ch9_s2",
          type: "choice",
          prompt: "Sospetto IBD: quale strada sceglie Camilla?",
          options: [
            {
              text: "Imposto valutazione con endoscopia e biopsie nel contesto clinico.",
              effects: { knowledge: 8, leadership: 3 },
              feedback: "Scelta centrata sul percorso diagnostico corretto.",
              transitionLine: "Il caso si chiarisce: dati oggettivi, non etichette frettolose."
            },
            {
              text: "Classifico subito come funzionale senza biopsie.",
              effects: { knowledge: -1 },
              feedback: "Approccio a rischio di sottodiagnosi.",
              transitionLine: "Camilla corregge: senza istologia qui non basta."
            },
            {
              text: "Rinvio ogni indagine per molti mesi.",
              effects: { determination: -1 },
              feedback: "Timing non adeguato con sospetto IBD.",
              transitionLine: "Reset: serve una valutazione completa in tempi utili."
            }
          ],
          sourceKey: "rcu_diagnosis_management"
        },
        {
          id: "ch9_s3",
          type: "quiz_mcq",
          prompt: "Quale affermazione e coerente con la dispensa su IBS?",
          options: [
            {
              text: "Nella forma funzionale non ci si aspetta calprotectina elevata.",
              correct: true,
              why: "Corretto: il testo sottolinea il carattere funzionale."
            },
            { text: "Calprotectina molto alta e tipica di IBS", correct: false, why: "Non coerente con quadro funzionale." },
            { text: "IBS richiede sempre terapia immunosoppressiva", correct: false, why: "Affermazione non coerente con il modulo IBS." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "calprotectin_ibd",
          teacherAsk: "Come usi la calprotectina nel distinguere IBD da IBS?"
        },
        {
          id: "ch9_s4",
          type: "quiz_clinical",
          prompt: "RCU: quale principio gestionale e esplicitamente citato in dispensa?",
          options: [
            {
              text: "Terapia modulata su estensione (proctite/proctocolite/pancolite) e severita.",
              correct: true,
              why: "Corretto: e riportato nel framework iniziale.",
              transitionLine: "Camilla ragiona per estensione di malattia, non per ricette fisse."
            },
            { text: "Stessa terapia identica per tutti i fenotipi", correct: false, why: "Non coerente con quanto riportato." },
            { text: "Nessun monitoraggio nel tempo", correct: false, why: "Il monitoraggio e parte del problem solving clinico." }
          ],
          onCorrect: { knowledge: 9, leadership: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "rcu_diagnosis_management",
          teacherAsk: "Come cambia la terapia nella RCU in base all'estensione?"
        },
        {
          id: "ch9_s5",
          type: "quiz_reasoning",
          prompt: "Nella classificazione IBS, quale sottotipo e associato a feci Bristol 6-7?",
          options: [
            {
              text: "IBS-D",
              correct: true,
              why: "Corretto: IBS-D corrisponde al fenotipo con diarrea prevalente."
            },
            { text: "IBS-C", correct: false, why: "E il sottotipo con stipsi." },
            { text: "IBS-M con prevalenza 1-2", correct: false, why: "Non corrisponde al dato richiesto." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "ibs_subtypes_bristol",
          teacherAsk: "Perche la scala di Bristol aiuta anche nel fenotipizzare IBS?"
        },
        {
          id: "ch9_s6",
          type: "narrative",
          speaker: "Contadino",
          text:
            "'Crohn e RCU fanno infiammazione vera. IBS no. Se confondi questi mondi, mandi fuori strada paziente e terapia.'",
          examHook: "Fine capitolo: IBD != IBS.",
          sourceKey: "ibd_core"
        }
      ]
    },
    {
      id: "ch10",
      title: "Capitolo 10 - Ischemia Intestinale e Diverticolosi",
      status: "playable",
      objective: "Riconoscere quadri vascolari e leggere correttamente l'anamnesi dell'alvo.",
      sourcePages: [18, 136],
      scenes: [
        {
          id: "ch10_s1",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "Cambio scenario: non solo infiammazione e funzionale. Qui entrano in gioco perfusione intestinale e complicanze del colon.",
          examHook: "Capitolo ad alta soglia clinica: non sottostimare dolore e contesto.",
          sourceKey: "ischemic_colitis_management"
        },
        {
          id: "ch10_s2",
          type: "choice",
          prompt: "Sospetto colite ischemica non complicata: come imposta la fase iniziale?",
          options: [
            {
              text: "Supporto medico con liquidi e riposo intestinale, poi rivalutazione strutturata.",
              effects: { knowledge: 8, leadership: 2 },
              feedback: "Scelta coerente con il principio gestionale riportato.",
              transitionLine: "Camilla tiene il paziente stabile e guadagna tempo clinico utile."
            },
            {
              text: "Nessun supporto, solo attesa.",
              effects: { knowledge: -1 },
              feedback: "Approccio non adeguato.",
              transitionLine: "Correzione immediata: nei quadri ischemici il supporto iniziale conta."
            },
            {
              text: "Trattamento casuale senza inquadramento.",
              effects: { knowledge: 0 },
              feedback: "Manca struttura decisionale.",
              transitionLine: "Camilla torna al protocollo e riordina le priorita."
            }
          ],
          sourceKey: "ischemic_colitis_management"
        },
        {
          id: "ch10_s3",
          type: "quiz_mcq",
          prompt: "Quale affermazione sulla colite ischemica e coerente con il testo?",
          options: [
            {
              text: "In molti casi la gestione e prevalentemente medica (liquidi + riposo intestinale).",
              correct: true,
              why: "Corretto: e il messaggio riportato in dispensa."
            },
            { text: "Richiede sempre chirurgia immediata", correct: false, why: "Affermazione assoluta non coerente." },
            { text: "Si gestisce solo con dieta senza supporto", correct: false, why: "Non rappresenta il principio riportato." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "ischemic_colitis_management",
          teacherAsk: "Quando il trattamento iniziale della colite ischemica e principalmente medico?"
        },
        {
          id: "ch10_s4",
          type: "quiz_clinical",
          prompt: "In anamnesi stipsi/diarrea alternate: quale ipotesi compare nella differenziale della dispensa?",
          options: [
            {
              text: "Diverticolosi del colon.",
              correct: true,
              why: "Corretto: e riportata come possibile associazione anamnestica.",
              transitionLine: "Dettaglio piccolo, ma decisivo: Camilla allinea anamnesi e differenziale."
            },
            { text: "Solo patologia esofagea", correct: false, why: "Non coerente col pattern dell'alvo." },
            { text: "Nessuna ipotesi utile", correct: false, why: "L'anamnesi qui orienta eccome." }
          ],
          onCorrect: { knowledge: 8, leadership: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "diverticulosis_alvo_alterno",
          teacherAsk: "Quali elementi anamnestici orientano verso diverticolosi?"
        },
        {
          id: "ch10_s5",
          type: "quiz_reasoning",
          prompt: "Qual e il principio corretto in questo capitolo?",
          options: [
            {
              text: "Dolore e alterazioni dell'alvo vanno letti nel contesto emodinamico e anamnestico, non isolati.",
              correct: true,
              why: "Corretto: il modulo insiste sul contesto clinico e sulla differenziale.",
              transitionLine: "Camilla consolida il metodo: contesto prima dell'etichetta."
            },
            { text: "Ignorare il contesto e usare un solo schema", correct: false, why: "Strategia a rischio errore." },
            { text: "Evitare sempre monitoraggio clinico", correct: false, why: "Non coerente con il problem solving richiesto." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "problem_solving_framework",
          teacherAsk: "Come integri anamnesi e stabilita clinica nella differenziale?"
        },
        {
          id: "ch10_s6",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Con l'intestino ischemico o fragile non devi essere brillante: devi essere affidabile. Metodo, monitoraggio, chiarezza.'",
          examHook: "Fine capitolo: contesto clinico prima della scorciatoia.",
          sourceKey: "ischemic_colitis_management"
        }
      ]
    },
    {
      id: "ch11",
      title: "Capitolo 11 - Pancreas e Vie Biliari",
      status: "playable",
      objective: "Riconoscere pancreatite acuta e quadri bilio-pancreatici urgenti.",
      sourcePages: [5, 141, 147, 154, 157],
      scenes: [
        {
          id: "ch11_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Notte di guardia. Dolore epigastrico intenso irradiato al dorso, nausea, laboratorio in arrivo. Camilla sa che qui i minuti pesano.",
          examHook: "Pancreatite e vie biliari: capitolo ad alta pressione.",
          sourceKey: "pancreatitis_diagnosis_criteria"
        },
        {
          id: "ch11_s2",
          type: "choice",
          prompt: "Quale set iniziale sceglie Camilla nel sospetto pancreatite acuta?",
          options: [
            {
              text: "Valuto quadro clinico + enzimi pancreatici e integro con imaging nel contesto.",
              effects: { knowledge: 8, leadership: 2 },
              feedback: "Approccio coerente con i criteri riportati.",
              transitionLine: "Il caso si stringe: i dati iniziano a puntare nella stessa direzione."
            },
            {
              text: "Mi baso solo sul dolore senza laboratorio.",
              effects: { knowledge: 1 },
              feedback: "Incompleto per la diagnosi.",
              transitionLine: "Camilla aggiunge subito il dato biochimico che mancava."
            },
            {
              text: "Mi baso solo su amilasi/lipasi senza contesto.",
              effects: { knowledge: 1 },
              feedback: "Anche questo e incompleto: serve integrazione clinica.",
              transitionLine: "Correzione utile: mai leggere un marker da solo."
            }
          ],
          sourceKey: "pancreatitis_diagnosis_criteria"
        },
        {
          id: "ch11_s3",
          type: "quiz_mcq",
          prompt: "Nel sospetto pancreatite acuta, quale dato laboratoristico e citato come criterio nel testo?",
          options: [
            {
              text: "Amilasi/lipasi oltre 3 volte il limite superiore.",
              correct: true,
              why: "Corretto: e riportato tra i criteri diagnostici."
            },
            { text: "Solo bilirubina isolata", correct: false, why: "Da sola non rappresenta il criterio pancreatico citato." },
            { text: "Solo VES normale", correct: false, why: "Non e criterio indicato qui." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "pancreatitis_diagnosis_criteria",
          teacherAsk: "Quali criteri combini per confermare pancreatite acuta?"
        },
        {
          id: "ch11_s4",
          type: "quiz_clinical",
          prompt: "Febbre + ittero + dolore addominale alto: a cosa devi pensare subito?",
          options: [
            {
              text: "Colangite acuta.",
              correct: true,
              why: "Corretto: triade clinica richiamata in dispensa.",
              transitionLine: "Camilla riconosce subito il pattern e accelera il percorso."
            },
            { text: "Solo dispepsia funzionale", correct: false, why: "Quadro non coerente con triade d'allarme." },
            { text: "Solo IBS", correct: false, why: "Non pertinente in questo contesto acuto." }
          ],
          onCorrect: { knowledge: 9, leadership: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "colangitis_triade",
          teacherAsk: "Quali triadi/segnali clinici usi nelle urgenze biliari?"
        },
        {
          id: "ch11_s5",
          type: "quiz_reasoning",
          prompt: "Quale segno e tipicamente associato a colecistite acuta nel testo?",
          options: [
            {
              text: "Segno di Murphy positivo.",
              correct: true,
              why: "Corretto: e riportato esplicitamente."
            },
            { text: "Segno di Lasegue", correct: false, why: "Non e un segno biliare." },
            { text: "Babinski", correct: false, why: "Segno neurologico, non biliare." }
          ],
          onCorrect: { knowledge: 7, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "colecistitis_murphy",
          teacherAsk: "Come distingui al letto del paziente colecistite e altri quadri addominali?"
        },
        {
          id: "ch11_s6",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "'Pancreas e bile sono una rete, non due capitoli separati. Se leggi i collegamenti, anticipi il rischio clinico.'",
          examHook: "Fine capitolo: integrazione bilio-pancreatica.",
          sourceKey: "biliary_anatomy_basics"
        }
      ]
    },
    {
      id: "ch12",
      title: "Capitolo 12 - Epatologia Integrata",
      status: "playable",
      objective:
        "Leggere pattern biochimici, criteri MAFLD/NAFLD e rischio evolutivo verso cirrosi/neoplasia.",
      sourcePages: [158, 161, 168, 167, 150],
      scenes: [
        {
          id: "ch12_s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Ultimo capitolo. Camilla e in aula studio, cuffie, appunti aperti: transaminasi, colestasi, MAFLD, cirrosi, HCC. Ultimo set, massimo focus.",
          examHook: "Qui il docente testa lettura integrata, non memoria isolata.",
          sourceKey: "liver_tests_true_lfts"
        },
        {
          id: "ch12_s2",
          type: "choice",
          prompt: "Arriva un pannello epatico alterato: come lo legge Camilla?",
          options: [
            {
              text: "Distingue pattern epatitico vs colestatico e valuta indici di funzione (albumina, INR, bilirubina).",
              effects: { knowledge: 9, leadership: 2 },
              feedback: "Approccio corretto e completo.",
              transitionLine: "I numeri smettono di essere una lista: diventano una storia clinica."
            },
            {
              text: "Guarda solo AST/ALT ignorando il resto.",
              effects: { knowledge: 1 },
              feedback: "Parziale: mancano pattern e funzione epatica.",
              transitionLine: "Camilla allarga il quadro e rientra nel metodo."
            },
            {
              text: "Interpreta tutto come colestasi senza confronto marker.",
              effects: { knowledge: -1 },
              feedback: "Rischio di errore interpretativo.",
              transitionLine: "Correzione immediata: prima pattern, poi etichetta."
            }
          ],
          sourceKey: "liver_tests_true_lfts"
        },
        {
          id: "ch12_s3",
          type: "quiz_mcq",
          prompt: "Quali sono i veri test di funzione epatica evidenziati nella dispensa?",
          options: [
            {
              text: "Albumina, INR, bilirubina.",
              correct: true,
              why: "Corretto: sono esplicitamente richiamati come veri LFTs."
            },
            { text: "Solo amilasi e lipasi", correct: false, why: "Marker pancreatici, non veri LFTs." },
            { text: "Solo calprotectina fecale", correct: false, why: "Marker intestinale, non epatico." }
          ],
          onCorrect: { knowledge: 8, determination: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "liver_tests_true_lfts",
          teacherAsk: "Che differenza fai tra marker di danno e marker di funzione epatica?"
        },
        {
          id: "ch12_s4",
          type: "quiz_clinical",
          prompt: "Quale pattern biochimico orienta alla colestasi nel testo?",
          options: [
            {
              text: "Incremento prevalente di fosfatasi alcalina e gamma-GT.",
              correct: true,
              why: "Corretto: e il pattern colestatico riportato.",
              transitionLine: "Camilla chiude il dubbio diagnostico con un pattern chiaro."
            },
            { text: "Solo riduzione sodio", correct: false, why: "Non definisce pattern colestatico." },
            { text: "Solo aumento amilasi", correct: false, why: "Non e il marker colestatico principale." }
          ],
          onCorrect: { knowledge: 9, leadership: 2 },
          onWrong: { knowledge: 2 },
          sourceKey: "cholestatic_pattern_alp_ggt",
          teacherAsk: "Come distingui pattern epatitico da colestatico alla lettura esami?"
        },
        {
          id: "ch12_s5",
          type: "quiz_reasoning",
          prompt: "Nei criteri MAFLD/NAFLD riportati, cosa serve oltre all'evidenza di grasso epatico?",
          options: [
            {
              text: "Almeno uno tra sovrappeso/obesita, diabete tipo 2 o disfunzione metabolica.",
              correct: true,
              why: "Corretto: e il criterio descritto nel modulo.",
              transitionLine: "Set point alto: Camilla sta ragionando da clinica completa."
            },
            { text: "Solo eta >50", correct: false, why: "Non e il criterio richiesto." },
            { text: "Solo dolore addominale isolato", correct: false, why: "Non sufficiente per definizione diagnostica." }
          ],
          onCorrect: { knowledge: 8, determination: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "mafl_diagnostic_criteria",
          teacherAsk: "Come spieghi al paziente il rischio evolutivo verso cirrosi/HCC?"
        },
        {
          id: "ch12_s6",
          type: "narrative",
          speaker: "Team Tutor",
          text:
            "'Hai chiuso la stagione. Dalla melena alle transaminasi, hai tenuto il metodo: priorita, razionale, monitoraggio, comunicazione.'",
          examHook:
            "Stagione completata: ora puoi fare run di ripasso e aggiungere casi avanzati su epatocarcinoma, colangiocarcinoma, autoimmunita.",
          sourceKey: "cirrhosis_hcc_risk"
        }
      ]
    }
  ]
};
