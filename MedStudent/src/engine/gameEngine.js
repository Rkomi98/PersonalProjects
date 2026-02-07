const STORAGE_KEY = "medstudent-rpg-save-v1";

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
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
    Object.entries(effects).forEach(([stat, delta]) => {
      const def = this.season.stats[stat];
      if (!def || typeof this.state.stats[stat] !== "number") return;
      this.state.stats[stat] = clamp(this.state.stats[stat] + delta, def.min, def.max);
    });
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
      exam: scene.teacherAsk || null,
      sourcePrimary: this.getSourceEntry(scene.sourceKey),
      sourceSecondary: this.getSourceEntry(scene.extraSourceKey),
      correct: null
    };

    if (scene.type === "choice") {
      this.applyEffects(option.effects);
      this.addTags(option.tags);
      this.state.history.push({ sceneId: scene.id, type: scene.type, optionIndex });
    }

    if (scene.type.startsWith("quiz_")) {
      const correct = Boolean(option.correct);
      feedback.correct = correct;

      if (correct) {
        feedback.title = "Risposta corretta";
        feedback.text = option.why;
        this.applyEffects(scene.onCorrect);
      } else {
        feedback.title = "Risposta da recuperare";
        feedback.text = `${option.why} Recupero: rivedi il razionale e riparti subito, senza game over.`;
        this.applyEffects(scene.onWrong);
      }

      const correctOption = scene.options.find((item) => item.correct);
      feedback.correctAnswer = correctOption ? correctOption.text : null;
      this.state.history.push({
        sceneId: scene.id,
        type: scene.type,
        optionIndex,
        correct
      });
    }

    this.state.pendingFeedback = feedback;
    this.save();

    return clone(feedback);
  }

  advance() {
    const chapter = this.getCurrentChapter();
    if (!chapter) return { done: true };

    if (this.state.pendingFeedback) {
      this.state.pendingFeedback = null;
    }

    const nextSceneIndex = this.state.sceneIndex + 1;
    if (chapter.scenes && nextSceneIndex < chapter.scenes.length) {
      this.state.sceneIndex = nextSceneIndex;
      this.save();
      return { done: false };
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
