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
          id: "s1",
          type: "narrative",
          speaker: "Narratore",
          text:
            "Ore 06:40. Palestra semi-vuota, scarpe che stridono sul parquet. Camilla chiude l'ultimo esercizio con le Under, si cambia al volo e parte per il reparto: oggi la partita vera e' doppia, corsia ed esame.",
          examHook:
            "Target didattico: problem solving clinico (diagnosi, monitoraggio, terapia, educazione).",
          sourceKey: "problem_solving_framework"
        },
        {
          id: "s2",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "'Ti voglio lucida, non perfetta. SBAR in testa e priorita chiare. Primo caso del turno: donna di 58 anni con dolore epigastrico, sazieta precoce, calo ponderale e feci picee occasionali.'",
          examHook:
            "Il docente vuole struttura: Situation, Background, Assessment, Recommendation.",
          sourceKey: "problem_solving_framework"
        },
        {
          id: "s3",
          type: "choice",
          prompt:
            "Fine allenamento. Camilla e' stanca ma deve ancora ripassare i sanguinamenti digestivi: come gestisce energia e focus?",
          options: [
            {
              text: "Una IPA veloce e poi dritta sui quiz.",
              effects: { morale: 6, balance: -5 },
              tags: ["ipa_taken"],
              feedback:
                "Ti tira su il morale, ma il corpo resta in debito. In dispensa l'alcol rientra tra i trigger da evitare nei sintomi da reflusso.",
              transitionLine:
                "Camilla sente la testa accendersi subito, ma lo stomaco le ricorda che domani si paga tutto."
            },
            {
              text: "Niente IPA: acqua, doccia e 40 minuti di sonno.",
              effects: { balance: 8, determination: 3 },
              feedback:
                "Scelta pulita. Recupero fisico migliore e piu' tenuta quando la pressione sale.",
              transitionLine:
                "Rientra in reparto con il cervello piu' acceso e la sensazione di avere margine vero."
            },
            {
              text: "Video-analisi con le Under e poi planning studio.",
              effects: { leadership: 7, determination: 4, balance: -2 },
              feedback:
                "Leadership forte: la squadra cresce, ma il recupero fisico resta tirato.",
              transitionLine:
                "Le ragazze escono piu' ordinate dal campo. Camilla invece arriva al caso con addosso tutta la giornata."
            }
          ],
          sourceKey: "reflux_lifestyle"
        },
        {
          id: "s4",
          type: "quiz_mcq",
          prompt:
            "Mini-simulazione d'esame. Donna 58 anni: dolore epigastrico, sazieta precoce, -6 kg in 6 mesi, Hb 9 g/dL, feci picee occasionali. Quale elemento NON e' red flag che da solo giustifica EGDS in questo contesto?",
          options: [
            {
              text: "Eta >45 anni nel contesto clinico",
              correct: false,
              why: "Qui non va bene: nel caso della dispensa questo elemento rafforza l'indicazione all'approfondimento.",
              transitionLine:
                "Camilla si ferma un secondo, rilegge il caso e capisce dove si era fatta trascinare."
            },
            {
              text: "Anemia",
              correct: false,
              why: "No: anemia e' red flag e nel contesto clinico richiede approfondimento endoscopico.",
              transitionLine:
                "Segna l'errore e non si abbatte: meglio correggere qui che davanti al docente."
            },
            {
              text: "Stipsi",
              correct: true,
              why: "Esatto. Nel quiz della dispensa la risposta corretta e' stipsi: da sola non giustifica EGDS del tratto superiore.",
              transitionLine:
                "Punto preso. Camilla sente il ritmo giusto e passa alla decisione clinica successiva."
            },
            {
              text: "Calo ponderale non intenzionale",
              correct: false,
              why: "No: calo ponderale non intenzionale e' sintomo d'allarme.",
              transitionLine:
                "Errore utile: ora il concetto di red flag le resta molto piu' nitido."
            },
            {
              text: "Melena",
              correct: false,
              why: "No: la melena orienta verso possibile sanguinamento GI superiore.",
              transitionLine:
                "Camilla si riallinea subito: sul sanguinamento non ci si puo' permettere confusione."
            }
          ],
          onCorrect: { knowledge: 10, determination: 4 },
          onWrong: { knowledge: 3 },
          sourceKey: "quiz_alarm_symptoms",
          teacherAsk:
            "All'orale: quali red flags GI ti fanno anticipare EGDS senza attendere ulteriori passaggi?"
        },
        {
          id: "s5",
          type: "quiz_clinical",
          prompt:
            "Scelta clinica narrativa. Paziente con melena osservata, ipoteso e tachicardico: qual e' la tua prima mossa?",
          options: [
            {
              text: "Stabilizzazione emodinamica: accessi venosi robusti + fluidi, poi gestione vie aeree se necessaria.",
              correct: true,
              why: "Corretto: in acuto la dispensa mette prima stabilizzazione emodinamica (e vie aeree se necessario), poi timing endoscopico.",
              transitionLine:
                "Scelta da reparto vero: prima metti in sicurezza, poi vai a cercare la causa."
            },
            {
              text: "EGDS immediata prima di qualunque stabilizzazione.",
              correct: false,
              why: "Non e' la priorita iniziale: EGDS e' cruciale, ma dopo ABC e stabilizzazione.",
              transitionLine:
                "Camilla lo segna in grande: mai inseguire l'esame strumentale saltando la sicurezza del paziente."
            },
            {
              text: "Attendere solo esami ematici prima di intervenire.",
              correct: false,
              why: "No: aspettare soltanto gli esami ritarda una fase tempo-dipendente in un quadro potenzialmente instabile.",
              transitionLine:
                "Respira, rilegge ABC e riparte: qui il tempo clinico conta piu' della teoria perfetta."
            }
          ],
          onCorrect: { knowledge: 9, leadership: 5 },
          onWrong: { knowledge: 2, determination: 2 },
          sourceKey: "melena_first_steps",
          extraSourceKey: "upper_bleeding_timing",
          teacherAsk:
            "All'esame: come motivi il timing EGDS rispetto alla stabilizzazione in emorragia digestiva superiore?"
        },
        {
          id: "s6",
          type: "quiz_reasoning",
          prompt:
            "Ragionamento clinico. Diarrea oltre 6 settimane: quale dato dell'anamnesi/esami orienta verso forma infiammatoria?",
          options: [
            {
              text: "Feci con sangue e muco, con calprotectina fecale elevata.",
              correct: true,
              why: "Giusto: in dispensa e' il pattern tipico della diarrea infiammatoria (Crohn/rettocolite ulcerosa).",
              transitionLine:
                "Camilla collega i pezzi: sintomo, marker fecale, ipotesi clinica. Ragionamento pulito."
            },
            {
              text: "Diarrea solo dopo latte, senza alterazioni infiammatorie fecali.",
              correct: false,
              why: "Questo quadro non orienta in prima battuta a fenotipo infiammatorio.",
              transitionLine:
                "Errore tecnico, ma utile: ora distingue meglio i quadri infiammatori da quelli non infiammatori."
            },
            {
              text: "Assenza di calo ponderale, alvo regolare notturno e nessun sangue.",
              correct: false,
              why: "Poco coerente con diarrea infiammatoria attiva.",
              transitionLine:
                "Camilla si riallinea subito: il ragionamento clinico si aggiusta passo dopo passo."
            }
          ],
          onCorrect: { knowledge: 8, determination: 3 },
          onWrong: { knowledge: 2 },
          sourceKey: "inflammatory_diarrhea_clues",
          teacherAsk:
            "Il docente spesso chiede: quali step imposti dopo sospetto di diarrea infiammatoria?"
        },
        {
          id: "s7",
          type: "narrative",
          speaker: "Osteopata",
          text:
            "'Bel lavoro. Hai tenuto insieme priorita e ragionamento. Adesso proteggi il sistema: stress, sonno, carico fisico, continuita di studio. Se vai in riserva fuori dal reparto, vai in riserva anche all'orale.'",
          examHook:
            "Nessun game over: gli errori diventano recupero guidato.",
          sourceKey: "problem_solving_framework"
        }
      ]
    },
    {
      id: "ch2",
      title: "Capitolo 2 - Dolore Addominale e Disfagia",
      status: "planned",
      objective: "Distinguere pattern clinici, allarmi e prime indagini.",
      sourcePages: [5]
    },
    {
      id: "ch3",
      title: "Capitolo 3 - Diarrea, Stipsi, Incontinenza",
      status: "planned",
      objective: "Classificazione fisiopatologica e iter diagnostico essenziale.",
      sourcePages: [15]
    },
    {
      id: "ch4",
      title: "Capitolo 4 - Emorragie GI Superiori e Inferiori",
      status: "planned",
      objective: "Urgenza, stratificazione rischio e timing endoscopico.",
      sourcePages: [27, 30, 34]
    },
    {
      id: "ch5",
      title: "Capitolo 5 - Endoscopia: EGDS, Pancolonscopia, VCE",
      status: "planned",
      objective: "Indicazioni, limiti, complicanze e scelta metodica.",
      sourcePages: [31, 37, 39]
    },
    {
      id: "ch6",
      title: "Capitolo 6 - Esofago: MRGE, Esofagiti, Barrett, Neoplasie",
      status: "planned",
      objective: "Fisiopatologia, red flags e diagnosi differenziale.",
      sourcePages: [45, 48, 49]
    },
    {
      id: "ch7",
      title: "Capitolo 7 - Stomaco e Ulcera Peptica",
      status: "planned",
      objective: "Quadri clinici, complicanze, H. pylori e terapia.",
      sourcePages: [69]
    },
    {
      id: "ch8",
      title: "Capitolo 8 - Malassorbimento: Celiachia e SIBO",
      status: "planned",
      objective: "Diagnosi differenziale della diarrea cronica.",
      sourcePages: [15, 87]
    },
    {
      id: "ch9",
      title: "Capitolo 9 - IBD e IBS",
      status: "planned",
      objective: "Crohn, rettocolite ulcerosa, monitoraggio e aderenza.",
      sourcePages: [39]
    },
    {
      id: "ch10",
      title: "Capitolo 10 - Intestino Critico e Diverticolosi",
      status: "planned",
      objective: "Ischemia, complicanze e gestione clinica.",
      sourcePages: [136]
    },
    {
      id: "ch11",
      title: "Capitolo 11 - Pancreas e Vie Biliari",
      status: "planned",
      objective: "Pancreatite, litiasi, colecistite, colangite.",
      sourcePages: [69, 121, 153]
    },
    {
      id: "ch12",
      title: "Capitolo 12 - Epatologia Integrata",
      status: "planned",
      objective:
        "Biochimica epatica, MAFLD/NAFLD, epatopatia alcolica, DILI, epatocarcinoma, colangiocarcinoma.",
      sourcePages: [158, 159, 167, 168, 150]
    }
  ]
};
