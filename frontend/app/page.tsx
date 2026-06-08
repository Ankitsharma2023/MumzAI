"use client";

import { useEffect, useRef, useState } from "react";
import { sendChat, Turn } from "@/lib/api";
import { Lang, STRINGS } from "@/lib/i18n";
import ChatMessage, { Message } from "@/components/ChatMessage";

export default function Home() {
  const [lang, setLang] = useState<Lang>("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tick, setTick] = useState(0);
  const [listening, setListening] = useState(false);
  const [speechOk, setSpeechOk] = useState(false);
  const [clarifySel, setClarifySel] = useState<Record<number, string>>({});
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  const t = STRINGS[lang];
  // Suggestions stay stable — we just hide anything already asked in this chat,
  // so the next unused ones take their place (no distracting auto-rotation).
  const asked = new Set(
    messages.filter((m) => m.role === "user").map((m) => m.text.trim().toLowerCase())
  );
  const visibleSugs = t.suggestions
    .filter((s) => !asked.has(s.trim().toLowerCase()))
    .slice(0, 4);

  // Auto-scroll to the newest message.
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Rotate the loading message every 1.4s so the wait feels alive.
  useEffect(() => {
    if (!loading) return;
    setTick(0);
    const id = setInterval(() => setTick((x) => x + 1), 1400);
    return () => clearInterval(id);
  }, [loading]);

  // Does this browser support speech recognition? (Chrome/Edge yes.)
  useEffect(() => {
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setSpeechOk(!!SR);
  }, []);

  async function ask(question: string) {
    const q = question.trim();
    if (!q || loading) return;
    // Recent turns BEFORE this question = the memory we send to the bot.
    const history: Turn[] = messages
      .slice(-8)
      .map((m) => ({ role: m.role === "bot" ? "assistant" : "user", content: m.text }));
    // Product IDs already shown, so "compare them"/"the first one" resolve correctly.
    const contextIds = messages
      .filter((m) => m.role === "bot" && m.response)
      .flatMap((m) => m.response!.products.map((p) => p.id))
      .slice(-6);
    setInput("");
    setClarifySel({}); // clear any pending MCQ selections
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const response = await sendChat(q, lang, history, contextIds);
      setMessages((m) => [...m, { role: "bot", text: response.answer, response }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "bot", text: "Sorry — I couldn't reach the assistant. Is the backend running?" },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus(); // keep cursor in the box for the next question
    }
  }

  // Clicking the logo starts a fresh conversation.
  function resetChat() {
    setMessages([]);
    setInput("");
    setClarifySel({});
  }

  // Compose the selected MCQ answers into one message and search.
  function clarifyContinue() {
    const last = messages[messages.length - 1];
    const qs = last?.response?.clarifying_questions ?? [];
    const parts = qs
      .map((q, i) => (clarifySel[i] ? `${q.question} ${clarifySel[i]}` : null))
      .filter((x): x is string => Boolean(x));
    if (parts.length === 0) return;
    ask(parts.join("; "));
  }

  // Voice input — browser speech-to-text in the current language (no Gemini cost).
  function toggleVoice() {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;
    const rec = new SR();
    rec.lang = lang === "ar" ? "ar-SA" : "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setListening(false);
      ask(transcript); // auto-send what was spoken
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    setListening(true);
    rec.start();
  }

  return (
    <div className="page" dir={t.dir}>
      {/* Header */}
      <header className="header">
        <div className="brand">
          <button type="button" className="brand-reset" onClick={resetChat} title="Start over" aria-label="Start over">
            <img className="brand-logo-img" src="/mumzworld-logo.svg" alt="Mumzworld" />
          </button>
          <span className="brand-pill">
            <img src="/images/agent-smiley.svg" alt="" /> {t.title}
          </span>
        </div>
        <button className="lang-btn" onClick={() => setLang(lang === "en" ? "ar" : "en")}>
          {t.langButton}
        </button>
      </header>

      {/* Chat history */}
      <div className="chat" ref={chatRef}>
        {messages.length === 0 && <div className="empty">{t.empty}</div>}
        {messages.map((m, i) => (
          <ChatMessage
            key={i}
            m={m}
            lang={lang}
            active={i === messages.length - 1 && !loading}
            clarifySel={clarifySel}
            onClarifySelect={(qi, opt) =>
              setClarifySel((s) => ({ ...s, [qi]: opt }))
            }
            onClarifyContinue={clarifyContinue}
          />
        ))}
        {loading && (
          <div className="msg msg-bot">
            <div className="msg-head">
              <img className="avatar" src="/images/agent-smiley.svg" alt="Mumz" />
              <span className="who">{t.bot}</span>
            </div>
            <div className="loading-line">
              <span className="loading-msg">{t.loadingMsgs[tick % t.loadingMsgs.length]}</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick suggestions */}
      <div className="suggestions">
        {visibleSugs.map((s, k) => (
          <button key={`${k}-${s}`} className="suggestion" onClick={() => ask(s)} disabled={loading}>
            {s}
          </button>
        ))}
      </div>

      {/* Composer */}
      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={listening ? t.listening : t.placeholder}
        />
        {speechOk && (
          <button
            type="button"
            className={"mic-btn" + (listening ? " mic-on" : "")}
            onClick={toggleVoice}
            disabled={loading}
            title={t.mic}
            aria-label={t.mic}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
              <path d="M17 11a1 1 0 1 1 2 0 7 7 0 0 1-6 6.93V20h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.07A7 7 0 0 1 5 11a1 1 0 1 1 2 0 5 5 0 0 0 10 0z" />
            </svg>
          </button>
        )}
        <button type="submit" disabled={loading || !input.trim()}>
          {t.send}
        </button>
      </form>
    </div>
  );
}
