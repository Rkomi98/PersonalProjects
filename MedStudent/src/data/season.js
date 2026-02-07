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
            "Ore 06:40. Palestra quasi vuota. Camilla ha appena finito la battuta in salto con le sue Under, poi corre in reparto per il tirocinio di gastroenterologia. Oggi sente che la stagione si decide su due campi: il parquet e l'esame.",
          examHook:
            "Target didattico: problem solving clinico (diagnosi, monitoraggio, terapia, educazione).",
          sourceKey: "problem_solving_framework"
        },
        {
          id: "s2",
          type: "narrative",
          speaker: "Ingegnere",
          text:
            "'Niente improvvisazione: SBAR, priorita e catena decisionale. Primo caso del turno: donna 58 anni con dolore epigastrico, sazieta precoce, calo ponderale e feci picee occasionali.'",
          examHook:
            "Il docente vuole struttura: Situation, Background, Assessment, Recommendation.",
          sourceKey: "problem_solving_framework"
        },
        {
          id: "s3",
          type: "choice",
          prompt:
            "Fine allenamento serale. Prima di ripassare i sanguinamenti digestivi, Camilla decide come gestire energia e focus.",
          options: [
            {
              text: "Beve una IPA e ripassa subito.",
              effects: { morale: 6, balance: -5 },
              tags: ["ipa_taken"],
              feedback:
                "Morale su, ma il corpo risente la fatica. Nella dispensa l'alcol e' citato tra i trigger da evitare nei sintomi da reflusso."
            },
            {
              text: "Salta la IPA, idratazione e 40 minuti di sonno.",
              effects: { balance: 8, determination: 3 },
              feedback:
                "Recupero fisico solido: migliora la tenuta quando la pressione aumenta."
            },
            {
              text: "Fa video-analisi con la squadra Under e poi pianifica lo studio.",
              effects: { leadership: 7, determination: 4, balance: -2 },
              feedback:
                "Leadership in crescita: la squadra migliora, ma il margine di recupero fisico resta stretto."
            }
          ],
          sourceKey: "reflux_lifestyle"
        },
        {
          id: "s4",
          type: "quiz_mcq",
          prompt:
            "Quiz d'esame. Donna 58 anni: dolore epigastrico, sazieta precoce, -6 kg in 6 mesi, Hb 9 g/dL, feci picee occasionali. Quale elemento NON e' un sintomo d'allarme che giustifica EGDS nel contesto descritto?",
          options: [
            {
              text: "Eta >45 anni nel contesto clinico",
              correct: false,
              why: "Nel caso in dispensa e' considerato elemento che rafforza l'indicazione ad approfondire."
            },
            {
              text: "Anemia",
              correct: false,
              why: "Anemia e' red flag e richiede approfondimento endoscopico nel contesto."
            },
            {
              text: "Stipsi",
              correct: true,
              why: "Nel quiz della dispensa e' l'opzione corretta: la stipsi, da sola, non giustifica EGDS del tratto superiore."
            },
            {
              text: "Calo ponderale non intenzionale",
              correct: false,
              why: "Il calo ponderale non intenzionale e' sintomo d'allarme."
            },
            {
              text: "Melena",
              correct: false,
              why: "La melena e' indicativa di possibile sanguinamento GI superiore."
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
            "Scelta clinica narrativa. Paziente con melena osservata, ipoteso e tachicardico. Qual e' la prima priorita?",
          options: [
            {
              text: "Stabilizzazione emodinamica: accessi venosi robusti + fluidi, poi gestione vie aeree se necessaria.",
              correct: true,
              why: "La dispensa indica questo come primo passaggio in acuto."
            },
            {
              text: "EGDS immediata prima di qualunque stabilizzazione.",
              correct: false,
              why: "EGDS e' cruciale, ma dopo priorita ABC e stabilizzazione iniziale."
            },
            {
              text: "Attendere solo esami ematici prima di intervenire.",
              correct: false,
              why: "Ritarda una fase tempo-dipendente in un quadro potenzialmente instabile."
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
            "Ragionamento clinico. Diarrea da oltre 6 settimane. Quale elemento orienta verso forma infiammatoria?",
          options: [
            {
              text: "Feci con sangue e muco, con calprotectina fecale elevata.",
              correct: true,
              why: "In dispensa e' il pattern tipico di diarrea infiammatoria (Crohn/rettocolite ulcerosa)."
            },
            {
              text: "Diarrea solo dopo latte, senza alterazioni infiammatorie fecali.",
              correct: false,
              why: "Non orienta in prima battuta a un fenotipo infiammatorio."
            },
            {
              text: "Assenza di calo ponderale, alvo regolare notturno e nessun sangue.",
              correct: false,
              why: "Quadro poco coerente con diarrea infiammatoria attiva."
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
            "'Hai gestito priorita e ragionamento. Ora ricordati il sistema completo: stress, sonno, carico fisico, aderenza allo studio. Se crolli fuori dal reparto, crolli anche al caso clinico.'",
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
