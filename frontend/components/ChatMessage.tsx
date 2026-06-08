import { ChatResponse } from "@/lib/api";
import { Lang, STRINGS } from "@/lib/i18n";
import ProductCard from "./ProductCard";

export interface Message {
  role: "user" | "bot";
  text: string;
  response?: ChatResponse; // present on bot messages
}

// Render **bold** markdown as dark-pink highlights (no visible asterisks).
function renderHighlights(text: string) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) =>
    i % 2 === 1 ? (
      <strong key={i} className="hl">{part}</strong>
    ) : (
      part
    )
  );
}

export default function ChatMessage({
  m,
  lang,
  active = false,
  clarifySel,
  onClarifySelect,
  onClarifyContinue,
}: {
  m: Message;
  lang: Lang;
  active?: boolean; // only the latest bot message has interactive MCQ chips
  clarifySel?: Record<number, string>;
  onClarifySelect?: (qi: number, opt: string) => void;
  onClarifyContinue?: () => void;
}) {
  const t = STRINGS[lang];
  const isUser = m.role === "user";
  const clarify = m.response?.clarifying_questions ?? [];

  return (
    <div className={"msg " + (isUser ? "msg-user" : "msg-bot")}>
      <div className="msg-head">
        {!isUser && <img className="avatar" src="/images/agent-smiley.svg" alt="Mumz" />}
        <span className="who">{isUser ? t.you : t.bot}</span>
      </div>
      <div className="bubble">{renderHighlights(m.text)}</div>

      {/* Bot-only extras */}
      {!isUser && m.response && (
        <>
          {m.response.safety_notes && (
            <div className="safety">⚠️ {m.response.safety_notes}</div>
          )}

          {/* MCQ clarifying questions (only interactive on the latest message) */}
          {active && clarify.length > 0 && (
            <div className="clarify">
              {clarify.map((q, qi) => (
                <div key={qi} className="clarify-q">
                  <div className="clarify-qtext">{q.question}</div>
                  <div className="clarify-opts">
                    {q.options.map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        className={"clarify-opt" + (clarifySel?.[qi] === opt ? " sel" : "")}
                        onClick={() => onClarifySelect?.(qi, opt)}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
              <button
                type="button"
                className="clarify-go"
                disabled={!clarifySel || Object.keys(clarifySel).length === 0}
                onClick={() => onClarifyContinue?.()}
              >
                {t.getRecs}
              </button>
            </div>
          )}

          {m.response.products.length > 0 && (
            <div className="cards">
              {m.response.products.map((p) => (
                <ProductCard key={p.id} p={p} lang={lang} />
              ))}
            </div>
          )}

          <div className="meta">
            <span className={"badge-conf conf-" + m.response.confidence}>
              {m.response.confidence}
            </span>{" "}
            {t.confidence} · {m.response.latency_ms} ms ·{" "}
            retrieved {m.response.retrieved_ids.join(", ") || "—"}
          </div>
        </>
      )}
    </div>
  );
}
