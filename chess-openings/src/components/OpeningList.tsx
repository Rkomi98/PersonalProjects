import type { OpeningSummary } from "../domain/types";

export function OpeningList(props: {
  openings: OpeningSummary[];
  onSelect: (id: string) => void;
}) {
  return (
    <div className="screen">
      <h1 className="title">Aperture</h1>
      <p className="subtitle">Scegli un percorso guidato (mobile-first, offline, no engine).</p>

      <div className="list">
        {props.openings.map(o => (
          <button
            key={o.id}
            className="card"
            onClick={() => props.onSelect(o.id)}
          >
            <div className="card-title">
              {o.name} {o.status === "stub" ? "🧩" : "⭐"}
            </div>
            {o.subtitle && <div className="card-sub">{o.subtitle}</div>}
            {o.tags && <div className="card-tags">{o.tags.join(" • ")}</div>}
            {o.status === "stub" && <div className="card-hint">Dataset in arrivo</div>}
          </button>
        ))}
      </div>
    </div>
  );
}
