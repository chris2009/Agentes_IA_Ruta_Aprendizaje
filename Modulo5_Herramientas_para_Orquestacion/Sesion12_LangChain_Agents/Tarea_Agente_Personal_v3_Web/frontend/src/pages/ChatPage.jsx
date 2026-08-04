import { useState } from "react";
import { Send } from "lucide-react";
import { sendChat } from "../api/client.js";
import Banner from "../components/Banner.jsx";
import ChatBubble from "../components/ChatBubble.jsx";

export default function ChatPage() {
  const [historial, setHistorial] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const enviar = (evento) => {
    evento.preventDefault();

    if (!mensaje.trim()) return;

    const textoUsuario = mensaje;
    setHistorial([...historial, { role: "user", content: textoUsuario }]);
    setMensaje("");
    setError("");
    setCargando(true);

    sendChat(textoUsuario, historial)
      .then((res) => setHistorial(res.history))
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  };

  return (
    <section className="chat-page">
      <h1>Chat con el agente</h1>

      <div className="chat-window">
        {!historial.length && (
          <div className="empty-state">
            <span>Pregúntale algo como "qué actividades tengo pendientes" o "arma mi plan de 14:00 a 20:00 hoy".</span>
          </div>
        )}
        {historial.map((m, i) => (
          <ChatBubble key={i} role={m.role} content={m.content} />
        ))}
        {cargando && <ChatBubble role="assistant" content="Pensando…" />}
      </div>

      <Banner type="error">{error}</Banner>

      <form className="chat-form" onSubmit={enviar}>
        <input
          value={mensaje}
          onChange={(e) => setMensaje(e.target.value)}
          placeholder="Ej: qué actividades tengo pendientes"
          disabled={cargando}
        />
        <button type="submit" className="btn-primary" disabled={cargando}>
          <Send />
          Enviar
        </button>
      </form>
    </section>
  );
}
