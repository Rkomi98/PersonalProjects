const STORAGE_KEY = "medstudent-rpg-save-v1";
const DEFAULT_WRONG_QUIZ_MALUS = { knowledge: -2 };

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function mergeDelta(target, incoming = {}) {
  Object.entries(incoming).forEach(([key, value]) => {
    target[key] = (target[key] || 0) + value;
  });
}

function hasAnyDelta(delta = {}) {
  return Object.values(delta).some((value) => value !== 0);
}

export class GameEngine {
  constructor(season, sourceBook) {
    this.season = season;
    this.sourceBook = sourceBook;
    this.state = this.buildInitialState();
    this.load();
  }

  buildInitialState() {
    const stats = {};
    Object.entries(this.season.stats).forEach(([key, def]) => {
      stats[key] = def.initial;
    });

    return {
      chapterIndex: 0,
      sceneIndex: 0,
      stats,
      tags: {},
      transitionLine: null,
      completedChapterIds: [],
      pendingFeedback: null,
      history: []
    };
  }

  load() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      this.save();
      return;
    }

    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        this.state = { ...this.state, ...parsed };
      }
    } catch (error) {
      console.warn("Save non valido, reset automatico.", error);
    }
  }

  save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
  }

  reset() {
    this.state = this.buildInitialState();
    this.save();
  }

  getChapters() {
    return this.season.chapters;
  }

  getCurrentChapter() {
    return this.season.chapters[this.state.chapterIndex];
  }

  getCurrentScene() {
    const chapter = this.getCurrentChapter();
    if (!chapter.scenes) return null;
    return chapter.scenes[this.state.sceneIndex] || null;
  }

  getSourceEntry(sourceKey) {
    if (!sourceKey) return null;
    return this.sourceBook.entries[sourceKey] || null;
  }

  getIpaImpact() {
    const ipaUsed = Boolean(this.state.tags.ipa_taken);
    return ipaUsed
      ? "IPA assunta: morale alto, ma attenzione a trigger reflusso/recupero fisico."
      : "Nessuna IPA in sessione: recupero fisico piu' stabile."
  }

  getVolleyballMirror() {
    const { knowledge, leadership, determination, balance } = this.state.stats;
    const composite = knowledge * 0.4 + leadership * 0.25 + determination * 0.2 + balance * 0.15;

    if (composite >= 75) {
      return "La Under gioca pulita: ricezione precisa e comunicazione alta.";
    }

    if (composite >= 58) {
      return "Partita gestibile: buona intensita', ma ancora errori nei momenti lunghi.";
    }

    return "La squadra va a strappi: errori non forzati quando cala la lucidita'.";
  }

  applyEffects(effects = {}) {
    const applied = {};
    Object.entries(effects).forEach(([stat, delta]) => {
      const def = this.season.stats[stat];
      if (!def || typeof this.state.stats[stat] !== "number") return;
      const before = this.state.stats[stat];
      const after = clamp(before + delta, def.min, def.max);
      this.state.stats[stat] = after;
      applied[stat] = (applied[stat] || 0) + (after - before);
    });
    return applied;
  }

  addTags(tags = []) {
    tags.forEach((tag) => {
      this.state.tags[tag] = true;
    });
  }

  answer(optionIndex) {
    const scene = this.getCurrentScene();
    if (!scene || this.state.pendingFeedback) return null;

    const option = scene.options?.[optionIndex];
    if (!option) return null;

    let feedback = {
      title: "Scelta registrata",
      text: option.feedback || "Decisione acquisita.",
      transitionLine: option.transitionLine || scene.transitionLine || null,
      exam: scene.teacherAsk || null,
      sourcePrimary: this.getSourceEntry(scene.sourceKey),
      sourceSecondary: this.getSourceEntry(scene.extraSourceKey),
      selectedOptionIndex: optionIndex,
      statDelta: {},
      correct: null
    };
    const statDelta = {};

    if (scene.type === "choice") {
      mergeDelta(statDelta, this.applyEffects(option.effects));
      this.addTags(option.tags);
      this.state.history.push({ sceneId: scene.id, type: scene.type, optionIndex });
    }

    if (scene.type.startsWith("quiz_")) {
      const correct = Boolean(option.correct);
      feedback.correct = correct;

      if (correct) {
        feedback.title = "Risposta corretta";
        feedback.text = option.why;
        mergeDelta(statDelta, this.applyEffects(scene.onCorrect));
      } else {
        feedback.title = "Risposta da recuperare";
        feedback.text = `${option.why} Recupero: rivedi il razionale e riparti subito, senza game over.`;
        mergeDelta(statDelta, this.applyEffects(scene.onWrong));
        mergeDelta(statDelta, this.applyEffects(scene.wrongMalus || DEFAULT_WRONG_QUIZ_MALUS));

        // Se un errore non porta a malus su conoscenza, forziamo almeno -1 (quando possibile).
        const knowledgeDelta = statDelta.knowledge || 0;
        if (knowledgeDelta >= 0) {
          mergeDelta(statDelta, this.applyEffects({ knowledge: -(knowledgeDelta + 1) }));
        }
      }

      const correctOptionIndex = scene.options.findIndex((item) => item.correct);
      const correctOption = scene.options[correctOptionIndex];
      feedback.correctOptionIndex = correctOptionIndex >= 0 ? correctOptionIndex : null;
      feedback.correctAnswer = correctOption ? correctOption.text : null;
      this.state.history.push({
        sceneId: scene.id,
        type: scene.type,
        optionIndex,
        correct
      });
    }

    if (!hasAnyDelta(statDelta)) {
      const fallbackSequence = scene.type.startsWith("quiz_")
        ? feedback.correct
          ? [{ determination: 1 }, { knowledge: 1 }, { morale: 1 }, { leadership: 1 }, { balance: 1 }]
          : [{ knowledge: -1 }, { determination: -1 }, { morale: -1 }, { leadership: -1 }, { balance: -1 }]
        : [{ determination: 1 }, { morale: 1 }, { leadership: 1 }, { knowledge: 1 }, { balance: 1 }];

      for (const fallback of fallbackSequence) {
        const applied = this.applyEffects(fallback);
        if (hasAnyDelta(applied)) {
          mergeDelta(statDelta, applied);
          break;
        }
      }
    }
    feedback.statDelta = statDelta;

    this.state.pendingFeedback = feedback;
    this.save();

    return clone(feedback);
  }

  advance() {
    const chapter = this.getCurrentChapter();
    if (!chapter) return { done: true };

    if (this.state.pendingFeedback) {
      this.state.transitionLine = this.state.pendingFeedback.transitionLine || null;
      this.state.pendingFeedback = null;
    }

    const nextSceneIndex = this.state.sceneIndex + 1;
    if (chapter.scenes && nextSceneIndex < chapter.scenes.length) {
      this.state.sceneIndex = nextSceneIndex;
      this.save();
      return { done: false };
    }

    if (!this.state.completedChapterIds.includes(chapter.id)) {
      this.state.completedChapterIds.push(chapter.id);
    }

    const nextChapterIndex = this.state.chapterIndex + 1;
    if (this.season.chapters[nextChapterIndex]) {
      this.state.chapterIndex = nextChapterIndex;
      this.state.sceneIndex = 0;
      this.state.transitionLine = `Nuovo capitolo: ${this.season.chapters[nextChapterIndex].title}`;
      this.save();
      return { done: false, chapterAdvanced: true };
    }

    this.save();
    return { done: true };
  }

  snapshot() {
    return {
      state: clone(this.state),
      chapter: clone(this.getCurrentChapter()),
      scene: clone(this.getCurrentScene()),
      feedback: clone(this.state.pendingFeedback),
      sourceBook: {
        title: this.sourceBook.title,
        pdfPath: this.sourceBook.pdfPath
      },
      volleyballMirror: this.getVolleyballMirror(),
      ipaImpact: this.getIpaImpact()
    };
  }
}
