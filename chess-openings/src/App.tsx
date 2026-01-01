import { useState } from "react";
import { book } from "./domain/book";
import type { Side, Stars } from "./domain/types";
import { OpeningList } from "./components/OpeningList";
import { OpeningTrainer } from "./components/OpeningTrainer";

export default function App() {
  const [selected, setSelected] = useState<string | null>(null);
  const [level, setLevel] = useState<Stars>(1);
  const [trainingSide, setTrainingSide] = useState<Side>("w");

  if (!selected) {
    return <OpeningList openings={book.openings} onSelect={setSelected} />;
  }

  return (
    <OpeningTrainer
      openingId={selected}
      level={level}
      trainingSide={trainingSide}
      onBack={() => setSelected(null)}
      onChangeLevel={setLevel}
      onChangeSide={setTrainingSide}
    />
  );
}
