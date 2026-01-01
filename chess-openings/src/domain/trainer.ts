import type { MoveKind, MoveOption, OpeningNode, Stars } from "./types";

export function visibleMoves(node: OpeningNode, level: Stars): MoveOption[] {
  return node.moves.filter(m => m.stars <= level);
}

export function findMoveOption(node: OpeningNode, san: string, level: Stars): MoveOption | undefined {
  return visibleMoves(node, level).find(m => m.san === san);
}

export function classifyMove(
  node: OpeningNode,
  san: string,
  level: Stars
): { kind: MoveKind; option?: MoveOption } {
  const opt = findMoveOption(node, san, level);
  if (opt) return { kind: opt.kind, option: opt };

  // legale ma non nel percorso: in base siamo tolleranti (è "giocabile" ma fuori repertorio)
  return { kind: "playable" };
}

export function pickAutoMove(node: OpeningNode, level: Stars): MoveOption | undefined {
  if (!node.auto || node.auto.pick === "none") return undefined;

  const moves = visibleMoves(node, level);
  if (moves.length === 0) return undefined;

  if (node.auto.pick === "first_any") return moves[0];

  // first_repertoire
  return moves.find(m => m.kind === "repertoire") ?? moves[0];
}

export function kindLabel(kind: MoveKind): string {
  switch (kind) {
    case "repertoire": return "Mossa consigliata";
    case "playable": return "Mossa ok";
    case "typical_error": return "Errore tipico";
  }
}

export function kindEmoji(kind: MoveKind): string {
  switch (kind) {
    case "repertoire": return "✅";
    case "playable": return "🟡";
    case "typical_error": return "⛔";
  }
}
