
/* La Grande "C" — mini sito / gioco
   - Static site: nessun backend.
   - Progressi salvati in localStorage.
   - I pulsanti .lockable vengono sbloccati quando completi tutte le tappe.

   Sostituisci i file:
   - downloads/la-grande-c.epub
   - downloads/la-grande-c.pdf
   - media/colonna-sonora.mp3
*/

(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const STORAGE_KEY = "lgc_passport_v1";

  const stops = [
    {
      id: "malpensa",
      badge: "Tappa 1 • ✈️",
      label: "Milano → Malpensa",
      title: "Zaini, Anubi e prime turbolenze",
      text: "Prima di partire, c'è un giudice severo: il cane che osserva lo zaino di Pietro.",
      question: "Come si chiama il cane di Pietro?",
      options: ["Anubi", "Pluto", "Cerbero", "Fuffi"],
      answer: 0,
      hint: "È un nome “mitologico”. E no, non è un gatto.",
      stamp: "MI"
    },
    {
      id: "liberdade",
      badge: "Tappa 2 • 🏮",
      label: "São Paulo",
      title: "Liberdade",
      text: "In Brasile… ma tra lanterne rosse, ramen e gyoza.",
      question: "Liberdade, nel libro, è…",
      options: [
        "il quartiere giapponese",
        "una spiaggia famosa per il surf",
        "lo stadio principale della città",
        "un museo di arte contemporanea"
      ],
      answer: 0,
      hint: "Non è una città: è un quartiere, e l'atmosfera è molto asiatica.",
      stamp: "SP"
    },
    {
      id: "campo-grande",
      badge: "Tappa 3 • 🧉",
      label: "Campo Grande",
      title: "Tereré e capibara",
      text: "Viali larghi, verde ovunque e… un laghetto con ospiti zen.",
      question: "Quale animale pascola vicino al laghetto al Parque das Nações Indígenas?",
      options: ["Capibara", "Alpaca", "Caimano", "Iguana"],
      answer: 0,
      hint: "È un roditore enorme e pacioso (molto instagrammabile).",
      stamp: "CG"
    },
    {
      id: "pantanal",
      badge: "Tappa 4 • 🐟",
      label: "Pantanal",
      title: "Barca, piranha e zanzare",
      text: "Su una chalana a due piani: acqua, cielo, uccelli… e denti.",
      question: "Che cosa pescano nel Pantanal, rischiando di terrorizzare Paolino?",
      options: ["Un piranha", "Un tonno", "Un salmone", "Una trota"],
      answer: 0,
      hint: "È piccolo, dentato e non adatto ai talloni delicati.",
      stamp: "PA"
    },
    {
      id: "la-paz",
      badge: "Tappa 5 • 🏔️",
      label: "La Paz",
      title: "Altitudine e teleférico",
      text: "Salita lunga: aria sottile, testa che gira e mate de coca.",
      question: "Come si chiama il mal di montagna che li colpisce arrivando in alto?",
      options: ["Soroche", "Jet lag", "Samba", "Ceviche"],
      answer: 0,
      hint: "È una parola usata spesso sulle Ande.",
      stamp: "LP"
    },
    {
      id: "uyuni",
      badge: "Tappa 6 • 🧂",
      label: "Uyuni",
      title: "Notti di sale",
      text: "Il mondo si “resetta”: bianco ovunque, cielo enorme, zero riferimenti.",
      question: "In che tipo di posto “assurdo” dormono durante il tour?",
      options: ["Un hotel di sale", "Una capsula spaziale", "Una casa sull'albero", "Un monastero"],
      answer: 0,
      hint: "Pareti, tavoli… persino il letto possono essere fatti dello stesso materiale.",
      stamp: "UY"
    },
    {
      id: "lima",
      badge: "Tappa 7 • 🍋",
      label: "Lima",
      title: "Barranco e sapore di lime",
      text: "Musica criolla, cajón, chitarra… e un piatto che sa di mare e agrumi.",
      question: "Quale piatto (con lime e pesce) assaggiano a Barranco?",
      options: ["Ceviche", "Carbonara", "Ramen", "Burrito"],
      answer: 0,
      hint: "È peruviano, freddo e “marinato”.",
      stamp: "LI"
    },
    {
      id: "quito",
      badge: "Tappa 8 • 🌎",
      label: "Quito",
      title: "Mitad del Mundo",
      text: "Un piede a nord, uno a sud: anche il tallone di Paolino deve accettarlo.",
      question: "Dove vanno per “stare in due emisferi” nello stesso momento?",
      options: ["Mitad del Mundo", "Parque del Amor", "Mercadão", "Plaza Murillo"],
      answer: 0,
      hint: "È un monumento legato alla linea dell'Equatore.",
      stamp: "QU"
    },
    {
      id: "cartagena",
      badge: "Tappa 9 • 🌴",
      label: "Cartagena de Indias",
      title: "Mura e Caribe",
      text: "Tramonto sulle mura e un centro storico fortificato (patrimonio UNESCO).",
      question: "Come si chiama il centro storico fortificato di Cartagena?",
      options: ["Ciudad Amurallada", "Ciudad de la Salsa", "Barrio de la Nieve", "Plaza del Sol"],
      answer: 0,
      hint: "È letteralmente la “città murata”.",
      stamp: "CA"
    },
    {
      id: "belem",
      badge: "Tappa 10 • 🛶",
      label: "Amazzonia → Belém",
      title: "Ver-o-Peso e chiudere la C",
      text: "Tra fiume e Atlantico: mercati, odori forti e cucina amazzonica.",
      question: "Qual è il mercato celebre di Belém che “profuma” tutta la città?",
      options: ["Ver-o-Peso", "Mercado Central", "La Boqueria", "San Pedro"],
      answer: 0,
      hint: "Il nome sembra quasi un imperativo: ‘guarda…’ qualcosa.",
      stamp: "BE"
    }
  ];

  const state = {
    started: false,
    currentIndex: 0,
    done: Array(stops.length).fill(false),
    score: 0,
    hintsUsed: 0,
    snowEnabled: true
  };

  // UI refs
  const els = {
    stampsCount: $("#stampsCount"),
    stampsTotal: $("#stampsTotal"),
    score: $("#score"),
    stamps: $("#stamps"),
    stopBadge: $("#stopBadge"),
    stopLabel: $("#stopLabel"),
    stopTitle: $("#stopTitle"),
    stopText: $("#stopText"),
    question: $("#question"),
    options: $("#options"),
    hint: $("#hint"),
    feedback: $("#feedback"),
    startGame: $("#startGame"),
    showHint: $("#showHint"),
    nextStop: $("#nextStop"),
    resetGame: $("#resetGame"),
    unlock: $("#unlock"),
    lockables: $$(".lockable"),
    toggleSnow: $("#toggleSnow"),
    snow: $("#snow"),
    routeDots: $("#routeDots"),
    routeSvg: $("#routeSvg"),
  };

  // ---------------------------
  // Persistence
  // ---------------------------
  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);

      if (typeof parsed !== "object" || parsed === null) return;

      state.started = !!parsed.started;
      state.currentIndex = clampInt(parsed.currentIndex, 0, stops.length - 1);
      if (Array.isArray(parsed.done) && parsed.done.length === stops.length) {
        state.done = parsed.done.map(Boolean);
      }
      state.score = clampInt(parsed.score, 0, 9999);
      state.hintsUsed = clampInt(parsed.hintsUsed, 0, 9999);
      state.snowEnabled = parsed.snowEnabled !== false;

    } catch (e) {
      console.warn("Load state failed:", e);
    }
  }

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn("Save state failed:", e);
    }
  }

  function resetAll() {
    state.started = false;
    state.currentIndex = 0;
    state.done = Array(stops.length).fill(false);
    state.score = 0;
    state.hintsUsed = 0;
    els.unlock.hidden = true;
    save();
    renderAll(true);
  }

  function clampInt(n, min, max) {
    n = Number.isFinite(Number(n)) ? Math.floor(Number(n)) : min;
    return Math.max(min, Math.min(max, n));
  }

  // ---------------------------
  // Lock / unlock downloads
  // ---------------------------
  function setLocked(locked) {
    els.lockables.forEach(a => {
      if (locked) {
        a.classList.add("is-disabled");
        a.setAttribute("aria-disabled", "true");
        a.dataset.locked = "1";
      } else {
        a.classList.remove("is-disabled");
        a.removeAttribute("aria-disabled");
        delete a.dataset.locked;
      }
    });
  }

  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a.lockable");
    if (!a) return;
    if (a.dataset.locked === "1") {
      ev.preventDefault();
      toast("🔒 Prima completa il gioco per sbloccare il regalo!");
    }
  });

  // ---------------------------
  // Route dots (SVG)
  // ---------------------------
  function renderRouteDots() {
    // Dots along a symbolic “C” path (approximated points).
    // Using fixed coordinates keeps it simple and predictable.
    const dots = [
      { x: 168, y: 38 },
      { x: 115, y: 42 },
      { x: 70,  y: 66 },
      { x: 54,  y: 106 },
      { x: 54,  y: 150 },
      { x: 62,  y: 188 },
      { x: 88,  y: 212 },
      { x: 122, y: 224 },
      { x: 152, y: 224 },
      { x: 168, y: 222 },
    ];

    const g = els.routeDots;
    g.innerHTML = "";
    dots.forEach((pt, i) => {
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", String(pt.x));
      c.setAttribute("cy", String(pt.y));
      c.setAttribute("r", "10");
      c.setAttribute("class", "route__dot");
      c.dataset.index = String(i);
      g.appendChild(c);
    });
  }

  function updateRouteDotClasses() {
    $$("#routeDots circle").forEach((c, i) => {
      c.classList.remove("route__dot--done", "route__dot--now");
      if (state.done[i]) c.classList.add("route__dot--done");
      if (i === state.currentIndex && !allDone()) c.classList.add("route__dot--now");
    });
  }

  // ---------------------------
  // Game render
  // ---------------------------
  function allDone() {
    return state.done.every(Boolean);
  }

  function stampsDoneCount() {
    return state.done.filter(Boolean).length;
  }

  function findNextIndex(from = 0) {
    for (let i = from; i < stops.length; i++) {
      if (!state.done[i]) return i;
    }
    return stops.length - 1;
  }

  function renderStamps() {
    els.stamps.innerHTML = "";
    stops.forEach((s, i) => {
      const el = document.createElement("div");
      el.className = "stamp" + (state.done[i] ? " is-done" : "");
      el.title = s.label;
      el.textContent = s.stamp;
      els.stamps.appendChild(el);
    });
  }

  function renderHeaderNumbers() {
    els.stampsTotal.textContent = String(stops.length);
    els.stampsCount.textContent = String(stampsDoneCount());
    els.score.textContent = String(state.score);
  }

  function renderStopCard(index) {
    const s = stops[index];
    els.stopBadge.textContent = s.badge;
    els.stopLabel.textContent = s.label;
    els.stopTitle.textContent = s.title;
    els.stopText.textContent = s.text;
  }

  function clearQuiz() {
    els.question.textContent = "—";
    els.options.innerHTML = "";
    els.hint.hidden = true;
    els.hint.textContent = "";
    els.feedback.textContent = "";
  }

  function renderQuiz(index, { fresh = false } = {}) {
    const s = stops[index];
    els.question.textContent = s.question;
    els.options.innerHTML = "";
    els.feedback.textContent = "";

    // Hint reset
    els.hint.hidden = true;
    els.hint.textContent = s.hint || "";
    els.showHint.disabled = false;

    // Next button disabled until correct
    els.nextStop.disabled = true;

    // Options
    s.options.forEach((label, optIndex) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option";
      btn.textContent = label;
      btn.addEventListener("click", () => onAnswer(optIndex));
      els.options.appendChild(btn);
    });

    // If user reloads mid-stop, keep it simple: treat as fresh
    if (fresh) {
      // nothing else
    }
  }

  function toast(msg) {
    els.feedback.textContent = msg;
  }

  let hintUsedThisStop = false;

  function onAnswer(optIndex) {
    const s = stops[state.currentIndex];
    const optionButtons = $$(".option", els.options);
    optionButtons.forEach(b => (b.disabled = true));

    if (optIndex === s.answer) {
      // Correct
      optionButtons[optIndex].classList.add("is-correct");

      const base = 10;
      const bonus = hintUsedThisStop ? 0 : 2; // reward for no hint
      const gained = base + bonus;

      state.score += gained;
      state.done[state.currentIndex] = true;

      toast(`✅ Corretto! +${gained} Vitamina C`);

      // Move currentIndex to next incomplete
      if (!allDone()) {
        state.currentIndex = findNextIndex(0);
      }

      // Unlock next button
      els.nextStop.disabled = false;
      els.showHint.disabled = true;

      save();
      renderHeaderNumbers();
      renderStamps();
      updateRouteDotClasses();

      // If completed all
      if (allDone()) {
        finish();
      }
      return;
    }

    // Wrong
    optionButtons[optIndex].classList.add("is-wrong");
    toast("❌ Quasi! Riprova 😉");

    // Re-enable after a short delay (so user sees the feedback)
    window.setTimeout(() => {
      optionButtons.forEach(b => (b.disabled = false));
      optionButtons[optIndex].classList.remove("is-wrong");
      els.feedback.textContent = "";
    }, 650);
  }

  function finish() {
    els.unlock.hidden = false;
    setLocked(false);
    els.startGame.disabled = true;
    els.nextStop.disabled = true;
    els.showHint.disabled = true;
    clearQuiz();
    renderStopCard(stops.length - 1);
    toast("🎁 Sbloccato! Vai ai download.");
    burstConfetti();
    save();
  }

  function start() {
    state.started = true;

    // If everything already done, just show unlock.
    if (allDone()) {
      finish();
      return;
    }

    // Jump to first incomplete if needed.
    state.currentIndex = findNextIndex(0);
    hintUsedThisStop = false;

    renderStopCard(state.currentIndex);
    renderQuiz(state.currentIndex, { fresh: true });

    els.startGame.disabled = true;
    els.showHint.disabled = false;
    els.nextStop.disabled = true;

    setLocked(true);

    save();
  }

  function next() {
    if (allDone()) return;

    // After correct answer we already set currentIndex to next incomplete.
    hintUsedThisStop = false;
    renderStopCard(state.currentIndex);
    renderQuiz(state.currentIndex, { fresh: true });
    els.nextStop.disabled = true;
    save();
  }

  function showHint() {
    if (els.showHint.disabled) return;
    if (!els.hint.textContent) return;

    hintUsedThisStop = true;
    state.hintsUsed += 1;

    // Small “cost” (but not below zero)
    state.score = Math.max(0, state.score - 2);

    els.hint.hidden = false;
    toast("💡 Suggerimento mostrato (-2 Vitamina C)");
    renderHeaderNumbers();
    save();
  }

  // ---------------------------
  // Snow effect (canvas)
  // ---------------------------
  let snowRAF = null;
  let snowParticles = [];
  let lastTS = 0;

  function snowResize() {
    const c = els.snow;
    const dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    c.width = Math.floor(window.innerWidth * dpr);
    c.height = Math.floor(window.innerHeight * dpr);
    c.style.width = window.innerWidth + "px";
    c.style.height = window.innerHeight + "px";

    // Rebuild particles
    const count = Math.floor(Math.min(160, Math.max(60, window.innerWidth / 14)));
    snowParticles = Array.from({ length: count }, () => makeSnowParticle(c.width, c.height));
  }

  function makeSnowParticle(w, h) {
    return {
      x: Math.random() * w,
      y: Math.random() * h,
      r: 1.2 + Math.random() * 2.6,
      vy: 16 + Math.random() * 44,
      vx: -10 + Math.random() * 20,
      drift: Math.random() * Math.PI * 2
    };
  }

  function snowStep(ts) {
    const c = els.snow;
    const ctx = c.getContext("2d");
    if (!ctx) return;

    const dt = Math.min(0.05, (ts - lastTS) / 1000 || 0.016);
    lastTS = ts;

    ctx.clearRect(0, 0, c.width, c.height);

    ctx.globalAlpha = 0.82;
    ctx.fillStyle = "rgba(255,255,255,1)";
    snowParticles.forEach(p => {
      p.drift += dt * 0.9;
      p.x += (p.vx + Math.sin(p.drift) * 12) * dt;
      p.y += p.vy * dt;

      if (p.y - p.r > c.height) {
        p.y = -p.r;
        p.x = Math.random() * c.width;
      }
      if (p.x < -20) p.x = c.width + 20;
      if (p.x > c.width + 20) p.x = -20;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    });

    snowRAF = requestAnimationFrame(snowStep);
  }

  function snowStart() {
    if (snowRAF) return;
    snowResize();
    lastTS = 0;
    snowRAF = requestAnimationFrame(snowStep);
  }

  function snowStop() {
    if (snowRAF) cancelAnimationFrame(snowRAF);
    snowRAF = null;
    const ctx = els.snow.getContext("2d");
    if (ctx) ctx.clearRect(0, 0, els.snow.width, els.snow.height);
  }

  function setSnowEnabled(enabled) {
    state.snowEnabled = !!enabled;
    els.toggleSnow.setAttribute("aria-pressed", String(!!enabled));
    if (enabled) snowStart();
    else snowStop();
    save();
  }

  // ---------------------------
  // Confetti (mini burst)
  // ---------------------------
  function burstConfetti() {
    // Quick burst drawn on the same canvas (snow). If snow is disabled,
    // we still do a tiny burst and then clear.
    const c = els.snow;
    const ctx = c.getContext("2d");
    if (!ctx) return;

    const dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    const w = c.width || Math.floor(window.innerWidth * dpr);
    const h = c.height || Math.floor(window.innerHeight * dpr);

    const centerX = w * 0.5;
    const centerY = h * 0.25;

    const pieces = Array.from({ length: 90 }, () => ({
      x: centerX,
      y: centerY,
      vx: (-220 + Math.random() * 440),
      vy: (-260 + Math.random() * 220),
      g: 520 + Math.random() * 240,
      s: 2 + Math.random() * 3,
      life: 0.9 + Math.random() * 0.5,
      rot: Math.random() * Math.PI,
      vr: (-8 + Math.random() * 16)
    }));

    const start = performance.now();
    const colors = [
      "rgba(255,59,59,.95)",
      "rgba(49,208,121,.95)",
      "rgba(255,210,122,.95)",
      "rgba(255,255,255,.90)"
    ];

    function tick(ts) {
      const t = (ts - start) / 1000;
      ctx.clearRect(0, 0, w, h);

      pieces.forEach((p, i) => {
        const dt = 1/60;
        p.life -= dt;
        p.vy += p.g * dt;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.rot += p.vr * dt;

        if (p.life <= 0) return;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(-p.s, -p.s, p.s * 2, p.s * 2);
        ctx.restore();
      });

      if (t < 1.2) {
        requestAnimationFrame(tick);
      } else {
        // Restore snow if enabled
        ctx.clearRect(0, 0, w, h);
        if (state.snowEnabled) {
          snowResize();
        }
      }
    }
    requestAnimationFrame(tick);
  }

  // ---------------------------
  // Initial render
  // ---------------------------
  function renderAll(first = false) {
    renderRouteDots();
    updateRouteDotClasses();

    renderHeaderNumbers();
    renderStamps();

    if (allDone()) {
      setLocked(false);
      els.startGame.disabled = true;
      finish();
      return;
    }

    setLocked(true);

    // If user already started, resume at currentIndex; otherwise show intro card.
    if (state.started) {
      els.startGame.disabled = true;
      els.showHint.disabled = false;
      els.nextStop.disabled = true;

      // Ensure currentIndex is valid
      state.currentIndex = findNextIndex(0);
      renderStopCard(state.currentIndex);
      renderQuiz(state.currentIndex, { fresh: true });
    } else {
      els.startGame.disabled = false;
      els.showHint.disabled = true;
      els.nextStop.disabled = true;
      clearQuiz();

      els.stopBadge.textContent = "Info";
      els.stopLabel.textContent = "Regole del gioco";
      els.stopTitle.textContent = "Completa la Grande C";
      els.stopText.textContent = "Rispondi alle domande per raccogliere i timbri. Quando li hai tutti, si sbloccano i download.";
    }

    save();

    // Snow
    const prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) {
      // Respect reduced motion: start disabled unless user explicitly enables.
      if (first && state.snowEnabled) {
        state.snowEnabled = false;
      }
    }
    setSnowEnabled(state.snowEnabled);
  }

  // ---------------------------
  // Events
  // ---------------------------
  els.startGame.addEventListener("click", start);
  els.nextStop.addEventListener("click", next);
  els.showHint.addEventListener("click", showHint);
  els.resetGame.addEventListener("click", resetAll);

  els.toggleSnow.addEventListener("click", () => {
    setSnowEnabled(!state.snowEnabled);
  });

  window.addEventListener("resize", () => {
    if (state.snowEnabled) snowResize();
  });

  // Init
  load();
  renderAll(true);
})();
