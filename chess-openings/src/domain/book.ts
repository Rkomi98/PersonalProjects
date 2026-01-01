import raw from "../data/openingBook_definitivo.json";
import type { OpeningBook, OpeningNode, OpeningSummary } from "./types";

export const book = raw as unknown as OpeningBook;

export function getOpening(id: string): OpeningSummary | undefined {
  return book.openings.find(o => o.id === id);
}

export function getNode(nodeId: string): OpeningNode | undefined {
  return book.nodes[nodeId];
}
