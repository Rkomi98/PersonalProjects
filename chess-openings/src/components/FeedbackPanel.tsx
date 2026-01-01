import type { MoveKind } from "../domain/types";
import { kindEmoji, kindLabel } from "../domain/trainer";

export type FeedbackMsg = {
  id: string;
  by: "user" | "system";
  san?: string;
  kind?: MoveKind;
  title: string;
  text: string;
};

export function FeedbackPanel(props: { messages: FeedbackMsg[] }) {
  return (
    <div className="feedback">
      <h2 className="section-title">Feedback</h2>

      {props.messages.length === 0 ? (
        <div className="muted">Fai una mossa per iniziare.</div>
      ) : (
        <div className="msgs">
          {props.messages.map(m => (
            <div key={m.id} className={`msg ${m.by}`}>
              <div className="msg-head">
                <span className="msg-by">{m.by === "user" ? "Tu" : "Guida"}</span>
                {m.kind && (
                  <span className="msg-kind">
                    {kindEmoji(m.kind)} {kindLabel(m.kind)}
                    {m.san ? ` • ${m.san}` : ""}
                  </span>
                )}
              </div>
              <div className="msg-title">{m.title}</div>
              <div className="msg-text">{m.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
