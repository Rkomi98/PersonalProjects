export type Stars = 1 | 3 | 5;
export type Side = "w" | "b";
export type MoveKind = "repertoire" | "playable" | "typical_error";

export interface MoveOption {
  san: string;          // SAN: "e4", "Nf3", "O-O", "exd5", ...
  kind: MoveKind;
  stars: Stars;         // 1 (base), 3 (intermedio), 5 (avanzato)
  why: string;          // feedback concettuale (no engine)
  leadsTo?: string;     // id nodo figlio (se modellato)
  tags?: string[];      // opzionale: "centro", "sviluppo", ...
}

export interface OpeningNode {
  id: string;
  openingId: string;

  fen: string;
  turn: Side;
  stars: Stars;

  title?: string;
  idea?: string;

  plans?: {
    w?: string[];
    b?: string[];
  };

  moves: MoveOption[];

  auto?: {
    pick: "first_repertoire" | "first_any" | "none";
  };
}

export interface OpeningSummary {
  id: string;
  name: string;
  subtitle?: string;
  root: string;
  tags?: string[];
  status?: "ready" | "stub";
}

export interface OpeningBook {
  version: number;
  openings: OpeningSummary[];
  nodes: Record<string, OpeningNode>;
}
