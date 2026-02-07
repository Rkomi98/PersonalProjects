import { season } from "./data/season.js";
import { sourceBook } from "./data/sourceBook.js";
import { GameEngine } from "./engine/gameEngine.js";

const engine = new GameEngine(season, sourceBook);

const elements = {
  seasonTitle: document.querySelector("#season-title"),
  chapterTitle: document.querySelector("#chapter-title"),
  sceneType: document.querySelector("#scene-type"),
  transition: document.querySelector("#transition"),
  speaker: document.querySelector("#speaker"),
  narrative: document.querySelector("#narrative"),
  examHook: document.querySelector("#exam-hook"),
  options: document.querySelector("#options"),
  advance: document.querySelector("#advance"),
  feedback: document.querySelector("#feedback"),
  feedbackTitle: document.querySelector("#feedback-title"),
  feedbackText: document.querySelector("#feedback-text"),
  feedbackExam: document.querySelector("#feedback-exam"),
  feedbackSource: document.querySelector("#feedback-source"),
  profile: document.querySelector("#profile"),
  stats: document.querySelector("#stats"),
  mirrors: document.querySelector("#mirrors"),
  chapters: document.querySelector("#chapters"),
  sourceBookTitle: document.querySelector("#source-book-title"),
  sourceBookPath: document.querySelector("#source-book-path"),
  sourceScene: document.querySelector("#source-scene"),
  resetButton: document.querySelector("#reset-progress")
};

function sceneLabel(type) {
  const map = {
    narrative: "Scena narrativa",
    choice: "Scelta significativa",
    quiz_mcq: "Quiz a scelta multipla",
    quiz_clinical: "Scelta clinica narrativa",
    quiz_reasoning: "Domanda di ragionamento"
  };
  return map[type] || "Interazione";
}

function clearChildren(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function renderStats(snapshot) {
  clearChildren(elements.stats);

  Object.entries(snapshot.state.stats).forEach(([key, value]) => {
    const statDef = season.stats[key];
    const row = document.createElement("li");

    const label = document.createElement("span");
    label.textContent = statDef.label;

    const val = document.createElement("strong");
    val.textContent = `${value}`;

    row.appendChild(label);
    row.appendChild(val);
    elements.stats.appendChild(row);
  });
}

function renderProfile() {
  clearChildren(elements.profile);
  season.protagonist.profile.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    elements.profile.appendChild(li);
  });
}

function renderMirrors(snapshot) {
  elements.mirrors.innerHTML = "";
  const volleyball = document.createElement("p");
  volleyball.textContent = `Pallavolo: ${snapshot.volleyballMirror}`;

  const ipa = document.createElement("p");
  ipa.textContent = `IPA: ${snapshot.ipaImpact}`;

  elements.mirrors.appendChild(volleyball);
  elements.mirrors.appendChild(ipa);
}

function renderChapters(snapshot) {
  clearChildren(elements.chapters);

  season.chapters.forEach((chapter, index) => {
    const item = document.createElement("li");
    const current = index === snapshot.state.chapterIndex;

    item.className = chapter.status;
    if (current) item.classList.add("active");

    const title = document.createElement("strong");
    title.textContent = chapter.title;

    const objective = document.createElement("p");
    objective.textContent = chapter.objective;

    const pages = document.createElement("span");
    pages.textContent = `Dispensa, pagine base: ${chapter.sourcePages.join(", ")}`;

    item.appendChild(title);
    item.appendChild(objective);
    item.appendChild(pages);
    elements.chapters.appendChild(item);
  });
}

function renderFeedback(snapshot) {
  const feedback = snapshot.feedback;
  if (!feedback) {
    elements.feedback.classList.add("hidden");
    return;
  }

  elements.feedback.classList.remove("hidden");
  elements.feedbackTitle.textContent = feedback.title;
  elements.feedbackText.textContent = feedback.text;
  elements.feedbackExam.textContent = feedback.exam ? `Focus docente: ${feedback.exam}` : "";

  const sources = [];
  if (feedback.sourcePrimary) {
    sources.push(`Fonte principale: p.${feedback.sourcePrimary.page} - ${feedback.sourcePrimary.topic}`);
  }
  if (feedback.sourceSecondary) {
    sources.push(`Fonte supporto: p.${feedback.sourceSecondary.page} - ${feedback.sourceSecondary.topic}`);
  }
  if (feedback.correct === false && feedback.correctAnswer) {
    sources.push(`Risposta corretta: ${feedback.correctAnswer}`);
  }

  elements.feedbackSource.textContent = sources.join(" | ");
}

