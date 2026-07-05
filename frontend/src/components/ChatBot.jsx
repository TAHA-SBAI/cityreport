import { useState, useEffect, useRef } from "react";
import { api } from "../api";

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "bot", text: "Bonjour 👋 Je suis l'assistant de CityReport. Posez-moi une question sur l'application !" },
  ]);
  const [suggestions, setSuggestions] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const bodyRef = useRef(null);

  useEffect(() => {
    api.assistantSuggestions().then((d) => setSuggestions(d.suggestions)).catch(() => {});
  }, []);

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, typing]);

  async function send(text) {
    const question = (text || input).trim();
    if (!question) return;
    setMessages((m) => [...m, { from: "user", text: question }]);
    setInput("");
    setSuggestions([]);
    setTyping(true);
    try {
      const r = await api.assistantMessage(question);
      // Petit délai pour un effet naturel
      setTimeout(() => {
        setMessages((m) => [...m, { from: "bot", text: r.reponse }]);
        setTyping(false);
      }, 400);
    } catch (e) {
      setTyping(false);
      setMessages((m) => [...m, { from: "bot", text: "Désolé, je n'ai pas pu répondre. Réessayez." }]);
    }
  }

  if (!open) {
    return (
      <button className="chat-fab" onClick={() => setOpen(true)} title="Assistant CityReport">
        💬
      </button>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="ch-title">
          <div className="ch-avatar">🤖</div>
          <div>
            <div className="ch-name">Assistant CityReport</div>
            <div className="ch-status">● En ligne</div>
          </div>
        </div>
        <button className="chat-close" onClick={() => setOpen(false)}>×</button>
      </div>

      <div className="chat-body" ref={bodyRef}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.from}`}>{m.text}</div>
        ))}

        {suggestions.length > 0 && (
          <div className="chat-suggestions">
            {suggestions.map((s, i) => (
              <button key={i} className="chat-sugg" onClick={() => send(s)}>{s}</button>
            ))}
          </div>
        )}

        {typing && <div className="chat-typing">L'assistant écrit…</div>}
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Écrivez votre question…"
        />
        <button className="chat-send" onClick={() => send()}>➤</button>
      </div>
    </div>
  );
}
