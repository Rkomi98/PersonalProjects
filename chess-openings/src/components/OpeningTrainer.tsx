import { useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";

import type { Stars, Side } from "../domain/types";
import { getOpening, getNode } from "../domain/book";
import { classifyMove, findMoveOption, pickAutoMove } from "../domain/trainer";
import { FeedbackPanel, type FeedbackMsg } from "./FeedbackPanel";

function clampBoardWidth() {
  return Math.min(window.innerWidth - 24, 520);
}

function uid() {
  return Math.random().toString(16).slice(2);
}

function promotionIfNeeded(piece: string, targetSquare: string) {
  // piece es. "wP", "bP"
  if (!piece || piece[1] !== "P") return undefined;
  const rank = targetSquare[1];
  if (rank === "8" || rank === "1") return "q";
  return undefined;
}

type NodeState =
  | { type: "book"; nodeId: string }
  | { type: "free" }; // fuori dataset (continui senza guida)

export function OpeningTrainer(props: {
  openingId: string;
  level: Stars;
  trainingSide: Side;
  onBack: () => void;
  onChangeLevel: (lvl: Stars) => void;
  onChangeSide: (side: Side) => void;
}) {
  const opening = getOpening(props.openingId);
  const gameRef = useRef(new Chess());

  const [boardWidth, setBoardWidth] = useState(clampBoardWidth());
  const [fen, setFen] = useState(gameRef.current.fen());
  const [nodeState, setNodeState] = useState<NodeState>(() => ({
    type: "book",
    nodeId: opening?.root ?? ""
  }));
  const [messages, setMessages] = useState<FeedbackMsg[]>([]);
  const canUndo = canUndoLastTurn();

  useEffect(() => {
    const onResize = () => setBoardWidth(clampBoardWidth());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  // reset quando cambia apertura
  useEffect(() => {
    gameRef.current.reset();
    setFen(gameRef.current.fen());

    const op = getOpening(props.openingId);
    if (op?.root) setNodeState({ type: "book", nodeId: op.root });
    else setNodeState({ type: "free" });

    setMessages([]);
  }, [props.openingId]);

  const currentNode = useMemo(() => {
    if (nodeState.type !== "book") return undefined;
    return getNode(nodeState.nodeId);
  }, [nodeState]);

  // Auto-mossa quando è il turno dell’avversario (se siamo nel libro)
  useEffect(() => {
    maybeAutoMove();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodeState, props.level, props.trainingSide]);

  function pushMessage(msg: Omit<FeedbackMsg, "id">) {
    setMessages(prev => {
      const next = [...prev, { ...msg, id: uid() }];
      return next.slice(-6);
    });
  }

  function restart() {
    gameRef.current.reset();
    setFen(gameRef.current.fen());
    if (opening?.root) setNodeState({ type: "book", nodeId: opening.root });
    else setNodeState({ type: "free" });
    setMessages([]);
  }

  function canUndoLastTurn() {
    const history = gameRef.current.history({ verbose: true }) as { color: Side }[];
    if (history.length === 0) return false;

    const last = history[history.length - 1];
    if (last.color === props.trainingSide) return true;

    if (history.length < 2) return false;
    return history[history.length - 2].color === props.trainingSide;
  }

  function nodeStateFromHistory(history: string[]): NodeState {
    const op = getOpening(props.openingId);
    if (!op?.root) return { type: "free" };

    let nodeId = op.root;
    for (const san of history) {
      const node = getNode(nodeId);
      if (!node) return { type: "free" };

      const option = findMoveOption(node, san, props.level);
      if (!option?.leadsTo) return { type: "free" };
      nodeId = option.leadsTo;
    }

    return { type: "book", nodeId };
  }

  function undoLastTurn() {
    const g = gameRef.current;
    const history = g.history({ verbose: true }) as { color: Side }[];
    if (history.length === 0) return;

    const last = history[history.length - 1];
    let movesToUndo = 0;
    if (last.color === props.trainingSide) {
      movesToUndo = 1;
    } else if (history.length >= 2 && history[history.length - 2].color === props.trainingSide) {
      movesToUndo = 2;
    } else {
      return;
    }

    for (let i = 0; i < movesToUndo; i += 1) {
      g.undo();
    }

    setFen(g.fen());
    setNodeState(nodeStateFromHistory(g.history()));
    setMessages([]);
  }

  function maybeAutoMove() {
    if (nodeState.type !== "book") return;

    const g = gameRef.current;
    if (g.turn() === props.trainingSide) return; // turno utente

    const node = getNode(nodeState.nodeId);
    if (!node) return;

    const auto = pickAutoMove(node, props.level);
    if (!auto) return;

    const res = g.move(auto.san);
    if (!res) return;

    pushMessage({
      by: "system",
      san: auto.san,
      kind: auto.kind,
      title: node.title ?? "Risposta",
      text: auto.why
    });

    setFen(g.fen());

    if (auto.leadsTo) {
      setNodeState({ type: "book", nodeId: auto.leadsTo });
    } else {
      setNodeState({ type: "free" });
      pushMessage({
        by: "system",
        title: "Fuori percorso",
        text: "La risposta era nel dataset, ma la posizione successiva non è ancora modellata. Puoi continuare in free mode oppure riavviare."
      });
    }
  }

  function onPieceDrop(sourceSquare: string, targetSquare: string, piece: string) {
    const g = gameRef.current;

    // blocca input se non è il turno del lato allenato
    if (g.turn() !== props.trainingSide) return false;

    const promo = promotionIfNeeded(piece, targetSquare);

    const move = g.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: promo as any
    });

    if (!move) return false;

    setFen(g.fen());

    if (nodeState.type !== "book") {
      pushMessage({
        by: "user",
        san: move.san,
        kind: "playable",
        title: "Free mode",
        text: "Mossa legale, ma sei fuori dal dataset di questa apertura. Per feedback più preciso, torna nel percorso o riavvia."
      });
      return true;
    }

    const node = getNode(nodeState.nodeId);
    if (!node) {
      setNodeState({ type: "free" });
      return true;
    }

    const { kind, option } = classifyMove(node, move.san, props.level);

    pushMessage({
      by: "user",
      san: move.san,
      kind,
      title: node.title ?? "La tua mossa",
      text: option?.why ?? "Mossa legale. In livello base siamo tolleranti: se vuoi restare nel percorso, prova una mossa di repertorio."
    });

    // Avanza nel libro se possibile, altrimenti entri in free mode (per non desincronizzare nodo/posizione)
    if (option?.leadsTo) {
      setNodeState({ type: "book", nodeId: option.leadsTo });
    } else {
      setNodeState({ type: "free" });

      pushMessage({
        by: "system",
        title: option ? "Nodo non ancora modellato" : "Fuori percorso (deviazione)",
        text: option
          ? "Questa mossa è nel dataset, ma la posizione successiva non è ancora descritta. Continuiamo in free mode."
          : "Questa deviazione non è coperta dal dataset. Continuiamo senza guida fino al restart."
      });
    }

    return true;
  }

  if (!opening) {
    return (
      <div className="screen">
        <button className="ghost" onClick={props.onBack}>← Aperture</button>
        <div className="muted">Apertura non trovata.</div>
      </div>
    );
  }

  return (
    <div className="screen">
      <div className="topbar">
        <button className="ghost" onClick={props.onBack}>← Aperture</button>
        <div className="topbar-title">
          <div className="title">{opening.name}</div>
          <div className="subtitle">{opening.subtitle}</div>
        </div>
      </div>

      <div className="controls">
        <div className="control">
          <span className="label">Livello</span>
          <select
            value={props.level}
            onChange={(e) => props.onChangeLevel(Number(e.target.value) as Stars)}
          >
            <option value={1}>⭐ Base</option>
            <option value={3}>⭐⭐⭐ Intermedio</option>
            <option value={5}>⭐⭐⭐⭐⭐ Avanzato</option>
          </select>
        </div>

        <div className="control">
          <span className="label">Alleni</span>
          <select
            value={props.trainingSide}
            onChange={(e) => props.onChangeSide(e.target.value as Side)}
          >
            <option value={"w"}>Bianco</option>
            <option value={"b"}>Nero</option>
          </select>
        </div>

        <button className="btn" onClick={undoLastTurn} disabled={!canUndo}>Undo</button>
        <button className="btn" onClick={restart}>Restart</button>
      </div>

      <div className="board-wrap">
        <Chessboard
          position={fen}
          boardWidth={boardWidth}
          onPieceDrop={onPieceDrop}
          arePiecesDraggable={gameRef.current.turn() === props.trainingSide}
          boardOrientation={props.trainingSide === "w" ? "white" : "black"}
        />
      </div>

      {currentNode?.idea && (
        <div className="idea">
          <h2 className="section-title">Idea della posizione</h2>
          <div className="idea-text">{currentNode.idea}</div>

          {(currentNode.plans?.w?.length || currentNode.plans?.b?.length) && (
            <div className="plans">
              {currentNode.plans?.w?.length ? (
                <div>
                  <div className="plans-title">Piani Bianco</div>
                  <ul>
                    {currentNode.plans.w.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              ) : null}

              {currentNode.plans?.b?.length ? (
                <div>
                  <div className="plans-title">Piani Nero</div>
                  <ul>
                    {currentNode.plans.b.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              ) : null}
            </div>
          )}
        </div>
      )}

      <FeedbackPanel messages={messages} />
    </div>
  );
}