function renderSceneSources(scene) {
  const primary = scene?.sourceKey ? sourceBook.entries[scene.sourceKey] : null;
  const extra = scene?.extraSourceKey ? sourceBook.entries[scene.extraSourceKey] : null;

  if (!scene || !primary) {
    elements.sourceScene.textContent = "Fonte scena non disponibile.";
    return;
  }

  const parts = [
    `Fonte scena: p.${primary.page} - ${primary.topic}`,
    `Estratto guida: ${primary.excerpt}`
  ];

  if (extra) {
    parts.push(`Supporto: p.${extra.page} - ${extra.topic}`);
  }

  elements.sourceScene.textContent = parts.join("\n");
}

function renderOptions(scene, snapshot) {
  clearChildren(elements.options);

  if (!scene) return;

  if (snapshot.feedback) {
    elements.advance.textContent = "Continua";
    elements.advance.classList.remove("hidden");
    return;
  }

  if (scene.type === "narrative") {
    elements.advance.textContent = "Prosegui";
    elements.advance.classList.remove("hidden");
    return;
  }

  elements.advance.classList.add("hidden");

  scene.options.forEach((option, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "option-btn";
    button.textContent = option.text;
    button.addEventListener("click", () => {
      engine.answer(index);
      render();
    });
    elements.options.appendChild(button);
  });
}

function renderComplete(snapshot) {
  elements.sceneType.textContent = "Capitolo completato";
  elements.transition.classList.add("hidden");
  elements.speaker.textContent = "Contadino";
  elements.narrative.textContent =
    "'Hai chiuso il primo set. I prossimi capitoli sono pronti in roadmap: si continua senza uscire dalla dispensa.'";
  elements.examHook.textContent =
    "Fine capitolo 1. Riapri la partita con Reset o prosegui estendendo i capitoli pianificati.";
  clearChildren(elements.options);
  elements.advance.classList.add("hidden");
  elements.feedback.classList.add("hidden");
  elements.sourceScene.textContent =
    "Capitolo 1 completato. Tutte le nozioni usate sono tracciate in pannello fonte.";
}

function render() {
  const snapshot = engine.snapshot();
  const scene = snapshot.scene;

  elements.seasonTitle.textContent = season.title;
  elements.chapterTitle.textContent = snapshot.chapter?.title || "Nessun capitolo attivo";
  elements.sourceBookTitle.textContent = sourceBook.title;
  elements.sourceBookPath.textContent = sourceBook.pdfPath;

  renderStats(snapshot);
  renderProfile();
  renderMirrors(snapshot);
  renderChapters(snapshot);
  renderFeedback(snapshot);

  if (!scene) {
    renderComplete(snapshot);
    return;
  }

  elements.sceneType.textContent = sceneLabel(scene.type);
  if (snapshot.state.transitionLine) {
    elements.transition.textContent = snapshot.state.transitionLine;
    elements.transition.classList.remove("hidden");
  } else {
    elements.transition.classList.add("hidden");
    elements.transition.textContent = "";
  }
  elements.speaker.textContent = scene.speaker || "Sistema";
  elements.narrative.textContent = scene.text || scene.prompt || "";
  elements.examHook.textContent = scene.examHook || "";

  renderSceneSources(scene);
  renderOptions(scene, snapshot);
}

elements.advance.addEventListener("click", () => {
  engine.advance();
  render();
});

elements.resetButton.addEventListener("click", () => {
  if (!window.confirm("Vuoi azzerare i progressi della stagione?")) return;
  engine.reset();
  render();
});

render();
